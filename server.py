from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Use local or Atlas URI
client = MongoClient(MONGO_URI)
db = client.health_db  # Database name
collection = db.health_data  # Collection name

@app.route('/health-data', methods=['GET'])
def get_health_data():
    """Return stored health data from MongoDB."""
    data = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default "_id" field
    return jsonify(data)

@app.route('/health-data', methods=['POST'])
def update_health_data():
    """Receive and store new health data in MongoDB."""
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    collection.insert_one(data)  # Store in MongoDB
    return jsonify({"message": "✅ Health data saved successfully!"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
