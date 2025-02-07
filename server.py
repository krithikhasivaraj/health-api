from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# ✅ MongoDB Connection
MONGO_URI = "mongodb://localhost:27017"  # Change if using MongoDB Atlas
client = MongoClient(MONGO_URI)

# ✅ Select database & collection
db = client.health_data  # Database name
collection = db.health_records  # Collection name

@app.route("/health-data", methods=["GET", "POST"])
def health_data():
    """Handles health data uploads and retrieval."""
    
    if request.method == "GET":
        return jsonify({"message": "Use POST to upload health data"}), 200

    elif request.method == "POST":
        try:
            data = request.json
            print(f"📥 Received data: {data}")  # Debugging log

            user_id = data.get("user_id")
            health_data = data.get("data")

            if not user_id or not health_data:
                return jsonify({"error": "Missing user_id or data"}), 400

            for date, health_metrics in health_data.items():
                # ✅ Upsert: If record exists, update it; otherwise, insert new entry
                collection.update_one(
                    {"user_id": user_id, "date": date},  
                    {"$set": health_metrics},  
                    upsert=True
                )

            print(f"✅ Data successfully stored for user: {user_id}")
            return jsonify({"message": f"✅ Data saved for user {user_id}"}), 200

        except Exception as e:
            print(f"❌ Error processing request: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

@app.route("/get-user-data", methods=["GET"])
def get_health_data():
    """Fetches health data for a specific user from MongoDB."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        user_records = list(
            collection.find({"user_id": user_id}, {"_id": 0}).sort("date", 1)
        )

        if not user_records:
            return jsonify({"error": f"No data found for user {user_id}"}), 404

        return jsonify({"user_id": user_id, "data": user_records}), 200

    except Exception as e:
        print(f"❌ Error fetching data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/all-data", methods=["GET"])
def get_all_users_data():
    """Fetches all health data from MongoDB."""
    try:
        all_records = list(collection.find({}, {"_id": 0}))
        return jsonify({"all_users": all_records}), 200
    except Exception as e:
        print(f"❌ Error fetching all users' data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Allows external access
