from saveNload import load_user_data

import os


BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER = os.getenv("OWNER")

waiting_users = []
active_pairs = {}
user_details = {int(k): v for k, v in load_user_data().items()}
user_input_stage = {}
edit_stage = {}  # Track which field the user is editing
