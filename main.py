import os
import time
import sqlite3
import asyncio
from collections import defaultdict

from pyrogram import Client, filters, enums
from pyrogram.types import (
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ============================================================
# ☠︎︎𝙰𝚁_乂 MANAGER
# Telegram Userbot | Session String | Railway
# ============================================================

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

DB_PATH = os.getenv("DB_PATH", "/data/ar_manager.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ============================================================
# DATABASE
# ============================================================

db = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

db.row_factory = sqlite3.Row

db.execute("""
CREATE TABLE IF NOT EXISTS chats (
    chat_id INTEGER PRIMARY KEY,
    welcome INTEGER DEFAULT 1,
    welcome_text TEXT,
    welcome_gif TEXT,
    autoreply INTEGER DEFAULT 1
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS replies (
    chat_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    response TEXT NOT NULL,
    UNIQUE(chat_id, keyword)
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS warnings (
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    warns INTEGER DEFAULT 0,
    PRIMARY KEY(chat_id, user_id)
)
""")

db.commit()

db_lock = asyncio.Lock()

# ============================================================
# CLIENT
# ============================================================

app = Client(
    "AR_MANAGER",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workers=16
)

START_TIME = time.time()

# ============================================================
# DEFAULT TEXT
# ============================================================

DEFAULT_WELCOME = """☠︎︎𝙰𝚁_乂 𝙈𝘼𝙉𝘼𝙂𝙀𝙍

╭━━━━━━━━━━━━━━━━━━╮
┃ 👋 𝙒𝙀𝙇𝘾𝙊𝙈𝙀
┃
┃ ✦ Hey {name}!
┃ ✦ Welcome to {chat}
┃
┃ 🖤 Enjoy Your Stay
┃ ✨ Have Fun!
╰━━━━━━━━━━━━━━━━━━╯"""

# ============================================================
# HELPERS
# ============================================================

def ensure_chat(chat_id):
    db.execute(
        "INSERT OR IGNORE INTO chats(chat_id) VALUES(?)",
        (chat_id,)
    )
    db.commit()


def get_chat(chat_id):
    ensure_chat(chat_id)
    return db.execute(
        "SELECT * FROM chats WHERE chat_id=?",
        (chat_id,)
    ).fetchone()


def uptime():
    seconds = int(time.time() - START_TIME)

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    return (
        f"{days}d {hours}h {minutes}m {seconds}s"
        if days else
        f"{hours}h {minutes}m {seconds}s"
    )


async def is_admin(chat_id, user_id):
    if OWNER_ID and user_id == OWNER_ID:
        return True

    try:
        member = await app.get_chat_member(
            chat_id,
            user_id
        )

        return member.status in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR
        )

    except Exception:
        return False


async def is_protected(chat_id, user_id):
    try:
        member = await app.get_chat_member(
            chat_id,
            user_id
        )

        return member.status in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR
        )

    except Exception:
        return False


async def target_user(message):
    if message.reply_to_message:
        return message.reply_to_message.from_user

    if len(message.command) >= 2:
        try:
            return await app.get_users(
                message.command[1]
            )
        except Exception:
            return None

    return None


def welcome_format(text, user, chat):
    return (
        text
        .replace(
            "{name}",
            user.first_name or "Friend"
        )
        .replace(
            "{username}",
            f"@{user.username}"
            if user.username else "No Username"
        )
        .replace(
            "{id}",
            str(user.id)
        )
        .replace(
            "{chat}",
            chat.title or "Group"
        )
    )


async def require_admin(message):
    if not message.from_user:
        return False

    if not await is_admin(
        message.chat.id,
        message.from_user.id
    ):
        return False

    return True


# ============================================================
# HELP
# ============================================================

