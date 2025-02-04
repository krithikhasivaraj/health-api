from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Store health data in memory (or use a database)
health_data = {}

@app.route('/health-data', methods=['GET'])
def get_health_data():
    """Returns the filtered health data."""
    return jsonify(health_data)

@app.route('/health-data', methods=['POST'])
def update_health_data():
    """Updates the health data with new JSON from the client."""
    global health_data
    health_data = request.json  # Store the received JSON
    return jsonify({"message": "✅ Health data updated successfully!"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
