from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from functools import wraps

from country import send_country_selection

import main


def check_user_profile(handler_func):
    @wraps(handler_func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if user_id not in main.user_details:
            main.user_details[user_id] = {
                "gender": None,
                "age": None,
                "country": None,
                "reports": 0,
                "reporters": [],
                "votes": {"up": 0, "down": 0},
                "voters": [],
                "feedback_track": {}
            }
            main.user_input_stage[user_id] = "gender"
            keyboard = [[
                InlineKeyboardButton("♂️ Male", callback_data="gender|M"),
                InlineKeyboardButton("♀️ Female", callback_data="gender|F")
            ]]
            markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("👋 Welcome to *Chat Zone - Anonymous Chat Bot!*", parse_mode="Markdown")
            await update.message.reply_text("*Let's set up your profile.*\nWhat's your gender?", reply_markup=markup, parse_mode="Markdown")
            return

        if not all([main.user_details[user_id].get("gender"), main.user_details[user_id].get("age"), main.user_details[user_id].get("country")]):
            stage = main.user_input_stage.get(user_id, "gender")
            if stage == "gender":
                keyboard = [[
                    InlineKeyboardButton("♂️ Male", callback_data="gender|M"),
                    InlineKeyboardButton("♀️ Female", callback_data="gender|F")
                ]]
                markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("*Please select your gender: *", reply_markup=markup, parse_mode="Markdown")
            elif stage == "age":
                await update.message.reply_text("📅 *Please enter your age:*", parse_mode="Markdown")
            return
        return await handler_func(update, context)
    return wrapper


async def handle_user_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Editing age
    if user_id in main.edit_stage and main.edit_stage[user_id] == "age":
        try:
            age = int(text)
            main.user_details[user_id]["age"] = age
            del main.edit_stage[user_id]
            await update.message.reply_text(f"✅ *Age updated to {age}.*", parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ *Please enter a valid number for age.*", parse_mode="Markdown")
        return

    # First-time setup age
    if user_id not in main.user_input_stage:
        return

    stage = main.user_input_stage[user_id]
    if stage == "age":
        try:
            age = int(text)
            main.user_details[user_id]["age"] = age
            main.user_input_stage[user_id] = "country"
            await update.message.reply_text(f"✅ *Age set to {age}.*\n🌍 Great! Now, please select your country:", parse_mode="Markdown")
            await send_country_selection(user_id, context)
        except ValueError:
            await update.message.reply_text("❌ *Please enter a valid number for age.*", parse_mode="Markdown")
