import os
import time
import sqlite3
import asyncio
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions


# ============================================================
# 💜 AR ADVANCED TELEGRAM MANAGER
# ============================================================

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

if not API_ID:
    raise RuntimeError("API_ID is missing in Railway Variables.")

if not API_HASH:
    raise RuntimeError("API_HASH is missing in Railway Variables.")

if not SESSION_STRING:
    raise RuntimeError("SESSION_STRING is missing in Railway Variables.")


BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"
ASSET_DIR.mkdir(exist_ok=True)

WELCOME_GIF = ASSET_DIR / "welcome.gif"
WELCOME_STICKER = ASSET_DIR / "welcome.webp"
DB_FILE = BASE_DIR / "ar_manager.db"


app = Client(
    "AR_ADVANCED_MANAGER",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


# ============================================================
# DATABASE
# ============================================================

db = sqlite3.connect(
    str(DB_FILE),
    check_same_thread=False
)

db.execute("""
CREATE TABLE IF NOT EXISTS first_users(
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    created INTEGER
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS group_settings(
    chat_id INTEGER PRIMARY KEY,
    welcome_text TEXT,
    enabled INTEGER DEFAULT 1,
    goodbye INTEGER DEFAULT 1,
    rules TEXT
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS settings(
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS notes(
    name TEXT PRIMARY KEY,
    content TEXT
)
""")

db.commit()


def get_setting(key, default=""):
    row = db.execute(
        "SELECT value FROM settings WHERE key=?",
        (key,)
    ).fetchone()

    if row:
        return row[0]

    db.execute(
        "INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
        (key, default)
    )

    db.commit()
    return default


def set_setting(key, value):
    db.execute(
        "INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
        (key, str(value))
    )
    db.commit()


DEFAULT_WELCOME = (
    "╭━━━〔 ✨ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 〕━━━╮\n"
    "│\n"
    "│ 👤 𝐍𝐚𝐦𝐞: {user}\n"
    "│ 🏠 𝐆𝐫𝐨𝐮𝐩: {group}\n"
    "│ 🆔 𝐈𝐃: {id}\n"
    "│ 🔗 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: {username}\n"
    "│\n"
    "│ 💜 Welcome to the family!\n"
    "│ 🌟 Have a great time here.\n"
    "│ 📜 Please follow the group rules.\n"
    "│\n"
    "╰━━━━━━━━━━━━━━━━━━━━╯"
)

DEFAULT_RULES = (
    "📜 𝐆𝐑𝐎𝐔𝐏 𝐑𝐔𝐋𝐄𝐒\n\n"
    "1️⃣ Be respectful.\n"
    "2️⃣ No spam or flooding.\n"
    "3️⃣ Follow admin instructions.\n"
    "4️⃣ Keep the group friendly."
)


def ensure_group(chat_id):

    row = db.execute(
        "SELECT chat_id FROM group_settings WHERE chat_id=?",
        (chat_id,)
    ).fetchone()

    if not row:

        db.execute(
            """
            INSERT INTO group_settings
            (chat_id,welcome_text,enabled,goodbye,rules)
            VALUES(?,?,?,?,?)
            """,
            (
                chat_id,
                DEFAULT_WELCOME,
                1,
                1,
                DEFAULT_RULES
            )
        )

        db.commit()


def get_group(chat_id):

    ensure_group(chat_id)

    return db.execute(
        """
        SELECT welcome_text,enabled,goodbye,rules
        FROM group_settings
        WHERE chat_id=?
        """,
        (chat_id,)
    ).fetchone()


def set_group(chat_id, column, value):

    if column not in {
        "welcome_text",
        "enabled",
        "goodbye",
        "rules"
    }:
        return

    ensure_group(chat_id)

    db.execute(
        f"UPDATE group_settings SET {column}=? WHERE chat_id=?",
        (value, chat_id)
    )

    db.commit()


# ============================================================
# ASSET GENERATOR
# ============================================================

def load_font(size, bold=False):

    if bold:

        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
        ]

    else:

        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
        ]

    for path in candidates:

        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def create_assets():

    if WELCOME_GIF.exists() and WELCOME_STICKER.exists():
        return

    width = 720
    height = 720

    frames = []

    title_font = load_font(58, True)
    ar_font = load_font(105, True)
    small_font = load_font(24, True)
    tiny_font = load_font(19, False)

    for frame_no in range(12):

        img = Image.new(
            "RGB",
            (width, height),
            (7, 4, 14)
        )

        draw = ImageDraw.Draw(img)

        # Animated glow
        glow = 90 + frame_no * 6

        cx = width // 2
        cy = 150

        for r in range(glow, 5, -10):

            alpha = max(
                10,
                int(100 * (glow - r + 10) / glow)
            )

            draw.ellipse(
                (
                    cx - r,
                    cy - r,
                    cx + r,
                    cy + r
                ),
                outline=(
                    70 + alpha // 3,
                    20,
                    150 + alpha // 2
                ),
                width=3
            )

        # Top line
        draw.line(
            (70, 55, 650, 55),
            fill=(165, 70, 255),
            width=3
        )

        # AR shield
        shield = [
            (360, 85),
            (500, 125),
            (475, 270),
            (360, 340),
            (245, 270),
            (220, 125)
        ]

        draw.polygon(
            shield,
            fill=(14, 8, 28),
            outline=(185, 75, 255)
        )

        draw.polygon(
            [
                (360, 105),
                (475, 140),
                (455, 250),
                (360, 310),
                (265, 250),
                (245, 140)
            ],
            outline=(95, 35, 190),
            width=4
        )

        draw.text(
            (360, 190),
            "AR",
            font=ar_font,
            anchor="mm",
            fill=(222, 180, 255),
            stroke_width=3,
            stroke_fill=(95, 25, 180)
        )

        # Welcome
        draw.text(
            (360, 370),
            "WELCOME",
            font=title_font,
            anchor="mm",
            fill=(226, 191, 255),
            stroke_width=2,
            stroke_fill=(110, 35, 210)
        )

        # Card
        draw.rounded_rectangle(
            (55, 425, 665, 650),
            radius=28,
            fill=(12, 7, 24),
            outline=(145, 55, 230),
            width=4
        )

        draw.text(
            (360, 470),
            "NEW MEMBER JOINED",
            font=small_font,
            anchor="mm",
            fill=(211, 156, 255)
        )

        draw.text(
            (360, 525),
            "Your name • Group • ID",
            font=tiny_font,
            anchor="mm",
            fill=(225, 225, 235)
        )

        draw.text(
            (360, 575),
            "💜 Welcome to the family!",
            font=small_font,
            anchor="mm",
            fill=(205, 150, 255)
        )

        draw.text(
            (360, 615),
            "AR ADVANCED MANAGER",
            font=tiny_font,
            anchor="mm",
            fill=(150, 120, 175)
        )

        frames.append(img)

    frames[0].save(
        str(WELCOME_GIF),
        save_all=True,
        append_images=frames[1:],
        duration=110,
        loop=0,
        optimize=True
    )

    # Transparent sticker
    sticker = Image.new(
        "RGBA",
        (512, 512),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(sticker)

    draw.ellipse(
        (35, 35, 477, 477),
        fill=(8, 4, 17, 255),
        outline=(190, 70, 255, 255),
        width=12
    )

    draw.polygon(
        [
            (256, 70),
            (385, 105),
            (365, 300),
            (256, 395),
            (147, 300),
            (127, 105)
        ],
        fill=(15, 8, 32, 255),
        outline=(210, 95, 255, 255)
    )

    draw.text(
        (256, 210),
        "AR",
        font=load_font(105, True),
        anchor="mm",
        fill=(230, 190, 255, 255),
        stroke_width=3,
        stroke_fill=(105, 25, 190, 255)
    )

    draw.text(
        (256, 330),
        "WELCOME",
        font=load_font(40, True),
        anchor="mm",
        fill=(215, 160, 255, 255)
    )

    sticker.save(
        str(WELCOME_STICKER),
        "WEBP",
        lossless=True,
        method=6
    )


# ============================================================
# TEXT HELPER
# ============================================================

def format_text(text, user, chat):

    name = user.first_name or "Friend"

    username = (
        f"@{user.username}"
        if user.username
        else "No username"
    )

    group = chat.title or "Group"

    return (
        text
        .replace("{user}", name)
        .replace("{name}", name)
        .replace("{group}", group)
        .replace("{id}", str(user.id))
        .replace("{username}", username)
    )


async def safe_delete(
    client,
    chat_id,
    message_id,
    seconds
):

    await asyncio.sleep(seconds)

    try:
        await client.delete_messages(
            chat_id,
            message_id
        )
    except Exception:
        pass


# ============================================================
# WELCOME
# ============================================================

@app.on_message(
    filters.group &
    filters.new_chat_members
)
async def welcome_handler(client, message):

    try:

        welcome_text, enabled, goodbye, rules = get_group(
            message.chat.id
        )

        if not enabled:
            return

        for user in message.new_chat_members:

            text = format_text(
                welcome_text,
                user,
                message.chat
            )

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄",
                        user_id=user.id
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📜 𝐑𝐔𝐋𝐄𝐒",
                        callback_data=f"RULES:{message.chat.id}"
                    )
                ]
            ])

            # Sticker
            try:

                await client.send_sticker(
                    message.chat.id,
                    str(WELCOME_STICKER)
                )

            except Exception as e:
                print(
                    "Sticker send error:",
                    e
                )

            # GIF
            try:

                sent = await client.send_animation(
                    message.chat.id,
                    str(WELCOME_GIF),
                    caption=text,
                    reply_markup=buttons
                )

            except Exception:

                sent = await client.send_message(
                    message.chat.id,
                    text,
                    reply_markup=buttons
                )

            asyncio.create_task(
                safe_delete(
                    client,
                    message.chat.id,
                    sent.id,
                    90
                )
            )

    except Exception as e:

        print(
            "WELCOME ERROR:",
            repr(e)
        )


