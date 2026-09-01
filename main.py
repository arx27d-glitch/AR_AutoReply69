import os
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
        "API_ID, API_HASH and SESSION_STRING Railway Variables me set karo."
    )

app = Client(
    "AR_MANAGER",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

# =========================================================
# AUTO REPLY
# =========================================================

AUTO_REPLY = True
COOLDOWN = 60
last_reply = {}

REPLY_TEXT = (
    "╭━━━〔 🤖 𝐀𝐑 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘 〕━━━╮\n"
    "│\n"
    "│ 👋 𝐇𝐞𝐥𝐥𝐨!\n"
    "│ 𝐌𝐚𝐢𝐧 𝐚𝐛𝐡𝐢 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐧𝐚𝐡𝐢 𝐡𝐨𝐨𝐧.\n"
    "│ 💌 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐫𝐞𝐜𝐞𝐢𝐯𝐞𝐝 ✅\n"
    "│\n"
    "╰━━━━━━━━━━━━━━━━━━━━╯"
)


@app.on_message(filters.private & ~filters.me & ~filters.bot)
async def auto_reply(client, message):
    if not AUTO_REPLY or not message.from_user:
        return

    uid = message.from_user.id
    now = time.time()

    if now - last_reply.get(uid, 0) < COOLDOWN:
        return

    last_reply[uid] = now

    try:
        await message.reply_text(REPLY_TEXT)
    except Exception as e:
        print("Auto Reply Error:", e)


# =========================================================
# ON / OFF / STATUS
# =========================================================

@app.on_message(filters.me & filters.command("on", prefixes="/"))
async def cmd_on(client, message):
    global AUTO_REPLY
    AUTO_REPLY = True
    await message.edit_text("🟢 **𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘 𝐎𝐍** ✅")


@app.on_message(filters.me & filters.command("off", prefixes="/"))
async def cmd_off(client, message):
    global AUTO_REPLY
    AUTO_REPLY = False
    await message.edit_text("🔴 **𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘 𝐎𝐅𝐅** ❌")


@app.on_message(filters.me & filters.command("status", prefixes="/"))
async def cmd_status(client, message):
    status = "🟢 𝐎𝐍" if AUTO_REPLY else "🔴 𝐎𝐅𝐅"
    await message.edit_text(
        f"╭━━〔 🤖 𝐀𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐑 〕━━╮\n"
        f"│ 📩 Auto Reply: {status}\n"
        f"│ ⏱️ Cooldown: {COOLDOWN}s\n"
        f"╰━━━━━━━━━━━━━━━━╯"
    )


@app.on_message(filters.me & filters.command("setreply", prefixes="/"))
async def cmd_setreply(client, message):
    global REPLY_TEXT

    parts = (message.text or "").split(maxsplit=1)

    if len(parts) < 2:
        await message.edit_text(
            "❌ Example:\n`/setreply Hello 👋`"
        )
        return

    REPLY_TEXT = parts[1]

    await message.edit_text(
        "╭━━〔 ✅ 𝐔𝐏𝐃𝐀𝐓𝐄𝐃 〕━━╮\n"
        "│ 💬 Auto reply updated!\n"
        "╰━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# ID
# =========================================================

@app.on_message(filters.me & filters.command("id", prefixes="/"))
async def cmd_id(client, message):
    text = (
        "╭━━〔 🆔 𝐈𝐃 𝐈𝐍𝐅𝐎 〕━━╮\n"
        f"│ 👤 Your ID: `{message.from_user.id}`\n"
        f"│ 💬 Chat ID: `{message.chat.id}`\n"
    )

    if message.reply_to_message and message.reply_to_message.from_user:
        text += (
            f"│ 👤 User ID: "
            f"`{message.reply_to_message.from_user.id}`\n"
        )

    text += "╰━━━━━━━━━━━━━━━━╯"

    await message.edit_text(text)


# =========================================================
# SAVE
# =========================================================

@app.on_message(filters.me & filters.command("save", prefixes="/"))
async def cmd_save(client, message):
    if not message.reply_to_message:
        await message.edit_text(
            "❌ Kisi message par reply karke `/save` bhejo."
        )
        return

    try:
        await client.forward_messages(
            "me",
            message.chat.id,
            message.reply_to_message.id,
        )

        await message.edit_text(
            "╭━━〔 💾 𝐒𝐀𝐕𝐄𝐃 〕━━╮\n"
            "│ ✅ Message Saved Messages mein save ho gaya.\n"
            "╰━━━━━━━━━━━━━━━━╯"
        )
    except Exception as e:
        await message.edit_text(f"❌ Save Error:\n`{e}`")


# =========================================================
# GROUP MANAGER
# =========================================================

@app.on_message(filters.me & filters.command("ban", prefixes="/") & filters.group)
async def cmd_ban(client, message):
    if not message.reply_to_message:
        await message.edit_text("❌ User ke message par reply karke `/ban` bhejo.")
        return

    user = message.reply_to_message.from_user
    if not user:
        return

    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await message.edit_text(
            f"🔨 **𝐁𝐀𝐍𝐍𝐄𝐃**\n👤 `{user.id}`"
        )
    except Exception as e:
        await message.edit_text(f"❌ Ban Error:\n`{e}`")


@app.on_message(filters.me & filters.command("unban", prefixes="/") & filters.group)
async def cmd_unban(client, message):
    parts = (message.text or "").split()

    if len(parts) < 2:
        await message.edit_text("❌ `/unban USER_ID`")
        return

    try:
        uid = int(parts[1])
        await client.unban_chat_member(message.chat.id, uid)
        await message.edit_text(f"✅ **𝐔𝐍𝐁𝐀𝐍𝐍𝐄𝐃** `{uid}`")
    except Exception as e:
        await message.edit_text(f"❌ Unban Error:\n`{e}`")


@app.on_message(filters.me & filters.command("kick", prefixes="/") & filters.group)
async def cmd_kick(client, message):
    if not message.reply_to_message:
        await message.edit_text("❌ User ke message par reply karo.")
        return

    user = message.reply_to_message.from_user
    if not user:
        return

    try:
        await client.ban_chat_member(message.chat.id, user.id)
        await client.unban_chat_member(message.chat.id, user.id)
        await message.edit_text(f"👢 **𝐊𝐈𝐂𝐊𝐄𝐃** `{user.id}`")
    except Exception as e:
        await message.edit_text(f"❌ Kick Error:\n`{e}`")


@app.on_message(filters.me & filters.command("mute", prefixes="/") & filters.group)
async def cmd_mute(client, message):
    if not message.reply_to_message:
        await message.edit_text("❌ User ke message par reply karo.")
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
            until_date=until,
        )

        await message.edit_text(
            f"🔇 **𝐌𝐔𝐓𝐄𝐃** `{user.id}`\n⏱️ 1 Hour"
        )
    except Exception as e:
        await message.edit_text(f"❌ Mute Error:\n`{e}`")


@app.on_message(filters.me & filters.command("unmute", prefixes="/") & filters.group)
async def cmd_unmute(client, message):
    if not message.reply_to_message:
        await message.edit_text("❌ User ke message par reply karo.")
        return

    user = message.reply_to_message.from_user
    if not user:
        return

    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )

        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            permissions=permissions,
        )

        await message.edit_text(f"🔊 **𝐔𝐍𝐌𝐔𝐓𝐄𝐃** `{user.id}`")
    except Exception as e:
        await message.edit_text(f"❌ Unmute Error:\n`{e}`")


