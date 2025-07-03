import os
import json

FILE_PATH = "user_data.json"

def save_user_data(user_data: dict):
    with open(FILE_PATH, "w") as f:
        json.dump(user_data, f)
    print("✅ Data saved to disk.")

def load_user_data() -> dict:
    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
        return {}
    try:
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Warning: userdata.json is corrupted or empty. Starting with a fresh dictionary.")
        return {}
