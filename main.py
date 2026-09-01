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

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]

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
        print("AUTO REPLY ERROR:", e)


# =========================================================
# /ON
# =========================================================

@app.on_message(
    filters.me
    & filters.command("on", prefixes="/")
)
async def cmd_on(client, message):

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
# /OFF
# =========================================================

@app.on_message(
    filters.me
    & filters.command("off", prefixes="/")
)
async def cmd_off(client, message):

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
# /STATUS
# =========================================================

@app.on_message(
    filters.me
    & filters.command("status", prefixes="/")
)
async def cmd_status(client, message):

    status = "🟢 𝐎𝐍" if AUTO_REPLY else "🔴 𝐎𝐅𝐅"

    await message.edit_text(
        "╭━━━〔 🤖 𝐀𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐑 〕━━━╮\n"
        "│\n"
        f"│ 📩 𝐀𝐮𝐭𝐨 𝐑𝐞𝐩𝐥𝐲: {status}\n"
        f"│ ⏱️ 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧: {COOLDOWN}s\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# /SETREPLY
# =========================================================

@app.on_message(
    filters.me
    & filters.command("setreply", prefixes="/")
)
async def cmd_setreply(client, message):

    global REPLY_TEXT

    parts = (message.text or "").split(maxsplit=1)

    if len(parts) < 2:
        await message.edit_text(
            "❌ 𝐔𝐬𝐚𝐠𝐞:\n\n"
            "`/setreply Hello 👋 Main abhi busy hoon.`"
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
# /REPLY
# =========================================================

@app.on_message(
    filters.me
    & filters.command("reply", prefixes="/")
)
async def cmd_reply(client, message):

    await message.edit_text(
        "╭━━━〔 💬 𝐂𝐔𝐑𝐑𝐄𝐍𝐓 𝐑𝐄𝐏𝐋𝐘 〕━━━╮\n"
        "│\n"
        f"│ {REPLY_TEXT}\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# /ID
# =========================================================

@app.on_message(
    filters.me
    & filters.command("id", prefixes="/")
)
async def cmd_id(client, message):

    text = (
        "╭━━━〔 🆔 𝐈𝐃 𝐈𝐍𝐅𝐎 〕━━━╮\n"
        "│\n"
        f"│ 👤 𝐘𝐨𝐮𝐫 𝐈𝐃: `{message.from_user.id}`\n"
        f"│ 💬 𝐂𝐡𝐚𝐭 𝐈𝐃: `{message.chat.id}`\n"
    )

    if message.reply_to_message:
        if message.reply_to_message.from_user:
            text += (
                f"│ 👤 𝐔𝐬𝐞𝐫 𝐈𝐃: "
                f"`{message.reply_to_message.from_user.id}`\n"
            )

    text += "│\n╰━━━━━━━━━━━━━━━━╯"

    await message.edit_text(text)


# =========================================================
# 💾 SAVE MESSAGE
# Reply + /save
# =========================================================

@app.on_message(
    filters.me
    & filters.command("save", prefixes="/")
)
async def cmd_save(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "╭━━〔 💾 𝐒𝐀𝐕𝐄 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 〕━━╮\n"
            "│\n"
            "│ ❌ Kisi message par reply karo.\n"
            "│\n"
            "│ Example: `/save`\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━╯"
        )
        return

    try:

        await client.forward_messages(
            "me",
            message.chat.id,
            message.reply_to_message.id,
        )

        await message.edit_text(
            "╭━━━〔 💾 𝐒𝐀𝐕𝐄𝐃 〕━━━╮\n"
            "│\n"
            "│ ✅ 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐒𝐚𝐯𝐞𝐝 𝐌𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐦𝐞𝐢𝐧\n"
            "│ 𝐬𝐚𝐯𝐞 𝐤𝐚𝐫 𝐝𝐢𝐲𝐚 𝐠𝐚𝐲𝐚.\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ 𝐒𝐚𝐯𝐞 𝐄𝐫𝐫𝐨𝐫:\n`{e}`"
        )


# =========================================================
# 🔨 BAN
# Reply + /ban
# =========================================================

@app.on_message(
    filters.me
    & filters.command("ban", prefixes="/")
    & filters.group
)
async def cmd_ban(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ User ke message par reply karke `/ban` bhejo."
        )
        return

    user = message.reply_to_message.from_user

    if not user:
        return

    try:

        await client.ban_chat_member(
            message.chat.id,
            user.id,
        )

        await message.edit_text(
            "╭━━〔 🔨 𝐁𝐀𝐍𝐍𝐄𝐃 〕━━╮\n"
            f"│ 👤 𝐔𝐬𝐞𝐫: `{user.id}`\n"
            "│\n"
            "╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ 𝐁𝐚𝐧 𝐄𝐫𝐫𝐨𝐫:\n`{e}`"
        )


# =========================================================
# UNBAN
# /unban USER_ID
# =========================================================

@app.on_message(
    filters.me
    & filters.command("unban", prefixes="/")
    & filters.group
)
async def cmd_unban(client, message):

    parts = (message.text or "").split()

    if len(parts) < 2:
        await message.edit_text(
            "❌ Example:\n`/unban 123456789`"
        )
        return

    try:

        user_id = int(parts[1])

        await client.unban_chat_member(
            message.chat.id,
            user_id,
        )

        await message.edit_text(
            "╭━━〔 ✅ 𝐔𝐍𝐁𝐀𝐍𝐍𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user_id}`\n"
            "╰━━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ 𝐔𝐧𝐛𝐚𝐧 𝐄𝐫𝐫𝐨𝐫:\n`{e}`"
        )


# =========================================================
# KICK
# =========================================================

@app.on_message(
    filters.me
    & filters.command("kick", prefixes="/")
    & filters.group
)
async def cmd_kick(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ User ke message par reply karke `/kick` bhejo."
        )
        return

    user = message.reply_to_message.from_user

    if not user:
        return

    try:

        await client.ban_chat_member(
            message.chat.id,
            user.id,
        )

        await client.unban_chat_member(
            message.chat.id,
            user.id,
        )

        await message.edit_text(
            "╭━━〔 👢 𝐊𝐈𝐂𝐊𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            "╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ 𝐊𝐢𝐜𝐤 𝐄𝐫𝐫𝐨𝐫:\n`{e}`"
        )


# =========================================================
# MUTE
# =========================================================

@app.on_message(
    filters.me
    & filters.command("mute", prefixes="/")
    & filters.group
)
async def cmd_mute(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ User ke message par reply karke `/mute` bhejo."
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
            until_date=until,
        )

        await message.edit_text(
            "╭━━〔 🔇 𝐌𝐔𝐓𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            "│ ⏱️ 𝐓𝐢𝐦𝐞: 𝟏 𝐇𝐨𝐮𝐫\n"
            "╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ 𝐌𝐮𝐭𝐞 𝐄𝐫𝐫𝐨𝐫:\n`{e}`"
        )


# =========================================================
# UNMUTE
# =========================================================

@app.on_message(
    filters.me
    & filters.command("unmute", prefixes="/")
    & filters.group
)
async def cmd_unmute(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ User ke message par reply karke `/unmute` bhejo."
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
            can_add_web_page_previews=True,
        )

        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            permissions=permissions,
        )

        await message.edit_text(
            "╭━━〔 🔊 𝐔𝐍𝐌𝐔𝐓𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            "╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ 𝐔𝐧𝐦𝐮𝐭𝐞 𝐄𝐫𝐫𝐨𝐫:\n`{e}`"
        )


# =========================================================
# DELETE
# =========================================================

@app.on_message(
    filters.me
    & filters.command("del", prefixes="/")
    & filters.group
)
async def cmd_delete(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ Delete karne wale message par reply karo."
        )
        return

    try:

        await message.reply_to_message.delete()
        await message.delete()

    except Exception as e:
        print("DELETE ERROR:", e)


# =========================================================
# PIN
# =========================================================

@app.on_message(
    filters.me
    & filters.command("pin", prefixes="/")
    & filters.group
)
async def cmd_pin(client, message):

    if not message.reply_to_message:
        await message.edit_text(
            "❌ Pin karne wale message par reply karo."
        )
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
        await message.edit_text(
            f"❌ 𝐏𝐢𝐧 𝐄𝐫𝐫𝐨𝐫:\n`{e}`"
        )


# =========================================================
# PROMOTE
# =========================================================

@app.on_message(
    filters.me
    & filters.command("promote", prefixes="/")
    & filters.group
)
async def cmd_promote(client, message):

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
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
        )

        await client.promote_chat_member(
            message.chat.id,
            user.id,
            privileges=privileges,
        )

        await message.edit_text(
            "╭━━〔 👑 𝐏𝐑𝐎𝐌𝐎𝐓𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            "╰━━━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ 𝐏𝐫𝐨𝐦𝐨𝐭𝐞 𝐄𝐫𝐫𝐨𝐫:\n`{e}`"
        )


# =========================================================
# DEMOTE
# =========================================================

@app.on_message(
    filters.me
    & filters.command("demote", prefixes="/")
    & filters.group
)
async def cmd_demote(client, message):

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
            privileges=ChatPrivileges(),
        )

        await message.edit_text(
            "╭━━〔 ⬇️ 𝐃𝐄𝐌𝐎𝐓𝐄𝐃 〕━━╮\n"
            f"│ 👤 `{user.id}`\n"
            "╰━━━━━━━━━━━━╯"
        )

    except Exception as e:
        await message.edit_text(
            f"❌ 𝐃𝐞𝐦𝐨𝐭𝐞 𝐄𝐫𝐫𝐨𝐫:\n`{e}`"
        )


