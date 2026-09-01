import os
import time
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

app = Client(
    "AR_AutoReply",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

AUTO_REPLY = False
REPLY_TEXT = "👋 Hello! Main abhi available nahi hoon. Tumhara message mil gaya hai ✅"

COOLDOWN = 60
last_reply = {}


# ---------- COMMANDS ----------

@app.on_message(filters.me & filters.command("on", prefixes="/"))
async def auto_on(client, message):
    global AUTO_REPLY
    AUTO_REPLY = True
    await message.edit_text("🟢 **Auto Reply ON**")


@app.on_message(filters.me & filters.command("off", prefixes="/"))
async def auto_off(client, message):
    global AUTO_REPLY
    AUTO_REPLY = False
    await message.edit_text("🔴 **Auto Reply OFF**")


@app.on_message(filters.me & filters.command("status", prefixes="/"))
async def status(client, message):
    status = "🟢 ON" if AUTO_REPLY else "🔴 OFF"

    await message.edit_text(
        f"🤖 **AR AutoReply Manager**\n\n"
        f"Status: {status}\n"
        f"Cooldown: `{COOLDOWN}s`"
    )


@app.on_message(filters.me & filters.command("setreply", prefixes="/"))
async def set_reply(client, message):
    global REPLY_TEXT

    parts = (message.text or "").split(maxsplit=1)

    if len(parts) < 2:
        await message.edit_text(
            "❌ Text missing!\n\n"
            "`/setreply Hello 👋 Main busy hoon.`"
        )
        return

    REPLY_TEXT = parts[1]

    await message.edit_text(
        "✅ **Auto Reply Updated!**\n\n"
        + REPLY_TEXT
    )


@app.on_message(filters.me & filters.command("reply", prefixes="/"))
async def current_reply(client, message):
    await message.edit_text(
        "💬 **Current Reply:**\n\n" + REPLY_TEXT
    )


@app.on_message(filters.me & filters.command("id", prefixes="/"))
async def get_id(client, message):
    await message.edit_text(
        f"👤 **Your ID:** `{message.from_user.id}`\n"
        f"💬 **Chat ID:** `{message.chat.id}`"
    )


@app.on_message(filters.me & filters.command("help", prefixes="/"))
async def help_command(client, message):
    await message.edit_text(
        "🤖 **AR AutoReply Manager**\n\n"
        "⚙️ Commands:\n\n"
        "`/on` — Auto Reply ON\n"
        "`/off` — Auto Reply OFF\n"
        "`/status` — Status\n"
        "`/setreply TEXT` — Change reply\n"
        "`/reply` — Current reply\n"
        "`/id` — IDs\n"
        "`/help` — Help"
    )


# ---------- AUTO REPLY ----------

@app.on_message(
    filters.private
    & ~filters.me
    & ~filters.bot
)
async def incoming_message(client, message):

    if not AUTO_REPLY:
        return

    if not message.from_user:
        return

    user_id = message.from_user.id
    now = time.time()

    if now - last_reply.get(user_id, 0) < COOLDOWN:
        return

    last_reply[user_id] = now

    try:
        await message.reply_text(REPLY_TEXT)

    except FloodWait as e:
        print(f"FloodWait: {e.value} seconds")
        await asyncio.sleep(e.value)

    except Exception as e:
        print("Auto Reply Error:", e)


print("================================")
print("🤖 AR AutoReply Manager")
print("🚀 Railway starting...")
print("================================")

app.run()
