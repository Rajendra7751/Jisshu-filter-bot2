import os
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from . import utils, pixeldrain, database, tasks

ADMIN_ID = int(os.getenv("ADMIN_ID"))

def admin_only(func):
    async def wrapper(client, message: Message):
        if message.from_user.id != ADMIN_ID:
            await message.reply("Unauthorized access. This bot is private.")
            return
        return await func(client, message)
    return wrapper

def register_handlers(app):
    @app.on_message(filters.command("start") & filters.private)
    @admin_only
    async def start(_, message):
        await message.reply(
            "👋 Hi! *[Your Name]*\n\n"
            "Use me to mirror and leech files to PixelDrain!\n\n"
            "/help — Full usage"
        )

    @app.on_message(filters.command("help") & filters.private)
    @admin_only
    async def help(_, message):
        await message.reply(utils.HELP_TEXT, disable_web_page_preview=True)

    @app.on_message(filters.command("mirror") & filters.private)
    @admin_only
    async def mirror_cmd(client, message):
        await tasks.handle_mirror(client, message)

    @app.on_message(filters.command("leech") & filters.private)
    @admin_only
    async def leech_cmd(client, message):
        await tasks.handle_leech(client, message)

    @app.on_message(filters.command("status") & filters.private)
    @admin_only
    async def status_cmd(_, message):
        await tasks.handle_status(message)

    @app.on_message(filters.command("thumb") & filters.private)
    @admin_only
    async def thumb_cmd(client, message):
        await tasks.handle_thumb(client, message)

    @app.on_message(filters.command("del_thumb") & filters.private)
    @admin_only
    async def del_thumb_cmd(client, message):
        database.del_thumb(message.from_user.id)
        await message.reply("Thumbnail successfully removed.")

    @app.on_message(filters.command("cancel") & filters.private)
    @admin_only
    async def cancel_cmd(_, message):
        await tasks.cancel_all(message.from_user.id)
        await message.reply("All ongoing tasks cancelled.")

    @app.on_message(filters.incoming & filters.reply & filters.command("leech") & filters.private)
    @admin_only
    async def leech_reply(client, message):
        await tasks.handle_leech(client, message, is_reply=True)
