from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

import main


async def send_country_selection(user_id, context):
    countries = [
        ("🇮🇳 India", "India"), ("🇺🇸 USA", "USA"),
        ("🇬🇧 UK", "UK"), ("🇨🇦 Canada", "Canada"),
        ("🇦🇺 Australia", "Australia"), ("🇫🇷 France", "France"),
        ("🇩🇪 Germany", "Germany"), ("🇮🇩 Indonesia", "Indonesia"),
        ("🇷🇺 Russia", "Russia"), ("🇧🇷 Brazil", "Brazil")
    ]
    keyboard = []
    for i in range(0, len(countries), 2):
        row = [
            InlineKeyboardButton(countries[i][0], callback_data=f"country|{countries[i][1]}"),
            InlineKeyboardButton(countries[i + 1][0], callback_data=f"country|{countries[i + 1][1]}")
        ]
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🌐 Other", callback_data="country|Other")])
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user_id, text="🌍 *Select your country:*", reply_markup=markup, parse_mode="Markdown")


async def handle_country_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    country = query.data.split("|")[1]

    if user_id in main.edit_stage and main.edit_stage[user_id] == "country":
        main.user_details[user_id]["country"] = country
        del main.edit_stage[user_id]
        await query.edit_message_text(text=f"✅ *Country updated to {country}.*", parse_mode="Markdown")
        return

    main.user_details[user_id]["country"] = country
    del main.user_input_stage[user_id]
    await query.edit_message_text(text=f"✅ *Country set to {country}.*\nYou're all set! Use /find to start chatting.", parse_mode="Markdown")