HELP_TEXT = """☠︎︎𝙰𝚁_乂 **𝙈𝘼𝙉𝘼𝙂𝙀𝙍**

╭━━━〔 ⚡ BASIC 〕━━━╮
┃ `/ping`
┃ `/alive`
┃ `/id`
┃ `/info`
┃ `/stats`
╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 🛡️ MODERATION 〕━━━╮
┃ `/ban`
┃ `/unban`
┃ `/kick`
┃ `/mute`
┃ `/unmute`
┃ `/warn`
┃ `/unwarn`
╰━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━〔 🧹 MESSAGE 〕━━━╮
┃ `/del`
┃ `/purge 10`
┃ `/pin`
┃ `/unpin`
╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 👋 WELCOME 〕━━━╮
┃ `/welcome on`
┃ `/welcome off`
┃ `/setwelcome TEXT`
┃ `/getwelcome`
┃ `/delwelcome`
┃ `/setgif`
┃ `/delgif`
╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 🤖 AUTOREPLY 〕━━━╮
┃ `/autoreply on`
┃ `/autoreply off`
┃ `/setreply hi | Hello 👋`
┃ `/delreply hi`
┃ `/replies`
╰━━━━━━━━━━━━━━━━━━━━━━╯
"""

# ============================================================
# /HELP
# ============================================================

@app.on_message(filters.command("help"))
async def help_cmd(_, message):
    await message.reply_text(
        HELP_TEXT,
        disable_web_page_preview=True
    )


# ============================================================
# /PING
# ============================================================

@app.on_message(filters.command("ping"))
async def ping_cmd(_, message):

    start = time.perf_counter()

    msg = await message.reply_text(
        "☠︎︎𝙰𝚁_乂 **𝙋𝙄𝙉𝙂𝙄𝙉𝙂...**"
    )

    ms = (time.perf_counter() - start) * 1000

    await msg.edit_text(
        "☠︎︎𝙰𝚁_乂 **𝙋𝙊𝙉𝙂! ⚡**\n\n"
        f"⚡ Response: `{ms:.0f} ms`\n"
        f"🟢 Status: `ONLINE`"
    )


# ============================================================
# /ALIVE
# ============================================================

@app.on_message(filters.command("alive"))
async def alive_cmd(_, message):

    me = await app.get_me()

    await message.reply_text(
        "☠︎︎𝙰𝚁_乂 **𝙎𝙔𝙎𝙏𝙀𝙈 𝘼𝙇𝙄𝙑𝙀**\n\n"
        f"👤 Account: `{me.first_name}`\n"
        f"🆔 ID: `{me.id}`\n"
        f"⏱ Uptime: `{uptime()}`\n"
        "🟢 Status: `ONLINE`"
    )


# ============================================================
# /ID
# ============================================================

@app.on_message(filters.command("id"))
async def id_cmd(_, message):

    if message.reply_to_message:
        user = message.reply_to_message.from_user

        await message.reply_text(
            "☠︎︎𝙰𝚁_乂 **𝙄𝘿 𝙄𝙉𝙁𝙊**\n\n"
            f"👤 User: {user.mention}\n"
            f"🆔 User ID: `{user.id}`\n"
            f"💬 Chat ID: `{message.chat.id}`"
        )
        return

    await message.reply_text(
        "☠︎︎𝙰𝚁_乂 **𝙄𝘿**\n\n"
        f"💬 Chat ID: `{message.chat.id}`\n"
        f"👤 Your ID: `{message.from_user.id}`"
    )


# ============================================================
# /INFO
# ============================================================

@app.on_message(filters.command("info"))
async def info_cmd(_, message):

    user = await target_user(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or use:\n"
            "`/info @username`"
        )
        return

    username = (
        f"@{user.username}"
        if user.username else "None"
    )

    await message.reply_text(
        "☠︎︎𝙰𝚁_乂 **𝙐𝙎𝙀𝙍 𝙄𝙉𝙁𝙊**\n\n"
        f"👤 Name: `{user.first_name or 'Unknown'}`\n"
        f"🆔 ID: `{user.id}`\n"
        f"🔗 Username: `{username}`\n"
        f"🤖 Bot: `{user.is_bot}`"
    )


# ============================================================
# /STATS
# ============================================================

