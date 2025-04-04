from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Get MongoDB connection string from Railway environment variables
MONGO_URI = os.getenv("MONGO_URL", "mongodb://mongo:your-password@mongodb.railway.internal:27017/health_data")

try:
    client = MongoClient(MONGO_URI)
    db = client.health_data 
    collection = db.health_records
    client.admin.command("ping")
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"MongoDB Connection Failed: {e}")

@app.route('/health-data', methods=['GET'])
def get_health_data():
    """Fetch stored health data from MongoDB for a specific user with optional date filters."""
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id parameter"}), 400

        query = {"user_id": user_id}

        start_date = request.args.get("startDate")
        end_date = request.args.get("endDate")

        if start_date and end_date:
            query["date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["date"] = {"$gte": start_date}
        elif end_date:
            query["date"] = {"$lte": end_date}

        print(f"Querying MongoDB with: {query}")  # Debugging log
        data = list(collection.find(query, {"_id": 0}))

        if not data:
            return jsonify({"error": "No health data found for this user"}), 404

        return jsonify(data), 200

    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({"error": f"Failed to fetch health data: {str(e)}"}), 500

@app.route('/health-data', methods=['POST'])
def store_health_data():
    """Stores health data received via API request into MongoDB."""
    try:
        data = request.get_json()
        
        if not data or "user_id" not in data or "data" not in data:
            return jsonify({"error": "Invalid JSON format. Must include 'user_id' and 'data'."}), 400
        
        user_id = data["user_id"]
        health_data = data["data"]

        records = [{"user_id": user_id, "date": date, **values} for date, values in health_data.items()]
        
        if records:
            collection.insert_many(records)
            print(f"Successfully stored {len(records)} records in MongoDB!")
            return jsonify({"message": "Health data saved successfully!"}), 201
        else:
            return jsonify({"error": "No valid records to store."}), 400

    except Exception as e:
        print(f"Error storing data in MongoDB: {e}")
        return jsonify({"error": "Failed to save health data"}), 500

if __name__ == '__main__':
    print("Flask API is running and connected to MongoDB...")
    app.run(debug=True, host="0.0.0.0", port=8080)
