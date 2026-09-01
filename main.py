import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions
)

# ═══════════════════════════════════════
# ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂
# Advanced Telegram Userbot Manager
# ═══════════════════════════════════════

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

# ═══════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════

db = sqlite3.connect(
    "ar_manager.db",
    check_same_thread=False
)

db.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS groups(
    chat_id INTEGER PRIMARY KEY,
    welcome INTEGER DEFAULT 1,
    goodbye INTEGER DEFAULT 1,
    welcome_text TEXT
)
""")

db.commit()


DEFAULT_WELCOME = """╭━━━〔 ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂 〕━━━╮
│
│ 🖤 𝙷𝙴𝙻𝙻𝙾 {user} ✨
│
│ 👤 𝙽𝙰𝙼𝙴 ➜ {user}
│ 🆔 𝙸𝙳 ➜ {id}
│ 🔗 𝚄𝚂𝙴𝚁 ➜ {username}
│ 🏠 𝙶𝚁𝙾𝚄𝙿 ➜ {group}
│
│ 💜 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝚃𝙾 𝚃𝙷𝙴 𝙵𝙰𝙼𝙸𝙻𝚈
│ ⚡ 𝙴𝙽𝙹𝙾𝚈 𝚈𝙾𝚄𝚁 𝚂𝚃𝙰𝚈
│
╰━━━━━━━━━━━━━━━━━━━━╯"""


def ensure_group(chat_id):
    row = db.execute(
        "SELECT chat_id FROM groups WHERE chat_id=?",
        (chat_id,)
    ).fetchone()

    if not row:
        db.execute(
            """
            INSERT INTO groups
            (chat_id,welcome,goodbye,welcome_text)
            VALUES(?,?,?,?)
            """,
            (chat_id, 1, 1, DEFAULT_WELCOME)
        )
        db.commit()


def get_group(chat_id):
    ensure_group(chat_id)

    return db.execute(
        """
        SELECT welcome,goodbye,welcome_text
        FROM groups
        WHERE chat_id=?
        """,
        (chat_id,)
    ).fetchone()


def style_user(user):
    name = user.first_name or "𝙵𝚛𝚒𝚎𝚗𝚍"

    username = (
        "@" + user.username
        if user.username
        else "𝙽𝚘 𝚄𝚜𝚎𝚛𝚗𝚊𝚖𝚎"
    )

    return name, username


def welcome_format(text, user, chat):
    name, username = style_user(user)

    return (
        text
        .replace("{user}", name)
        .replace("{name}", name)
        .replace("{id}", str(user.id))
        .replace("{username}", username)
        .replace("{group}", chat.title or "𝙶𝚛𝚘𝚞𝚙")
    )


# ═══════════════════════════════════════
# WELCOME
# ═══════════════════════════════════════

@app.on_message(
    filters.group & filters.new_chat_members
)
async def welcome(client, message):

    try:
        enabled = get_group(
            message.chat.id
        )[0]

        if not enabled:
            return

        for user in message.new_chat_members:

            text = welcome_format(
                get_group(message.chat.id)[2],
                user,
                message.chat
            )

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "☠︎︎ 𝙿𝚁𝙾𝙵𝙸𝙻𝙴",
                        user_id=user.id
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📜 𝚁𝚄𝙻𝙴𝚂",
                        callback_data="rules"
                    )
                ]
            ])

            await message.reply_text(
                text,
                reply_markup=buttons
            )

    except Exception as e:
        print("WELCOME ERROR:", e)


# ═══════════════════════════════════════
# GOODBYE
# ═══════════════════════════════════════

@app.on_message(
    filters.group & filters.left_chat_member
)
async def goodbye(client, message):

    try:
        enabled = get_group(
            message.chat.id
        )[1]

        if not enabled:
            return

        user = message.left_chat_member

        if not user:
            return

        name = user.first_name or "𝙼𝚎𝚖𝚋𝚎𝚛"

        await message.reply_text(
            f"""╭━━〔 👋 𝙶𝙾𝙾𝙳𝙱𝚈𝙴 〕━━╮
│
│ 👤 {name}
│
│ 😢 𝙼𝚎𝚖𝚋𝚎𝚛 𝚑𝚊𝚜 𝚕𝚎𝚏𝚝.
│ 💜 𝚆𝚎 𝚠𝚒𝚜𝚑 𝚢𝚘𝚞 𝚠𝚎𝚕𝚕!
│
╰━━━━━━━━━━━━━━╯"""
        )

    except Exception as e:
        print("GOODBYE ERROR:", e)


# ═══════════════════════════════════════
# FIRST DM AUTO REPLY
# ═══════════════════════════════════════

@app.on_message(
    filters.private &
    ~filters.me &
    ~filters.bot
)
async def auto_reply(client, message):

    try:
        user = message.from_user

        if not user:
            return

        exists = db.execute(
            "SELECT user_id FROM users WHERE user_id=?",
            (user.id,)
        ).fetchone()

        if exists:
            return

        name, username = style_user(user)

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
│ ⚡ 𝙸'𝚕𝚕 𝚛𝚎𝚙𝚕𝚢 𝚠𝚑𝚎𝚗 𝙸 𝚌𝚊𝚗.
│
╰━━━━━━━━━━━━━━━━━━━━╯"""
        )

    except Exception as e:
        print("AUTO REPLY ERROR:", e)