@app.on_message(filters.command("stats"))
async def stats_cmd(_, message):

    try:
        dialogs = 0
        groups = 0
        private = 0

        async for dialog in app.get_dialogs():

            dialogs += 1

            if dialog.chat.type in (
                enums.ChatType.GROUP,
                enums.ChatType.SUPERGROUP
            ):
                groups += 1

            elif dialog.chat.type == enums.ChatType.PRIVATE:
                private += 1

        await message.reply_text(
            "☠︎︎𝙰𝚁_乂 **𝙎𝙏𝘼𝙏𝙎**\n\n"
            f"💬 Dialogs: `{dialogs}`\n"
            f"👥 Groups: `{groups}`\n"
            f"👤 Private: `{private}`\n"
            f"⏱ Uptime: `{uptime()}`"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Stats error:\n`{e}`"
        )


# ============================================================
# BAN
# ============================================================

@app.on_message(filters.command("ban") & filters.group)
async def ban_cmd(_, message):

    if not await require_admin(message):
        return

    user = await target_user(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or `/ban @username`"
        )
        return

    if await is_protected(
        message.chat.id,
        user.id
    ):
        await message.reply_text(
            "❌ Admin ko ban nahi kar sakta."
        )
        return

    try:
        await app.ban_chat_member(
            message.chat.id,
            user.id
        )

        await message.reply_text(
            f"☠︎︎𝙰𝚁_乂 **𝘽𝘼𝙉𝙉𝙀𝘿**\n\n"
            f"👤 {user.mention}\n"
            f"🆔 `{user.id}`"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Ban failed:\n`{e}`"
        )


# ============================================================
# UNBAN
# ============================================================

@app.on_message(filters.command("unban") & filters.group)
async def unban_cmd(_, message):

    if not await require_admin(message):
        return

    user = await target_user(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or `/unban @username`"
        )
        return

    try:
        await app.unban_chat_member(
            message.chat.id,
            user.id
        )

        await message.reply_text(
            f"☠︎︎𝙰𝚁_乂 **𝙐𝙉𝘽𝘼𝙉𝙉𝙀𝘿**\n\n"
            f"👤 {user.mention}"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Unban failed:\n`{e}`"
        )


# ============================================================
# KICK
# ============================================================

@app.on_message(filters.command("kick") & filters.group)
async def kick_cmd(_, message):

    if not await require_admin(message):
        return

    user = await target_user(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or `/kick @username`"
        )
        return

    if await is_protected(
        message.chat.id,
        user.id
    ):
        await message.reply_text(
            "❌ Admin ko kick nahi kar sakta."
        )
        return

    try:
        await app.ban_chat_member(
            message.chat.id,
            user.id
        )

        await app.unban_chat_member(
            message.chat.id,
            user.id
        )

        await message.reply_text(
            f"👢 ☠︎︎𝙰𝚁_乂 **𝙆𝙄𝘾𝙆𝙀𝘿**\n\n"
            f"👤 {user.mention}"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Kick failed:\n`{e}`"
        )


# ============================================================
# MUTE
# ============================================================

@app.on_message(filters.command("mute") & filters.group)
async def mute_cmd(_, message):

    if not await require_admin(message):
        return

    user = await target_user(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or `/mute @username`"
        )
        return

    if await is_protected(
        message.chat.id,
        user.id
    ):
        await message.reply_text(
            "❌ Admin ko mute nahi kar sakta."
        )
        return

    try:
        await app.restrict_chat_member(
            message.chat.id,
            user.id,
            ChatPermissions(
                can_send_messages=False
            )
        )

        await message.reply_text(
            f"🔇 ☠︎︎𝙰𝚁_乂 **𝙈𝙐𝙏𝙀𝘿**\n\n"
            f"👤 {user.mention}"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Mute failed:\n`{e}`"
        )


# ============================================================
# UNMUTE
# ============================================================

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_cmd(_, message):

    if not await require_admin(message):
        return

    user = await target_user(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or `/unmute @username`"
        )
        return

    try:
        await app.restrict_chat_member(
            message.chat.id,
            user.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )

        await message.reply_text(
            f"🔊 ☠︎︎𝙰𝚁_乂 **𝙐𝙉𝙈𝙐𝙏𝙀𝘿**\n\n"
            f"👤 {user.mention}"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Unmute failed:\n`{e}`"
        )


