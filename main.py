import os
import threading
from flask import Flask
from pyrogram import Client
from bot.handlers import register_handlers

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def root():
    return "Bot is running!"

def start_pyrogram():
    client = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workers=8)
    register_handlers(client)
    client.run()

if __name__ == "__main__":
    threading.Thread(target=start_pyrogram).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