# ═══════════════════════════════════════
# COMMANDS
# ═══════════════════════════════════════

@app.on_message(
    filters.me &
    filters.command(
        [
            "ping",
            "help",
            "id",
            "status",
            "welcomeon",
            "welcomeoff",
            "goodbyeon",
            "goodbyeoff"
        ],
        prefixes="/"
    )
)
async def basic_commands(client, message):

    cmd = message.command[0].lower()

    if cmd == "ping":

        await message.reply_text(
            """╭━━〔 🏓 𝙿𝙾𝙽𝙶 〕━━╮
│
│ 🟢 𝙱𝙾𝚃 𝙸𝚂 𝙾𝙽𝙻𝙸𝙽𝙴
│ ⚡ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂
│
╰━━━━━━━━━━━━╯"""
        )

    elif cmd == "id":

        if (
            message.reply_to_message and
            message.reply_to_message.from_user
        ):
            user = message.reply_to_message.from_user

            await message.reply_text(
                f"""☠︎︎ 𝚄𝚂𝙴𝚁 𝙸𝙽𝙵𝙾

👤 𝙽𝙰𝙼𝙴 ➜ {user.first_name}
🆔 𝙸𝙳 ➜ `{user.id}`
🔗 𝚄𝚂𝙴𝚁 ➜ @{user.username or 'none'}"""
            )
        else:
            await message.reply_text(
                f"🆔 𝙲𝙷𝙰𝚃 𝙸𝙳 ➜ `{message.chat.id}`"
            )

    elif cmd == "status":

        users = db.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        await message.reply_text(
            f"""╭━━〔 ⚡ 𝚂𝚃𝙰𝚃𝚄𝚂 〕━━╮
│
│ 🟢 𝙾𝙽𝙻𝙸𝙽𝙴
│ 👥 𝙵𝙸𝚁𝚂𝚃 𝙳𝙼 ➜ {users}
│ 👋 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 ➜ 🟢
│
╰━━━━━━━━━━━━━━╯"""
        )

    elif cmd == "welcomeon":

        ensure_group(message.chat.id)

        db.execute(
            "UPDATE groups SET welcome=1 WHERE chat_id=?",
            (message.chat.id,)
        )
        db.commit()

        await message.reply_text(
            "🟢 ☠︎︎ 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝙾𝙽"
        )

    elif cmd == "welcomeoff":

        ensure_group(message.chat.id)

        db.execute(
            "UPDATE groups SET welcome=0 WHERE chat_id=?",
            (message.chat.id,)
        )
        db.commit()

        await message.reply_text(
            "🔴 ☠︎︎ 𝚆𝙴𝙻𝙲𝙾𝙼𝙴 𝙾𝙵𝙵"
        )

    elif cmd == "goodbyeon":

        ensure_group(message.chat.id)

        db.execute(
            "UPDATE groups SET goodbye=1 WHERE chat_id=?",
            (message.chat.id,)
        )
        db.commit()

        await message.reply_text(
            "🟢 👋 𝙶𝙾𝙾𝙳𝙱𝚈𝙴 𝙾𝙽"
        )

    elif cmd == "goodbyeoff":

        ensure_group(message.chat.id)

        db.execute(
            "UPDATE groups SET goodbye=0 WHERE chat_id=?",
            (message.chat.id,)
        )
        db.commit()

        await message.reply_text(
            "🔴 👋 𝙶𝙾𝙾𝙳𝙱𝚈𝙴 𝙾𝙵𝙵"
        )

    elif cmd == "help":

        await message.reply_text(
            """╭━━━〔 ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂 〕━━━╮
│
│ ⚡ 𝙱𝙰𝚂𝙸𝙲
│ ├ /ping
│ ├ /status
│ └ /id
│
│ 👋 𝚆𝙴𝙻𝙲𝙾𝙼𝙴
│ ├ /welcomeon
│ ├ /welcomeoff
│ ├ /goodbyeon
│ └ /goodbyeoff
│
│ 🛡️ 𝙼𝙾𝙳𝙴𝚁𝙰𝚃𝙸𝙾𝙽
│ ├ /ban
│ ├ /kick
│ ├ /mute
│ ├ /unmute
│ ├ /unban
│ ├ /pin
│ └ /del
│
│ 🎮 𝙶𝙰𝙼𝙴
│ └ /xo
│
╰━━━━━━━━━━━━━━━━━━━━╯"""
        )


