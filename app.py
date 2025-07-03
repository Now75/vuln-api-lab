from flask import Flask, request, jsonify, render_template, redirect, session, url_for
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # Required for sessions

# Load user DB from file
with open('users.json') as f:
    users = json.load(f)

# --- Vulnerable API Login (BOLA Demo) ---
@app.route('/commerce/v1/<user_id>/login', methods=['POST'])
def login(user_id):
    data = request.get_json()

    user = users.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if data.get("password") == user["password"]:
        return jsonify({"message": f"Logged in as {user['username']} (userID={user_id})"}), 200

    return jsonify({"error": "Invalid credentials"}), 401

# --- Landing Page ---
@app.route('/')
def home():
    return render_template('index.html')

# --- Web Form Login Handler ---
@app.route('/web-login', methods=['POST'])
def web_login():
    username = request.form.get('username')
    password = request.form.get('password')

    for user_id, user in users.items():
        if user['username'] == username and user['password'] == password:
            return f"<h2>Login successful for user: {username} (userID={user_id})</h2>"

    return "<h3>Login failed: Invalid credentials</h3>", 401

@app.route('/secure-login', methods=['POST'])
def secure_login():
    username = request.form.get('username')
    password = request.form.get('password')

    for user_id, user in users.items():
        if user['username'] == username and user['password'] == password:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('dashboard'))

    return "<h3>Login failed: Invalid credentials</h3>", 401


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return f"""
        <h2>Welcome to your dashboard, {session['username']}!</h2>
        <p>Your session userID: {session['user_id']}</p>
        <a href="/logout">Logout</a>
    """


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# --- Run App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)