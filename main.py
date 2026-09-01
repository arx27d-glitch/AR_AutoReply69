import os
import sqlite3
import time

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# =========================================================
# CONFIG
# =========================================================

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

if API_ID == 0:
    raise RuntimeError("API_ID missing")

if not API_HASH:
    raise RuntimeError("API_HASH missing")

if not SESSION_STRING:
    raise RuntimeError("SESSION_STRING missing")


app = Client(
    "AR_MANAGER",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


# =========================================================
# DATABASE
# =========================================================

db = sqlite3.connect(
    "ar_manager.db",
    check_same_thread=False
)

db.execute("""
CREATE TABLE IF NOT EXISTS first_users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    created INTEGER
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS settings (
    name TEXT PRIMARY KEY,
    value TEXT
)
""")

db.commit()


def setting(name, default=""):
    row = db.execute(
        "SELECT value FROM settings WHERE name=?",
        (name,)
    ).fetchone()

    if row:
        return row[0]

    db.execute(
        "INSERT INTO settings(name,value) VALUES(?,?)",
        (name, default)
    )
    db.commit()

    return default


def set_setting(name, value):
    db.execute(
        "INSERT OR REPLACE INTO settings(name,value) VALUES(?,?)",
        (name, value)
    )
    db.commit()


# =========================================================
# DEFAULT SETTINGS
# =========================================================

setting("auto_reply", "on")

setting(
    "reply_text",
    "╭━━〔 👋 𝐇𝐄𝐋𝐋𝐎 〕━━╮\n"
    "│\n"
    "│ Hello {name}! 👋\n"
    "│ Tumhara message mil gaya.\n"
    "│ Main abhi available nahi hoon.\n"
    "│\n"
    "╰━━━━━━━━━━━━━━╯"
)

setting(
    "welcome_text",
    "👋 Welcome {name}!\n"
    "Group mein welcome! 🎉"
)


# =========================================================
# VARIABLES
# =========================================================

AFK = False
AFK_REASON = ""
AFK_TIME = 0

afk_users = set()

xo_games = {}


# =========================================================
# FIRST DM AUTO REPLY
# =========================================================

@app.on_message(
    filters.private
    & ~filters.me
    & ~filters.bot
)
async def first_dm(client, message):

    if setting("auto_reply", "on") != "on":
        return

    user = message.from_user

    if not user:
        return

    user_id = user.id

    exists = db.execute(
        "SELECT user_id FROM first_users WHERE user_id=?",
        (user_id,)
    ).fetchone()

    if exists:
        return

    name = user.first_name or "Friend"
    username = user.username or ""

    db.execute(
        """
        INSERT OR IGNORE INTO first_users
        (user_id,name,username,created)
        VALUES(?,?,?,?)
        """,
        (
            user_id,
            name,
            username,
            int(time.time())
        )
    )

    db.commit()

    text = setting("reply_text")

    text = text.replace("{name}", name)
    text = text.replace(
        "{username}",
        "@" + username if username else name
    )

    try:
        await message.reply_text(text)
    except Exception as e:
        print("AutoReply:", e)


# =========================================================
# WELCOME NEW MEMBERS
# =========================================================

@app.on_message(
    filters.group & filters.new_chat_members
)
async def welcome(client, message):

    template = setting("welcome_text")

    for user in message.new_chat_members:

        name = user.first_name or "Friend"

        text = template.replace(
            "{name}",
            name
        )

        try:
            await message.reply_text(text)
        except Exception as e:
            print("Welcome:", e)


# =========================================================
# SELF COMMAND HANDLER
# =========================================================

@app.on_message(
    filters.me & filters.text
)
async def commands(client, message):

    global AFK
    global AFK_REASON
    global AFK_TIME

    text = message.text.strip()

    if not text.startswith("/"):
        return

    parts = text.split(maxsplit=1)

    command = parts[0].lower()

    if "@" in command:
        command = command.split("@")[0]

    argument = parts[1] if len(parts) > 1 else ""


    # =====================================================
    # PING
    # =====================================================

    if command == "/ping":

        await message.reply_text(
            "🏓 **PONG!**\n"
            "🤖 AR Manager is working ✅"
        )
        return


    # =====================================================
    # TEST
    # =====================================================

    if command == "/test":

        await message.reply_text(
            "╭━━〔 🧪 TEST 〕━━╮\n"
            "│\n"
            "│ ✅ Pyrogram: Working\n"
            "│ ✅ Session: Working\n"
            "│ ✅ Commands: Working\n"
            "│\n"
            "╰━━━━━━━━━━━━╯"
        )
        return


    # =====================================================
    # ON
    # =====================================================

    if command == "/on":

        set_setting("auto_reply", "on")

        await message.reply_text(
            "🟢 **AUTO REPLY ON**\n\n"
            "📩 Sirf first-time DM par reply hoga."
        )
        return


    # =====================================================
    # OFF
    # =====================================================

    if command == "/off":

        set_setting("auto_reply", "off")

        await message.reply_text(
            "🔴 **AUTO REPLY OFF**"
        )
        return


    # =====================================================
    # SETREPLY
    # =====================================================

    if command == "/setreply":

        if not argument:

            await message.reply_text(
                "❌ Example:\n\n"
                "`/setreply Hello {name} 👋`"
            )
            return

        set_setting(
            "reply_text",
            argument
        )

        await message.reply_text(
            "✅ First DM reply updated."
        )
        return


    # =====================================================
    # WELCOME
    # =====================================================

    if command == "/welcome":

        if not argument:

            await message.reply_text(
                "📢 Current welcome:\n\n"
                f"{setting('welcome_text')}\n\n"
                "Change:\n"
                "`/welcome Welcome {name} 👋`"
            )
            return

        set_setting(
            "welcome_text",
            argument
        )

        await message.reply_text(
            "✅ Welcome message updated."
        )
        return


    # =====================================================
    # STATUS
    # =====================================================

    if command == "/status":

        count = db.execute(
            "SELECT COUNT(*) FROM first_users"
        ).fetchone()[0]

        await message.reply_text(
            "╭━━〔 📊 AR STATUS 〕━━╮\n"
            "│\n"
            f"│ 📩 Auto Reply: "
            f"{'🟢 ON' if setting('auto_reply') == 'on' else '🔴 OFF'}\n"
            f"│ 👥 First Contacts: {count}\n"
            f"│ 💤 AFK: {'🟢 ON' if AFK else '🔴 OFF'}\n"
            f"│ 🎮 Active XO: {len(xo_games)}\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━╯"
        )
        return


    # =====================================================
    # ID
    # =====================================================

    if command == "/id":

        if message.reply_to_message:
            user = message.reply_to_message.from_user

            if user:
                await message.reply_text(
                    "🆔 **USER INFO**\n\n"
                    f"👤 Name: {user.first_name}\n"
                    f"🆔 ID: `{user.id}`\n"
                    f"🔗 Username: "
                    f"`@{user.username}`"
                    if user.username
                    else
                    "🆔 **USER INFO**\n\n"
                    f"👤 Name: {user.first_name}\n"
                    f"🆔 ID: `{user.id}`"
                )
                return

        await message.reply_text(
            "🆔 **CHAT INFO**\n\n"
            f"💬 Chat ID: `{message.chat.id}`"
        )
        return


    # =====================================================
    # RESET USER
    # =====================================================

    if command == "/resetuser":

        user_id = None

        if message.reply_to_message:
            if message.reply_to_message.from_user:
                user_id = message.reply_to_message.from_user.id

        elif argument:

            try:
                user_id = int(argument.split()[0])
            except:
                pass

        if not user_id:

            await message.reply_text(
                "❌ Reply to user or use:\n"
                "`/resetuser USER_ID`"
            )
            return

        db.execute(
            "DELETE FROM first_users WHERE user_id=?",
            (user_id,)
        )

        db.commit()

        await message.reply_text(
            f"✅ User `{user_id}` reset.\n"
            "Next DM par first-time reply milega."
        )
        return


    # =====================================================
    # LIST USERS
    # =====================================================

    if command == "/listusers":

        rows = db.execute(
            """
            SELECT user_id,name,username
            FROM first_users
            ORDER BY created DESC
            LIMIT 20
            """
        ).fetchall()

        if not rows:

            await message.reply_text(
                "📭 No first-contact users."
            )
            return

        output = (
            "╭━━〔 👥 FIRST CONTACTS 〕━━╮\n"
            "│\n"
        )

        for uid, name, username in rows:

            output += (
                f"│ 👤 {name}\n"
                f"│ 🆔 `{uid}`\n"
            )

            if username:
                output += f"│ 🔗 @{username}\n"

            output += "│\n"

        output += "╰━━━━━━━━━━━━━━━━━━╯"

        await message.reply_text(output)
        return


    # =====================================================
    # CLEAR USERS
    # =====================================================

    if command == "/clearusers":

        db.execute(
            "DELETE FROM first_users"
        )

        db.commit()

        await message.reply_text(
            "🗑️ First-contact database cleared."
        )
        return


    # =====================================================
    # AFK
    # =====================================================

    if command == "/afk":

        AFK = True
        AFK_TIME = time.time()
        AFK_REASON = (
            argument
            if argument
            else "Busy right now."
        )

        afk_users.clear()

        await message.reply_text(
            "💤 **AFK MODE ON**\n\n"
            f"📝 {AFK_REASON}"
        )
        return


    # =====================================================
    # NOTE
    # =====================================================

    if command == "/note":

        p = argument.split(maxsplit=1)

        if len(p) < 2:

            await message.reply_text(
                "❌ Example:\n"
                "`/note study Physics chapter 1`"
            )
            return

        name = p[0].lower()
        content = p[1]

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS notes(
                name TEXT PRIMARY KEY,
                content TEXT
            )
            """
        )

        db.execute(
            "INSERT OR REPLACE INTO notes VALUES(?,?)",
            (name, content)
        )

        db.commit()

        await message.reply_text(
            f"📝 Note `{name}` saved."
        )
        return


    # =====================================================
    # GET NOTE
    # =====================================================

    if command == "/getnote":

        if not argument:

            await message.reply_text(
                "`/getnote NAME`"
            )
            return

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS notes(
                name TEXT PRIMARY KEY,
                content TEXT
            )
            """
        )

        row = db.execute(
            "SELECT content FROM notes WHERE name=?",
            (argument.lower(),)
        ).fetchone()

        if not row:

            await message.reply_text(
                "❌ Note not found."
            )
            return

        await message.reply_text(
            f"📝 **{argument}**\n\n"
            f"{row[0]}"
        )
        return


    # =====================================================
    # BAN
    # =====================================================

    if command == "/ban":

        if not message.reply_to_message:

            await message.reply_text(
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

            await message.reply_text(
                f"🔨 **BANNED**\n"
                f"👤 {user.first_name}\n"
                f"🆔 `{user.id}`"
            )

        except Exception as e:

            await message.reply_text(
                f"❌ Ban Error:\n`{e}`"
            )

        return


    # =====================================================
    # UNBAN
    # =====================================================

    if command == "/unban":

        if not argument:

            await message.reply_text(
                "`/unban USER_ID`"
            )
            return

        try:

            uid = int(argument.split()[0])

            await client.unban_chat_member(
                message.chat.id,
                uid
            )

            await message.reply_text(
                f"✅ Unbanned `{uid}`"
            )

        except Exception as e:

            await message.reply_text(
                f"❌ Error:\n`{e}`"
            )

        return


    # =====================================================
    # KICK
    # =====================================================

    if command == "/kick":

        if not message.reply_to_message:

            await message.reply_text(
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

            await message.reply_text(
                f"👢 **KICKED** `{user.id}`"
            )

        except Exception as e:

            await message.reply_text(
                f"❌ Error:\n`{e}`"
            )

        return


    # =====================================================
    # MUTE
    # =====================================================

    if command == "/mute":

        if not message.reply_to_message:

            await message.reply_text(
                "❌ User ke message par reply karo."
            )
            return

        user = message.reply_to_message.from_user

        if not user:
            return

        try:

            await client.restrict_chat_member(
                message.chat.id,
                user.id,
                permissions={
                    "can_send_messages": False
                }
            )

            await message.reply_text(
                f"🔇 **MUTED** `{user.id}`"
            )

        except Exception as e:

            await message.reply_text(
                f"❌ Mute Error:\n`{e}`"
            )

        return


    # =====================================================
    # UNMUTE
    # =====================================================

    if command == "/unmute":

        if not message.reply_to_message:

            await message.reply_text(
                "❌ User ke message par reply karo."
            )
            return

        user = message.reply_to_message.from_user

        if not user:
            return

        try:

            await client.restrict_chat_member(
                message.chat.id,
                user.id,
                permissions={
                    "can_send_messages": True,
                    "can_send_media_messages": True,
                    "can_send_other_messages": True,
                    "can_add_web_page_previews": True
                }
            )

            await message.reply_text(
                f"🔊 **UNMUTED** `{user.id}`"
            )

        except Exception as e:

            await message.reply_text(
                f"❌ Error:\n`{e}`"
            )

        return


    # =====================================================
    # DELETE
    # =====================================================

    if command == "/del":

        if not message.reply_to_message:

            await message.reply_text(
                "❌ Message par reply karo."
            )
            return

        try:

            await message.reply_to_message.delete()
            await message.delete()

        except Exception as e:

            print("Delete:", e)

        return


    # =====================================================
    # PIN
    # =====================================================

    if command == "/pin":

        if not message.reply_to_message:

            await message.reply_text(
                "❌ Message par reply karo."
            )
            return

        try:

            await message.reply_to_message.pin()

            await message.reply_text(
                "📌 **MESSAGE PINNED ✅**"
            )

        except Exception as e:

            await message.reply_text(
                f"❌ Pin Error:\n`{e}`"
            )

        return


    # =====================================================
    # HELP
    # =====================================================

    if command == "/help":

        await message.reply_text(
            "╭━━━〔 🤖 AR MANAGER 〕━━━╮\n"
            "│\n"
            "│ ⚡ BASIC\n"
            "│ /ping\n"
            "│ /test\n"
            "│ /status\n"
            "│ /id\n"
            "│\n"
            "│ 📩 AUTO REPLY\n"
            "│ /on\n"
            "│ /off\n"
            "│ /setreply TEXT\n"
            "│ /resetuser ID\n"
            "│ /listusers\n"
            "│ /clearusers\n"
            "│\n"
            "│ 👋 WELCOME\n"
            "│ /welcome TEXT\n"
            "│\n"
            "│ 💤 AFK\n"
            "│ /afk REASON\n"
            "│\n"
            "│ 📝 NOTES\n"
            "│ /note NAME TEXT\n"
            "│ /getnote NAME\n"
            "│\n"
            "│ 🛡️ GROUP\n"
            "│ /ban\n"
            "│ /unban ID\n"
            "│ /kick\n"
            "│ /mute\n"
            "│ /unmute\n"
            "│ /pin\n"
            "│ /del\n"
            "│\n"
            "│ 🎮 GAME\n"
            "│ /xo\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━╯"
        )
        return


# =========================================================
# AFK RESPONSE
# =========================================================

@app.on_message(
    ~filters.me
    & ~filters.bot
)
async def afk_response(client, message):

    if not AFK:
        return

    if not message.from_user:
        return

    uid = message.from_user.id

    if uid in afk_users:
        return

    afk_users.add(uid)

    minutes = int(
        (time.time() - AFK_TIME) / 60
    )

    try:

        await message.reply_text(
            "💤 **AFK**\n\n"
            f"📝 {AFK_REASON}\n"
            f"⏱️ {minutes} minute(s)"
        )

    except Exception:
        pass


# =========================================================
# XO FUNCTIONS
# =========================================================

def xo_keyboard(board):

    rows = []

    for r in range(3):

        row = []

        for c in range(3):

            i = r * 3 + c

            if board[i] == "X":
                text = "❌"

            elif board[i] == "O":
                text = "⭕"

            else:
                text = "▫️"

            row.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"XO_MOVE_{i}"
                )
            )

        rows.append(row)

    rows.append([
        InlineKeyboardButton(
            "🔄 NEW GAME",
            callback_data="XO_NEW"
        ),
        InlineKeyboardButton(
            "✖️ CLOSE",
            callback_data="XO_CLOSE"
        )
    ])

    return InlineKeyboardMarkup(rows)


