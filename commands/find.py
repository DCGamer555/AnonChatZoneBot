from telegram import Update
from telegram.ext import ContextTypes

from handlers.setup import check_user_profile

import main


@check_user_profile
async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in main.active_pairs:
        await update.message.reply_text("⚠️ *You're already in a chat.*\nUse /stop or /next first.", parse_mode="Markdown")
        return
    if user_id not in main.waiting_users:
        main.waiting_users.append(user_id)
        await update.message.reply_text("🔍*Looking for a partner...*", parse_mode="Markdown")
    if len(main.waiting_users) >= 2:
        user1 = main.waiting_users.pop(0)
        user2 = main.waiting_users.pop(0)
        main.active_pairs[user1] = user2
        main.active_pairs[user2] = user1
        uv1, uv2 = main.user_details[user1]["votes"], main.user_details[user2]["votes"]
        await context.bot.send_message(chat_id=user1, text=f"🎯 *Found Someone.... Say Hi!!*\nRating: {uv2['up']} 👍 {uv2['down']} 👎\n/next - Next Chat\n/stop - Stop Chat", parse_mode="Markdown")
        await context.bot.send_message(chat_id=user2, text=f"🎯 *Found Someone.... Say Hi!!*\nRating: {uv1['up']} 👍 {uv1['down']} 👎\n/next - Next Chat\n/stop - Stop Chat", parse_mode="Markdown")