@app.on_message(filters.me & filters.command("del", prefixes="/") & filters.group)
async def cmd_del(client, message):
    if not message.reply_to_message:
        await message.edit_text("❌ Delete karne wale message par reply karo.")
        return

    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception as e:
        print("Delete Error:", e)


@app.on_message(filters.me & filters.command("pin", prefixes="/") & filters.group)
async def cmd_pin(client, message):
    if not message.reply_to_message:
        await message.edit_text("❌ Pin karne wale message par reply karo.")
        return

    try:
        await message.reply_to_message.pin()
        await message.edit_text("📌 **𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐏𝐈𝐍𝐍𝐄𝐃** ✅")
    except Exception as e:
        await message.edit_text(f"❌ Pin Error:\n`{e}`")


# =========================================================
# 🎮 TIC TAC TOE
# =========================================================

xo_games = {}


def make_board(board):
    rows = []

    for r in range(3):
        row = []

        for c in range(3):
            index = r * 3 + c
            value = board[index]

            if value == "X":
                text = "❌"
            elif value == "O":
                text = "⭕"
            else:
                text = "▫️"

            row.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"XO_MOVE:{index}",
                )
            )

        rows.append(row)

    rows.append([
        InlineKeyboardButton(
            "🔄 𝐍𝐄𝐖 𝐆𝐀𝐌𝐄",
            callback_data="XO_NEW",
        ),
        InlineKeyboardButton(
            "✖️ 𝐂𝐋𝐎𝐒𝐄",
            callback_data="XO_CLOSE",
        ),
    ])

    return InlineKeyboardMarkup(rows)