# ═══════════════════════════════════════
# MODERATION
# ═══════════════════════════════════════

@app.on_message(
    filters.me &
    filters.command(
        [
            "ban",
            "kick",
            "mute",
            "unmute",
            "unban",
            "pin",
            "del"
        ],
        prefixes="/"
    )
)
async def moderation(client, message):

    cmd = message.command[0].lower()

    try:

        if cmd in (
            "ban",
            "kick",
            "mute",
            "unmute"
        ):

            if not message.reply_to_message:
                await message.reply_text(
                    "❌ 𝚁𝚎𝚙𝚕𝚢 𝚝𝚘 𝚊 𝚞𝚜𝚎𝚛."
                )
                return

            user = (
                message.reply_to_message
                .from_user
            )

            if cmd == "ban":

                await client.ban_chat_member(
                    message.chat.id,
                    user.id
                )

                await message.reply_text(
                    f"🔨 ☠︎︎ 𝙱𝙰𝙽𝙽𝙴𝙳 ➜ {user.first_name}"
                )

            elif cmd == "kick":

                await client.ban_chat_member(
                    message.chat.id,
                    user.id
                )

                await client.unban_chat_member(
                    message.chat.id,
                    user.id
                )

                await message.reply_text(
                    f"👢 𝙺𝙸𝙲𝙺𝙀𝙳 ➜ {user.first_name}"
                )

            elif cmd == "mute":

                await client.restrict_chat_member(
                    message.chat.id,
                    user.id,
                    ChatPermissions(
                        can_send_messages=False
                    )
                )

                await message.reply_text(
                    f"🔇 𝙼𝚄𝚃𝙴𝙳 ➜ {user.first_name}"
                )

            elif cmd == "unmute":

                await client.restrict_chat_member(
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
                    f"🔊 𝚄𝙽𝙼𝚄𝚃𝙴𝙳 ➜ {user.first_name}"
                )

        elif cmd == "unban":

            if len(message.command) < 2:
                await message.reply_text(
                    "Use `/unban USER_ID`"
                )
                return

            user_id = int(
                message.command[1]
            )

            await client.unban_chat_member(
                message.chat.id,
                user_id
            )

            await message.reply_text(
                f"✅ 𝚄𝙽𝙱𝙰𝙽𝙽𝙴𝙳 ➜ `{user_id}`"
            )

        elif cmd == "pin":

            if not message.reply_to_message:
                await message.reply_text(
                    "❌ 𝚁𝚎𝚙𝚕𝚢 𝚝𝚘 𝚖𝚎𝚜𝚜𝚊𝚐𝚎."
                )
                return

            await message.reply_to_message.pin()

            await message.reply_text(
                "📌 𝙼𝙴𝚂𝚂𝙰𝙶𝙴 𝙿𝙸𝙽𝙽𝙴𝙳"
            )

        elif cmd == "del":

            if not message.reply_to_message:
                await message.reply_text(
                    "❌ 𝚁𝚎𝚙𝚕𝚢 𝚝𝚘 𝚖𝚎𝚜𝚜𝚊𝚐𝚎."
                )
                return

            await message.reply_to_message.delete()
            await message.delete()

    except Exception as e:

        await message.reply_text(
            f"❌ 𝙴𝚁𝚁𝙾𝚁\n`{e}`"
        )


# ═══════════════════════════════════════
# XO GAME
# ═══════════════════════════════════════

games = {}


def board_keyboard(board):

    buttons = []

    for i in range(9):

        value = board[i]

        if value == "X":
            text = "❌"
        elif value == "O":
            text = "⭕"
        else:
            text = "▫️"

        buttons.append(
            InlineKeyboardButton(
                text,
                callback_data=f"xo_{i}"
            )
        )

    rows = [
        buttons[0:3],
        buttons[3:6],
        buttons[6:9],
        [
            InlineKeyboardButton(
                "🔄 𝙽𝙴𝚆",
                callback_data="xo_new"
            ),
            InlineKeyboardButton(
                "✖️ 𝙲𝙻𝙾𝚂𝙴",
                callback_data="xo_close"
            )
        ]
    ]

    return InlineKeyboardMarkup(rows)


def winner(board):

    combinations = [
        (0,1,2),
        (3,4,5),
        (6,7,8),
        (0,3,6),
        (1,4,7),
        (2,5,8),
        (0,4,8),
        (2,4,6)
    ]

    for a,b,c in combinations:

        if (
            board[a] and
            board[a] == board[b] == board[c]
        ):
            return board[a]

    if all(board):
        return "DRAW"

    return None


