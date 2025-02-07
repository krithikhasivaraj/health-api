from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Use local or Atlas URI
client = MongoClient(MONGO_URI)
db = client.health_data  # Database name
collection = db.health_records  # Collection name

@app.route('/health-data', methods=['GET'])
def get_health_data():
    """Fetch stored health data from MongoDB for a specific user."""
    try:
        user_id = request.args.get("user_id")  # Get user_id from query parameters
        if not user_id:
            return jsonify({"error": "Missing user_id parameter"}), 400

        # Fetch health records for the given user_id
        data = list(collection.find({"user_id": user_id}, {"_id": 0}))  # Exclude MongoDB's _id field

        if not data:
            return jsonify({"error": "No health data found for this user"}), 404

        return jsonify(data), 200
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return jsonify({"error": "Failed to fetch health data"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