# ============================================================
# GOODBYE
# ============================================================

@app.on_message(
    filters.group &
    filters.left_chat_member
)
async def goodbye_handler(client, message):

    try:

        _, _, enabled_goodbye, _ = get_group(
            message.chat.id
        )

        if not enabled_goodbye:
            return

        user = message.left_chat_member

        if not user:
            return

        name = user.first_name or "Member"

        sent = await message.reply_text(
            "╭━━〔 👋 𝐆𝐎𝐎𝐃𝐁𝐘𝐄 〕━━╮\n"
            "│\n"
            f"│ 👤 {name}\n"
            "│\n"
            "│ 😢 Member has left the group.\n"
            "│ 💜 We wish you well!\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━╯"
        )

        asyncio.create_task(
            safe_delete(
                client,
                message.chat.id,
                sent.id,
                30
            )
        )

    except Exception as e:

        print(
            "GOODBYE ERROR:",
            repr(e)
        )


# ============================================================
# FIRST DM AUTO REPLY
# ============================================================

@app.on_message(
    filters.private &
    ~filters.me &
    ~filters.bot
)
async def first_dm_handler(client, message):

    try:

        if get_setting(
            "auto_reply",
            "on"
        ) != "on":
            return

        user = message.from_user

        if not user:
            return

        exists = db.execute(
            "SELECT user_id FROM first_users WHERE user_id=?",
            (user.id,)
        ).fetchone()

        if exists:
            return

        db.execute(
            """
            INSERT OR IGNORE INTO first_users
            (user_id,name,username,created)
            VALUES(?,?,?,?)
            """,
            (
                user.id,
                user.first_name or "Friend",
                user.username or "",
                int(time.time())
            )
        )

        db.commit()

        text = get_setting(
            "reply_text",
            (
                "╭━━〔 👋 𝐇𝐄𝐋𝐋𝐎 〕━━╮\n"
                "│\n"
                "│ Hey {name}! 💜\n"
                "│ Your message was received.\n"
                "│ I may reply later.\n"
                "│\n"
                "╰━━━━━━━━━━━━━━━━╯"
            )
        )

        text = text.replace(
            "{name}",
            user.first_name or "Friend"
        )

        text = text.replace(
            "{username}",
            (
                f"@{user.username}"
                if user.username
                else "No username"
            )
        )

        await message.reply_text(text)

    except Exception as e:

        print(
            "AUTOREPLY ERROR:",
            repr(e)
        )


