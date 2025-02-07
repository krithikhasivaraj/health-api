from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = "all_users.json"  # Store all user data in one JSON file

# Ensure the file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)  # Start with an empty JSON object

@app.route("/health-data", methods=["GET", "POST"])
def health_data():
    """Handles GET and POST requests for health data."""

    if request.method == "GET":
        return jsonify({"message": "Use POST to upload health data"}), 200

    elif request.method == "POST":
        try:
            data = request.json
            print(f"📥 Received data: {json.dumps(data, indent=4)}")  # Debugging log

            user_id = data.get("user_id")
            health_data = data.get("data")

            if not user_id or not health_data:
                return jsonify({"error": "Missing user_id or data"}), 400

            # Load existing data
            with open(DATA_FILE, "r") as f:
                all_users_data = json.load(f)

            # If user does not exist, initialize their data
            if user_id not in all_users_data:
                all_users_data[user_id] = {}

            # Merge new data with existing user data
            for date, health_metrics in health_data.items():
                if date in all_users_data[user_id]:
                    # Sum step counts, distance, and active energy
                    all_users_data[user_id][date]["step_count"] += health_metrics.get("step_count", 0)
                    all_users_data[user_id][date]["distance"] += health_metrics.get("distance", 0.0)
                    all_users_data[user_id][date]["active_energy"] += health_metrics.get("active_energy", 0.0)

                    # Merge categories
                    for category, values in health_metrics.get("categories", {}).items():
                        if category in all_users_data[user_id][date]["categories"]:
                            all_users_data[user_id][date]["categories"][category].extend(values)
                        else:
                            all_users_data[user_id][date]["categories"][category] = values
                else:
                    all_users_data[user_id][date] = health_metrics

            # Save back to file
            with open(DATA_FILE, "w") as f:
                json.dump(all_users_data, f, indent=4)

            print(f"✅ Data successfully stored for user: {user_id}")
            return jsonify({"message": f"✅ Data saved for user {user_id}"}), 200

        except Exception as e:
            print(f"❌ Error processing request: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

@app.route("/get-data", methods=["GET"])
def get_health_data():
    """Returns health data for a specific user."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        # Load data
        with open(DATA_FILE, "r") as f:
            all_users_data = json.load(f)

        if user_id not in all_users_data:
            return jsonify({"error": "No data found for this user"}), 404

        return jsonify({"user_id": user_id, "data": all_users_data[user_id]})

    except Exception as e:
        print(f"❌ Error fetching data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/all-data", methods=["GET"])
def get_all_users_data():
    """Returns health data for all users."""
    try:
        with open(DATA_FILE, "r") as f:
            all_users_data = json.load(f)

        return jsonify(all_users_data)

    except Exception as e:
        print(f"❌ Error fetching all users' data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Allows external access