# ============================================================
# WARN
# ============================================================

@app.on_message(filters.command("warn") & filters.group)
async def warn_cmd(_, message):

    if not await require_admin(message):
        return

    user = await target_user(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or `/warn @username`"
        )
        return

    if await is_protected(
        message.chat.id,
        user.id
    ):
        await message.reply_text(
            "❌ Admin ko warn nahi kar sakta."
        )
        return

    row = db.execute(
        "SELECT warns FROM warnings "
        "WHERE chat_id=? AND user_id=?",
        (message.chat.id, user.id)
    ).fetchone()

    warns = (row["warns"] if row else 0) + 1

    db.execute("""
        INSERT INTO warnings(chat_id,user_id,warns)
        VALUES(?,?,?)
        ON CONFLICT(chat_id,user_id)
        DO UPDATE SET warns=excluded.warns
    """, (
        message.chat.id,
        user.id,
        warns
    ))

    db.commit()

    if warns >= 3:

        try:
            await app.ban_chat_member(
                message.chat.id,
                user.id
            )

            db.execute(
                "DELETE FROM warnings "
                "WHERE chat_id=? AND user_id=?",
                (message.chat.id, user.id)
            )

            db.commit()

            await message.reply_text(
                f"☠︎︎𝙰𝚁_乂 **𝟯/𝟯 𝙒𝘼𝙍𝙉𝙄𝙉𝙂𝙎**\n\n"
                f"👤 {user.mention}\n"
                "🔨 **BANNED**"
            )

        except Exception as e:
            await message.reply_text(
                f"❌ Auto-ban failed:\n`{e}`"
            )

    else:

        await message.reply_text(
            f"⚠️ ☠︎︎𝙰𝚁_乂 **𝙒𝘼𝙍𝙉**\n\n"
            f"👤 {user.mention}\n"
            f"📊 `{warns}/3`"
        )


# ============================================================
# UNWARN
# ============================================================

@app.on_message(filters.command("unwarn") & filters.group)
async def unwarn_cmd(_, message):

    if not await require_admin(message):
        return

    user = await target_user(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user."
        )
        return

    row = db.execute(
        "SELECT warns FROM warnings "
        "WHERE chat_id=? AND user_id=?",
        (message.chat.id, user.id)
    ).fetchone()

    if not row:
        await message.reply_text(
            "ℹ️ No warnings found."
        )
        return

    warns = max(
        0,
        row["warns"] - 1
    )

    if warns:
        db.execute(
            "UPDATE warnings SET warns=? "
            "WHERE chat_id=? AND user_id=?",
            (
                warns,
                message.chat.id,
                user.id
            )
        )
    else:
        db.execute(
            "DELETE FROM warnings "
            "WHERE chat_id=? AND user_id=?",
            (
                message.chat.id,
                user.id
            )
        )

    db.commit()

    await message.reply_text(
        f"✅ **Warning removed**\n"
        f"👤 {user.mention}\n"
        f"📊 `{warns}/3`"
    )


# ============================================================
# DELETE
# ============================================================

@app.on_message(filters.command("del") & filters.group)
async def del_cmd(_, message):

    if not await require_admin(message):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ Reply to a message."
        )
        return

    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception:
        pass


# ============================================================
# PURGE
# ============================================================

@app.on_message(filters.command("purge") & filters.group)
async def purge_cmd(_, message):

    if not await require_admin(message):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ Reply to the first message."
        )
        return

    try:
        amount = 10

        if len(message.command) >= 2:
            try:
                amount = min(
                    int(message.command[1]),
                    100
                )
            except ValueError:
                pass

        messages = []

        async for msg in app.get_chat_history(
            message.chat.id,
            limit=amount + 1,
            offset_id=message.reply_to_message.id
        ):
            if msg.id >= message.reply_to_message.id:
                messages.append(msg.id)

        if messages:
            await app.delete_messages(
                message.chat.id,
                messages
            )

    except Exception as e:
        await message.reply_text(
            f"❌ Purge failed:\n`{e}`"
        )


