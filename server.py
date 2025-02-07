from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB (Local or Cloud)
MONGO_URI = "mongodb://localhost:27017"  # Change this if using MongoDB Atlas
client = MongoClient(MONGO_URI)

# Select database & collection
db = client.health_data_db  # Database name
collection = db.health_records  # Collection name

@app.route("/health-data", methods=["POST"])
def upload_health_data():
    """Receives health data and saves it in MongoDB."""
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    for date, health_metrics in data["data"].items():
        existing_entry = collection.find_one({"user_id": user_id, "date": date})

        if existing_entry:
            # Update the existing record
            collection.update_one(
                {"user_id": user_id, "date": date},
                {"$set": {
                    "step_count": existing_entry["step_count"] + health_metrics.get("step_count", 0),
                    "distance": existing_entry["distance"] + health_metrics.get("distance", 0.0),
                    "active_energy": existing_entry["active_energy"] + health_metrics.get("active_energy", 0.0),
                    "avg_heart_rate": health_metrics.get("avg_heart_rate", existing_entry.get("avg_heart_rate")),
                    "categories": health_metrics.get("categories", existing_entry.get("categories"))
                }}
            )
        else:
            # Insert new record
            collection.insert_one({
                "user_id": user_id,
                "date": date,
                "step_count": health_metrics.get("step_count", 0),
                "distance": health_metrics.get("distance", 0.0),
                "avg_heart_rate": health_metrics.get("avg_heart_rate"),
                "active_energy": health_metrics.get("active_energy", 0.0),
                "categories": health_metrics.get("categories", {})
            })

    return jsonify({"message": f"✅ Data saved for user {user_id}"}), 200

@app.route("/get-data", methods=["GET"])
def get_health_data():
    """Returns health data for a specific user."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    user_records = list(collection.find({"user_id": user_id}, {"_id": 0}))  # Exclude MongoDB's _id field

    if not user_records:
        return jsonify({"error": "No data found for this user"}), 404

    return jsonify({"user_id": user_id, "data": user_records})

@app.route("/all-data", methods=["GET"])
def get_all_users_data():
    """Returns all health data from MongoDB."""
    all_records = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's _id field
    return jsonify({"all_users": all_records})

if __name__ == "__main__":
    app.run(debug=True)
