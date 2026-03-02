import os
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

MONGO_URI = "mongodb+srv://Swarna:reddy@cluster0.rxezs.mongodb.net/attendance_db"

client = MongoClient(MONGO_URI)
db = client["attendance_db"]

users_collection = db["users"]
attendance_collection = db["attendance"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register_page")
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data["name"]
    descriptor = data["descriptor"]

    users_collection.insert_one({
        "name": name,
        "descriptor": descriptor
    })

    return jsonify({"message": "User registered"})

@app.route("/users")
def get_users():
    users = list(users_collection.find({}, {"_id": 0}))
    return jsonify(users)

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    data = request.json
    name = data["name"]

    attendance_collection.insert_one({
        "name": name,
        "timestamp": datetime.now()
    })

    return jsonify({"message": "Attendance marked"})

@app.route("/records")
def records():
    records = list(attendance_collection.find({}, {"_id": 0}))
    return jsonify(records)

if __name__ == "__main__":
    app.run()