# ============================================================
# XO GAME
# ============================================================

xo_games = {}


def xo_keyboard(board):

    rows = []

    for r in range(3):

        row = []

        for c in range(3):

            index = r * 3 + c
            value = board[index]

            if value == "X":
                label = "❌"

            elif value == "O":
                label = "⭕"

            else:
                label = "▫️"

            row.append(
                InlineKeyboardButton(
                    label,
                    callback_data=f"XO:{index}"
                )
            )

        rows.append(row)

    rows.append([
        InlineKeyboardButton(
            "🔄 NEW",
            callback_data="XO:NEW"
        ),
        InlineKeyboardButton(
            "✖️ CLOSE",
            callback_data="XO:CLOSE"
        )
    ])

    return InlineKeyboardMarkup(rows)


def check_winner(board):

    lines = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6)
    ]

    for a, b, c in lines:

        if board[a] and board[a] == board[b] == board[c]:
            return board[a]

    if all(board):
        return "DRAW"

    return None


@app.on_message(
    filters.group &
    filters.command("xo", prefixes="/") &
    filters.me
)
async def xo_start(client, message):

    chat_id = message.chat.id

    if chat_id in xo_games:

        await message.reply_text(
            "🎮 **XO is already running!**"
        )

        return

    user = message.from_user

    xo_games[chat_id] = {
        "board": [None] * 9,
        "x": user.id,
        "x_name": user.first_name or "X",
        "o": None,
        "o_name": None,
        "turn": "X"
    }

    await message.reply_text(
        "╭━━〔 🎮 𝐓𝐈𝐂 𝐓𝐀𝐂 𝐓𝐎𝐄 〕━━╮\n"
        "│\n"
        f"│ ❌ X: {user.first_name or 'X'}\n"
        "│ ⭕ O: Join by pressing a box\n"
        "│\n"
        "│ 🎯 X starts!\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━╯",
        reply_markup=xo_keyboard(
            xo_games[chat_id]["board"]
        )
    )


