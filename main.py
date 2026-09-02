import os
import sqlite3
import asyncio

from pyrogram import Client, filters, enums
from pyrogram.types import (
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ============================================================
# ☠︎︎𝙰𝚁_乂 𝙼𝙰𝙽𝙰𝙶𝙴𝚁
# SESSION STRING USERBOT
# Railway Ready
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

db = sqlite3.connect(DB_PATH, check_same_thread=False)
db.row_factory = sqlite3.Row

db.execute("""
CREATE TABLE IF NOT EXISTS settings (
    chat_id INTEGER PRIMARY KEY,
    autoreply INTEGER DEFAULT 1,
    welcome INTEGER DEFAULT 1,
    welcome_text TEXT DEFAULT NULL,
    welcome_gif TEXT DEFAULT NULL
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS replies (
    chat_id INTEGER,
    keyword TEXT,
    response TEXT,
    UNIQUE(chat_id, keyword)
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS warnings (
    chat_id INTEGER,
    user_id INTEGER,
    warns INTEGER DEFAULT 0,
    PRIMARY KEY(chat_id, user_id)
)
""")

db.commit()

# ============================================================
# CLIENT
# ============================================================

app = Client(
    "AR_MANAGER",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# ============================================================
# DEFAULT WELCOME
# ============================================================

DEFAULT_WELCOME = """☠︎︎𝙰𝚁_乂 𝙼𝙰𝙽𝙰𝙶𝙴𝚁

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

def ensure_settings(chat_id):
    db.execute(
        "INSERT OR IGNORE INTO settings(chat_id) VALUES(?)",
        (chat_id,)
    )
    db.commit()


def get_settings(chat_id):
    ensure_settings(chat_id)

    row = db.execute(
        "SELECT * FROM settings WHERE chat_id=?",
        (chat_id,)
    ).fetchone()

    return row


async def is_admin(chat_id, user_id):
    if OWNER_ID and user_id == OWNER_ID:
        return True

    try:
        member = await app.get_chat_member(chat_id, user_id)

        return member.status in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR
        )

    except Exception:
        return False


async def is_protected(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)

        return member.status in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR
        )

    except Exception:
        return False


async def get_target(message):
    if message.reply_to_message:
        return message.reply_to_message.from_user

    if len(message.command) > 1:
        try:
            return await app.get_users(message.command[1])
        except Exception:
            return None

    return None


def format_welcome(text, user, chat):
    name = user.first_name or "Friend"

    username = (
        f"@{user.username}"
        if user.username
        else name
    )

    return (
        text
        .replace("{name}", name)
        .replace("{username}", username)
        .replace("{id}", str(user.id))
        .replace("{chat}", chat.title or "Group")
    )


# ============================================================
# START
# ============================================================

@app.on_message(filters.command("start") & filters.private)
async def start_handler(_, message):

    me = await app.get_me()

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📚 𝙃𝙀𝙇𝙋",
                callback_data="ar_help"
            ),
            InlineKeyboardButton(
                "⚙️ 𝘾𝙈𝘿𝙎",
                callback_data="ar_commands"
            )
        ]
    ])

    await message.reply_text(
        "☠︎︎𝙰𝚁_乂 **𝙼𝙰𝙽𝙰𝙶𝙴𝚁**\n\n"
        "╭━━━━━━━━━━━━━━━━━━╮\n"
        "┃ 🤖 𝘼𝙪𝙩𝙤 𝙍𝙚𝙥𝙡𝙮\n"
        "┃ 🛡️ 𝙂𝙧𝙤𝙪𝙥 𝙈𝙖𝙣𝙖𝙜𝙚𝙧\n"
        "┃ 🔨 𝘽𝙖𝙣 • 𝙈𝙪𝙩𝙚\n"
        "┃ ⚠️ 𝙒𝙖𝙧𝙣 𝙎𝙮𝙨𝙩𝙚𝙢\n"
        "┃ 👋 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙂𝙄𝙁\n"
        "╰━━━━━━━━━━━━━━━━━━╯\n\n"
        f"👤 **Account:** @{me.username or 'NoUsername'}\n"
        "🟢 **𝙎𝙔𝙎𝙏𝙀𝙈 𝙊𝙉𝙇𝙄𝙉𝙀**",
        reply_markup=buttons
    )


# ============================================================
# CALLBACK HELP
# ============================================================

@app.on_callback_query(filters.regex("^ar_help$"))
async def help_callback(_, query):

    await query.answer()

    await query.message.edit_text(
        "☠︎︎𝙰𝚁_乂 **𝙼𝙰𝙽𝙰𝙶𝙴𝚁**\n\n"

        "🛡️ **𝙈𝙊𝘿𝙀𝙍𝘼𝙏𝙄𝙊𝙉**\n"
        "`/ban` • `/unban`\n"
        "`/mute` • `/unmute`\n"
        "`/warn` • `/unwarn`\n\n"

        "🧹 **𝙈𝙀𝙎𝙎𝘼𝙂𝙀**\n"
        "`/del` • `/pin` • `/unpin`\n\n"

        "👤 **𝙐𝙎𝙀𝙍**\n"
        "`/id` • `/info`\n\n"

        "🤖 **𝘼𝙐𝙏𝙊𝙍𝙀𝙋𝙇𝙔**\n"
        "`/autoreply on`\n"
        "`/autoreply off`\n"
        "`/setreply hello | Hello 👋`\n"
        "`/delreply hello`\n\n"

        "👋 **𝙒𝙀𝙇𝘾𝙊𝙈𝙀**\n"
        "`/setgif` — Reply to GIF\n"
        "`/delgif`\n"
        "`/setwelcome message`\n"
        "`/delwelcome`\n"
        "`/welcome on`\n"
        "`/welcome off`\n"
        "`/getwelcome`",

        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 𝘽𝘼𝘾𝙆",
                    callback_data="ar_back"
                )
            ]
        ])
    )


@app.on_callback_query(filters.regex("^ar_commands$"))
async def commands_callback(_, query):

    await query.answer()

    await query.message.edit_text(
        "☠︎︎𝙰𝚁_乂 **𝙌𝙐𝙄𝘾𝙆 𝘾𝙈𝘿𝙎**\n\n"

        "🔨 `/ban @user`\n"
        "🔇 `/mute @user`\n"
        "🔊 `/unmute @user`\n"
        "⚠️ `/warn @user`\n"
        "📢 `/unwarn @user`\n"
        "🧹 `/del` *(reply)*\n"
        "📌 `/pin` *(reply)*\n"
        "📌 `/unpin`\n"
        "🆔 `/id`\n"
        "ℹ️ `/info @user`\n\n"

        "👋 **WELCOME**\n"
        "Reply GIF → `/setgif`\n"
        "`/setwelcome Hey {name}!`\n"
        "`/welcome on`\n"
        "`/welcome off`",

        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 𝘽𝘼𝘾𝙆",
                    callback_data="ar_back"
                )
            ]
        ])
    )


@app.on_callback_query(filters.regex("^ar_back$"))
async def back_callback(_, query):

    await query.answer()

    await query.message.edit_text(
        "☠︎︎𝙰𝚁_乂 **𝙼𝙰𝙽𝙰𝙶𝙀𝚁**\n\n"
        "🟢 **𝙎𝙔𝙎𝙏𝙀𝙈 𝙊𝙉𝙇𝙄𝙉𝙀**",

        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📚 𝙃𝙀𝙇𝙋",
                    callback_data="ar_help"
                ),
                InlineKeyboardButton(
                    "⚙️ 𝘾𝙈𝘿𝙎",
                    callback_data="ar_commands"
                )
            ]
        ])
    )


# ============================================================
# ID
# ============================================================

@app.on_message(filters.command("id"))
async def id_handler(_, message):

    if message.reply_to_message:
        user = message.reply_to_message.from_user

        await message.reply_text(
            "☠︎︎𝙰𝚁_乂 **𝙄𝘿 𝙄𝙉𝙁𝙊**\n\n"
            f"👤 Name: {user.mention}\n"
            f"🆔 User ID: `{user.id}`\n"
            f"💬 Chat ID: `{message.chat.id}`"
        )
    else:
        await message.reply_text(
            f"☠︎︎𝙰𝚁_乂\n\n"
            f"💬 **Chat ID:** `{message.chat.id}`"
        )


# ============================================================
# INFO
# ============================================================

@app.on_message(filters.command("info"))
async def info_handler(_, message):

    user = await get_target(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or use `/info @username`"
        )
        return

    username = (
        f"@{user.username}"
        if user.username
        else "None"
    )

    await message.reply_text(
        "☠︎︎𝙰𝚁_乂 **𝙐𝙎𝙀𝙍 𝙄𝙉𝙁𝙊**\n\n"
        f"👤 Name: {user.first_name or 'Unknown'}\n"
        f"🆔 ID: `{user.id}`\n"
        f"🔗 Username: `{username}`\n"
        f"🤖 Bot: `{user.is_bot}`"
    )


# ============================================================
# BAN
# ============================================================

@app.on_message(filters.command("ban") & filters.group)
async def ban_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    user = await get_target(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or use `/ban @username`"
        )
        return

    if await is_protected(message.chat.id, user.id):
        await message.reply_text(
            "❌ **Admin ko ban nahi kar sakta.**"
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
async def unban_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    user = await get_target(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or use `/unban @username`"
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
# MUTE
# ============================================================

@app.on_message(filters.command("mute") & filters.group)
async def mute_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    user = await get_target(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or use `/mute @username`"
        )
        return

    if await is_protected(message.chat.id, user.id):
        await message.reply_text(
            "❌ **Admin ko mute nahi kar sakta.**"
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
            f"☠︎︎𝙰𝚁_乂 **𝙈𝙐𝙏𝙀𝘿**\n\n"
            f"👤 {user.mention}\n"
            f"🆔 `{user.id}`"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Mute failed:\n`{e}`"
        )


# ============================================================
# UNMUTE
# ============================================================

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    user = await get_target(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or use `/unmute @username`"
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
            f"☠︎︎𝙰𝚁_乂 **𝙐𝙉𝙈𝙐𝙏𝙀𝘿**\n\n"
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
async def warn_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    user = await get_target(message)

    if not user:
        await message.reply_text(
            "❌ Reply to a user or use `/warn @username`"
        )
        return

    if await is_protected(message.chat.id, user.id):
        await message.reply_text(
            "❌ **Admin ko warn nahi kar sakta.**"
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
            f"⚠️ ☠︎︎𝙰𝚁_乂 **𝙒𝘼𝙍𝙉𝙄𝙉𝙂**\n\n"
            f"👤 {user.mention}\n"
            f"📊 **Warning:** `{warns}/3`"
        )


# ============================================================
# UNWARN
# ============================================================

@app.on_message(filters.command("unwarn") & filters.group)
async def unwarn_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    user = await get_target(message)

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

    warns = max(0, row["warns"] - 1)

    if warns == 0:
        db.execute(
            "DELETE FROM warnings "
            "WHERE chat_id=? AND user_id=?",
            (message.chat.id, user.id)
        )
    else:
        db.execute(
            "UPDATE warnings SET warns=? "
            "WHERE chat_id=? AND user_id=?",
            (warns, message.chat.id, user.id)
        )

    db.commit()

    await message.reply_text(
        f"✅ ☠︎︎𝙰𝚁_乂 **𝙒𝘼𝙍𝙉 𝙍𝙀𝙈𝙊𝙑𝙀𝘿**\n\n"
        f"👤 {user.mention}\n"
        f"📊 `{warns}/3`"
    )


# ============================================================
# DELETE
# ============================================================

@app.on_message(filters.command("del") & filters.group)
async def delete_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ **Reply to a message.**"
        )
        return

    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception:
        pass


# ============================================================
# PIN
# ============================================================

@app.on_message(filters.command("pin") & filters.group)
async def pin_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ **Reply to the message you want to pin.**"
        )
        return

    try:
        await message.reply_to_message.pin()

        await message.reply_text(
            "📌 ☠︎︎𝙰𝚁_乂 **𝙈𝙀𝙎𝙎𝘼𝙂𝙀 𝙋𝙄𝙉𝙉𝙀𝘿**"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Pin failed:\n`{e}`"
        )


# ============================================================
# UNPIN
# ============================================================

@app.on_message(filters.command("unpin") & filters.group)
async def unpin_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    try:
        await app.unpin_chat_message(message.chat.id)

        await message.reply_text(
            "📌 ☠︎︎𝙰𝚁_乂 **𝙈𝙀𝙎𝙎𝘼𝙂𝙀 𝙐𝙉𝙋𝙄𝙉𝙉𝙀𝘿**"
        )

    except Exception as e:
        await message.reply_text(
            f"❌ Unpin failed:\n`{e}`"
        )


# ============================================================
# AUTOREPLY ON/OFF
# ============================================================

@app.on_message(filters.command("autoreply") & filters.group)
async def autoreply_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    ensure_settings(message.chat.id)

    if len(message.command) < 2:

        row = get_settings(message.chat.id)

        await message.reply_text(
            "🤖 ☠︎︎𝙰𝚁_乂 **𝘼𝙐𝙏𝙊𝙍𝙀𝙋𝙇𝙔**\n\n"
            f"Status: **{'ON 🟢' if row['autoreply'] else 'OFF 🔴'}**\n\n"
            "`/autoreply on`\n"
            "`/autoreply off`"
        )
        return

    value = message.command[1].lower()

    if value not in ("on", "off"):
        await message.reply_text(
            "❌ `/autoreply on` या `/autoreply off`"
        )
        return

    state = 1 if value == "on" else 0

    db.execute(
        "UPDATE settings SET autoreply=? WHERE chat_id=?",
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
async def setreply_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.text or "|" not in message.text:
        await message.reply_text(
            "❌ **Format:**\n\n"
            "`/setreply hello | Hello bro 👋`"
        )
        return

    data = message.text.split(None, 1)[1]

    keyword, response = data.split("|", 1)

    keyword = keyword.strip().lower()
    response = response.strip()

    if not keyword or not response:
        await message.reply_text(
            "❌ Keyword और reply required है."
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
        "☠︎︎𝙰𝚁_乂 **𝘼𝙐𝙏𝙊𝙍𝙀𝙋𝙇𝙔 𝙎𝘼𝙑𝙀𝘿**\n\n"
        f"🔑 Keyword: `{keyword}`\n"
        f"💬 Reply: {response}"
    )


# ============================================================
# DELETE REPLY
# ============================================================

@app.on_message(filters.command("delreply") & filters.group)
async def delreply_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if len(message.command) < 2:
        await message.reply_text(
            "❌ Example: `/delreply hello`"
        )
        return

    keyword = message.command[1].lower()

    db.execute(
        "DELETE FROM replies WHERE chat_id=? AND keyword=?",
        (message.chat.id, keyword)
    )

    db.commit()

    await message.reply_text(
        f"🗑️ **Reply Removed:** `{keyword}`"
    )


# ============================================================
# SET WELCOME GIF
# ============================================================

@app.on_message(filters.command("setgif") & filters.group)
async def setgif_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ **Kisi GIF/Animation ko reply karke `/setgif` likho.**"
        )
        return

    replied = message.reply_to_message

    file_id = None

    if replied.animation:
        file_id = replied.animation.file_id

    elif replied.document and replied.document.mime_type:
        if replied.document.mime_type.startswith("video/"):
            file_id = replied.document.file_id

    if not file_id:
        await message.reply_text(
            "❌ **Sirf GIF/Animation ko reply karke `/setgif` use karo.**"
        )
        return

    ensure_settings(message.chat.id)

    db.execute(
        "UPDATE settings SET welcome_gif=? WHERE chat_id=?",
        (file_id, message.chat.id)
    )
    db.commit()

    await message.reply_text(
        "✅ ☠︎︎𝙰𝚁_乂 **𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙂𝙄𝙁 𝙎𝘼𝙑𝙀𝘿!**\n\n"
        "👋 Ab naye member ke welcome par ye GIF use hogi."
    )


# ============================================================
# DELETE GIF
# ============================================================

@app.on_message(filters.command("delgif") & filters.group)
async def delgif_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    ensure_settings(message.chat.id)

    db.execute(
        "UPDATE settings SET welcome_gif=NULL WHERE chat_id=?",
        (message.chat.id,)
    )
    db.commit()

    await message.reply_text(
        "🗑️ ☠︎︎𝙰𝚁_乂 **𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙂𝙄𝙁 𝙍𝙀𝙈𝙊𝙑𝙀𝘿**"
    )


# ============================================================
# SET WELCOME TEXT
# ============================================================

@app.on_message(filters.command("setwelcome") & filters.group)
async def setwelcome_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if len(message.text.split(None, 1)) < 2:
        await message.reply_text(
            "❌ **Example:**\n\n"
            "`/setwelcome ☠︎︎𝙰𝚁_乂 Hey {name}! Welcome to {chat} 👋`"
        )
        return

    welcome_text = message.text.split(None, 1)[1].strip()

    if len(welcome_text) > 3000:
        await message.reply_text(
            "❌ Welcome message too long."
        )
        return

    ensure_settings(message.chat.id)

    db.execute(
        "UPDATE settings SET welcome_text=? WHERE chat_id=?",
        (welcome_text, message.chat.id)
    )
    db.commit()

    await message.reply_text(
        "✅ ☠︎︎𝙰𝚁_乂 **𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙈𝙀𝙎𝙎𝘼𝙂𝙀 𝙎𝘼𝙑𝙀𝘿!**\n\n"
        "Available placeholders:\n"
        "`{name}`\n"
        "`{username}`\n"
        "`{id}`\n"
        "`{chat}`"
    )


# ============================================================
# DELETE WELCOME TEXT
# ============================================================

@app.on_message(filters.command("delwelcome") & filters.group)
async def delwelcome_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    ensure_settings(message.chat.id)

    db.execute(
        "UPDATE settings SET welcome_text=NULL WHERE chat_id=?",
        (message.chat.id,)
    )
    db.commit()

    await message.reply_text(
        "🗑️ ☠︎︎𝙰𝚁_乂 **Custom Welcome Removed!**\n"
        "Default welcome message restored."
    )


# ============================================================
# WELCOME ON/OFF
# ============================================================

@app.on_message(filters.command("welcome") & filters.group)
async def welcome_toggle_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    ensure_settings(message.chat.id)

    if len(message.command) < 2:

        row = get_settings(message.chat.id)

        await message.reply_text(
            "👋 ☠︎︎𝙰𝚁_乂 **𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙎𝙔𝙎𝙏𝙀𝙈**\n\n"
            f"Status: **{'ON 🟢' if row['welcome'] else 'OFF 🔴'}**\n\n"
            "`/welcome on`\n"
            "`/welcome off`"
        )
        return

    value = message.command[1].lower()

    if value not in ("on", "off"):
        await message.reply_text(
            "❌ Use `/welcome on` or `/welcome off`"
        )
        return

    state = 1 if value == "on" else 0

    db.execute(
        "UPDATE settings SET welcome=? WHERE chat_id=?",
        (state, message.chat.id)
    )
    db.commit()

    await message.reply_text(
        f"👋 **Welcome {'ON 🟢' if state else 'OFF 🔴'}**"
    )


# ============================================================
# GET WELCOME
# ============================================================

@app.on_message(filters.command("getwelcome") & filters.group)
async def getwelcome_handler(_, message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    row = get_settings(message.chat.id)

    text = row["welcome_text"] or DEFAULT_WELCOME

    gif_status = (
        "🟢 SET"
        if row["welcome_gif"]
        else "🔴 NOT SET"
    )

    await message.reply_text(
        "☠︎︎𝙰𝚁_乂 **𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙎𝙀𝙏𝙏𝙄𝙉𝙂𝙎**\n\n"
        f"👋 Welcome: **{'ON 🟢' if row['welcome'] else 'OFF 🔴'}**\n"
        f"🎞️ GIF: **{gif_status}**\n\n"
        "📝 **Message:**\n"
        f"{text}"
    )


# ============================================================
# WELCOME NEW MEMBERS
# ============================================================

@app.on_message(filters.new_chat_members)
async def new_member_handler(_, message):

    row = get_settings(message.chat.id)

    if not row["welcome"]:
        return

    welcome_text = row["welcome_text"] or DEFAULT_WELCOME

    for user in message.new_chat_members:

        if user.is_self:
            continue

        text = format_welcome(
            welcome_text,
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

                await message.reply_text(
                    text
                )

        except Exception:

            try:
                await message.reply_text(text)
            except Exception:
                pass


# ============================================================
# AUTOREPLY ENGINE
# ============================================================

COMMANDS = [
    "start",
    "id",
    "info",
    "ban",
    "unban",
    "mute",
    "unmute",
    "warn",
    "unwarn",
    "del",
    "pin",
    "unpin",
    "autoreply",
    "setreply",
    "delreply",
    "setgif",
    "delgif",
    "setwelcome",
    "delwelcome",
    "welcome",
    "getwelcome"
]


@app.on_message(
    filters.group
    & filters.text
    & ~filters.command(COMMANDS)
)
async def autoreply_engine(_, message):

    if not message.text:
        return

    row = get_settings(message.chat.id)

    if not row["autoreply"]:
        return

    text = message.text.lower()

    replies = db.execute(
        "SELECT keyword,response FROM replies WHERE chat_id=?",
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
# PRIVATE AUTO REPLY
# ============================================================

PRIVATE_AUTOREPLY = (
    os.getenv("PRIVATE_AUTOREPLY", "false").lower()
    == "true"
)

PRIVATE_REPLY = os.getenv(
    "PRIVATE_REPLY",
    "☠︎︎𝙰𝚁_乂 👋 Hello! Abhi unavailable hoon."
)

private_cooldown = set()


@app.on_message(
    filters.private
    & filters.text
    & ~filters.command(["start"])
)
async def private_reply(_, message):

    if not PRIVATE_AUTOREPLY:
        return

    if not message.from_user:
        return

    if message.from_user.is_self:
        return

    user_id = message.from_user.id

    if user_id in private_cooldown:
        return

    private_cooldown.add(user_id)

    try:
        await message.reply_text(
            PRIVATE_REPLY
        )
    except Exception:
        pass

    async def cooldown():

        await asyncio.sleep(60)

        private_cooldown.discard(user_id)

    asyncio.create_task(cooldown())


# ============================================================
# STARTUP
# ============================================================

async def startup():

    me = await app.get_me()

    print("=" * 55)
    print("☠︎︎𝙰𝚁_乂 𝙼𝙰𝙽𝙰𝙶𝙴𝚁")
    print("=" * 55)
    print(f"👤 Name     : {me.first_name}")
    print(f"🆔 ID       : {me.id}")
    print(f"🔗 Username : @{me.username or 'None'}")
    print(f"💾 Database : {DB_PATH}")
    print("🟢 Status   : ONLINE")
    print("=" * 55)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print("☠︎︎𝙰𝚁_乂 Starting...")

    app.start()

    try:
        app.loop.run_until_complete(startup())
        app.loop.run_forever()

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        app.stop()
        db.close()
