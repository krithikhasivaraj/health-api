from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# 🔹 Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/health_data")  # Change this if using MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client.health_data  # Database name
collection = db.health_records  # Collection name

@app.route('/health-data', methods=['GET'])
def get_health_data():
    """Fetch stored health data from MongoDB for a specific user with optional date filters."""
    try:
        user_id = request.args.get("user_id")  # Required
        start_date = request.args.get("startDate")  # Optional
        end_date = request.args.get("endDate")  # Optional

        if not user_id:
            return jsonify({"error": "Missing user_id parameter"}), 400

        # 🔹 Build MongoDB query
        query = {"user_id": user_id}
        if start_date and end_date:
            query["date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["date"] = {"$gte": start_date}
        elif end_date:
            query["date"] = {"$lte": end_date}

        print(f"🔍 Querying MongoDB with: {query}")  # Debugging log

        # 🔹 Fetch data from MongoDB
        data = list(collection.find(query, {"_id": 0}))  # Exclude MongoDB's _id field

        if not data:
            return jsonify({"error": "No health data found for this user"}), 404

        return jsonify(data), 200

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return jsonify({"error": "Failed to fetch health data"}), 500

if __name__ == '__main__':
    print("✅ Flask API is running and connected to MongoDB...")
    app.run(debug=True, host="0.0.0.0", port=8080)