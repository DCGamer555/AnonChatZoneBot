from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from saveNload import save_user_data, load_user_data
from app import home, run, keep_alive
from relay import relay_message

from commands.start import start
from commands.find import find
from commands.next import next
from commands.stop import stop
from commands.help import help_command
from commands.profile import show_profile

from handlers.rating import handle_vote
from handlers.gender import handle_gender_selection
from handlers.country import handle_country_selection
from handlers.edit import handle_edit_selection


import os
import asyncio


BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER = os.getenv("OWNER")

waiting_users = []
active_pairs = {}
user_details = {int(k): v for k, v in load_user_data().items()}
user_input_stage = {}
edit_stage = {}  # Track which field the user is editing


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


async def periodic_save():
    global user_details
    while True:
        save_user_data(user_details)
        user_details = {int(k): v for k, v in load_user_data().items()}
        await asyncio.sleep(60)

async def periodic_feedback_clear():
    global user_details
    while True:
        for v in user_details.values():
            v["feedback_track"] = {}
        await asyncio.sleep(28800)



async def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await set_commands(app)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find))
    app.add_handler(CommandHandler("next", next))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", show_profile))
    app.add_handler(CallbackQueryHandler(handle_vote, pattern="rate\\|\\d+\\|(up|down)$"))
    app.add_handler(CallbackQueryHandler(handle_gender_selection, pattern="^gender\\|[MF]$"))
    app.add_handler(CallbackQueryHandler(handle_country_selection, pattern="^country\\|.+$"))
    app.add_handler(CallbackQueryHandler(handle_vote, pattern="^report\\|\\d+$"))
    app.add_handler(CallbackQueryHandler(handle_edit_selection, pattern="^edit\\|.+$"))
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.Sticker.ALL | filters.PHOTO | filters.VIDEO |
         filters.VIDEO_NOTE | filters.AUDIO | filters.Document.ALL | filters.VOICE) & ~filters.COMMAND,
        relay_message
    ))

    asyncio.create_task(periodic_save())
    asyncio.create_task(periodic_feedback_clear())
    await app.run_polling()


if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
