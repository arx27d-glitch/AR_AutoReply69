import os
import sqlite3
import asyncio

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions
)
from pyrogram.errors import RPCError


# ============================================================
# ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂
# ADVANCED TELEGRAM MANAGER
# ============================================================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION_STRING:
    raise RuntimeError(
        "❌ API_ID, API_HASH aur SESSION_STRING Railway Variables me add karo."
    )


app = Client(
    "AR_UNKNOWN_MANAGER",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


# ============================================================
# DATABASE
# ============================================================

db = sqlite3.connect(
    "ar_manager.db",
    check_same_thread=False
)

db.execute("""
CREATE TABLE IF NOT EXISTS settings(
    id INTEGER PRIMARY KEY CHECK(id=1),
    welcome_gif TEXT DEFAULT '',
    auto_reply INTEGER DEFAULT 1
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS groups(
    chat_id INTEGER PRIMARY KEY,
    welcome INTEGER DEFAULT 1,
    goodbye INTEGER DEFAULT 1,
    gif INTEGER DEFAULT 1,
    welcome_text TEXT
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS stats(
    chat_id INTEGER PRIMARY KEY,
    welcomes INTEGER DEFAULT 0,
    goodbyes INTEGER DEFAULT 0,
    bans INTEGER DEFAULT 0,
    kicks INTEGER DEFAULT 0,
    mutes INTEGER DEFAULT 0,
    deletes INTEGER DEFAULT 0
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS warnings(
    chat_id INTEGER,
    user_id INTEGER,
    warns INTEGER DEFAULT 0,
    PRIMARY KEY(chat_id,user_id)
)
""")

db.execute("""
INSERT OR IGNORE INTO settings
(id,welcome_gif,auto_reply)
VALUES(1,'',1)
""")

db.commit()


# ============================================================
# DEFAULT WELCOME
# ============================================================

DEFAULT_WELCOME = """╭━━━〔 ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂 〕━━━╮
│
│ 🖤 𝙷𝙴𝙻𝙻𝙾 {user} ✨
│
│ 👤 𝙽𝙰𝙼𝙴 ➜ {name}
│ 🆔 𝙸𝙳 ➜ {id}
│ 🔗 𝚄𝚂𝙴𝚁 ➜ {username}
│ 🏠 𝙶𝚁𝙾𝚄𝙿 ➜ {group}
│
│ 💜 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝚃𝙾 𝚃𝙷𝙴 𝙵𝙰𝙼𝙸𝙻𝚈
│
│ ⚡ 𝙴𝙽𝙹𝙾𝚈 𝚈𝙾𝚄𝚁 𝚂𝚃𝙰𝚈
│
│ ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂
│
╰━━━━━━━━━━━━━━━━━━━━╯"""


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def ensure_group(chat_id):

    row = db.execute(
        "SELECT chat_id FROM groups WHERE chat_id=?",
        (chat_id,)
    ).fetchone()

    if not row:

        db.execute(
            """
            INSERT INTO groups
            (chat_id,welcome,goodbye,gif,welcome_text)
            VALUES(?,?,?,?,?)
            """,
            (
                chat_id,
                1,
                1,
                1,
                DEFAULT_WELCOME
            )
        )

        db.execute(
            """
            INSERT OR IGNORE INTO stats
            (chat_id,welcomes,goodbyes,bans,kicks,mutes,deletes)
            VALUES(?,?,?,?,?,?,?)
            """,
            (chat_id,0,0,0,0,0,0)
        )

        db.commit()


def get_group(chat_id):

    ensure_group(chat_id)

    return db.execute(
        """
        SELECT welcome,goodbye,gif,welcome_text
        FROM groups
        WHERE chat_id=?
        """,
        (chat_id,)
    ).fetchone()


def get_gif():

    row = db.execute(
        "SELECT welcome_gif FROM settings WHERE id=1"
    ).fetchone()

    return row[0] if row else ""


def save_gif(file_id):

    db.execute(
        """
        UPDATE settings
        SET welcome_gif=?
        WHERE id=1
        """,
        (file_id,)
    )

    db.commit()


def remove_gif():

    db.execute(
        """
        UPDATE settings
        SET welcome_gif=''
        WHERE id=1
        """
    )

    db.commit()


def update_group(chat_id, column, value):

    allowed = {
        "welcome",
        "goodbye",
        "gif"
    }

    if column not in allowed:
        return

    ensure_group(chat_id)

    db.execute(
        f"""
        UPDATE groups
        SET {column}=?
        WHERE chat_id=?
        """,
        (value,chat_id)
    )

    db.commit()


def add_stat(chat_id, column):

    allowed = {
        "welcomes",
        "goodbyes",
        "bans",
        "kicks",
        "mutes",
        "deletes"
    }

    if column not in allowed:
        return

    ensure_group(chat_id)

    db.execute(
        f"""
        UPDATE stats
        SET {column}={column}+1
        WHERE chat_id=?
        """,
        (chat_id,)
    )

    db.commit()


# ============================================================
# USER FORMAT
# ============================================================

def get_name(user):

    return user.first_name or "𝙵𝚛𝚒𝚎𝚗𝚍"


def get_username(user):

    if user.username:
        return "@" + user.username

    return "𝙽𝚘 𝚄𝚜𝚎𝚛𝚗𝚊𝚖𝚎"


def format_welcome(text,user,chat):

    name = get_name(user)
    username = get_username(user)

    return (
        text
        .replace("{user}",name)
        .replace("{name}",name)
        .replace("{id}",str(user.id))
        .replace("{username}",username)
        .replace(
            "{group}",
            chat.title or "𝙶𝚛𝚘𝚞𝚙"
        )
    )


# ============================================================
# WELCOME BUTTONS
# ============================================================

def welcome_buttons(user_id):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "☠︎︎ 𝙿𝚁𝙾𝙵𝙸𝙻𝙴",
                user_id=user_id
            )
        ],
        [
            InlineKeyboardButton(
                "📜 𝚁𝚄𝙻𝙴𝚂",
                callback_data="ar_rules"
            ),
            InlineKeyboardButton(
                "⚡ 𝙰𝙱𝙾𝚄𝚃",
                callback_data="ar_about"
            )
        ]
    ])