@app.on_callback_query(
    filters.regex(r"^XO:(\d)$")
)
async def xo_move(client, query):

    chat_id = query.message.chat.id

    game = xo_games.get(chat_id)

    if not game:

        await query.answer(
            "Game closed.",
            show_alert=True
        )

        return

    uid = query.from_user.id

    if uid == game["x"]:

        player = "X"

    elif game["o"] is None:

        game["o"] = uid
        game["o_name"] = (
            query.from_user.first_name or "O"
        )

        player = "O"

    elif uid == game["o"]:

        player = "O"

    else:

        await query.answer(
            "👥 Two players are already in this game.",
            show_alert=True
        )

        return

    if game["turn"] != player:

        await query.answer(
            "⏳ Not your turn.",
            show_alert=True
        )

        return

    index = int(
        query.matches[0].group(1)
    )

    if game["board"][index]:

        await query.answer(
            "❌ Box already used.",
            show_alert=True
        )

        return

    game["board"][index] = player

    result = check_winner(
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
            "╭━━〔 🏆 𝐆𝐀𝐌𝐄 𝐎𝐕𝐄𝐑 〕━━╮\n"
            "│\n"
            f"│ {result_text}\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━╯"
        )

        xo_games.pop(
            chat_id,
            None
        )

        await query.answer()

        return

    game["turn"] = (
        "O"
        if player == "X"
        else "X"
    )

    await query.message.edit_reply_markup(
        xo_keyboard(
            game["board"]
        )
    )

    await query.answer()


@app.on_callback_query(
    filters.regex(r"^XO:NEW$")
)
async def xo_new(client, query):

    chat_id = query.message.chat.id
    user = query.from_user

    xo_games[chat_id] = {
        "board": [None] * 9,
        "x": user.id,
        "x_name": user.first_name or "X",
        "o": None,
        "o_name": None,
        "turn": "X"
    }

    await query.message.edit_reply_markup(
        xo_keyboard(
            xo_games[chat_id]["board"]
        )
    )

    await query.answer(
        "🔄 New game!"
    )


@app.on_callback_query(
    filters.regex(r"^XO:CLOSE$")
)
async def xo_close(client, query):

    xo_games.pop(
        query.message.chat.id,
        None
    )

    await query.message.edit_text(
        "✖️ **XO GAME CLOSED**\n\n"
        "🎮 Start again with `/xo`"
    )

    await query.answer(
        "Game closed."
    )


