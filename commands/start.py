from telegram import Update
from telegram.ext import ContextTypes

from handlers.setup import check_user_profile

import init


@check_user_profile
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not all([init.user_details[user_id].get("gender"), init.user_details[user_id].get("age"), init.user_details[user_id].get("country")]):
        return
    await update.message.reply_text("👋 Welcome back to *Chat Zone - Anonymous Chat Bot!* Use /find to look for a partner.", parse_mode="Markdown")
