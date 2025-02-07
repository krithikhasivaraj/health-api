from flask import Flask, request, jsonify
from pymongo import MongoClient
import json

app = Flask(__name__)

# ✅ Connect to MongoDB (Local or Atlas)
MONGO_URI = "mongodb://localhost:27017"  # Change this if using MongoDB Atlas
client = MongoClient(MONGO_URI)

# Select database & collection
db = client.health_data  # Database name
collection = db.health_records  # Collection name

@app.route("/health-data", methods=["POST"])
def upload_health_data():
    """Receives health data and saves it in MongoDB."""
    data = request.json
    user_id = data.get("user_id")

    if not user_id or "data" not in data:
        return jsonify({"error": "Missing user_id or data"}), 400

    records = []

    for date, health_metrics in data["data"].items():
        record = {
            "user_id": user_id,
            "date": date,
            "step_count": health_metrics.get("step_count", 0),
            "distance": health_metrics.get("distance", 0.0),
            "active_energy": health_metrics.get("active_energy", 0.0),
            "avg_heart_rate": health_metrics.get("avg_heart_rate"),
            "categories": health_metrics.get("categories", {})
        }
        records.append(record)

    try:
        # ✅ Prevent duplicates: Update existing or insert new entries
        for record in records:
            collection.update_one(
                {"user_id": record["user_id"], "date": record["date"]},  
                {"$set": record},  
                upsert=True  # If not found, insert it
            )

        return jsonify({"message": f"✅ Data successfully saved for user {user_id}"}), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/get-user-data", methods=["GET"])
def get_user_data():
    """Fetches health data for a specific user directly from MongoDB."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        # ✅ Fetch all health records for the user, sorted by date
        user_records = list(
            collection.find({"user_id": user_id}, {"_id": 0}).sort("date", 1)  # Sort in ascending order
        )

        if not user_records:
            return jsonify({"error": f"No data found for user {user_id}"}), 404

        return jsonify({"user_id": user_id, "data": user_records}), 200

    except Exception as e:
        return jsonify({"error": f"Database query error: {str(e)}"}), 500

@app.route("/all-data", methods=["GET"])
def get_all_users_data():
    """Returns all health data from MongoDB."""
    try:
        all_records = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB _id field
        return jsonify({"all_users": all_records})
    except Exception as e:
        return jsonify({"error": f"Database query error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
