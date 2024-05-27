from flask import Flask, render_template, session
from flask_session import Session
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

version = os.getenv('APP_VERSION', '1.0')

import mysql.connector

def create_connection():
    return mysql.connector.connect(
        host="mysql",  # Hostname of your MySQL service
        user="user",
        password="password",
        database="app_db"
    )



def init_db():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS visitors (id INT AUTO_INCREMENT PRIMARY KEY, visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), email VARCHAR(255))")
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    conn = create_connection()
    cursor = conn.cursor()

    # Record a new visit if the session is new
    if 'visited' not in session:
        cursor.execute("INSERT INTO visitors () VALUES ()")
        conn.commit()
        session['visited'] = True

    # Get total visitors
    cursor.execute("SELECT COUNT(*) FROM visitors")
    total_visitors = cursor.fetchone()[0]

    # Calculate live visitors (e.g., visits in the last 5 minutes)
    five_minutes_ago = datetime.now() - timedelta(minutes=5)
    cursor.execute("SELECT COUNT(*) FROM visitors WHERE visit_time >= %s", (five_minutes_ago,))
    live_visitors = cursor.fetchone()[0]

    # Get total registered users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template('index.html', version=version, total_visitors=total_visitors, live_visitors=live_visitors, total_users=total_users)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