# =========================================================
# 🎮 XO GAME
# =========================================================

xo_games = {}


def xo_keyboard(board):

    buttons = []

    for row in range(3):

        line = []

        for col in range(3):

            pos = row * 3 + col

            if board[pos] == "X":
                text = "❌"

            elif board[pos] == "O":
                text = "⭕"

            else:
                text = "⬜"

            line.append(
                InlineKeyboardButton(
                    text,
                    callback_data=f"xo:{pos}",
                )
            )

        buttons.append(line)

    buttons.append([
        InlineKeyboardButton(
            "🔄 𝐍𝐄𝐖 𝐆𝐀𝐌𝐄",
            callback_data="xo_new",
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
        (2, 4, 6),
    ]

    for a, b, c in wins:

        if board[a] and board[a] == board[b] == board[c]:
            return board[a]

    if all(board):
        return "DRAW"

    return None


# =========================================================
# /XO
# =========================================================

@app.on_message(
    filters.group
    & filters.command("xo", prefixes="/")
)
async def cmd_xo(client, message):

    chat_id = message.chat.id

    if chat_id in xo_games:

        await message.reply_text(
            "🎮 **XO GAME ALREADY RUNNING!**"
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
        "╭━━━〔 🎮 𝐓𝐈𝐂 𝐓𝐀𝐂 𝐓𝐎𝐄 〕━━━╮\n"
        "│\n"
        f"│ ❌ 𝐗: {game['x_name']}\n"
        "│ ⭕ 𝐎: Waiting for player...\n"
        "│\n"
        "│ 👇 Empty box press karke\n"
        "│ game join karo.\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯",
        reply_markup=xo_keyboard(game["board"]),
    )


# =========================================================
# XO MOVE
# =========================================================

@app.on_callback_query(
    filters.regex(r"^xo:(\d)$")
)
async def xo_move(client, callback):

    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    if chat_id not in xo_games:

        await callback.answer(
            "❌ Game khatam ho gaya.",
            show_alert=True,
        )
        return

    game = xo_games[chat_id]
    board = game["board"]

    # Second player joins
    if game["o"] is None and user_id != game["x"]:

        game["o"] = user_id
        game["o_name"] = (
            callback.from_user.first_name or "Player O"
        )

    # Only players
    if user_id not in [game["x"], game["o"]]:

        await callback.answer(
            "👥 Game already 2 players ka hai.",
            show_alert=True,
        )
        return

    # Turn check
    if game["turn"] == "X":

        if user_id != game["x"]:

            await callback.answer(
                "⏳ Abhi ❌ X ki turn hai.",
                show_alert=True,
            )
            return

    else:

        if user_id != game["o"]:

            await callback.answer(
                "⏳ Abhi ⭕ O ki turn hai.",
                show_alert=True,
            )
            return

    position = int(callback.matches[0].group(1))

    if board[position] is not None:

        await callback.answer(
            "❌ Ye box already filled hai.",
            show_alert=True,
        )
        return

    board[position] = game["turn"]

    winner = check_winner(board)

    if winner:

        if winner == "X":

            result = (
                f"🏆 ❌ **{game['x_name']} WINS!**"
            )

        elif winner == "O":

            result = (
                f"🏆 ⭕ **{game['o_name']} WINS!**"
            )

        else:

            result = "🤝 **GAME DRAW!**"

        xo_games.pop(chat_id, None)

        await callback.message.edit_text(
            "╭━━━〔 🎮 𝐗𝐎 𝐑𝐄𝐒𝐔𝐋𝐓 〕━━━╮\n"
            "│\n"
            f"│ {result}\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯",
            reply_markup=xo_keyboard(board),
        )

        await callback.answer()
        return

    game["turn"] = (
        "O"
        if game["turn"] == "X"
        else "X"
    )

    turn_name = (
        game["x_name"]
        if game["turn"] == "X"
        else game["o_name"]
    )

    await callback.message.edit_text(
        "╭━━━〔 🎮 𝐓𝐈𝐂 𝐓𝐀𝐂 𝐓𝐎𝐄 〕━━━╮\n"
        "│\n"
        f"│ ❌ {game['x_name']}\n"
        f"│ ⭕ {game['o_name'] or 'Waiting...'}\n"
        "│\n"
        f"│ 🎯 Turn: **{turn_name}**\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯",
        reply_markup=xo_keyboard(board),
    )

    await callback.answer()


# =========================================================
# NEW XO GAME
# =========================================================

@app.on_callback_query(
    filters.regex("^xo_new$")
)
async def new_xo(client, callback):

    chat_id = callback.message.chat.id
    user = callback.from_user

    old_game = xo_games.get(chat_id)

    if old_game:

        if user.id != old_game["x"]:

            await callback.answer(
                "❌ Sirf game creator restart kar sakta hai.",
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

    await callback.message.edit_text(
        "╭━━━〔 🎮 𝐍𝐄𝐖 𝐗𝐎 𝐆𝐀𝐌𝐄 〕━━━╮\n"
        "│\n"
        f"│ ❌ 𝐗: {user.first_name or 'Player X'}\n"
        "│ ⭕ 𝐎: Waiting for player...\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯",
        reply_markup=xo_keyboard(
            xo_games[chat_id]["board"]
        ),
    )

    await callback.answer(
        "🎮 New game started!"
    )


# =========================================================
# HELP
# =========================================================

@app.on_message(
    filters.me
    & filters.command("help", prefixes="/")
)
async def cmd_help(client, message):

    await message.edit_text(
        "╭━━━〔 🤖 𝐀𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐑 〕━━━╮\n"
        "│\n"
        "│ 📩 𝐀𝐔𝐓𝐎 𝐑𝐄𝐏𝐋𝐘\n"
        "│ `/on` — ON\n"
        "│ `/off` — OFF\n"
        "│ `/setreply TEXT` — Change\n"
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
        "│ 🎮 𝐆𝐀𝐌𝐄\n"
        "│ `/xo` — Tic-Tac-Toe\n"
        "│\n"
        "│ 🆔 `/id` — Get IDs\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )


# =========================================================
# START
# =========================================================

print("==========================================")
print("🤖 AR MANAGER")
print("📩 AUTO REPLY")
print("🛡️ GROUP MANAGER")
print("💾 SAVE MESSAGE")
print("🎮 TIC-TAC-TOE")
print("🚀 RAILWAY STARTING...")
print("==========================================")

app.run()
