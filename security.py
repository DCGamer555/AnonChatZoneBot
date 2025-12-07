from telegram.error import Forbidden


async def is_blocked_by(user_id, context):
    try:
        await context.bot.send_chat_action(chat_id=user_id, action="typing")
        return False
    except Forbidden:
        return True
