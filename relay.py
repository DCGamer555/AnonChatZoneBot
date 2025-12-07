from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import Forbidden

from security import is_blocked_by

from commands.stop import stop

from handlers.setup import handle_user_setup

import init


async def relay_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_blocked_by(user_id, context):
        return
    if user_id in init.user_input_stage or user_id in init.edit_stage:
        await handle_user_setup(update, context)
        return
    if user_id in init.active_pairs:
        partner_id = init.active_pairs[user_id]
        if await is_blocked_by(partner_id, context):
            await stop(update, context)
            return
        msg = update.message
        try:
            if msg.text:
                await context.bot.send_message(chat_id=partner_id, text=msg.text)
            elif msg.sticker:
                await context.bot.send_sticker(chat_id=partner_id, sticker=msg.sticker.file_id)
            elif msg.photo:
                await context.bot.send_photo(chat_id=partner_id, photo=msg.photo[-1].file_id)
            elif msg.video:
                await context.bot.send_video(chat_id=partner_id, video=msg.video.file_id)
            elif msg.video_note:
                await context.bot.send_video_note(chat_id=partner_id, video_note=msg.video_note.file_id)
            elif msg.voice:
                await context.bot.send_voice(chat_id=partner_id, voice=msg.voice.file_id)
            elif msg.audio:
                await context.bot.send_audio(chat_id=partner_id, audio=msg.audio.file_id)
            elif msg.document:
                await context.bot.send_document(chat_id=partner_id, document=msg.document.file_id)
        except Forbidden:
            await stop(update, context)
            return
        except Exception as e:
            await update.message.reply_text("❌ *Failed to send message.*", parse_mode="Markdown")
            print(e)
    else:
        await update.message.reply_text("❗ *You're not in a chat.* Use /find to connect.", parse_mode="Markdown")
