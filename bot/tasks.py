import os
import aiohttp
import tempfile
import asyncio
import zipfile
from . import utils, pixeldrain, database

user_tasks = {}

async def handle_mirror(client, message):
    args = message.text.split(maxsplit=1)
    orig_link = ""
    if message.reply_to_message and message.reply_to_message.document:
        file_message = message.reply_to_message
        file = await file_message.download()
        orig_link = None
    elif len(args) > 1:
        orig_link = args[1].strip()
    else:
        await message.reply("Send /mirror [link] or reply to a file.")
        return

    reply = await message.reply("Processing file...")
    filename = None

    if orig_link:  # Download from URL
        temp = tempfile.NamedTemporaryFile(delete=False)
        await download_url(orig_link, temp.name, reply)
        filename = os.path.basename(temp.name)
        path = temp.name
    else:  # Telegram file
        file = await message.reply_to_message.download()
        filename = message.reply_to_message.document.file_name
        path = file

    # Ask for rename
    resp = await client.ask(message.chat.id, "Send new filename or 'no' to keep original:", reply_to_message_id=reply.id, timeout=60)
    if resp.text.lower() != "no":
        filename = resp.text

    pid = pixeldrain.upload_file(path, filename)
    await reply.edit(f"Uploaded!
PixelDrain: https://pixeldrain.com/u/{pid}")
    os.remove(path)

async def handle_leech(client, message, is_reply=False):
    args = message.text.split()
    url, extract = None, False
    # Support "leech [url] -e"
    if len(args) > 2:
        url, extract = (args[1], args[2] == "-e")
    elif len(args) > 1:
        extract = args[1] == "-e"
        url = args[1] if not extract else None
    else:
        url = None

    paths = []
    if is_reply and message.reply_to_message.document:
        file = await message.reply_to_message.download()
        if extract and zipfile.is_zipfile(file):
            with zipfile.ZipFile(file, 'r') as z:
                paths = z.namelist()
                z.extractall("/tmp/leechzip")
            os.remove(file)
            for f in paths:
                await client.send_document(message.chat.id, f"/tmp/leechzip/{f}", thumb=database.get_thumb(message.from_user.id))
            for f in paths:
                os.remove(f"/tmp/leechzip/{f}")
        else:  # No extract
            await client.send_document(message.chat.id, file, thumb=database.get_thumb(message.from_user.id))
            os.remove(file)
        return
    elif url:
        temp = tempfile.NamedTemporaryFile(delete=False)
        await download_url(url, temp.name, message)
        if extract and zipfile.is_zipfile(temp.name):
            with zipfile.ZipFile(temp.name, 'r') as z:
                paths = z.namelist()
                z.extractall("/tmp/leechzip")
            os.remove(temp.name)
            for f in paths:
                await client.send_document(message.chat.id, f"/tmp/leechzip/{f}", thumb=database.get_thumb(message.from_user.id))
                os.remove(f"/tmp/leechzip/{f}")
        else:
            await client.send_document(message.chat.id, temp.name, thumb=database.get_thumb(message.from_user.id))
            os.remove(temp.name)
    else:
        await message.reply("Send a link or reply to a document.")

async def download_url(url, dest, message=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            size = int(resp.headers.get('content-length', 0))
            downloaded = 0
            with open(dest, 'wb') as f:
                async for chunk in resp.content.iter_chunked(10240):
                    if not chunk: break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if message:
                        pct = downloaded / size if size else 0
                        speed = int(len(chunk) / 1)
                        bar = utils.progress_bar_string(pct)
                        await message.edit(f"{bar} ({utils.human_readable_size(downloaded)}/{utils.human_readable_size(size)})")

async def handle_status(message):
    await message.reply("All queued/leech/mirror tasks are running. (Add per-user tracking if needed)")

async def handle_thumb(client, message):
    thumb_id = database.get_thumb(message.from_user.id)
    if thumb_id:
        await message.reply_photo(thumb_id, caption="Current thumbnail.
Send new photo, or reply /no to keep.")
        resp = await client.ask(message.chat.id, "Send new thumbnail or /no:", timeout=60)
        if resp.text == "/no":
            return
        elif resp.photo:
            database.set_thumb(message.from_user.id, resp.photo.file_id)
            await message.reply("Thumbnail updated! 🚀")
    else:
        msg = await client.ask(message.chat.id, "Send an image or image URL…", timeout=60)
        if msg.photo:
            database.set_thumb(message.from_user.id, msg.photo.file_id)
            await message.reply("Thumbnail set!")
        elif msg.text:
            # You could support custom download of thumb by URL here if desired.
            await message.reply("Send photo as image (not URL) for now.")

async def cancel_all(user_id):
    # For future: add task cancelling per user (if using custom queues)
    pass
