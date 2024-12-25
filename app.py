# backend/app.py
from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

DB_CONFIG = {
    'dbname': 'weather_db',
    'user': 'user',
    'password': 'pass',
    'host': 'postgres_db',
    'port': 5432
}

def get_data():
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    
    cursor.execute("SELECT * FROM weather ORDER BY timestamp DESC LIMIT 10")
    data = cursor.fetchall()

    
    cursor.close()
    conn.close()

    return data

@app.route('/')
def index():
    
    return jsonify(get_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