# ============================================================
# PIN
# ============================================================

@app.on_message(filters.command("pin") & filters.group)
async def pin_cmd(_, message):

    if not await require_admin(message):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ Reply to a message."
        )
        return

    try:
        await message.reply_to_message.pin()

        await message.reply_text(
            "📌 ☠︎︎𝙰𝚁_乂 **𝙋𝙄𝙉𝙉𝙀𝘿**"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Pin failed:\n`{e}`"
        )


# ============================================================
# UNPIN
# ============================================================

@app.on_message(filters.command("unpin") & filters.group)
async def unpin_cmd(_, message):

    if not await require_admin(message):
        return

    try:
        await app.unpin_chat_message(
            message.chat.id
        )

        await message.reply_text(
            "📌 ☠︎︎𝙰𝚁_乂 **𝙐𝙉𝙋𝙄𝙉𝙉𝙀𝘿**"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Unpin failed:\n`{e}`"
        )


# ============================================================
# WELCOME ON/OFF
# ============================================================

@app.on_message(filters.command("welcome"))
async def welcome_cmd(_, message):

    if message.chat.type not in (
        enums.ChatType.GROUP,
        enums.ChatType.SUPERGROUP
    ):
        await message.reply_text(
            "❌ Welcome system groups ke liye hai."
        )
        return

    if not await require_admin(message):
        return

    ensure_chat(message.chat.id)

    if len(message.command) < 2:
        row = get_chat(message.chat.id)

        await message.reply_text(
            "👋 **WELCOME STATUS**\n\n"
            f"Status: "
            f"**{'ON 🟢' if row['welcome'] else 'OFF 🔴'}**"
        )
        return

    value = message.command[1].lower()

    if value not in ("on", "off"):
        await message.reply_text(
            "❌ `/welcome on` or `/welcome off`"
        )
        return

    state = 1 if value == "on" else 0

    db.execute(
        "UPDATE chats SET welcome=? WHERE chat_id=?",
        (state, message.chat.id)
    )

    db.commit()

    await message.reply_text(
        f"👋 **Welcome {'ON 🟢' if state else 'OFF 🔴'}**"
    )


# ============================================================
# SET WELCOME
# ============================================================

@app.on_message(filters.command("setwelcome") & filters.group)
async def setwelcome_cmd(_, message):

    if not await require_admin(message):
        return

    if len(message.text.split(None, 1)) < 2:
        await message.reply_text(
            "❌ Example:\n\n"
            "`/setwelcome Hey {name}! "
            "Welcome to {chat} 👋`"
        )
        return

    text = message.text.split(None, 1)[1]

    if len(text) > 3000:
        await message.reply_text(
            "❌ Message too long."
        )
        return

    ensure_chat(message.chat.id)

    db.execute(
        "UPDATE chats SET welcome_text=? "
        "WHERE chat_id=?",
        (text, message.chat.id)
    )

    db.commit()

    await message.reply_text(
        "✅ ☠︎︎𝙰𝚁_乂 **𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙎𝘼𝙑𝙀𝘿!**\n\n"
        "Available:\n"
        "`{name}` `{username}` `{id}` `{chat}`"
    )


# ============================================================
# GET WELCOME
# ============================================================

@app.on_message(filters.command("getwelcome") & filters.group)
async def getwelcome_cmd(_, message):

    if not await require_admin(message):
        return

    row = get_chat(message.chat.id)

    text = row["welcome_text"] or DEFAULT_WELCOME

    await message.reply_text(
        "☠︎︎𝙰𝚁_乂 **𝙒𝙀𝙇𝘾𝙊𝙈𝙀**\n\n"
        f"👋 Status: "
        f"**{'ON 🟢' if row['welcome'] else 'OFF 🔴'}**\n"
        f"🎞️ GIF: "
        f"**{'SET 🟢' if row['welcome_gif'] else 'NOT SET 🔴'}**\n\n"
        "📝 **Message:**\n"
        f"{text}"
    )