def xo_winner(board):

    wins = [
        (0,1,2),
        (3,4,5),
        (6,7,8),
        (0,3,6),
        (1,4,7),
        (2,5,8),
        (0,4,8),
        (2,4,6)
    ]

    for a,b,c in wins:

        if (
            board[a]
            and board[a] == board[b]
            and board[b] == board[c]
        ):
            return board[a]

    if all(board):
        return "DRAW"

    return None


def xo_text(game):

    return (
        "╭━━〔 🎮 TIC TAC TOE 〕━━╮\n"
        "│\n"
        f"│ ❌ X: {game['x_name']}\n"
        f"│ ⭕ O: "
        f"{game['o_name'] or 'Waiting...'}\n"
        "│\n"
        f"│ 🎯 Turn: "
        f"{'❌ X' if game['turn']=='X' else '⭕ O'}\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# XO COMMAND
# =========================================================

@app.on_message(
    filters.group
    & filters.command("xo", prefixes="/")
)
async def xo_start(client, message):

    chat_id = message.chat.id

    if chat_id in xo_games:

        await message.reply_text(
            "🎮 **XO game already running!**"
        )
        return

    user = message.from_user

    if not user:
        return

    xo_games[chat_id] = {
        "board": [None] * 9,
        "x": user.id,
        "x_name": user.first_name or "X",
        "o": None,
        "o_name": None,
        "turn": "X"
    }

    game = xo_games[chat_id]

    await message.reply_text(
        xo_text(game),
        reply_markup=xo_keyboard(
            game["board"]
        )
    )


# =========================================================
# XO MOVE
# =========================================================

@app.on_callback_query(
    filters.regex(r"^XO_MOVE_(\d)$")
)
async def xo_move(client, query):

    chat_id = query.message.chat.id

    game = xo_games.get(chat_id)

    if not game:

        await query.answer(
            "❌ Game closed.",
            show_alert=True
        )
        return

    uid = query.from_user.id

    if uid == game["x"]:

        player = "X"

    elif game["o"] is None:

        game["o"] = uid
        game["o_name"] = (
            query.from_user.first_name
            or "O"
        )

        player = "O"

    elif uid == game["o"]:

        player = "O"

    else:

        await query.answer(
            "👥 Game already has 2 players.",
            show_alert=True
        )
        return

    if game["turn"] != player:

        await query.answer(
            "⏳ Tumhari turn nahi hai.",
            show_alert=True
        )
        return

    position = int(
        query.matches[0].group(1)
    )

    if game["board"][position]:

        await query.answer(
            "❌ Box already used.",
            show_alert=True
        )
        return

    game["board"][position] = player

    result = xo_winner(
        game["board"]
    )

    if result:

        if result == "X":
            result_text = (
                f"🏆 ❌ {game['x_name']} WINS!"
            )

        elif result == "O":
            result_text = (
                f"🏆 ⭕ {game['o_name']} WINS!"
            )

        else:
            result_text = "🤝 GAME DRAW!"

        await query.message.edit_text(
            "╭━━〔 🏆 GAME OVER 〕━━╮\n"
            "│\n"
            f"│ {result_text}\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━╯",
            reply_markup=xo_keyboard(
                game["board"]
            )
        )

        xo_games.pop(chat_id, None)

        await query.answer()
        return

    game["turn"] = (
        "O"
        if player == "X"
        else "X"
    )

    await query.message.edit_text(
        xo_text(game),
        reply_markup=xo_keyboard(
            game["board"]
        )
    )

    await query.answer()


# =========================================================
# XO NEW
# =========================================================

@app.on_callback_query(
    filters.regex("^XO_NEW$")
)
async def xo_new(client, query):

    chat_id = query.message.chat.id
    uid = query.from_user.id

    old = xo_games.get(chat_id)

    if old and uid != old["x"]:

        await query.answer(
            "❌ Sirf creator new game kar sakta hai.",
            show_alert=True
        )
        return

    xo_games[chat_id] = {
        "board": [None] * 9,
        "x": uid,
        "x_name": (
            query.from_user.first_name
            or "X"
        ),
        "o": None,
        "o_name": None,
        "turn": "X"
    }

    game = xo_games[chat_id]

    await query.message.edit_text(
        xo_text(game),
        reply_markup=xo_keyboard(
            game["board"]
        )
    )

    await query.answer(
        "🔄 New game!"
    )


# =========================================================
# XO CLOSE
# =========================================================

@app.on_callback_query(
    filters.regex("^XO_CLOSE$")
)
async def xo_close(client, query):

    chat_id = query.message.chat.id

    game = xo_games.get(chat_id)

    if game:

        if query.from_user.id not in [
            game["x"],
            game["o"]
        ]:

            await query.answer(
                "❌ Tum player nahi ho.",
                show_alert=True
            )
            return

        xo_games.pop(chat_id, None)

    await query.message.edit_text(
        "╭━━〔 ✖️ XO CLOSED 〕━━╮\n"
        "│\n"
        "│ Game successfully closed.\n"
        "│\n"
        "│ 🎮 New game: `/xo`\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━╯"
    )

    await query.answer(
        "Game closed."
    )


# =========================================================
# START
# =========================================================

print("")
print("================================")
print("🤖 AR MANAGER STARTED")
print("================================")
print("📩 First DM Auto Reply : ON")
print("👋 Welcome             : ON")
print("💤 AFK                 : ON")
print("📝 Notes               : ON")
print("🛡️ Group Manager       : ON")
print("🎮 XO                  : ON")
print("================================")

app.run()
