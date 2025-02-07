from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection with error handling
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Local or Atlas URI
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # Timeout to detect connection issues
    db = client.health_data  # Database name
    collection = db.health_records  # Collection name
    client.admin.command("ping")  # Test MongoDB connection
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")
    exit(1)  # Stop server if DB connection fails

@app.route('/health-data', methods=['GET'])
def get_health_data():
    """Return stored health data from MongoDB."""
    try:
        data = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's "_id" field
        return jsonify(data), 200
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return jsonify({"error": "Failed to fetch health data"}), 500

@app.route('/health-data', methods=['POST'])
def update_health_data():
    """Receive and store new health data in MongoDB."""
    try:
        data = request.get_json()  # Ensure valid JSON
        if not data:
            return jsonify({"error": "Invalid JSON format"}), 400

        collection.insert_one(data)  # Store in MongoDB
        return jsonify({"message": "✅ Health data saved successfully!"}), 201
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        return jsonify({"error": "Failed to save health data"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
