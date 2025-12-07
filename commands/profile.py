# Imports everything needed from the telegram module
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from handlers.setup import check_user_profile  # Imports the handler which checks if the user's profile exists

import init  # Importing the bot credentials and users' details


# Function shows the user their profile and asks if they wanna edit them and what to edit
@check_user_profile
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = init.user_details[user_id]
    votes = user.get("votes", {"up": 0, "down": 0})
    profile_text = f"""
<b>User Profile</b>

<b>Name:</b> <i>{update.effective_user.full_name}</i> | @{(update.effective_user.username)}
<b>ID:</b> {user_id}
<b>Gender:</b> {"Male" if user["gender"] == "M" else "Female"}
<b>Age:</b> {user["age"]}
<b>Country:</b> {user["country"]}
<b>Rating:</b> {votes["up"]} 👍 {votes["down"]} 👎
"""
    keyboard = [
        [InlineKeyboardButton("✏️ Edit Gender", callback_data="edit|gender"),
         InlineKeyboardButton("✏️ Edit Age", callback_data="edit|age")],
        [InlineKeyboardButton("✏️ Edit Country", callback_data="edit|country")]
    ]
    await update.message.reply_text(profile_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