@app.on_message(
    filters.me &
    filters.command("xo", prefixes="/")
)
async def xo(client, message):

    chat_id = message.chat.id

    games[chat_id] = {
        "board": [None] * 9,
        "x": message.from_user.id,
        "o": None,
        "turn": "X"
    }

    await message.reply_text(
        """╭━━〔 🎮 𝚃𝙸𝙲 𝚃𝙰𝙲 𝚃𝙾𝙴 〕━━╮
│
│ ❌ 𝚇 ➜ 𝙾𝚠𝚗𝚎𝚛
│ ⭕ 𝙾 ➜ 𝙵𝚒𝚛𝚜𝚝 𝙿𝚕𝚊𝚢𝚎𝚛
│
│ ⚡ 𝚇 𝙼𝙾𝚅𝙴 𝙵𝙸𝚁𝚂𝚃
│
╰━━━━━━━━━━━━━━━━╯""",
        reply_markup=board_keyboard(
            games[chat_id]["board"]
        )
    )


@app.on_callback_query(
    filters.regex(r"^xo_(\d)$")
)
async def xo_move(client, query):

    chat_id = query.message.chat.id

    if chat_id not in games:

        await query.answer(
            "❌ Game closed!",
            show_alert=True
        )

        return

    game = games[chat_id]

    uid = query.from_user.id

    if uid == game["x"]:

        player = "X"

    elif game["o"] is None:

        game["o"] = uid
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
            "⏳ 𝚆𝙰𝙸𝚃 𝙵𝙾𝚁 𝚈𝙾𝚄𝚁 𝚃𝚄𝚁𝙽",
            show_alert=True
        )

        return

    index = int(
        query.matches[0].group(1)
    )

    if game["board"][index]:

        await query.answer(
            "❌ Already selected!",
            show_alert=True
        )

        return

    game["board"][index] = player

    result = winner(
        game["board"]
    )

    if result:

        if result == "DRAW":
            text = "🤝 𝙶𝙰𝙼𝙴 𝙳𝚁𝙰𝚆!"

        else:
            text = (
                f"🏆 {result} 𝚆𝙸𝙽𝚂!"
            )

        await query.message.edit_text(
            f"""╭━━〔 🏆 𝙶𝙰𝙼𝙴 𝙾𝚅𝙴𝚁 〕━━╮
│
│ {text}
│
│ ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂
│
╰━━━━━━━━━━━━━━━━╯"""
        )

        del games[chat_id]

        await query.answer()
        return

    game["turn"] = (
        "O"
        if player == "X"
        else "X"
    )

    await query.message.edit_reply_markup(
        board_keyboard(
            game["board"]
        )
    )

    await query.answer()


@app.on_callback_query(
    filters.regex("^xo_close$")
)
async def xo_close(client, query):

    games.pop(
        query.message.chat.id,
        None
    )

    await query.message.edit_text(
        """✖️ 𝙓𝙾 𝙶𝙰𝙼𝙴 𝙲𝙻𝙾𝚂𝙴𝙳

☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂"""
    )

    await query.answer(
        "Game closed!"
    )


@app.on_callback_query(
    filters.regex("^xo_new$")
)
async def xo_new(client, query):

    chat_id = query.message.chat.id

    games[chat_id] = {
        "board": [None] * 9,
        "x": query.from_user.id,
        "o": None,
        "turn": "X"
    }

    await query.message.edit_reply_markup(
        board_keyboard(
            games[chat_id]["board"]
        )
    )

    await query.answer(
        "🔄 New game started!"
    )


# ═══════════════════════════════════════
# RULES BUTTON
# ═══════════════════════════════════════

@app.on_callback_query(
    filters.regex("^rules$")
)
async def rules(client, query):

    await query.answer(
        "📜 𝚁𝚄𝙻𝙴𝚂\n\n"
        "1️⃣ Respect everyone.\n"
        "2️⃣ No spam.\n"
        "3️⃣ No flooding.\n"
        "4️⃣ Follow admin instructions.\n"
        "5️⃣ Enjoy the group! 💜",
        show_alert=True
    )


# ═══════════════════════════════════════
# START
# ═══════════════════════════════════════

print("""
╔══════════════════════════════════════╗
║     ☠︎︎ 𝙰𝚁_𝚄𝚗𝚔𝚗𝚘𝚠𝚗乂              ║
║     ADVANCED MANAGER                 ║
║                                      ║
║     🟢 SYSTEM STARTING...            ║
║     👋 WELCOME                       ║
║     📩 AUTO REPLY                    ║
║     🛡️ MODERATION                    ║
║     🎮 XO GAME                       ║
╚══════════════════════════════════════╝
""")

app.run()
