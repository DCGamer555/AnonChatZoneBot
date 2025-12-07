from flask import Flask
from threading import Thread

web_app = Flask('')


def run():
    web_app.run(host='0.0.0.0', port=8080)


@web_app.route('/')
def home():
    return "✅ Anonymous Chat Bot is running!"


def keep_alive():
    Thread(target=run).start()
