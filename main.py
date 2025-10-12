from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from flask import Flask
from threading import Thread
from functools import wraps
from saveNload import save_user_data, load_user_data

import os

web_app = Flask('')


@web_app.route('/')
def home():
    return "✅ Anonymous Chat Bot is running!"


def run():
    web_app.run(host='0.0.0.0', port=8080)


def keep_alive():
    Thread(target=run).start()


BOT_TOKEN = os.getenv("BOT_TOKEN")

waiting_users = []
active_pairs = {}
user_details = {int(k): v for k, v in load_user_data().items()}
user_input_stage = {}


async def set_commands(application):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("find", "Find a new chat partner"),
        BotCommand("next", "Skip your current partner"),
        BotCommand("stop", "Stop the current chat"),
        BotCommand("help", "Show help"),
        BotCommand("profile", "Show user profile"),
    ]
    await application.bot.set_my_commands(commands)


def check_user_profile(handler_func):
    @wraps(handler_func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if user_id not in user_details:
            user_details[user_id] = {
                "gender": None,
                "age": None,
                "country": None,
                "reports": 0,
                "reporters": [],
                "votes": {"up": 0, "down": 0},
                "voters": [],
                "feedback_track": {}
            }
            user_input_stage[user_id] = "gender"
            keyboard = [[
                InlineKeyboardButton("♂️ Male", callback_data="gender|M"),
                InlineKeyboardButton("♀️ Female", callback_data="gender|F")
            ]]
            markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("👋 Welcome to *Chat Zone - Anonymous Chat Bot!*", parse_mode="Markdown")
            await update.message.reply_text("*Let's set up your profile.*\nWhat's your gender?", reply_markup=markup, parse_mode="Markdown")
            return

        if not all([user_details[user_id].get("gender"), user_details[user_id].get("age"), user_details[user_id].get("country")]):
            stage = user_input_stage.get(user_id, "gender")
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


async def handle_gender_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    gender = query.data.split("|")[1]
    user_details[user_id]["gender"] = gender
    user_input_stage[user_id] = "age"
    await query.edit_message_text(text=f"*Gender is set to {"Male" if gender == "M" else "Female"}.*\n📅 Please enter your age:", parse_mode="Markdown")


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
    user_id = update.effective_user.id
    country = query.data.split("|")[1]
    user_details[user_id]["country"] = country
    del user_input_stage[user_id]
    await query.edit_message_text(text=f"✅ *Country set to {country}.*\nYou're all set! Use /find to start chatting.", parse_mode="Markdown")


async def handle_user_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if user_id not in user_input_stage:
        return
    stage = user_input_stage[user_id]
    if stage == "age":
        try:
            age = int(text)
            user_details[user_id]["age"] = age
            user_input_stage[user_id] = "country"
            await update.message.reply_text(f"✅ *Age set to {age}.*\n🌍 Great! Now, please select your country:", parse_mode="Markdown")
            await send_country_selection(user_id, context)
        except ValueError:
            await update.message.reply_text("❌ *Please enter a valid number for age.*", parse_mode="Markdown")


async def askForRating(bot, from_id, to_id):
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

    user_details[to_id].setdefault("feedback_track", {})
    user_details[to_id]["feedback_track"][from_id] = {"voted": False, "reported": False}

    await bot.send_message(from_id,
                            text="""
💡 *If the interlocutor misbehaved or violated the rules, send a complaint against them.

Give a rating to the interlocutor which will affect their ratings.*
""", reply_markup=markup, parse_mode="Markdown")

async def handleVote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query: CallbackQuery = update.callback_query
    await query.answer()

    data = query.data.split("|")

    if not (2 <= len(data) <= 3):
        return

    action = data[0]
    target_id = int(data[1])

    if target_id not in user_details:
        user_details[target_id] = {
            "gender": None,
            "age": None,
            "country": None,
            "reports": 0,
            "reporters": [],
            "votes": {"up": 0, "down": 0},
            "voters": [],
            "feedback_track": {}
        }

    track = user_details[target_id].setdefault("feedback_track", {})
    track.setdefault(user_id, {"voted": False, "reported": False})

    if action == "rate":
        vote_type = data[2]
        if not track[user_id]["voted"]:
            if user_id not in user_details[target_id]["voters"]:
                user_details[target_id]["votes"][vote_type] += 1
                user_details[target_id]["voters"].append(user_id)
            track[user_id]["voted"] = True

    elif action == "report":
        if not track[user_id]["reported"]:
            if user_id not in user_details[target_id]["reporters"]:
                user_details[target_id]["reports"] += 1
                user_details[target_id]["reporters"].append(user_id)
            track[user_id]["reported"] = True

    voted = track[user_id]["voted"]
    reported = track[user_id]["reported"]

    if voted and reported:
        await query.edit_message_text("""
    *Thank You for your feedback.

    Your feedback helps other users to be safe and secure.*
    """, parse_mode="Markdown")
    else:
        rateStartText = "💡 If the interlocutor misbehaved or violated the rules, send a complaint against them."
        rateEndText = ""
        buttons = []
        if not voted:
            rateEndText = "Give a rating to your Interlocutor to help ensure others' safety."
            buttons.append([
                InlineKeyboardButton("👍", callback_data=f"rate|{target_id}|up"),
                InlineKeyboardButton("👎", callback_data=f"rate|{target_id}|down")
            ])

        if not reported:
            rateEndText = "Report the Interlocutor, if they violated any rules, which may eventually lead to their banned if noticed."
            buttons.append([
                InlineKeyboardButton("🚩 Report", callback_data=f"report|{target_id}")
            ])
        await query.edit_message_text(text=f"""
*{rateStartText}

{rateEndText}*
""", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")


async def handle_edit_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    action = query.data.split("|")[1]

    if action == "gender":
        keyboard = [
            [InlineKeyboardButton("♂️ Male", callback_data="gender|M"),
             InlineKeyboardButton("♀️ Female", callback_data="gender|F")]
        ]
        await query.edit_message_text("*Select your new gender:*", parse_mode="Markdown",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
        user_input_stage[user_id] = "gender"

    elif action == "age":
        await query.edit_message_text("📅 *Please enter your new age:*", parse_mode="Markdown")
        user_input_stage[user_id] = "age"

    elif action == "country":
        await query.edit_message_text("🌍 *Select your new country:*", parse_mode="Markdown")
        user_input_stage[user_id] = "country"
        await send_country_selection(user_id, context)


@check_user_profile
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_details:
        user_input_stage[user_id] = "gender"
        await update.message.reply_text("👋 Welcome to *Chat Zone - Anonymous Chat Bot! \nLet's set up your profile.*\nWhat's your gender? (M/F):", parse_mode="Markdown")
        return

    await update.message.reply_text("👋 Welcome back to *Chat Zone - Anonymous Chat Bot!* Use /find to look for a partner.", parse_mode="Markdown")


@check_user_profile
async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_pairs:
        await update.message.reply_text("⚠️ *You're already in a chat.*\nUse /stop or /next first.", parse_mode="Markdown")
        return
    if user_id not in waiting_users:
        waiting_users.append(user_id)
        await update.message.reply_text("🔍*Looking for a partner...*", parse_mode="Markdown")
    if len(waiting_users) >= 2:
        user1 = waiting_users.pop(0)
        user2 = waiting_users.pop(0)
        active_pairs[user1] = user2
        active_pairs[user2] = user1
        uv1, uv2 = user_details[user1].get("votes", {"up" : 0, "down" : 0}), user_details[user2].get("votes", {"up" : 0, "down" : 0})
        await context.bot.send_message(chat_id=user1,
                                       text=f"""
🎯 *Found Someone.... Say Hi!!

Rating:* {uv2["up"]} 👍 {uv2["down"]} 👎

/next - Next Chat
/stop - Stop Chat
""", parse_mode="Markdown")
        await context.bot.send_message(chat_id=user2,
                                       text=f"""
🎯 *Found Someone.... Say Hi!!

Rating:* {uv1["up"]} 👍 {uv1["down"]} 👎

/next - Next Chat
/stop - Stop Chat
""", parse_mode="Markdown")


async def relay_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user.id
    if sender in active_pairs:
        receiver = active_pairs[sender]
        try:
            await context.bot.send_message(chat_id=receiver, text=update.message.text)
        except:
            await update.message.reply_text("❌ *Failed to send message.*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❗ *You're not in a chat.* Use /find to connect.", parse_mode="Markdown")


@check_user_profile
async def next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_pairs:
        partner = active_pairs.pop(user_id)
        active_pairs.pop(partner, None)
        await context.bot.send_message(chat_id=partner, text="⛔ *Your partner left the chat.*", parse_mode="Markdown")
        await askForRating(context.bot, user_id, partner)
        await askForRating(context.bot, partner, user_id)
        await update.message.reply_text("🔁 *Partner skipped...\nYou're added to the waiting queue...\nFinding new one...*", parse_mode="Markdown")
        await find(update, context)
    else:
        await update.message.reply_text("❗*You're not in a chat.*\nUse /find to connect.", parse_mode="Markdown")


@check_user_profile
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_pairs:
        partner = active_pairs.pop(user_id)
        active_pairs.pop(partner, None)
        await context.bot.send_message(chat_id=partner, text="⛔ *Your partner left the chat.*", parse_mode="Markdown")
        await askForRating(context.bot, user_id, partner)
        await askForRating(context.bot, partner, user_id)
        await update.message.reply_text("👋 *Chat ended.*", parse_mode="Markdown")
    elif user_id in waiting_users:
        await update.message.reply_text("❗ *You've been popped out of the Waiting Queue.*\nUse /find to search for a partner.", parse_mode="Markdown")
    else:
        await update.message.reply_text("❗*You're not in a chat.*", parse_mode="Markdown")
    if user_id in waiting_users:
        waiting_users.remove(user_id)


@check_user_profile
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    user = user_details[user_id]
    votes = user.get("votes", {"up": 0, "down": 0})

    profile_text = f"""
*User Profile*

*Name:* _{name}_
*ID:* {user_id}
*Gender:* {"Male" if user["gender"] == "M" else "Female"}
*Age:* {user["age"]}
*Country:* {user["country"]}
*Rating:* {votes["up"]} 👍 {votes["down"]} 👎
"""

    # Buttons for editing
    keyboard = [
        [
            InlineKeyboardButton("✏️ Edit Gender", callback_data="edit|gender"),
            InlineKeyboardButton("✏️ Edit Age", callback_data="edit|age")
        ],
        [
            InlineKeyboardButton("✏️ Edit Country", callback_data="edit|country")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(profile_text, reply_markup=markup, parse_mode="Markdown")


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in user_input_stage:
        await handle_user_setup(update, context)
        return

    if user_id in active_pairs:
        partner_id = active_pairs[user_id]
        try:
            if update.message.text:
                await context.bot.send_message(chat_id=partner_id, text=update.message.text)
            elif update.message.sticker:
                await context.bot.send_sticker(chat_id=partner_id, sticker=update.message.sticker.file_id)
            elif update.message.photo:
                await context.bot.send_photo(chat_id=partner_id, photo=update.message.photo[-1].file_id)
            elif update.message.video:
                await context.bot.send_video(chat_id=partner_id, video=update.message.video.file_id)
            elif update.message.video_note:
                await context.bot.send_video_note(chat_id=partner_id, video_note=update.message.video_note.file_id)
            elif update.message.voice:
                await context.bot.send_voice(chat_id=partner_id, voice=update.message.voice.file_id)
            elif update.message.audio:
                await context.bot.send_audio(chat_id=partner_id, audio=update.message.audio.file_id)
            elif update.message.document:
                await context.bot.send_document(chat_id=partner_id, document=update.message.document.file_id)
        except Exception as e:
            await update.message.reply_text("❌ *Failed to send message.*", parse_mode="Markdown")
            print(e)
    else:
        await update.message.reply_text("❗ *You're not in a chat.* Use /find to connect.", parse_mode="Markdown")

@check_user_profile
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🤖 *Anonymous Chat Bot*
Commands:
/start - Show welcome message
/find - Find a new partner
/next - Skip current chat
/stop - Stop current chat
/help - Show this message
/profile - Show user profile
""", parse_mode="Markdown")

async def periodic_save():
    global user_details
    while True:
        save_user_data(user_details)
        user_details = {int(k): v for k, v in load_user_data().items()}
        await asyncio.sleep(60)


def migrate_feedback_track(user_details):
    updated_count = 0

    for uid, details in user_details.items():
        feedback = details.get("feedback_track")
        if uid == "6618474423":
            user_details[uid]["vote_up"] = 10
            user_details[uid]["vote_down"] = 0
            user_details[uid]["reports"] = 0
            user_details[uid]["voters"] = []
            user_details[uid]["reporters"] = []
            user_details[uid]["feedback_track"] = {}

        # Skip if none or not dict
        if not isinstance(feedback, dict):
            user_details[uid]["feedback_track"] = {}
            continue

        cleaned_feedback = {}
        for partner_id, record in feedback.items():
            # Only keep proper dicts
            if isinstance(record, dict):
                # Rebuild only with valid keys
                new_record = {
                    "voted": bool(record.get("voted", False)),
                    "reported": bool(record.get("reported", False))
                }
                cleaned_feedback[partner_id] = new_record

        user_details[uid]["feedback_track"] = cleaned_feedback
        updated_count += 1

    print(f"✅ Feedback migration completed. Processed {updated_count} users.")


async def main():
    keep_alive()
    migrate_feedback_track(user_details)
    save_user_data(user_details)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await set_commands(app)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(CommandHandler("next", next))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", show_profile))
    app.add_handler(CallbackQueryHandler(handleVote, pattern="rate\\|\\d+\\|(up|down)$"))
    app.add_handler(CallbackQueryHandler(handle_gender_selection, pattern="^gender\\|[MF]$"))
    app.add_handler(CallbackQueryHandler(handle_country_selection, pattern="^country\\|.+$"))
    app.add_handler(CallbackQueryHandler(handleVote, pattern="^report\\|\\d+$"))
    app.add_handler(CallbackQueryHandler(handle_edit_selection, pattern="^edit\\|.+$"))
    app.add_handler(MessageHandler((filters.TEXT | filters.Sticker.ALL | filters.PHOTO | filters.VIDEO |
                                    filters.VIDEO_NOTE | filters.AUDIO | filters.Document.ALL | filters.VOICE) & ~filters.COMMAND, handle_messages))

    asyncio.create_task(periodic_save())
    await app.run_polling()


if __name__ == '__main__':
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())