# ============================================================
# SET GIF
# ============================================================

@app.on_message(
    filters.me &
    filters.command(
        "setgif",
        prefixes="/"
    )
)
async def set_gif(client,message):

    try:

        if not message.reply_to_message:

            await message.reply_text(
                """❌ 𝚁𝙴𝙿𝙻𝚈 𝚃𝙾 𝙰 𝙶𝙸𝙵

Example:

1️⃣ Telegram me KGF/Rocky-style GIF bhejo
2️⃣ Us GIF ko reply karo
3️⃣ `/setgif` bhejo"""
            )

            return

        replied = message.reply_to_message

        file_id = None

        # Telegram animation
        if replied.animation:

            file_id = replied.animation.file_id

        # Telegram video
        elif replied.video:

            file_id = replied.video.file_id

        # Telegram document
        elif replied.document:

            mime = replied.document.mime_type or ""

            if (
                mime.startswith("video/")
                or mime == "image/gif"
            ):
                file_id = replied.document.file_id

        if not file_id:

            await message.reply_text(
                "❌ Reply kiya hua message GIF/Animation nahi hai."
            )

            return

        save_gif(file_id)

        await message.reply_text(
            """╭━━〔 🎬 𝙶𝙸𝙵 𝚂𝙰𝚅𝙴𝙳 〕━━╮
│
│ 🟢 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝙶𝙸𝙵 𝚂𝙴𝚃
│
│ ⚡ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂
│
╰━━━━━━━━━━━━━━╯"""
        )

    except Exception as e:

        await message.reply_text(
            f"❌ SETGIF ERROR\n`{e}`"
        )


# ============================================================
# REMOVE GIF
# ============================================================

@app.on_message(
    filters.me &
    filters.command(
        "removegif",
        prefixes="/"
    )
)
async def remove_gif_command(client,message):

    remove_gif()

    await message.reply_text(
        """🎬 🔴 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝙶𝙸𝙵 𝚁𝙴𝙼𝙾𝚅𝙴𝙳"""
    )


# ============================================================
# WELCOME
# ============================================================

@app.on_message(
    filters.group &
    filters.new_chat_members
)
async def welcome(client,message):

    try:

        settings = get_group(
            message.chat.id
        )

        if not settings[0]:
            return

        gif_enabled = settings[2]

        for user in message.new_chat_members:

            text = format_welcome(
                settings[3],
                user,
                message.chat
            )

            buttons = welcome_buttons(
                user.id
            )

            gif_id = get_gif()

            # ------------------------------------------------
            # GIF WELCOME
            # ------------------------------------------------

            if gif_enabled and gif_id:

                try:

                    await client.send_animation(
                        chat_id=message.chat.id,
                        animation=gif_id,
                        caption=text,
                        reply_markup=buttons
                    )

                except Exception as e:

                    print(
                        "GIF SEND ERROR:",
                        e
                    )

                    await message.reply_text(
                        text,
                        reply_markup=buttons
                    )

            else:

                await message.reply_text(
                    text,
                    reply_markup=buttons
                )

            add_stat(
                message.chat.id,
                "welcomes"
            )

            await asyncio.sleep(1)

    except Exception as e:

        print(
            "WELCOME ERROR:",
            e
        )


