from flask import Flask, request, jsonify, render_template, redirect, session, url_for
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # Required for sessions

# --- Load Users and Orders ---
with open('users.json') as f:
    users = json.load(f)

with open('orders.json') as f:
    orders = json.load(f)

# --- Vulnerable API Login (BOLA Demo) ---
@app.route('/commerce/v1/<user_id>/login', methods=['POST'])
def vuln_login(user_id):
    data = request.get_json()
    user = users.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if data.get("password") == user["password"]:
        session['user_id'] = user_id
        session['username'] = user["username"]
        session['login_type'] = "vuln"
        return jsonify({"message": "Login successful", "redirect": "/vuln-dashboard"}), 200

    return jsonify({"error": "Invalid credentials"}), 401

# --- Vulnerable Orders Endpoint (BOLA) ---
@app.route('/commerce/v1/<user_id>/orders')
def vuln_orders(user_id):
    user_orders = orders.get(user_id)
    if user_orders is None:
        return jsonify({"error": "No orders found"}), 404

    return jsonify({
        "user_id": user_id,
        "orders": user_orders
    })

# --- Secure Login Handler ---
@app.route('/secureCom/v1/<user_id>/login', methods=['POST'])
def secure_login(user_id):
    print(f"Received login for {user_id}")

    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    print(f"Request data: {data}")
    
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    user = users.get(user_id)
    if not user or user['username'] != username or user['password'] != password:
        return "<h3>Login failed: Invalid credentials</h3>", 401

    session['user_id'] = user_id
    session['username'] = username
    session['login_type'] = "secure"
    return redirect(url_for('dashboard'))

# --- Secure Orders Endpoint (BOLA Protected) ---
@app.route('/secureCom/v1/<user_id>/orders')
def secure_orders(user_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if session['user_id'] != user_id:
        return jsonify({"error": "Forbidden: You can't access other users' data"}), 403

    user_orders = orders.get(user_id)
    if user_orders is None:
        return jsonify({"error": "No orders found"}), 404

    return jsonify({
        "user_id": user_id,
        "orders": user_orders
    })

# --- Dashboard & Session Management (Vulnerable EP) ---
@app.route('/vuln-dashboard')
def vuln_dashboard():
    if 'user_id' not in session or session.get('login_type') != 'vuln':
        return redirect(url_for('home'))

    return f"""
        <h2>Welcome, {session['username']}!</h2>
        <p>User ID (from session): {session['user_id']}</p>
        <a href="/commerce/v1/{session['user_id']}/orders">
            <button>View Orders</button>
        </a><br><br>
        <a href="/logout">Logout</a>
    """

# --- Secure Dashboard ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    admin_button = ""
    if session.get('user_id') == "202" and session.get('username') == "youaresecure":
        admin_button = f"""
            <a href="/admin">
                <button>Admin Page</button>
            </a><br><br>
        """

    return f"""
        <h2>Welcome to your dashboard, {session['username']}!</h2>
        <p>Your session userID: {session['user_id']}</p>
        <a href="/logout">Logout</a><br><br>
        <a href="/secureCom/v1/{session['user_id']}/orders">
            <button>View Secure Orders</button>
        </a><br><br>
        {admin_button}
    """

# --- Admin Panel (Only for user_id 202 and username youaresecure) ---
@app.route('/admin')
def admin_panel():
    if 'user_id' not in session or 'username' not in session:
        return redirect(url_for('home'))

    if session['user_id'] != "202" or session['username'] != "youaresecure":
        return "<h3>Access Denied: You are not authorized to view this page.</h3>", 403

    return """
        <h2>Welcome to the Admin Panel</h2>
        <p>You are logged in as an authorized admin: youaresecure</p>
        <a href="/dashboard"><button>Back to Dashboard</button></a>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)