# ============================================================
# DELETE WELCOME
# ============================================================

@app.on_message(filters.command("delwelcome") & filters.group)
async def delwelcome_cmd(_, message):

    if not await require_admin(message):
        return

    db.execute(
        "UPDATE chats SET welcome_text=NULL "
        "WHERE chat_id=?",
        (message.chat.id,)
    )

    db.commit()

    await message.reply_text(
        "🗑️ **Custom welcome removed.**"
    )


# ============================================================
# SET GIF
# ============================================================

@app.on_message(filters.command("setgif") & filters.group)
async def setgif_cmd(_, message):

    if not await require_admin(message):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ Kisi GIF/animation ko reply karke `/setgif` bhejo."
        )
        return

    msg = message.reply_to_message

    file_id = None

    if msg.animation:
        file_id = msg.animation.file_id

    elif msg.document:
        mime = msg.document.mime_type or ""

        if mime.startswith("video/"):
            file_id = msg.document.file_id

    if not file_id:
        await message.reply_text(
            "❌ Reply message mein GIF/animation nahi mila."
        )
        return

    ensure_chat(message.chat.id)

    db.execute(
        "UPDATE chats SET welcome_gif=? "
        "WHERE chat_id=?",
        (file_id, message.chat.id)
    )

    db.commit()

    await message.reply_text(
        "✅ ☠︎︎𝙰𝚁_乂 **𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙂𝙄𝙁 𝙎𝙀𝙏!** 🎞️"
    )


# ============================================================
# DELETE GIF
# ============================================================

@app.on_message(filters.command("delgif") & filters.group)
async def delgif_cmd(_, message):

    if not await require_admin(message):
        return

    db.execute(
        "UPDATE chats SET welcome_gif=NULL "
        "WHERE chat_id=?",
        (message.chat.id,)
    )

    db.commit()

    await message.reply_text(
        "🗑️ **Welcome GIF removed.**"
    )


# ============================================================
# NEW MEMBER
# ============================================================

@app.on_message(filters.new_chat_members)
async def new_member(_, message):

    row = get_chat(message.chat.id)

    if not row["welcome"]:
        return

    for user in message.new_chat_members:

        if user.is_self:
            continue

        text = welcome_format(
            row["welcome_text"] or DEFAULT_WELCOME,
            user,
            message.chat
        )

        try:

            if row["welcome_gif"]:

                await message.reply_animation(
                    row["welcome_gif"],
                    caption=text
                )

            else:

                await message.reply_text(text)

        except Exception:

            try:
                await message.reply_text(text)
            except Exception:
                pass


# ============================================================
# AUTOREPLY ON/OFF
# ============================================================

@app.on_message(filters.command("autoreply") & filters.group)
async def autoreply_cmd(_, message):

    if not await require_admin(message):
        return

    ensure_chat(message.chat.id)

    if len(message.command) < 2:

        row = get_chat(message.chat.id)

        await message.reply_text(
            "🤖 **AUTOREPLY**\n\n"
            f"Status: "
            f"**{'ON 🟢' if row['autoreply'] else 'OFF 🔴'}**"
        )
        return

    value = message.command[1].lower()

    if value not in ("on", "off"):
        await message.reply_text(
            "❌ `/autoreply on` or `/autoreply off`"
        )
        return

    state = 1 if value == "on" else 0

    db.execute(
        "UPDATE chats SET autoreply=? "
        "WHERE chat_id=?",
        (state, message.chat.id)
    )

    db.commit()

    await message.reply_text(
        f"🤖 **AutoReply {'ON 🟢' if state else 'OFF 🔴'}**"
    )


# ============================================================
# SET REPLY
# ============================================================