# ============================================================
# GOODBYE
# ============================================================

@app.on_message(
    filters.group &
    filters.left_chat_member
)
async def goodbye(client,message):

    try:

        settings = get_group(
            message.chat.id
        )

        if not settings[1]:
            return

        user = message.left_chat_member

        if not user:
            return

        name = get_name(user)

        await message.reply_text(
            f"""╭━━〔 👋 𝙶𝙾𝙾𝙳𝙱𝚈𝙴 〕━━╮
│
│ 👤 {name}
│
│ 😢 𝙼𝚎𝚖𝚋𝚎𝚛 𝚑𝚊𝚜 𝚕𝚎𝚏𝚝.
│
│ 💜 𝚆𝚎 𝚠𝚒𝚜𝚑 𝚢𝚘𝚞 𝚠𝚎𝚕𝚕!
│
│ ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂
│
╰━━━━━━━━━━━━━━━━╯"""
        )

        add_stat(
            message.chat.id,
            "goodbyes"
        )

    except Exception as e:

        print(
            "GOODBYE ERROR:",
            e
        )


# ============================================================
# GIF ON / OFF
# ============================================================

@app.on_message(
    filters.me &
    filters.command(
        [
            "gifon",
            "gifoff"
        ],
        prefixes="/"
    )
)
async def gif_toggle(client,message):

    cmd = message.command[0].lower()

    value = 1 if cmd == "gifon" else 0

    update_group(
        message.chat.id,
        "gif",
        value
    )

    await message.reply_text(
        "🎬 🟢 𝙶𝙸𝙵 𝙾𝙽"
        if value
        else
        "🎬 🔴 𝙶𝙸𝙵 𝙾𝙵𝙵"
    )


# ============================================================
# WELCOME ON / OFF
# ============================================================

@app.on_message(
    filters.me &
    filters.command(
        [
            "welcomeon",
            "welcomeoff"
        ],
        prefixes="/"
    )
)
async def welcome_toggle(client,message):

    cmd = message.command[0].lower()

    value = 1 if cmd == "welcomeon" else 0

    update_group(
        message.chat.id,
        "welcome",
        value
    )

    await message.reply_text(
        "🟢 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝙾𝙽"
        if value
        else
        "🔴 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝙾𝙵𝙵"
    )


# ============================================================
# GOODBYE ON / OFF
# ============================================================

@app.on_message(
    filters.me &
    filters.command(
        [
            "goodbyeon",
            "goodbyeoff"
        ],
        prefixes="/"
    )
)
async def goodbye_toggle(client,message):

    cmd = message.command[0].lower()

    value = 1 if cmd == "goodbyeon" else 0

    update_group(
        message.chat.id,
        "goodbye",
        value
    )

    await message.reply_text(
        "🟢 👋 𝙶𝙾𝙾𝙳𝙱𝚈𝙴 𝙾𝙽"
        if value
        else
        "🔴 👋 𝙶𝙾𝙾𝙳𝙱𝚈𝙴 𝙾𝙵𝙵"
    )


# ============================================================
# DM AUTO REPLY
# ============================================================

@app.on_message(
    filters.private &
    ~filters.me &
    ~filters.bot
)
async def auto_reply(client,message):

    try:

        user = message.from_user

        if not user:
            return

        exists = db.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id=?
            """,
            (user.id,)
        ).fetchone()

        if exists:
            return

        name = get_name(user)
        username = get_username(user)

        db.execute(
            """
            INSERT OR IGNORE INTO users
            (user_id,name,username)
            VALUES(?,?,?)
            """,
            (
                user.id,
                name,
                username
            )
        )

        db.commit()

        await message.reply_text(
            f"""╭━━〔 ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂 〕━━╮
