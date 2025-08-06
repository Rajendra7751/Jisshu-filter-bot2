import os
from pyrogram import Client
from bot.handlers import register_handlers

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

if __name__ == "__main__":
    bot = Client(
        "bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        workers=8  # You can reduce to 1 if system is low-memory
    )
    register_handlers(bot)
    bot.run()
