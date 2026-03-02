import insightface
import numpy as np
import cv2
from pymongo import MongoClient

THRESHOLD = 0.35

# ===============================
# CONNECT TO ATLAS
# ===============================
MONGO_URI = "mongodb+srv://Swarna:reddy@cluster0.rxezs.mongodb.net/attendance_db?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client["attendance_db"]
students_col = db["Students"]

# ===============================
# LOAD EMBEDDINGS ONCE
# ===============================
def load_embeddings():
    face_db = {}
    students = students_col.find({"embedding": {"$exists": True}})

    for student in students:
        face_db[student["name"]] = np.array(student["embedding"])

    print("Loaded identities:", list(face_db.keys()))
    return face_db

FACE_DB = load_embeddings()

# ===============================
# LOAD INSIGHTFACE MODEL
# ===============================
app = insightface.app.FaceAnalysis(
    providers=['CPUExecutionProvider']
)
app.prepare(ctx_id=-1)

# ===============================
# BLUR FILTER
# ===============================
def blur_score(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# ===============================
# MATCH FUNCTION
# ===============================
def match_embedding(embedding):
    best_name = "Unknown"
    best_score = -1

    for name, ref in FACE_DB.items():
        score = float(np.dot(embedding, ref))

        if score > best_score:
            best_score = score
            best_name = name

    if best_score < THRESHOLD:
        return "Unknown", best_score

    return best_name, best_score

# ===============================
# MAIN FUNCTION USED BY FLASK
# ===============================
def recognize_faces(frame):

    results = []
    H, W = frame.shape[:2]

    faces = app.get(frame)

    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(W, x2)
        y2 = min(H, y2)

        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        if blur_score(crop) < 60:
            continue

        emb = face.embedding
        emb = emb / np.linalg.norm(emb)

        name, score = match_embedding(emb)

        results.append({
            "name": name,
            "score": float(score),
            "bbox": [x1, y1, x2, y2]
        })

    return results