│
│ 👋 𝙷𝚎𝚢 {name}!
│
│ 💜 𝙼𝚎𝚜𝚜𝚊𝚐𝚎 𝚛𝚎𝚌𝚎𝚒𝚟𝚎𝚍.
│
│ ⚡ 𝙸'𝚕𝚕 𝚛𝚎𝚙𝚕𝚢 𝚠𝚑𝚎𝚗 𝙸 𝚌𝚊𝚗.
│
╰━━━━━━━━━━━━━━━━━━━━╯"""
        )

    except Exception as e:

        print(
            "AUTO REPLY ERROR:",
            e
        )


# ============================================================
# TARGET USER
# ============================================================

async def get_target(message):

    if message.reply_to_message:

        user = (
            message.reply_to_message
            .from_user
        )

        if user:

            return (
                user.id,
                get_name(user)
            )

    if len(message.command) >= 2:

        try:

            user_id = int(
                message.command[1]
            )

            try:

                user = await client.get_users(
                    user_id
                )

                return (
                    user.id,
                    get_name(user)
                )

            except Exception:

                return (
                    user_id,
                    str(user_id)
                )

        except ValueError:

            return None,None

    return None,None


# ============================================================
# MODERATION
# ============================================================

@app.on_message(
    filters.me &
    filters.command(
        [
            "ban",
            "unban",
            "kick",
            "mute",
            "unmute",
            "pin",
            "unpin",
            "del"
        ],
        prefixes="/"
    )
)
async def moderation(client,message):

    cmd = message.command[0].lower()

    try:

        # ====================================================
        # USER MODERATION
        # ====================================================

        if cmd in (
            "ban",
            "kick",
            "mute",
            "unmute"
        ):

            user_id,name = await get_target(
                message
            )

            if not user_id:

                await message.reply_text(
                    "❌ Reply to a user message."
                )

                return

            # ------------------------------------------------
            # BAN
            # ------------------------------------------------

            if cmd == "ban":

                await client.ban_chat_member(
                    message.chat.id,
                    user_id
                )

                add_stat(
                    message.chat.id,
                    "bans"
                )

                await message.reply_text(
                    f"""🔨 ☠︎︎ 𝙱𝙰𝙽𝙽𝙴𝙳

👤 ➜ {name}
🆔 ➜ `{user_id}`"""
                )

            # ------------------------------------------------
            # KICK
            # ------------------------------------------------

            elif cmd == "kick":

                await client.ban_chat_member(
                    message.chat.id,
                    user_id
                )

                await client.unban_chat_member(
                    message.chat.id,
                    user_id
                )

                add_stat(
                    message.chat.id,
                    "kicks"
                )

                await message.reply_text(
                    f"""👢 𝙺𝙸𝙲𝙺𝙴𝙳

👤 ➜ {name}
🆔 ➜ `{user_id}`"""
                )

            # ------------------------------------------------
            # MUTE
            # ------------------------------------------------

            elif cmd == "mute":

                permissions = ChatPermissions(
                    can_send_messages=False
                )

                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id,
                    permissions=permissions
                )

                add_stat(
                    message.chat.id,
                    "mutes"
                )

                await message.reply_text(
                    f"""🔇 𝙼𝚄𝚃𝙴𝙳

👤 ➜ {name}
🆔 ➜ `{user_id}`"""
                )

            # ------------------------------------------------
            # UNMUTE
            # ------------------------------------------------

            elif cmd == "unmute":

                permissions = ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_invite_users=True
                )

                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id,
                    permissions=permissions
                )

                await message.reply_text(
                    f"""🔊 𝚄𝙽𝙼𝚄𝚃𝙴𝙳

👤 ➜ {name}
🆔 ➜ `{user_id}`"""
                )

        # ====================================================
        # UNBAN
        # ====================================================

        elif cmd == "unban":

            user_id,name = await get_target(
                message
            )

            if not user_id:

                await message.reply_text(
                    "❌ Use `/unban USER_ID`"
                )

                return

            await client.unban_chat_member(
                message.chat.id,
                user_id
            )

            await message.reply_text(
                f"""✅ 𝚄𝙽𝙱𝙰𝙽𝙽𝙴𝙳

👤 ➜ {name}
🆔 ➜ `{user_id}`"""
            )

        # ====================================================
        # PIN
        # ====================================================

        elif cmd == "pin":

            if not message.reply_to_message:

                await message.reply_text(
                    "❌ Reply to a message."
                )

                return

            await client.pin_chat_message(
                message.chat.id,
                message.reply_to_message.id,
                disable_notification=True
            )

            await message.reply_text(
                "📌 𝙿𝙸𝙽𝙽𝙴𝙳"
            )

        # ====================================================
        # UNPIN
        # ====================================================

        elif cmd == "unpin":

            await client.unpin_chat_message(
                message.chat.id
            )

            await message.reply_text(
                "📌 𝚄𝙽𝙿𝙸𝙽𝙽𝙴𝙳"
            )

        # ====================================================
        # DELETE
        # ====================================================

        elif cmd == "del":

            if not message.reply_to_message:

                await message.reply_text(
                    "❌ Reply to a message."
                )

                return

            await message.reply_to_message.delete()

            await message.delete()

            add_stat(
                message.chat.id,
                "deletes"
            )

    except RPCError as e:

        await message.reply_text(
            f"""❌ 𝙼𝙾𝙳 𝙴𝚁𝚁𝙾𝚁

