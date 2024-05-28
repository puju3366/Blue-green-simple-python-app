import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, session
from flask_session import Session
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

version = os.getenv('APP_VERSION', '1.0')

def create_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database='app_db'
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db(conn):
    if conn is None:
        return
    try:
        cursor = conn.cursor()

        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS app_db")

        # Switch to the 'app_db' database
        cursor.execute("USE app_db")

        # Create visitors table if not exists
        cursor.execute("CREATE TABLE IF NOT EXISTS visitors (id INT AUTO_INCREMENT PRIMARY KEY, visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

        # Create users table if not exists
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), email VARCHAR(255))")

        conn.commit()
        print("Database initialization successful.")
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn.is_connected():
            cursor.close()

@app.route('/')
def index():
    conn = create_connection()
    if conn is None:
        return "Error connecting to database"

    cursor = conn.cursor()

    # Initialize database if not already initialized
    init_db(conn)

    # Record a new visit if the session is new
    if 'visited' not in session:
        try:
            cursor.execute("INSERT INTO visitors () VALUES ()")
            conn.commit()
            session['visited'] = True
        except Error as e:
            print(f"Error inserting visit record: {e}")

    # Get total visitors
    try:
        cursor.execute("SELECT COUNT(*) FROM visitors")
        total_visitors = cursor.fetchone()[0]
    except Error as e:
        print(f"Error retrieving total visitors: {e}")
        total_visitors = 0

    # Calculate live visitors (e.g., visits in the last 5 minutes)
    try:
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        cursor.execute("SELECT COUNT(*) FROM visitors WHERE visit_time >= %s", (five_minutes_ago,))
        live_visitors = cursor.fetchone()[0]
    except Error as e:
        print(f"Error retrieving live visitors: {e}")
        live_visitors = 0

    # Get total registered users
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
    except Error as e:
        print(f"Error retrieving total users: {e}")
        total_users = 0

    cursor.close()
    conn.close()

    return render_template('index.html', version=version, total_visitors=total_visitors, live_visitors=live_visitors, total_users=total_users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
