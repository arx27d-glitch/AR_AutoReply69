import os
import sqlite3
import time
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions,
    ChatPrivileges,
)

# =========================================================
# CONFIG
# =========================================================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION_STRING:
    raise RuntimeError(
        "Railway Variables me API_ID, API_HASH aur SESSION_STRING set karo."
    )

app = Client(
    "AR_ADVANCED_MANAGER",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

# =========================================================
# DATABASE
# =========================================================

DB = "ar_manager.db"

db = sqlite3.connect(DB, check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS first_users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    first_seen TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS notes (
    name TEXT PRIMARY KEY,
    content TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS filters (
    word TEXT PRIMARY KEY,
    reply TEXT
)
""")

db.commit()


def get_setting(key, default=None):
    cur.execute(
        "SELECT value FROM settings WHERE key=?",
        (key,)
    )
    row = cur.fetchone()
    return row[0] if row else default


def set_setting(key, value):
    cur.execute(
        "INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
        (key, str(value))
    )
    db.commit()


# =========================================================
# DEFAULT SETTINGS
# =========================================================

if get_setting("auto_reply") is None:
    set_setting("auto_reply", "1")

if get_setting("welcome") is None:
    set_setting(
        "welcome",
        "👋 Welcome {name}!\n\n🤖 Welcome to the group."
    )

if get_setting("first_reply") is None:
    set_setting(
        "first_reply",
        "╭━━〔 👋 𝐇𝐄𝐋𝐋𝐎 〕━━╮\n"
        "│\n"
        "│ 𝐇𝐞𝐥𝐥𝐨 {name}! 👋\n"
        "│\n"
        "│ 📩 Tumhara message mil gaya.\n"
        "│ Main abhi available nahi hoon.\n"
        "│\n"
        "╰━━━━━━━━━━━━━━╯"
    )


# =========================================================
# AUTO REPLY — ONLY FIRST DM
# =========================================================

@app.on_message(
    filters.private
    & ~filters.me
    & ~filters.bot
)
async def first_message_reply(client, message):

    if get_setting("auto_reply", "1") != "1":
        return

    user = message.from_user

    if not user:
        return

    uid = user.id

    cur.execute(
        "SELECT user_id FROM first_users WHERE user_id=?",
        (uid,)
    )

    exists = cur.fetchone()

    if exists:
        return

    name = user.first_name or "Friend"
    username = user.username or ""

    cur.execute(
        """
        INSERT OR IGNORE INTO first_users
        (user_id,name,username,first_seen)
        VALUES (?,?,?,?)
        """,
        (
            uid,
            name,
            username,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
    )

    db.commit()

    reply = get_setting("first_reply")

    reply = reply.replace("{name}", name)
    reply = reply.replace(
        "{username}",
        f"@{username}" if username else name
    )

    try:
        await message.reply_text(reply)
    except Exception as e:
        print("AUTO REPLY ERROR:", e)


# =========================================================
# /ON
# =========================================================

@app.on_message(
    filters.me & filters.command("on", prefixes="/")
)
async def auto_on(client, message):

    set_setting("auto_reply", "1")

    await message.edit_text(
        "╭━━〔 🟢 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘 〕━━╮\n"
        "│\n"
        "│ ✅ Status: ON\n"
        "│ 👤 Sirf FIRST DM par reply\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# /OFF
# =========================================================

@app.on_message(
    filters.me & filters.command("off", prefixes="/")
)
async def auto_off(client, message):

    set_setting("auto_reply", "0")

    await message.edit_text(
        "╭━━〔 🔴 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘 〕━━╮\n"
        "│\n"
        "│ ❌ Status: OFF\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# /WELCOME
# =========================================================

@app.on_message(
    filters.me & filters.command("welcome", prefixes="/")
)
async def welcome_command(client, message):

    parts = (message.text or "").split(maxsplit=1)

    if len(parts) == 1:
        current = get_setting("welcome")
        await message.edit_text(
            "📢 **Current Welcome:**\n\n"
            f"{current}\n\n"
            "Change:\n"
            "`/welcome Welcome {name} 👋`"
        )
        return

    set_setting("welcome", parts[1])

    await message.edit_text(
        "✅ **Welcome message updated!**"
    )


# =========================================================
# NEW MEMBER WELCOME
# =========================================================

@app.on_message(
    filters.group & filters.new_chat_members
)
async def new_member(client, message):

    template = get_setting("welcome")

    for user in message.new_chat_members:

        name = user.first_name or "Friend"

        text = template.replace(
            "{name}",
            name
        )

        text = text.replace(
            "{username}",
            f"@{user.username}"
            if user.username
            else name
        )

        try:
            await message.reply_text(text)
        except Exception as e:
            print("WELCOME ERROR:", e)


# =========================================================
# /SETREPLY
# =========================================================

@app.on_message(
    filters.me & filters.command("setreply", prefixes="/")
)
async def set_reply(client, message):

    parts = (message.text or "").split(maxsplit=1)

    if len(parts) < 2:
        await message.edit_text(
            "❌ Example:\n"
            "`/setreply Hello {name} 👋`"
        )
        return

    set_setting("first_reply", parts[1])

    await message.edit_text(
        "✅ **First DM auto-reply updated!**"
    )


# =========================================================
# /RESETUSER
# =========================================================

@app.on_message(
    filters.me & filters.command("resetuser", prefixes="/")
)
async def reset_user(client, message):

    parts = (message.text or "").split()

    if len(parts) < 2:

        if message.reply_to_message:
            user = message.reply_to_message.from_user

            if user:
                uid = user.id
            else:
                await message.edit_text("❌ User not found.")
                return
        else:
            await message.edit_text(
                "❌ Reply to user or use:\n"
                "`/resetuser USER_ID`"
            )
            return
    else:
        try:
            uid = int(parts[1])
        except ValueError:
            await message.edit_text("❌ Invalid User ID.")
            return

    cur.execute(
        "DELETE FROM first_users WHERE user_id=?",
        (uid,)
    )

    db.commit()

    await message.edit_text(
        f"✅ First-message status reset for `{uid}`"
    )


# =========================================================
# /LISTUSERS
# =========================================================

@app.on_message(
    filters.me & filters.command("listusers", prefixes="/")
)
async def list_users(client, message):

    cur.execute(
        """
        SELECT user_id,name,username,first_seen
        FROM first_users
        ORDER BY first_seen DESC
        LIMIT 30
        """
    )

    rows = cur.fetchall()

    if not rows:
        await message.edit_text(
            "📭 **No first-contact users yet.**"
        )
        return

    text = "╭━━〔 👥 𝐅𝐈𝐑𝐒𝐓 𝐂𝐎𝐍𝐓𝐀𝐂𝐓𝐒 〕━━╮\n│\n"

    for uid, name, username, date in rows:

        text += (
            f"│ 👤 {name}\n"
            f"│ 🆔 `{uid}`\n"
            f"│ 🕒 {date}\n"
            "│\n"
        )

    text += "╰━━━━━━━━━━━━━━━━━━━━╯"

    await message.edit_text(text)


# =========================================================
# /CLEARUSERS
# =========================================================

@app.on_message(
    filters.me & filters.command("clearusers", prefixes="/")
)
async def clear_users(client, message):

    cur.execute("DELETE FROM first_users")
    db.commit()

    await message.edit_text(
        "🗑️ **First-contact database cleared.**"
    )


# =========================================================
# AFK
# =========================================================

AFK = False
AFK_REASON = ""
AFK_TIME = 0
afk_notified = set()


@app.on_message(
    filters.me & filters.command("afk", prefixes="/")
)
async def afk_on(client, message):

    global AFK, AFK_REASON, AFK_TIME

    parts = (message.text or "").split(maxsplit=1)

    AFK = True
    AFK_TIME = time.time()

    AFK_REASON = (
        parts[1]
        if len(parts) > 1
        else "Busy right now."
    )

    afk_notified.clear()

    await message.edit_text(
        "💤 **𝐀𝐅𝐊 𝐌𝐎𝐃𝐄 𝐎𝐍**\n\n"
        f"📝 {AFK_REASON}"
    )


@app.on_message(
    ~filters.me
    & ~filters.bot
)
async def afk_reply(client, message):

    global AFK

    if not AFK:
        return

    if not message.from_user:
        return

    uid = message.from_user.id

    if uid in afk_notified:
        return

    afk_notified.add(uid)

    minutes = int(
        (time.time() - AFK_TIME) / 60
    )

    try:
        await message.reply_text(
            "💤 **𝐀𝐅𝐊**\n\n"
            f"👤 {message.from_user.first_name}\n"
            f"📝 {AFK_REASON}\n"
            f"⏱️ AFK: {minutes} min"
        )
    except Exception:
        pass


@app.on_message(
    filters.me
)
async def afk_off_detector(client, message):

    global AFK

    if not AFK:
        return

    if not (message.text or "").startswith("/afk"):

        AFK = False
        afk_notified.clear()

        try:
            await message.reply_text(
                "🟢 **Welcome back! AFK mode OFF.**"
            )
        except Exception:
            pass


# =========================================================
# NOTES
# =========================================================

@app.on_message(
    filters.me & filters.command("note", prefixes="/")
)
async def note_command(client, message):

    parts = (message.text or "").split(maxsplit=2)

    if len(parts) < 3:
        await message.edit_text(
            "❌ Example:\n"
            "`/note study Physics chapter 1`"
        )
        return

    name = parts[1].lower()
    content = parts[2]

    cur.execute(
        "INSERT OR REPLACE INTO notes(name,content)"
        " VALUES(?,?)",
        (name, content)
    )

    db.commit()

    await message.edit_text(
        f"📝 Note `{name}` saved!"
    )


@app.on_message(
    filters.me & filters.command("getnote", prefixes="/")
)
async def get_note(client, message):

    parts = (message.text or "").split()

    if len(parts) < 2:
        await message.edit_text(
            "❌ `/getnote NAME`"
        )
        return

    name = parts[1].lower()

    cur.execute(
        "SELECT content FROM notes WHERE name=?",
        (name,)
    )

    row = cur.fetchone()

    if not row:
        await message.edit_text(
            "❌ Note not found."
        )
        return

    await message.edit_text(
        f"📝 **{name}**\n\n{row[0]}"
    )


@app.on_message(
    filters.me & filters.command("delnote", prefixes="/")
)
async def delete_note(client, message):

    parts = (message.text or "").split()

    if len(parts) < 2:
        await message.edit_text(
            "❌ `/delnote NAME`"
        )
        return

    name = parts[1].lower()

    cur.execute(
        "DELETE FROM notes WHERE name=?",
        (name,)
    )

    db.commit()

    await message.edit_text(
        f"🗑️ Note `{name}` deleted."
    )


# =========================================================
# GROUP MANAGER
# =========================================================

@app.on_message(
    filters.me & filters.command("ban", prefixes="/") & filters.group
)
async def ban_user(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ User ke message par reply karo."
        )
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
            f"🔨 **𝐁𝐀𝐍𝐍𝐄𝐃**\n"
            f"👤 {user.first_name}\n"
            f"🆔 `{user.id}`"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ Ban Error:\n`{e}`"
        )


@app.on_message(
    filters.me & filters.command("kick", prefixes="/") & filters.group
)
async def kick_user(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ User ke message par reply karo."
        )
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
            f"👢 **𝐊𝐈𝐂𝐊𝐄𝐃** `{user.id}`"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ Kick Error:\n`{e}`"
        )


@app.on_message(
    filters.me & filters.command("mute", prefixes="/") & filters.group
)
async def mute_user(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ User ke message par reply karo."
        )
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
            f"🔇 **𝐌𝐔𝐓𝐄𝐃 𝟏 𝐇𝐎𝐔𝐑**\n"
            f"👤 `{user.id}`"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ Mute Error:\n`{e}`"
        )


@app.on_message(
    filters.me & filters.command("unmute", prefixes="/") & filters.group
)
async def unmute_user(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ User ke message par reply karo."
        )
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
            f"🔊 **𝐔𝐍𝐌𝐔𝐓𝐄𝐃** `{user.id}`"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ Unmute Error:\n`{e}`"
        )


@app.on_message(
    filters.me & filters.command("del", prefixes="/") & filters.group
)
async def delete_message(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ Message par reply karo."
        )
        return

    try:

        await message.reply_to_message.delete()
        await message.delete()

    except Exception as e:
        print("Delete Error:", e)


@app.on_message(
    filters.me & filters.command("pin", prefixes="/") & filters.group
)
async def pin_message(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ Message par reply karo."
        )
        return

    try:

        await message.reply_to_message.pin()

        await message.edit_text(
            "📌 **𝐏𝐈𝐍𝐍𝐄𝐃 ✅**"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ Pin Error:\n`{e}`"
        )


# =========================================================
# PROMOTE
# =========================================================

@app.on_message(
    filters.me & filters.command("promote", prefixes="/") & filters.group
)
async def promote(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ User ke message par reply karo."
        )
        return

    user = message.reply_to_message.from_user

    if not user:
        return

    try:

        privileges = ChatPrivileges(
            can_manage_chat=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_manage_video_chats=True,
            can_change_info=True,
            can_promote_members=False,
        )

        await client.promote_chat_member(
            message.chat.id,
            user.id,
            privileges=privileges
        )

        await message.edit_text(
            f"👑 **𝐏𝐑𝐎𝐌𝐎𝐓𝐄𝐃**\n"
            f"👤 `{user.id}`"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ Promote Error:\n`{e}`"
        )


# =========================================================
# DEMOTE
# =========================================================

@app.on_message(
    filters.me & filters.command("demote", prefixes="/") & filters.group
)
async def demote(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ User ke message par reply karo."
        )
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
            f"⬇️ **𝐃𝐄𝐌𝐎𝐓𝐄𝐃** `{user.id}`"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ Demote Error:\n`{e}`"
        )


# =========================================================
# 🎮 TIC TAC TOE
# =========================================================

games = {}


def board_keyboard(board):

    buttons = []

    for row in range(3):

        line = []

        for col in range(3):

            index = row * 3 + col

            value = board[index]

            if value == "X":
                text = "❌"

            elif value == "O":
                text = "⭕"

            else:
                text = "▫️"

            line.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"XO:{index}"
                )
            )

        buttons.append(line)

    buttons.append([
        InlineKeyboardButton(
            "🔄 𝐍𝐄𝐖",
            callback_data="XO_NEW"
        ),
        InlineKeyboardButton(
            "✖️ 𝐂𝐋𝐎𝐒𝐄",
            callback_data="XO_CLOSE"
        )
    ])

    return InlineKeyboardMarkup(buttons)


def check_winner(board):

    wins = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6)
    ]

    for a, b, c in wins:

        if (
            board[a]
            and board[a] == board[b]
            and board[b] == board[c]
        ):
            return board[a]

    if all(board):
        return "DRAW"

    return None


def game_header(game):

    x = game["x_name"]
    o = game["o_name"] or "Waiting..."

    turn = (
        f"❌ {x}"
        if game["turn"] == "X"
        else f"⭕ {o}"
    )

    return (
        "╭━━━〔 🎮 𝐓𝐈𝐂 𝐓𝐀𝐂 𝐓𝐎𝐄 〕━━━╮\n"
        "│\n"
        f"│ ❌ X : {x}\n"
        f"│ ⭕ O : {o}\n"
        "│\n"
        f"│ 🎯 Turn : {turn}\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )


# ---------------------------------------------------------
# /XO
# ---------------------------------------------------------

@app.on_message(
    filters.group & filters.command("xo", prefixes="/")
)
async def xo_start(client, message):

    chat_id = message.chat.id

    if chat_id in games:

        await message.reply_text(
            "🎮 **XO GAME ALREADY RUNNING!**"
        )
        return

    user = message.from_user

    if not user:
        return

    games[chat_id] = {
        "board": [None] * 9,
        "x": user.id,
        "x_name": user.first_name or "Player X",
        "o": None,
        "o_name": None,
        "turn": "X"
    }

    game = games[chat_id]

    await message.reply_text(
        game_header(game),
        reply_markup=board_keyboard(game["board"])
    )


# ---------------------------------------------------------
# XO MOVE
# ---------------------------------------------------------

@app.on_callback_query(
    filters.regex(r"^XO:(\d)$")
)
async def xo_move(client, query):

    chat_id = query.message.chat.id
    uid = query.from_user.id

    game = games.get(chat_id)

    if not game:

        await query.answer(
            "❌ Game closed.",
            show_alert=True
        )
        return

    if uid == game["x"]:

        player = "X"

    elif game["o"] is None:

        game["o"] = uid
        game["o_name"] = (
            query.from_user.first_name
            or "Player O"
        )

        player = "O"

    elif uid == game["o"]:

        player = "O"

    else:

        await query.answer(
            "👥 Already 2 players joined.",
            show_alert=True
        )
        return

    if game["turn"] != player:

        await query.answer(
            "⏳ Abhi tumhari turn nahi hai.",
            show_alert=True
        )
        return

    position = int(
        query.matches[0].group(1)
    )

    if game["board"][position] is not None:

        await query.answer(
            "❌ Box already filled.",
            show_alert=True
        )
        return

    game["board"][position] = player

    result = check_winner(game["board"])

    if result:

        if result == "X":

            result_text = (
                f"🏆 ❌ **{game['x_name']} WINS!**"
            )

        elif result == "O":

            result_text = (
                f"🏆 ⭕ **{game['o_name']} WINS!**"
            )

        else:

            result_text = "🤝 **GAME DRAW!**"

        await query.message.edit_text(
            "╭━━〔 🏆 𝐆𝐀𝐌𝐄 𝐎𝐕𝐄𝐑 〕━━╮\n"
            "│\n"
            f"│ {result_text}\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━╯",
            reply_markup=board_keyboard(
                game["board"]
            )
        )

        games.pop(chat_id, None)

        await query.answer()
        return

    game["turn"] = (
        "O"
        if player == "X"
        else "X"
    )

    await query.message.edit_text(
        game_header(game),
        reply_markup=board_keyboard(
            game["board"]
        )
    )

    await query.answer()


# ---------------------------------------------------------
# NEW GAME
# ---------------------------------------------------------

@app.on_callback_query(
    filters.regex("^XO_NEW$")
)
async def xo_new(client, query):

    chat_id = query.message.chat.id
    uid = query.from_user.id

    old = games.get(chat_id)

    if old and uid != old["x"]:

        await query.answer(
            "❌ Sirf game creator New Game kar sakta hai.",
            show_alert=True
        )
        return

    games[chat_id] = {
        "board": [None] * 9,
        "x": uid,
        "x_name": (
            query.from_user.first_name
            or "Player X"
        ),
        "o": None,
        "o_name": None,
        "turn": "X"
    }

    game = games[chat_id]

    await query.message.edit_text(
        game_header(game),
        reply_markup=board_keyboard(
            game["board"]
        )
    )

    await query.answer(
        "🔄 New Game Started!"
    )


# ---------------------------------------------------------
# CLOSE
# ---------------------------------------------------------

@app.on_callback_query(
    filters.regex("^XO_CLOSE$")
)
async def xo_close(client, query):

    chat_id = query.message.chat.id
    uid = query.from_user.id

    game = games.get(chat_id)

    if game:

        if uid not in [
            game["x"],
            game["o"]
        ]:

            await query.answer(
                "❌ Sirf players game close kar sakte hain.",
                show_alert=True
            )
            return

        games.pop(chat_id, None)

    await query.message.edit_text(
        "╭━━〔 ✖️ 𝐗𝐎 𝐂𝐋𝐎𝐒𝐄𝐃 〕━━╮\n"
        "│\n"
        "│ 🎮 Game closed successfully.\n"
        "│\n"
        "│ New game: `/xo`\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━╯"
    )

    await query.answer(
        "✖️ Game Closed!"
    )


# =========================================================
# HELP
# =========================================================

@app.on_message(
    filters.me & filters.command("help", prefixes="/")
)
async def help_command(client, message):

    await message.edit_text(
        "╭━━━〔 🤖 𝐀𝐑 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 〕━━━╮\n"
        "│\n"
        "│ 📩 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘\n"
        "│ /on /off /status\n"
        "│ /setreply TEXT\n"
        "│ /resetuser ID\n"
        "│ /listusers\n"
        "│ /clearusers\n"
        "│\n"
        "│ 👋 𝐖𝐄𝐋𝐂𝐎𝐌𝐄\n"
        "│ /welcome TEXT\n"
        "│\n"
        "│ 💤 𝐀𝐅𝐊\n"
        "│ /afk REASON\n"
        "│\n"
        "│ 📝 𝐍𝐎𝐓𝐄𝐒\n"
        "│ /note NAME TEXT\n"
        "│ /getnote NAME\n"
        "│ /delnote NAME\n"
        "│\n"
        "│ 🛡️ 𝐌𝐀𝐍𝐀𝐆𝐄𝐑\n"
        "│ /ban /kick /mute /unmute\n"
        "│ /pin /del\n"
        "│ /promote /demote\n"
        "│\n"
        "│ 🎮 𝐆𝐀𝐌𝐄\n"
        "│ /xo\n"
        "│\n"
        "│ 🆔 /id\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# STATUS
# =========================================================

@app.on_message(
    filters.me & filters.command("status", prefixes="/")
)
async def status_command(client, message):

    auto = (
        "🟢 ON"
        if get_setting("auto_reply", "1") == "1"
        else "🔴 OFF"
    )

    cur.execute(
        "SELECT COUNT(*) FROM first_users"
    )
    users = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM notes"
    )
    notes = cur.fetchone()[0]

    await message.edit_text(
        "╭━━〔 📊 𝐀𝐑 𝐒𝐓𝐀𝐓𝐔𝐒 〕━━╮\n"
        "│\n"
        f"│ 📩 Auto Reply: {auto}\n"
        f"│ 👥 First Contacts: {users}\n"
        f"│ 📝 Notes: {notes}\n"
        f"│ 🎮 Active Games: {len(games)}\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# START
# =========================================================

print("========================================")
print("🤖 AR ADVANCED MANAGER")
print("📩 First DM Auto Reply : ON")
print("👋 Welcome             : ON")
print("💤 AFK                 : ON")
print("📝 Notes               : ON")
print("🛡️ Group Manager       : ON")
print("🎮 XO                  : ON")
print("💾 SQLite              : ON")
print("🚀 Railway Ready")
print("========================================")

app.run()
