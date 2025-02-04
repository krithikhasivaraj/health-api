from flask import Flask, request, jsonify
import json
import os

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
    """Return stored health data."""
    return jsonify(load_health_data())

@app.route('/health-data', methods=['POST'])
def update_health_data():
    """Receive and store new health data."""
    data = request.json
    save_health_data(data)
    return jsonify({"message": "✅ Health data saved successfully!"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
