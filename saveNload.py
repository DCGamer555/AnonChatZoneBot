import psycopg2
import os
import json

def get_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        database=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        port=os.getenv("PGPORT")
    )

def save_user_data(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            data JSONB
        );
    """)

    for user_id, user_data in data.items():
        cur.execute("""
            INSERT INTO users (user_id, data)
            VALUES (%s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET data = EXCLUDED.data;
        """, (user_id, json.dumps(user_data)))

    conn.commit()
    cur.close()
    conn.close()

def load_user_data():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_id, data FROM users;")
    rows = cur.fetchall()

    data = {int(user_id): user_data for user_id, user_data in rows}

    cur.close()
    conn.close()
    return data
