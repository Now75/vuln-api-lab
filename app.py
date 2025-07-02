from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Load user DB from file
with open('users.json') as f:
    users = json.load(f)

@app.route('/commerce/v1/<user_id>/login', methods=['POST'])
def login(user_id):
    data = request.get_json()

    user = users.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if data.get("password") == user["password"]:
        return jsonify({"message": f"Logged in as {user['username']} (userID={user_id})"}), 200

    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
