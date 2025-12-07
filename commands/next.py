from telegram import Update
from telegram.ext import ContextTypes

from commands.find import find

from handlers.setup import check_user_profile
from handlers.rating import ask_for_rating

import init


@check_user_profile
async def next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in init.active_pairs:
        partner = init.active_pairs.pop(user_id)
        init.active_pairs.pop(partner, None)
        await context.bot.send_message(chat_id=partner, text="⛔ *Your partner left the chat.*", parse_mode="Markdown")
        await update.message.reply_text("🔁 *Partner skipped...\nYou're added to the waiting queue...\nFinding new one...*", parse_mode="Markdown")
        await ask_for_rating(context.bot, user_id, partner)
        await ask_for_rating(context.bot, partner, user_id)
        await find(update, context)
    else:
        await update.message.reply_text("❗*You're not in a chat.*\nUse /find to connect.", parse_mode="Markdown")