# ============================================================
# RULES BUTTON
# ============================================================

@app.on_callback_query(
    filters.regex(r"^RULES:")
)
async def rules_callback(client, query):

    try:

        chat_id = int(
            query.data.split(":", 1)[1]
        )

        rules = get_group(
            chat_id
        )[3]

    except Exception:

        rules = DEFAULT_RULES

    await query.answer(
        rules[:190],
        show_alert=True
    )


# ============================================================
# COMMAND HANDLER
# ============================================================

@app.on_message(
    filters.me &
    filters.text
)
async def command_handler(client, message):

    text = message.text.strip()

    if not text.startswith("/"):
        return

    parts = text.split(
        maxsplit=1
    )

    command = parts[0].lower().split("@")[0]

    arg = (
        parts[1]
        if len(parts) > 1
        else ""
    )

    try:

        # ================= BASIC =================

        if command == "/ping":

            await message.reply_text(
                "🏓 **PONG!**\n\n"
                "🤖 𝐀𝐑 𝐀𝐝𝐯𝐚𝐧𝐜𝐞𝐝 𝐌𝐚𝐧𝐚𝐠𝐞𝐫\n"
                "🟢 Online & working."
            )

        elif command == "/status":

            users = db.execute(
                "SELECT COUNT(*) FROM first_users"
            ).fetchone()[0]

            await message.reply_text(
                "╭━━〔 📊 𝐀𝐑 𝐒𝐓𝐀𝐓𝐔𝐒 〕━━╮\n"
                "│\n"
                f"│ 📩 Auto Reply: "
                f"{'🟢 ON' if get_setting('auto_reply','on') == 'on' else '🔴 OFF'}\n"
                f"│ 👥 First Contacts: {users}\n"
                f"│ 🎮 XO Games: {len(xo_games)}\n"
                "│ 👋 Welcome: 🟢 ON\n"
                "│ 🎬 GIF: 🟢 Built-in\n"
                "│ 🖼️ Sticker: 🟢 Built-in\n"
                "│\n"
                "╰━━━━━━━━━━━━━━━━━━╯"
            )

        elif command == "/id":

            if (
                message.reply_to_message
                and message.reply_to_message.from_user
            ):

                user = (
                    message.reply_to_message.from_user
                )

                await message.reply_text(
                    "🆔 **USER INFO**\n\n"
                    f"👤 {user.first_name}\n"
                    f"🆔 `{user.id}`\n"
                    f"🔗 "
                    f"{('@' + user.username) if user.username else 'No username'}"
                )

            else:

                await message.reply_text(
                    f"🆔 **CHAT ID:** `{message.chat.id}`"
                )

        # ================= AUTOREPLY =================

        elif command == "/on":

            set_setting(
                "auto_reply",
                "on"
            )

            await message.reply_text(
                "🟢 **FIRST-DM AUTO REPLY ON**"
            )

        elif command == "/off":

            set_setting(
                "auto_reply",
                "off"
            )

            await message.reply_text(
                "🔴 **FIRST-DM AUTO REPLY OFF**"
            )

        elif command == "/setreply":

            if not arg:

                await message.reply_text(
                    "Use:\n"
                    "`/setreply Hello {name} 👋`"
                )

            else:

                set_setting(
                    "reply_text",
                    arg
                )

                await message.reply_text(
                    "✅ First-DM reply updated."
                )

        elif command == "/resetuser":

            uid = None

            if (
                message.reply_to_message
                and message.reply_to_message.from_user
            ):

                uid = (
                    message.reply_to_message
                    .from_user.id
                )

            elif arg:

                try:
                    uid = int(
                        arg.split()[0]
                    )
                except ValueError:
                    pass

            if not uid:

                await message.reply_text(
                    "❌ Reply to a user or use "
                    "`/resetuser USER_ID`"
                )

            else:

                db.execute(
                    "DELETE FROM first_users WHERE user_id=?",
                    (uid,)
                )

                db.commit()

                await message.reply_text(
                    f"✅ `{uid}` reset."
                )

        elif command == "/listusers":

            rows = db.execute(
                """
                SELECT user_id,name,username
                FROM first_users
                ORDER BY created DESC
                LIMIT 30
                """
            ).fetchall()

            if not rows:

                await message.reply_text(
                    "📭 No first-contact users."
                )

            else:

                out = (
                    "╭━━〔 👥 𝐅𝐈𝐑𝐒𝐓 𝐂𝐎𝐍𝐓𝐀𝐂𝐓𝐒 〕━━╮\n"
                    "│\n"
                )

                for uid, name, username in rows:

                    out += (
                        f"│ 👤 {name}\n"
                        f"│ 🆔 `{uid}`\n"
                    )

                    if username:
                        out += (
                            f"│ 🔗 @{username}\n"
                        )

                    out += "│\n"

                out += (
                    "╰━━━━━━━━━━━━━━━━━━━━╯"
                )

                await message.reply_text(
                    out
                )

        # ================= WELCOME =================

        elif command == "/welcome":

            if message.chat.type not in (
                "group",
                "supergroup"
            ):

                await message.reply_text(
                    "❌ Use this inside a group."
                )

            elif not arg:

                await message.reply_text(
                    "📢 **Current welcome:**\n\n"
                    + get_group(
                        message.chat.id
                    )[0]
                    + "\n\nVariables: "
                    "`{user}` `{group}` `{id}` `{username}`"
                )

            else:

                set_group(
                    message.chat.id,
                    "welcome_text",
                    arg
                )

                await message.reply_text(
                    "✅ Welcome text saved."
                )

        elif command == "/welcomeon":

            set_group(
                message.chat.id,
                "enabled",
                1
            )

            await message.reply_text(
                "🟢 **Welcome system ON**"
            )

        elif command == "/welcomeoff":

            set_group(
                message.chat.id,
                "enabled",
                0
            )

            await message.reply_text(
                "🔴 **Welcome system OFF**"
            )

        elif command == "/goodbyeon":

            set_group(
                message.chat.id,
                "goodbye",
                1
            )

            await message.reply_text(
                "🟢 **Goodbye ON**"
            )

        elif command == "/goodbyeoff":

            set_group(
                message.chat.id,
                "goodbye",
                0
            )

            await message.reply_text(
                "🔴 **Goodbye OFF**"
            )

        elif command == "/setrules":

            if not arg:

                await message.reply_text(
                    "Use:\n"
                    "`/setrules Be respectful...`"
                )

            else:

                set_group(
                    message.chat.id,
                    "rules",
                    arg
                )

                await message.reply_text(
                    "✅ Rules saved."
                )

        elif command == "/welcometest":

            if message.chat.type not in (
                "group",
                "supergroup"
            ):

                await message.reply_text(
                    "❌ Use inside a group."
                )

            else:

                user = message.from_user

                welcome_text = get_group(
                    message.chat.id
                )[0]

                caption = format_text(
                    welcome_text,
                    user,
                    message.chat
                )

                buttons = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "👤 𝐏𝐑𝐎𝐅𝐈𝐋𝐄",
                            user_id=user.id
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "📜 𝐑𝐔𝐋𝐄𝐒",
                            callback_data=f"RULES:{message.chat.id}"
                        )
                    ]
                ])

                try:

                    await client.send_sticker(
                        message.chat.id,
                        str(WELCOME_STICKER)
                    )

                except Exception as e:

                    print(
                        "Test sticker error:",
                        e
                    )

                await client.send_animation(
                    message.chat.id,
                    str(WELCOME_GIF),
                    caption=caption,
                    reply_markup=buttons
                )

        # ================= MODERATION =================

        elif command in (
            "/ban",
            "/kick",
            "/mute",
            "/unmute"
        ):

            if message.chat.type not in (
                "group",
                "supergroup"
            ):

                await message.reply_text(
                    "❌ Use this inside a group."
                )

                return

            if (
                not message.reply_to_message
                or not message.reply_to_message.from_user
            ):

                await message.reply_text(
                    "❌ Reply to the user's message."
                )

                return

            uid = (
                message.reply_to_message
                .from_user.id
            )

            if command == "/ban":

                await client.ban_chat_member(
                    message.chat.id,
                    uid
                )

                await message.reply_text(
                    f"🔨 **BANNED:** `{uid}`"
                )

            elif command == "/kick":

                await client.ban_chat_member(
                    message.chat.id,
                    uid
                )

                await client.unban_chat_member(
                    message.chat.id,
                    uid
                )

                await message.reply_text(
                    f"👢 **KICKED:** `{uid}`"
                )

            elif command == "/mute":

                await client.restrict_chat_member(
                    message.chat.id,
                    uid,
                    permissions=ChatPermissions(
                        can_send_messages=False
                    )
                )

                await message.reply_text(
                    f"🔇 **MUTED:** `{uid}`"
                )

            elif command == "/unmute":

                await client.restrict_chat_member(
                    message.chat.id,
                    uid,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True
                    )
                )

                await message.reply_text(
                    f"🔊 **UNMUTED:** `{uid}`"
                )

        elif command == "/unban":

            if not arg:

                await message.reply_text(
                    "Use `/unban USER_ID`"
                )

            else:

                uid = int(
                    arg.split()[0]
                )

                await client.unban_chat_member(
                    message.chat.id,
                    uid
                )

                await message.reply_text(
                    f"✅ **UNBANNED:** `{uid}`"
                )

        elif command == "/del":

            if not message.reply_to_message:

                await message.reply_text(
                    "❌ Reply to a message."
                )

            else:

                await message.reply_to_message.delete()
                await message.delete()

        elif command == "/pin":

            if not message.reply_to_message:

                await message.reply_text(
                    "❌ Reply to a message."
                )

            else:

                await message.reply_to_message.pin()

                await message.reply_text(
                    "📌 **PINNED ✅**"
                )

        # ================= NOTES =================

        elif command == "/note":

            p = arg.split(
                maxsplit=1
            )

            if len(p) < 2:

                await message.reply_text(
                    "Use `/note name content`"
                )

            else:

                db.execute(
                    """
                    INSERT OR REPLACE INTO notes
                    (name,content)
                    VALUES(?,?)
                    """,
                    (
                        p[0].lower(),
                        p[1]
                    )
                )

                db.commit()

                await message.reply_text(
                    f"📝 Note `{p[0]}` saved."
                )

        elif command == "/getnote":

            row = db.execute(
                "SELECT content FROM notes WHERE name=?",
                (arg.lower(),)
            ).fetchone()

            if not row:

                await message.reply_text(
                    "❌ Note not found."
                )

            else:

                await message.reply_text(
                    f"📝 **{arg}**\n\n{row[0]}"
                )

        # ================= HELP =================

        elif command == "/help":

            await message.reply_text(
                "╭━━━〔 💜 𝐀𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐑 〕━━━╮\n"
                "│\n"
                "│ ⚡ BASIC\n"
                "│ /ping  /status  /id\n"
                "│\n"
                "│ 👋 WELCOME\n"
                "│ /welcome TEXT\n"
                "│ /welcomeon  /welcomeoff\n"
                "│ /goodbyeon  /goodbyeoff\n"
                "│ /setrules TEXT\n"
                "│ /welcometest\n"
                "│\n"
                "│ 📩 FIRST-DM AUTO REPLY\n"
                "│ /on  /off\n"
                "│ /setreply TEXT\n"
                "│ /resetuser ID\n"
                "│ /listusers\n"
                "│\n"
                "│ 🛡️ GROUP MANAGER\n"
                "│ /ban  /kick  /mute  /unmute\n"
                "│ /unban ID  /pin  /del\n"
                "│\n"
                "│ 📝 NOTES\n"
                "│ /note NAME TEXT\n"
                "│ /getnote NAME\n"
                "│\n"
                "│ 🎮 GAME\n"
                "│ /xo\n"
                "│\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯"
            )

    except Exception as e:

        await message.reply_text(
            "❌ **Command Error**\n\n"
            f"`{type(e).__name__}: {e}`"
        )


# ============================================================
# START
# ============================================================

create_assets()

print("=" * 50)
print("💜 AR ADVANCED MANAGER")
print("🟢 Starting...")
print("🎬 Purple/black welcome GIF")
print("🖼️ Matching WEBP sticker")
print("👋 Per-group welcome + goodbye")
print("📩 First-DM auto reply")
print("🛡️ Group manager")
print("🎮 XO game")
print("=" * 50)

app.run()
