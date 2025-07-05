import psycopg2
import os
import json

def ensure_table_exists(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS "user" (
            id BIGINT PRIMARY KEY,
            gender VARCHAR(10),
            age INTEGER,
            country VARCHAR(50),
            reports INTEGER,
            reporters TEXT[],
            votes_up INTEGER,
            votes_down INTEGER,
            voters TEXT[],
            feedback_track JSONB
        )
        """)
        conn.commit()

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "user" (
        id BIGINT PRIMARY KEY,
        gender VARCHAR(10),
        age INTEGER,
        country VARCHAR(50),
        reports INTEGER,
        reporters TEXT[],
        votes_up INTEGER,
        votes_down INTEGER,
        voters TEXT[],
        feedback_track JSONB
    )
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
    ensure_table_exists(conn)
    cur = conn.cursor()

    cur.execute("SELECT user_id, data FROM 'user';")
    rows = cur.fetchall()

    data = {int(user_id): user_data for user_id, user_data in rows}

    cur.close()
    conn.close()
    return data
