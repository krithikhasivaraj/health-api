from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import traceback

app = Flask(__name__)

# === MongoDB Atlas Connection ===
MONGO_URI = os.getenv("MONGODB_URI")  # Ensure this is correctly set in Railway

try:
    client = MongoClient(MONGO_URI)  # ✅ Let pymongo auto-handle TLS
    db = client.health_data
    collection = db.health_records
    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")
    traceback.print_exc()


# === GET Route ===
@app.route('/health-data', methods=['GET'])
def get_health_data():
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

        print(f"🔍 Querying MongoDB with: {query}")
        data = list(collection.find(query, {"_id": 0}))

        if not data:
            return jsonify({"error": "No health data found for this user"}), 404

        return jsonify(data), 200

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch health data: {str(e)}"}), 500

# === POST Route ===
@app.route('/health-data', methods=['POST'])
def store_health_data():
    try:
        data = request.get_json(force=True)
        print("📦 Received Payload:", data)

        if not data or "user_id" not in data or "data" not in data:
            return jsonify({"error": "Invalid JSON format. Must include 'user_id' and 'data'."}), 400

        user_id = data["user_id"]
        health_data = data["data"]

        records = [{"user_id": user_id, "date": date, **values} for date, values in health_data.items()]
        print("📄 Records to insert:", records)

        if records:
            try:
                # TEST INSERT: to confirm DB works before batch insert
                collection.insert_one({"test_insert": True})
                print("✅ Test insert successful.")

                # ACTUAL INSERT
                collection.insert_many(records)
                print(f"✅ Inserted {len(records)} records.")
                return jsonify({"message": "Health data saved successfully!"}), 201

            except Exception as e:
                print(f"❌ MongoDB insert error: {e}")
                traceback.print_exc()
                return jsonify({"error": "Insert failed"}), 500
        else:
            return jsonify({"error": "No valid records to store."}), 400

    except Exception as e:
        print(f"❌ Error storing data in MongoDB: {e}")
        traceback.print_exc()
        return jsonify({"error": "Failed to save health data"}), 500

# === Root Test Route ===
@app.route("/", methods=["GET"])
def home():
    return "✅ Health API is running!"

# === Run the server ===
if __name__ == '__main__':
    print("🚀 Flask API is starting...")
    app.run(debug=True, host="0.0.0.0", port=8080)
