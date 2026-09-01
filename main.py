import os
import time
from pyrogram import Client, filters

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

app = Client(
    "auto_reply",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

AUTO_REPLY = True
REPLY = "👋 Hello! Main abhi available nahi hoon. Tumhara message mil gaya hai ✅"

cooldown = {}

# ON
@app.on_message(filters.me & filters.command("on"))
async def on(client, message):
    global AUTO_REPLY
    AUTO_REPLY = True
    await message.edit("🟢 Auto Reply ON")


# OFF
@app.on_message(filters.me & filters.command("off"))
async def off(client, message):
    global AUTO_REPLY
    AUTO_REPLY = False
    await message.edit("🔴 Auto Reply OFF")


# STATUS
@app.on_message(filters.me & filters.command("status"))
async def status(client, message):
    state = "🟢 ON" if AUTO_REPLY else "🔴 OFF"
    await message.edit(f"🤖 Auto Reply: {state}")


# SET REPLY
@app.on_message(filters.me & filters.command("setreply"))
async def setreply(client, message):
    global REPLY

    text = message.text.split(" ", 1)

    if len(text) == 1:
        await message.edit("❌ Example: /setreply Hello 👋")
        return

    REPLY = text[1]
    await message.edit("✅ Reply updated!")


# ID
@app.on_message(filters.me & filters.command("id"))
async def get_id(client, message):
    await message.edit(
        f"👤 Your ID: `{message.from_user.id}`\n"
        f"💬 Chat ID: `{message.chat.id}`"
    )


# AUTO REPLY
@app.on_message(
    filters.private &
    ~filters.me &
    ~filters.bot
)
async def reply(client, message):

    if not AUTO_REPLY:
        return

    user_id = message.from_user.id
    now = time.time()

    # 60 second cooldown
    if now - cooldown.get(user_id, 0) < 60:
        return

    cooldown[user_id] = now

    await message.reply_text(REPLY)


print("🤖 Auto Reply Userbot Starting...")
app.run()
