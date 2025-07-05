import os
import psycopg2
import json

DATABASE_URL = os.getenv("postgresql://postgres:jnXzfZuGEmQlDqtNLzOxchHaCBbIBblJ@postgres.railway.internal:5432/railway")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def save_user_data(data):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    data JSONB
                )
            """)
            for user_id, user_data in data.items():
                cur.execute("""
                    INSERT INTO users (user_id, data)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id)
                    DO UPDATE SET data = EXCLUDED.data
                """, (user_id, json.dumps(user_data)))
        conn.commit()

def load_user_data():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, data FROM users")
            rows = cur.fetchall()
            return {str(row[0]): row[1] for row in rows}