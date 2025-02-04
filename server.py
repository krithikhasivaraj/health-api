from flask import Flask, request, jsonify
import json
import os
import datetime

app = Flask(__name__)
DATA_FILE = "health_data.json"

def load_health_data():
    """Load health data from a file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_health_data(data):
    """Save health data to a file."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@app.route('/health-data', methods=['GET'])
def get_health_data():
    """Return filtered health data based on startDate and endDate query parameters."""
    data = load_health_data()

    # Get startDate & endDate from query params
    start_date = request.args.get("startDate")  # Example: "2024-02-01"
    end_date = request.args.get("endDate")      # Example: "2024-02-07"

    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    # Filter records by date
    if isinstance(data, list):
        data = [
            record for record in data 
            if start_date <= datetime.datetime.strptime(record["start_date"], "%Y-%m-%d") <= end_date
        ]

    return jsonify(data)

@app.route('/health-data', methods=['POST'])
def update_health_data():
    """Receive and store new health data."""
    data = request.json
    save_health_data(data)
    return jsonify({"message": "✅ Health data saved successfully!"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
