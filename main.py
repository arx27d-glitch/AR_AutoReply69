import os
import time
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, ChatPrivileges


# =========================================================
# CONFIG
# =========================================================

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

app = Client(
    "AR_Manager",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


# =========================================================
# AUTO REPLY
# =========================================================

AUTO_REPLY = True

REPLY_TEXT = (
    "╭━━━〔 🤖 𝐀𝐑 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘 〕━━━╮\n"
    "│\n"
    "│ 👋 𝐇𝐞𝐥𝐥𝐨!\n"
    "│\n"
    "│ 𝐌𝐚𝐢𝐧 𝐚𝐛𝐡𝐢 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐧𝐚𝐡𝐢 𝐡𝐨𝐨𝐧.\n"
    "│ 💌 𝐘𝐨𝐮𝐫 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐫𝐞𝐜𝐞𝐢𝐯𝐞𝐝 ✅\n"
    "│\n"
    "╰━━━━━━━━━━━━━━━━━━━━╯"
)

COOLDOWN = 60
last_reply = {}


# =========================================================
# AUTO REPLY HANDLER
# =========================================================

@app.on_message(
    filters.private
    & ~filters.me
    & ~filters.bot
)
async def auto_reply(client, message):

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

    except Exception as e:
        print("Auto Reply Error:", e)


# =========================================================
# ON
# =========================================================

@app.on_message(filters.me & filters.command("on", prefixes="/"))
async def turn_on(client, message):

    global AUTO_REPLY
    AUTO_REPLY = True

    await message.edit_text(
        "╭━━━〔 🟢 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘 〕━━━╮\n"
        "│\n"
        "│ ✅ 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐎𝐍\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# OFF
# =========================================================

@app.on_message(filters.me & filters.command("off", prefixes="/"))
async def turn_off(client, message):

    global AUTO_REPLY
    AUTO_REPLY = False

    await message.edit_text(
        "╭━━━〔 🔴 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘 〕━━━╮\n"
        "│\n"
        "│ ❌ 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐎𝐅𝐅\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# STATUS
# =========================================================

@app.on_message(filters.me & filters.command("status", prefixes="/"))
async def status(client, message):

    state = "🟢 𝐎𝐍" if AUTO_REPLY else "🔴 𝐎𝐅𝐅"

    await message.edit_text(
        "╭━━━〔 🤖 𝐀𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐑 〕━━━╮\n"
        "│\n"
        f"│ 📩 𝐀𝐮𝐭𝐨 𝐑𝐞𝐩𝐥𝐲: {state}\n"
        f"│ ⏱️ 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧: {COOLDOWN}s\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# SET REPLY
# =========================================================

@app.on_message(filters.me & filters.command("setreply", prefixes="/"))
async def set_reply(client, message):

    global REPLY_TEXT

    parts = (message.text or "").split(maxsplit=1)

    if len(parts) < 2:
        await message.edit_text(
            "╭━━━〔 ❌ 𝐄𝐑𝐑𝐎𝐑 〕━━━╮\n"
            "│\n"
            "│ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐞𝐱𝐭 𝐦𝐢𝐬𝐬𝐢𝐧𝐠!\n"
            "│\n"
            "│ Example:\n"
            "│ `/setreply Hello 👋`\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━╯"
        )
        return

    REPLY_TEXT = parts[1]

    await message.edit_text(
        "╭━━━〔 ✅ 𝐔𝐏𝐃𝐀𝐓𝐄𝐃 〕━━━╮\n"
        "│\n"
        "│ 💬 𝐀𝐮𝐭𝐨 𝐫𝐞𝐩𝐥𝐲 𝐮𝐩𝐝𝐚𝐭𝐞𝐝!\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# CURRENT REPLY
# =========================================================

@app.on_message(filters.me & filters.command("reply", prefixes="/"))
async def current_reply(client, message):

    await message.edit_text(
        "╭━━━〔 💬 𝐂𝐔𝐑𝐑𝐄𝐍𝐓 𝐑𝐄𝐏𝐋𝐘 〕━━━╮\n"
        "│\n"
        f"│ {REPLY_TEXT}\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# ID
# =========================================================

@app.on_message(filters.me & filters.command("id", prefixes="/"))
async def get_id(client, message):

    text = (
        "╭━━━〔 🆔 𝐈𝐃 𝐈𝐍𝐅𝐎 〕━━━╮\n"
        "│\n"
        f"│ 👤 𝐘𝐨𝐮𝐫 𝐈𝐃: `{message.from_user.id}`\n"
        f"│ 💬 𝐂𝐡𝐚𝐭 𝐈𝐃: `{message.chat.id}`\n"
    )

    if message.reply_to_message:
        if message.reply_to_message.from_user:
            text += (
                f"│ 👤 𝐑𝐞𝐩𝐥𝐢𝐞𝐝 𝐔𝐬𝐞𝐫: "
                f"`{message.reply_to_message.from_user.id}`\n"
            )

    text += "│\n╰━━━━━━━━━━━━━━━━╯"

    await message.edit_text(text)


# =========================================================
# SAVE MESSAGE
# Reply to any message + /save
# =========================================================

@app.on_message(
    filters.me
    & filters.command("save", prefixes="/")
)
async def save_message(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "╭━━━〔 ❌ 𝐒𝐀𝐕𝐄 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 〕━━━╮\n"
            "│\n"
            "│ 𝐊𝐢𝐬𝐢 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐩𝐚𝐫 𝐫𝐞𝐩𝐥𝐲 𝐤𝐚𝐫𝐤𝐞\n"
            "│ `/save` 𝐥𝐢𝐤𝐡𝐨.\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯"
        )
        return

    try:
        await client.forward_messages(
            "me",
            message.chat.id,
            message.reply_to_message.id
        )

        await message.edit_text(
            "╭━━━〔 💾 𝐒𝐀𝐕𝐄𝐃 〕━━━╮\n"
            "│\n"
            "│ ✅ 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐒𝐚𝐯𝐞𝐝 𝐌𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐦𝐞𝐢𝐧\n"
            "│ 𝐬𝐚𝐯𝐞 𝐤𝐚𝐫 𝐝𝐢𝐲𝐚 𝐠𝐚𝐲𝐚.\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ **Save Error:**\n`{e}`"
        )


# =========================================================
# BAN
# =========================================================

@app.on_message(
    filters.me
    & filters.command("ban", prefixes="/")
    & filters.group
)
async def ban_user(client, message):

    if not message.reply_to_message:
        await message.edit_text("❌ User ke message par reply karke `/ban` bhejo.")
        return

    user = message.reply_to_message.from_user

    if not user:
        return

    try:
        await client.ban_chat_member(
            message.chat.id,
            user.id
        )

        await message.edit_text(
            f"╭━━〔 🔨 𝐁𝐀𝐍𝐍𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            f"╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(f"❌ Ban Error:\n`{e}`")


# =========================================================
# UNBAN
# =========================================================

@app.on_message(
    filters.me
    & filters.command("unban", prefixes="/")
    & filters.group
)
async def unban_user(client, message):

    parts = (message.text or "").split()

    if len(parts) < 2:
        await message.edit_text(
            "❌ Example: `/unban 123456789`"
        )
        return

    try:
        user_id = int(parts[1])

        await client.unban_chat_member(
            message.chat.id,
            user_id
        )

        await message.edit_text(
            f"╭━━〔 ✅ 𝐔𝐍𝐁𝐀𝐍𝐍𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user_id}`\n"
            f"╰━━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(f"❌ Unban Error:\n`{e}`")


# =========================================================
# KICK
# =========================================================

@app.on_message(
    filters.me
    & filters.command("kick", prefixes="/")
    & filters.group
)
async def kick_user(client, message):

    if not message.reply_to_message:
        await message.edit_text("❌ User ke message par reply karke `/kick` bhejo.")
        return

    user = message.reply_to_message.from_user

    if not user:
        return

    try:
        await client.ban_chat_member(
            message.chat.id,
            user.id
        )

        await client.unban_chat_member(
            message.chat.id,
            user.id
        )

        await message.edit_text(
            f"╭━━〔 👢 𝐊𝐈𝐂𝐊𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            f"╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(f"❌ Kick Error:\n`{e}`")


# =========================================================
# MUTE
# =========================================================

@app.on_message(
    filters.me
    & filters.command("mute", prefixes="/")
    & filters.group
)
async def mute_user(client, message):

    if not message.reply_to_message:
        await message.edit_text("❌ User ke message par reply karke `/mute` bhejo.")
        return

    user = message.reply_to_message.from_user

    if not user:
        return

    try:
        until = datetime.now() + timedelta(hours=1)

        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            permissions=ChatPermissions(),
            until_date=until
        )

        await message.edit_text(
            f"╭━━〔 🔇 𝐌𝐔𝐓𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            f"│ ⏱️ 𝐓𝐢𝐦𝐞: 𝟏 𝐇𝐨𝐮𝐫\n"
            f"╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(f"❌ Mute Error:\n`{e}`")


# =========================================================
# UNMUTE
# =========================================================

@app.on_message(
    filters.me
    & filters.command("unmute", prefixes="/")
    & filters.group
)
async def unmute_user(client, message):

    if not message.reply_to_message:
        await message.edit_text("❌ User ke message par reply karke `/unmute` bhejo.")
        return

    user = message.reply_to_message.from_user

    if not user:
        return

    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )

        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            permissions=permissions
        )

        await message.edit_text(
            f"╭━━〔 🔊 𝐔𝐍𝐌𝐔𝐓𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            f"╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(f"❌ Unmute Error:\n`{e}`")


# =========================================================
# DELETE
# =========================================================

@app.on_message(
    filters.me
    & filters.command("del", prefixes="/")
    & filters.group
)
async def delete_message(client, message):

    if not message.reply_to_message:
        await message.edit_text("❌ Delete karne wale message par reply karo.")
        return

    try:
        await message.reply_to_message.delete()
        await message.delete()

    except Exception as e:
        print("Delete Error:", e)


# =========================================================
# PIN
# =========================================================

@app.on_message(
    filters.me
    & filters.command("pin", prefixes="/")
    & filters.group
)
async def pin_message(client, message):

    if not message.reply_to_message:
        await message.edit_text("❌ Pin karne wale message par reply karo.")
        return

    try:
        await message.reply_to_message.pin()

        await message.edit_text(
            "╭━━〔 📌 𝐏𝐈𝐍𝐍𝐄𝐃 〕━━╮\n"
            "│\n"
            "│ ✅ 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐩𝐢𝐧𝐧𝐞𝐝!\n"
            "│\n"
            "╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(f"❌ Pin Error:\n`{e}`")


# =========================================================
# PROMOTE
# =========================================================

@app.on_message(
    filters.me
    & filters.command("promote", prefixes="/")
    & filters.group
)
async def promote_user(client, message):

    if not message.reply_to_message:
        await message.edit_text("❌ User ke message par reply karo.")
        return

    user = message.reply_to_message.from_user

    if not user:
        return

    try:
        privileges = ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        )

        await client.promote_chat_member(
            message.chat.id,
            user.id,
            privileges=privileges
        )

        await message.edit_text(
            f"╭━━〔 👑 𝐏𝐑𝐎𝐌𝐎𝐓𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            f"╰━━━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(f"❌ Promote Error:\n`{e}`")


# =========================================================
# DEMOTE
# =========================================================

@app.on_message(
    filters.me
    & filters.command("demote", prefixes="/")
    & filters.group
)
async def demote_user(client, message):

    if not message.reply_to_message:
        await message.edit_text("❌ User ke message par reply karo.")
        return

    user = message.reply_to_message.from_user

    if not user:
        return

    try:
        await client.promote_chat_member(
            message.chat.id,
            user.id,
            privileges=ChatPrivileges()
        )

        await message.edit_text(
            f"╭━━〔 ⬇️ 𝐃𝐄𝐌𝐎𝐓𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            f"╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(f"❌ Demote Error:\n`{e}`")


# =========================================================
# HELP
# =========================================================

@app.on_message(filters.me & filters.command("help", prefixes="/"))
async def help_command(client, message):

    await message.edit_text(
        "╭━━━〔 🤖 𝐀𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐑 〕━━━╮\n"
        "│\n"
        "│ 📩 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘\n"
        "│ `/on` — ON\n"
        "│ `/off` — OFF\n"
        "│ `/setreply TEXT` — Reply change\n"
        "│ `/reply` — Current reply\n"
        "│ `/status` — Status\n"
        "│\n"
        "│ 🛡️ 𝐆𝐑𝐎𝐔𝐏 𝐌𝐀𝐍𝐀𝐆𝐄𝐑\n"
        "│ `/ban` — Reply → Ban\n"
        "│ `/unban ID` — Unban\n"
        "│ `/kick` — Reply → Kick\n"
        "│ `/mute` — Reply → Mute\n"
        "│ `/unmute` — Unmute\n"
        "│ `/promote` — Reply → Admin\n"
        "│ `/demote` — Reply → Remove Admin\n"
        "│ `/pin` — Reply → Pin\n"
        "│ `/del` — Reply → Delete\n"
        "│\n"
        "│ 💾 𝐒𝐀𝐕𝐄\n"
        "│ `/save` — Reply → Saved Messages\n"
        "│\n"
        "│ 🆔 `/id` — Get IDs\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# START
# =========================================================

print("======================================")
print("🤖 AR AUTO REPLY + GROUP MANAGER")
print("💾 SAVE MESSAGE ENABLED")
print("🚀 RAILWAY STARTING...")
print("======================================")

app.run()
