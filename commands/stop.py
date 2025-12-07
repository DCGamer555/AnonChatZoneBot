from telegram import Update
from telegram.ext import ContextTypes

from handlers.setup import check_user_profile
from handlers.rating import ask_for_rating

import init


@check_user_profile
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in init.active_pairs:
        partner = init.active_pairs.pop(user_id)
        init.active_pairs.pop(partner, None)
        await context.bot.send_message(chat_id=partner, text="⛔ *Your partner left the chat.*", parse_mode="Markdown")
        await update.message.reply_text("👋 *Chat ended.*", parse_mode="Markdown")
        await ask_for_rating(context.bot, user_id, partner)
        await ask_for_rating(context.bot, partner, user_id)
    elif user_id in init.waiting_users:
        init.waiting_users.remove(user_id)
        await update.message.reply_text("❗ *You've been popped out of the Waiting Queue.*\nUse /find to search for a partner.", parse_mode="Markdown")
    else:
        await update.message.reply_text("❗*You're not in a chat.*", parse_mode="Markdown")