def winner(board):
    combinations = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]

    for a, b, c in combinations:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]

    if all(board):
        return "DRAW"

    return None


def game_text(game, extra=""):
    x_name = game["x_name"]
    o_name = game["o_name"] or "Waiting..."

    if game["turn"] == "X":
        turn = f"❌ {x_name}"
    else:
        turn = f"⭕ {o_name}"

    return (
        "╭━━━〔 🎮 𝐓𝐈𝐂 𝐓𝐀𝐂 𝐓𝐎𝐄 〕━━━╮\n"
        "│\n"
        f"│ ❌ 𝐗 : {x_name}\n"
        f"│ ⭕ 𝐎 : {o_name}\n"
        "│\n"
        f"│ 🎯 𝐓𝐮𝐫𝐧 : {turn}\n"
        f"│ {extra}\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )


# ---------------------------------------------------------
# /xo
# ---------------------------------------------------------

@app.on_message(
    filters.group & filters.command("xo", prefixes="/")
)
async def start_xo(client, message):

    chat_id = message.chat.id

    if chat_id in xo_games:
        await message.reply_text(
            "🎮 **XO GAME ALREADY RUNNING!**\n"
            "Pehle current game finish ya close karo."
        )
        return

    user = message.from_user

    if not user:
        return

    xo_games[chat_id] = {
        "board": [None] * 9,
        "x": user.id,
        "x_name": user.first_name or "Player X",
        "o": None,
        "o_name": None,
        "turn": "X",
    }

    game = xo_games[chat_id]

    await message.reply_text(
        game_text(
            game,
            "👥 Koi doosra player empty box press karke join kare."
        ),
        reply_markup=make_board(game["board"]),
    )


# ---------------------------------------------------------
# XO MOVE
# ---------------------------------------------------------

@app.on_callback_query(
    filters.regex(r"^XO_MOVE:(\d)$")
)
async def xo_move(client, query):

    chat_id = query.message.chat.id
    uid = query.from_user.id

    if chat_id not in xo_games:
        await query.answer(
            "❌ Game available nahi hai.",
            show_alert=True,
        )
        return

    game = xo_games[chat_id]
    board = game["board"]

    # First player = X
    if uid == game["x"]:
        player = "X"

    # Second player joins as O
    elif game["o"] is None:
        game["o"] = uid
        game["o_name"] = query.from_user.first_name or "Player O"
        player = "O"

    elif uid == game["o"]:
        player = "O"

    else:
        await query.answer(
            "👥 Ye game already 2 players ka hai.",
            show_alert=True,
        )
        return

    # Turn check
    if game["turn"] != player:
        await query.answer(
            "⏳ Abhi tumhari turn nahi hai!",
            show_alert=True,
        )
        return

    position = int(query.matches[0].group(1))

    # Box check
    if board[position] is not None:
        await query.answer(
            "❌ Ye box already filled hai!",
            show_alert=True,
        )
        return

    board[position] = player

    result = winner(board)

    # WIN / DRAW
    if result:

        if result == "X":
            result_text = f"🏆 ❌ **{game['x_name']} WINS!**"

        elif result == "O":
            result_text = f"🏆 ⭕ **{game['o_name']} WINS!**"

        else:
            result_text = "🤝 **GAME DRAW!**"

        await query.message.edit_text(
            "╭━━━〔 🏆 𝐆𝐀𝐌𝐄 𝐎𝐕𝐄𝐑 〕━━━╮\n"
            "│\n"
            f"│ {result_text}\n"
            "│\n"
            "│ 🔄 New Game ke liye button dabao.\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯",
            reply_markup=make_board(board),
        )

        xo_games.pop(chat_id, None)

        await query.answer()
        return

    # Change turn
    game["turn"] = "O" if player == "X" else "X"

    await query.message.edit_text(
        game_text(game),
        reply_markup=make_board(board),
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
    user = query.from_user

    old = xo_games.get(chat_id)

    # Existing game's X can restart
    if old and user.id != old["x"]:
        await query.answer(
            "❌ Sirf game creator New Game kar sakta hai.",
            show_alert=True,
        )
        return

    xo_games[chat_id] = {
        "board": [None] * 9,
        "x": user.id,
        "x_name": user.first_name or "Player X",
        "o": None,
        "o_name": None,
        "turn": "X",
    }

    game = xo_games[chat_id]

    await query.message.edit_text(
        game_text(
            game,
            "👥 Koi doosra player empty box press kare."
        ),
        reply_markup=make_board(game["board"]),
    )

    await query.answer("🎮 New Game Started!")


# ---------------------------------------------------------
# CLOSE GAME
# ---------------------------------------------------------

@app.on_callback_query(
    filters.regex("^XO_CLOSE$")
)
async def xo_close(client, query):

    chat_id = query.message.chat.id
    user = query.from_user

    game = xo_games.get(chat_id)

    if game:
        # X player ya O player close kar sakta hai
        if user.id not in [game["x"], game["o"]]:
            await query.answer(
                "❌ Sirf game players close kar sakte hain.",
                show_alert=True,
            )
            return

        xo_games.pop(chat_id, None)

    try:
        await query.message.edit_text(
            "╭━━━〔 🎮 𝐗𝐎 𝐆𝐀𝐌𝐄 〕━━━╮\n"
            "│\n"
            "│ ✖️ **Game Closed!**\n"
            "│\n"
            "│ Naya game start karne ke liye:\n"
            "│ `/xo`\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━╯"
        )
    except Exception as e:
        print("XO Close Error:", e)

    await query.answer("✖️ Game Closed")


# =========================================================
# HELP
# =========================================================

@app.on_message(
    filters.me & filters.command("help", prefixes="/")
)
async def cmd_help(client, message):

    await message.edit_text(
        "╭━━━〔 🤖 𝐀𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐑 〕━━━╮\n"
        "│\n"
        "│ 📩 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘\n"
        "│ /on • /off • /status\n"
        "│ /setreply TEXT\n"
        "│\n"
        "│ 🛡️ 𝐆𝐑𝐎𝐔𝐏\n"
        "│ /ban • /unban ID • /kick\n"
        "│ /mute • /unmute\n"
        "│ /pin • /del\n"
        "│\n"
        "│ 💾 /save\n"
        "│ 🆔 /id\n"
        "│\n"
        "│ 🎮 𝐆𝐀𝐌𝐄\n"
        "│ /xo — Tic-Tac-Toe\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# START
# =========================================================

print("======================================")
print("🤖 AR MANAGER STARTING...")
print("📩 Auto Reply       : ON")
print("🛡️ Group Manager    : ON")
print("💾 Save Message     : ON")
print("🎮 Tic-Tac-Toe      : ON")
print("🔄 New Game         : ON")
print("✖️ Close Game       : ON")
print("🚀 Railway Ready")
print("======================================")

app.run()
