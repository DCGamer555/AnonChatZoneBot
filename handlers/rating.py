from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import ContextTypes

import main


async def ask_for_rating(bot, from_id, to_id):
    keyboard = [
        [
            InlineKeyboardButton("👍", callback_data=f"rate|{to_id}|up"),
            InlineKeyboardButton("👎", callback_data=f"rate|{to_id}|down")
        ],
        [
            InlineKeyboardButton("🚩 Report", callback_data=f"report|{to_id}")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    main.user_details[to_id].setdefault("feedback_track", {})
    main.user_details[to_id]["feedback_track"][from_id] = {"voted": False, "reported": False}
    await bot.send_message(from_id,
                           text="""💡 *If the interlocutor misbehaved or violated the rules, send a complaint against them.*
Give a rating to the interlocutor which will affect their ratings.""",
                           reply_markup=markup, parse_mode="Markdown")


async def handle_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query: CallbackQuery = update.callback_query
    await query.answer()
    data = query.data.split("|")
    if not (2 <= len(data) <= 3):
        return

    action = data[0]
    target_id = int(data[1])
    if target_id not in main.user_details:
        main.user_details[target_id] = {
            "gender": None, "age": None, "country": None,
            "reports": 0, "reporters": [], "votes": {"up": 0, "down": 0},
            "voters": [], "feedback_track": {}
        }

    track = main.user_details[target_id].setdefault("feedback_track", {})
    track.setdefault(user_id, {"voted": False, "reported": False})

    if action == "rate":
        vote_type = data[2]
        if not track[user_id]["voted"]:
            if user_id not in main.user_details[target_id]["voters"]:
                main.user_details[target_id]["votes"][vote_type] += 1
                main.user_details[target_id]["voters"].append(user_id)
            track[user_id]["voted"] = True
    elif action == "report":
        if not track[user_id]["reported"]:
            if user_id not in main.user_details[target_id]["reporters"]:
                main.user_details[target_id]["reports"] += 1
                main.user_details[target_id]["reporters"].append(user_id)
            track[user_id]["reported"] = True

    voted = track[user_id]["voted"]
    reported = track[user_id]["reported"]

    if (voted and reported) or (not voted and not reported):
        del main.user_details[target_id]["feedback_track"][user_id]
    if voted and reported:
        await query.edit_message_text("*Thank You for your feedback.\nYour feedback helps other users to be safe and secure.*", parse_mode="Markdown")
    else:
        buttons = []
        rate_text = "💡 If the interlocutor misbehaved or violated the rules, send a complaint against them."
        if not voted:
            buttons.append([InlineKeyboardButton("👍", callback_data=f"rate|{target_id}|up"),
                            InlineKeyboardButton("👎", callback_data=f"rate|{target_id}|down")])
        if not reported:
            buttons.append([InlineKeyboardButton("🚩 Report", callback_data=f"report|{target_id}")])
        await query.edit_message_text(f"*{rate_text}*", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
