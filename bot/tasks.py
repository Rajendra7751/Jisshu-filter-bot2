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
        file = await message.reply_to_message.download()
        filename = message.reply_to_message.document.file_name
        path = file
    elif len(args) > 1:
        orig_link = args[1].strip()
        temp = tempfile.NamedTemporaryFile(delete=False)
        reply = await message.reply("Downloading from URL...")
        await download_url(orig_link, temp.name, reply)
        filename = os.path.basename(temp.name)
        path = temp.name
    else:
        await message.reply("Send /mirror [link] or reply to a file.")
        return

    # SKIP filename prompt for now
    # Just use detected/original filename
    uploading_msg = await message.reply("Uploading to PixelDrain...")
    try:
        pid = pixeldrain.upload_file(path, filename)
        await uploading_msg.edit(f"Uploaded!\nPixelDrain: https://pixeldrain.com/u/{pid}")
    except Exception as e:
        await uploading_msg.edit(f"Failed to upload: {e}")
    finally:
        if os.path.exists(path):
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

    if is_reply and message.reply_to_message and message.reply_to_message.document:
        file = await message.reply_to_message.download()
        filename = message.reply_to_message.document.file_name
        if extract and zipfile.is_zipfile(file):
            await send_zip_contents(client, message, file)
            os.remove(file)
        else:
            await message.reply_document(file, caption=f"Here is your file:\n{filename}")
            os.remove(file)
        return
    elif url:
        temp = tempfile.NamedTemporaryFile(delete=False)
        reply = await message.reply(f"Downloading from {url}...")
        await download_url(url, temp.name, reply)
        filename = os.path.basename(temp.name)
        if extract and zipfile.is_zipfile(temp.name):
            await send_zip_contents(client, message, temp.name)
            os.remove(temp.name)
        else:
            await message.reply_document(temp.name, caption=f"Here is your file:\n{filename}")
            os.remove(temp.name)
    else:
        await message.reply("Send a link or reply to a document.")

async def send_zip_contents(client, message, zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall("/tmp/leechzip")
        files = [os.path.join("/tmp/leechzip", f) for f in z.namelist()]
        for file in files:
            if os.path.isdir(file):
                continue
            await message.reply_document(file, caption=f"Extracted: {os.path.basename(file)}")
            os.remove(file)
        os.rmdir("/tmp/leechzip")

async def download_url(url, dest, reply_message):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            size = int(resp.headers.get('content-length', 0))
            downloaded = 0
            with open(dest, 'wb') as f:
                async for chunk in resp.content.iter_chunked(10240):
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Only try to update bot's own reply message!
                    if reply_message:
                        pct = downloaded / size if size else 0
                        bar = utils.progress_bar_string(pct)
                        try:
                            await reply_message.edit(f"{bar} ({utils.human_readable_size(downloaded)}/{utils.human_readable_size(size)})")
                        except Exception:
                            pass  # Don't crash on edit errors

async def handle_status(message):
    await message.reply("All queued/leech/mirror tasks are running. (Add per-user tracking if needed)")

async def handle_thumb(client, message):
    thumb_id = database.get_thumb(message.from_user.id)
    if thumb_id:
        await message.reply_photo(thumb_id, caption="Current thumbnail. To update: currently not supported (prompt removed).")
        # For now, not supporting in-chat change prompt. FSM needed.
    else:
        await message.reply("Send an image to set a thumbnail (feature coming soon).")

async def cancel_all(user_id):
    # For future: add task cancelling per user (if tracking jobs)
    pass
