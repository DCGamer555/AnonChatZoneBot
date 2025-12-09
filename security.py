from telegram.error import Forbidden  # Importing the 'Forbidden' exception


# Function which checks if the bot is blocked by the given user
async def safe_tele_func_call(caller, *args, **kwargs):
    try:  # Tries to send a typing action to the user to check if it is blocked by the user
        return await caller(*args, **kwargs)
    except Forbidden:
        return None
