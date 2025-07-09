import sqlite3, json, psycopg2, os

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def ensure_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_details (
                    user_id BIGINT PRIMARY KEY,
                    gender VARCHAR(1),
                    age INTEGER,
                    country VARCHAR(25),
                    reports INTEGER,
                    reporters TEXT,
                    vote_up INTEGER,
                    vote_down INTEGER,
                    voters TEXT,
                    feedback_track JSON
            )
        """)
        conn.commit()

def save_user_data(data: dict):
    with get_connection() as conn:
        cursor = conn.cursor()

        ensure_db()

        for user_id, details in data.items():
            cursor.execute("""
                    INSERT INTO user_details (
                        user_id, gender, age, country, reports, reporters, 
                        vote_up, vote_down, voters, feedback_track
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        gender = EXCLUDED.gender,
                        age = EXCLUDED.age,
                        country = EXCLUDED.country,
                        reports = EXCLUDED.reports,
                        reporters = EXCLUDED.reporters,
                        vote_up = EXCLUDED.vote_up,
                        vote_down = EXCLUDED.vote_down,
                        voters = EXCLUDED.voters,
                        feedback_track = EXCLUDED.feedback_track
            """, (
                user_id,
                details.get("gender"),
                details.get("age"),
                details.get("country"),
                details.get("reports", 0),
                json.dumps(details.get("reporters", [])),
                details.get("votes", {}).get("up", 0),
                details.get("votes", {}).get("down", 0),
                json.dumps(details.get("voters", [])),
                json.dumps(details.get("feedback_track", {}))
            ))
        conn.commit()
        print("✅ User Data Saved to Drive Successfully.")

def load_user_data() -> dict:
    ensure_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_details")
        rows = cursor.fetchall()

        data = {}
        for row in rows:
            user_id = row[0]
            data[user_id] = {
                "gender": row[1],
                "age": row[2],
                "country": row[3],
                "reports": row[4],
                "reporters": json.loads(row[5]),
                "votes": {
                    "up": row[6],
                    "down": row[7],
                },
                "voters": json.loads(row[8]),
                "feedback_track": json.loads(row[9]),
            }
        return data