@app.on_message(filters.command("setreply") & filters.group)
async def setreply_cmd(_, message):

    if not await require_admin(message):
        return

    if not message.text or "|" not in message.text:

        await message.reply_text(
            "❌ **Format:**\n\n"
            "`/setreply hi | Hello 👋`"
        )
        return

    data = message.text.split(None, 1)[1]

    keyword, response = data.split("|", 1)

    keyword = keyword.strip().lower()
    response = response.strip()

    if not keyword or not response:
        await message.reply_text(
            "❌ Keyword/reply missing."
        )
        return

    db.execute("""
        INSERT INTO replies(chat_id,keyword,response)
        VALUES(?,?,?)
        ON CONFLICT(chat_id,keyword)
        DO UPDATE SET response=excluded.response
    """, (
        message.chat.id,
        keyword,
        response
    ))

    db.commit()

    await message.reply_text(
        "✅ ☠︎︎𝙰𝚁_乂 **𝙍𝙀𝙋𝙇𝙔 𝙎𝘼𝙑𝙀𝘿**\n\n"
        f"🔑 `{keyword}`\n"
        f"💬 {response}"
    )


# ============================================================
# DELETE REPLY
# ============================================================

@app.on_message(filters.command("delreply") & filters.group)
async def delreply_cmd(_, message):

    if not await require_admin(message):
        return

    if len(message.command) < 2:
        await message.reply_text(
            "❌ `/delreply keyword`"
        )
        return

    keyword = message.command[1].lower()

    db.execute(
        "DELETE FROM replies "
        "WHERE chat_id=? AND keyword=?",
        (message.chat.id, keyword)
    )

    db.commit()

    await message.reply_text(
        f"🗑️ Reply removed: `{keyword}`"
    )


# ============================================================
# LIST REPLIES
# ============================================================

@app.on_message(filters.command("replies") & filters.group)
async def replies_cmd(_, message):

    if not await require_admin(message):
        return

    rows = db.execute(
        "SELECT keyword FROM replies "
        "WHERE chat_id=? ORDER BY keyword",
        (message.chat.id,)
    ).fetchall()

    if not rows:
        await message.reply_text(
            "📭 **No AutoReplies saved.**"
        )
        return

    text = "🤖 ☠︎︎𝙰𝚁_乂 **𝘼𝙐𝙏𝙊𝙍𝙀𝙋𝙇𝙄𝙀𝙎**\n\n"

    for i, row in enumerate(rows, 1):
        text += f"`{i}.` `{row['keyword']}`\n"

    await message.reply_text(text)


# ============================================================
# AUTOREPLY ENGINE
# ============================================================

COMMAND_NAMES = [
    "help",
    "ping",
    "alive",
    "id",
    "info",
    "stats",
    "ban",
    "unban",
    "kick",
    "mute",
    "unmute",
    "warn",
    "unwarn",
    "del",
    "purge",
    "pin",
    "unpin",
    "welcome",
    "setwelcome",
    "getwelcome",
    "delwelcome",
    "setgif",
    "delgif",
    "autoreply",
    "setreply",
    "delreply",
    "replies",
]


@app.on_message(
    filters.group
    & filters.text
    & ~filters.command(COMMAND_NAMES)
)
async def autoreply_engine(_, message):

    text = message.text.lower().strip()

    if not text:
        return

    row = get_chat(message.chat.id)

    if not row["autoreply"]:
        return

    replies = db.execute(
        "SELECT keyword,response FROM replies "
        "WHERE chat_id=?",
        (message.chat.id,)
    ).fetchall()

    for item in replies:

        if item["keyword"] in text:

            try:
                await message.reply_text(
                    item["response"],
                    disable_web_page_preview=True
                )
            except Exception:
                pass

            break


# ============================================================
# STARTUP
# ============================================================

async def startup():

    me = await app.get_me()

    print("=" * 55)
    print("☠︎︎𝙰𝚁_乂 MANAGER")
    print("=" * 55)
    print(f"Name     : {me.first_name}")
    print(f"ID       : {me.id}")
    print(f"Username : @{me.username or 'None'}")
    print(f"Database : {DB_PATH}")
    print("Status   : ONLINE")
    print("=" * 55)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print("☠︎︎𝙰𝚁_乂 Starting...")

    app.start()

    try:
        app.loop.run_until_complete(
            startup()
        )

        app.loop.run_forever()

    except KeyboardInterrupt:
        pass

    finally:
        app.stop()
        db.close()