`{e}`

☠︎︎ Check:
• Account group admin hai?
• Ban Users permission hai?
• Delete Messages permission hai?
• Pin Messages permission hai?"""
        )

    except Exception as e:

        await message.reply_text(
            f"❌ 𝙴𝚁𝚁𝙾𝚁\n`{e}`"
        )


# ============================================================
# STATS
# ============================================================

@app.on_message(
    filters.me &
    filters.command(
        "stats",
        prefixes="/"
    )
)
async def stats(client,message):

    ensure_group(
        message.chat.id
    )

    row = db.execute(
        """
        SELECT
        welcomes,
        goodbyes,
        bans,
        kicks,
        mutes,
        deletes
        FROM stats
        WHERE chat_id=?
        """,
        (message.chat.id,)
    ).fetchone()

    await message.reply_text(
        f"""╭━━〔 📊 𝚂𝚃𝙰𝚃𝚂 〕━━╮
│
│ 👋 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 ➜ {row[0]}
│ 🚪 𝙶𝙾𝙾𝙳𝙱𝚈𝙴 ➜ {row[1]}
│ 🔨 𝙱𝙰𝙽 ➜ {row[2]}
│ 👢 𝙺𝙸𝙲𝙺 ➜ {row[3]}
│ 🔇 𝙼𝚄𝚃𝙴 ➜ {row[4]}
│ 🗑️ 𝙳𝙴𝙻𝙴𝚃𝙴 ➜ {row[5]}
│
╰━━━━━━━━━━━━━━━━╯"""
    )


# ============================================================
# HELP
# ============================================================

@app.on_message(
    filters.me &
    filters.command(
        "help",
        prefixes="/"
    )
)
async def help_command(client,message):

    await message.reply_text(
        """╭━━━〔 ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂 〕━━━╮
│
│ ⚡ 𝙱𝙰𝚂𝙸𝙲
│ ├ /ping
│ ├ /id
│ ├ /status
│ └ /stats
│
│ 👋 𝚆𝙴𝙻𝙲𝙾𝙼𝙴
│ ├ /welcomeon
│ ├ /welcomeoff
│ ├ /setgif
│ ├ /removegif
│ ├ /gifon
│ └ /gifoff
│
│ 🚪 𝙶𝙾𝙾𝙳𝙱𝚈𝙴
│ ├ /goodbyeon
│ └ /goodbyeoff
│
│ 🛡️ 𝙼𝙾𝙳𝙴𝚁𝙰𝚃𝙸𝙾𝙽
│ ├ /ban
│ ├ /unban ID
│ ├ /kick
│ ├ /mute
│ ├ /unmute
│ ├ /pin
│ ├ /unpin
│ └ /del
│
│ ⚠️ 𝚆𝙰𝚁𝙽𝙸𝙽𝙶
│ ├ /warn
│ └ /unwarn
│
│ 🎮 𝙶𝙰𝙼𝙴
│ └ /xo
│
╰━━━━━━━━━━━━━━━━━━━━╯"""
    )


# ============================================================
# RULES BUTTON
# ============================================================

@app.on_callback_query(
    filters.regex("^ar_rules$")
)
async def rules(client,query):

    await query.answer(
        "📜 𝚁𝚄𝙻𝙴𝚂\n\n"
        "1️⃣ Respect everyone.\n"
        "2️⃣ No spam.\n"
        "3️⃣ No flooding.\n"
        "4️⃣ Follow admin instructions.\n"
        "5️⃣ Enjoy the group! 💜",
        show_alert=True
    )


# ============================================================
# ABOUT BUTTON
# ============================================================

@app.on_callback_query(
    filters.regex("^ar_about$")
)
async def about(client,query):

    await query.answer(
        "☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂\n\n"
        "⚡ Advanced Manager\n"
        "👋 Welcome + GIF\n"
        "🚪 Goodbye\n"
        "🛡️ Moderation\n"
        "📊 Statistics",
        show_alert=True
    )


# ============================================================
# START
# ============================================================

print("""
╔══════════════════════════════════════════════╗
║                                              ║
║       ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂                         ║
║       ADVANCED TELEGRAM MANAGER              ║
║                                              ║
║       🟢 SYSTEM STARTING                     ║
║       🎬 GIF SYSTEM                          ║
║       👋 WELCOME                             ║
║       🚪 GOODBYE                             ║
║       🛡️ MODERATION                          ║
║       📊 STATS                               ║
║                                              ║
╚══════════════════════════════════════════════╝
""")

app.run()
