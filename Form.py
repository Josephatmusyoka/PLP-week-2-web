from flask import Flask, request, render_template, jsonify
import sqlite3
import json
import os

app = Flask(__name__)

# Database setup
DB_FILE = "userdata.db"
JSON_FILE = "user.json"

def init_db():
    """Initialize the database if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            gender TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Ensure DB is initialized

@app.route('/')
def index():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register():
    """Handles user registration and saves data in SQLite and JSON."""
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    gender = request.form.get('gender')

    if not (name and email and password and gender):
        return "All fields are required", 400

    # Save to SQLite
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password, gender) VALUES (?, ?, ?, ?)", 
                       (name, email, password, gender))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return "Email already registered", 400

    # Save to JSON
    user_data = {"name": name, "email": email, "password": password, "gender": gender}
    
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(user_data)

    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return "Registration successful!", 200

if __name__ == '__main__':
    app.run(debug=True,port=5001)
