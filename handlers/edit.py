from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from handlers.country import send_country_selection

import init


async def handle_edit_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    action = query.data.split("|")[1]

    if action == "gender":
        keyboard = [[InlineKeyboardButton("♂️ Male", callback_data="gender|M"),
                     InlineKeyboardButton("♀️ Female", callback_data="gender|F")]]
        await query.edit_message_text("*Select your new gender:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        init.edit_stage[user_id] = "gender"
    elif action == "age":
        await query.edit_message_text("📅 *Please enter your new age:*", parse_mode="Markdown")
        init.edit_stage[user_id] = "age"
    elif action == "country":
        await query.edit_message_text("🌍 *Select your new country:*", parse_mode="Markdown")
        init.edit_stage[user_id] = "country"
        await send_country_selection(user_id, context)
