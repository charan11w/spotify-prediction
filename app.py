from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import joblib
import numpy as np
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load model and scaler
model = joblib.load("spotify_popularity_model.pkl")
scaler = joblib.load("scaler.pkl")

# Define feature names
feature_names = [
    "Danceability", "Energy", "Key", "Loudness", "Mode", "Speechiness", "Acousticness",
    "Instrumentalness", "Liveness", "Valence", "Tempo", "Duration (ms)", "Time Signature",
    "Chorus Hit", "Sections"
]

USER_FILE = 'users.json'

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump({}, f)
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/')
def root():
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    return render_template("landing.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/home')
def home():
    if not session.get("user"):
        return redirect(url_for('login'))
    return render_template("index.html", feature_names=feature_names)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    if request.method == 'POST':
        try:
            features = [float(request.form[feature]) for feature in feature_names]
            scaled_features = scaler.transform([features])
            prediction = model.predict(scaled_features)[0]
            result = "🎵 Popular 🎵" if prediction == 1 else "❌ Not Popular ❌"
            return jsonify({"prediction": result})
        except Exception as e:
            return jsonify({"error": str(e)})

    # GET request: render the predict form page
    return render_template('predict.html', feature_names=feature_names)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        if username in users and users[username]["password"] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")
        users = load_users()
        if username in users:
            return render_template("signup.html", error="Username already exists")
        users[username] = {"email": email, "password": password}
        save_users(users)
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
