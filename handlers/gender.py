from telegram import Update
from telegram.ext import ContextTypes

import main


async def handle_gender_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    gender = query.data.split("|")[1]

    # Editing flow
    if user_id in main.edit_stage and main.edit_stage[user_id] == "gender":
        main.user_details[user_id]["gender"] = gender
        del main.edit_stage[user_id]
        await query.edit_message_text(text=f"*Gender updated to {'Male' if gender=='M' else 'Female'}.*", parse_mode="Markdown")
        return

    # First-time setup
    main.user_details[user_id]["gender"] = gender
    main.user_input_stage[user_id] = "age"
    await query.edit_message_text(text=f"*Gender is set to {'Male' if gender == 'M' else 'Female'}.*\n📅 Please enter your age:", parse_mode="Markdown")
