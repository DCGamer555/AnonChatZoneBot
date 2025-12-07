from telegram.error import Forbidden  # Importing the 'Forbidden' exception


# Function which checks if the bot is blocked by the given user
async def is_blocked_by(user_id, context):
    try:  # Tries to send a typing action to the user to check if it is blocked by the user
        await context.bot.send_chat_action(chat_id=user_id, action="typing")
        return False  # Returns False if it's not blocked
    except Forbidden:
        return True  # Returns True if it's blocked
