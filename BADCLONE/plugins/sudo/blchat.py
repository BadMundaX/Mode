from pyrogram import filters
from pyrogram.types import Message

from BADCLONE import app
from BADCLONE.misc import SUDOERS
from BADCLONE.utils.database import blacklist_chat, blacklisted_chats, whitelist_chat
from BADCLONE.utils.decorators.language import language
from config import BANNED_USERS
from BADCLONE.utils.rich_ui import rich_reply


@app.on_message(filters.command(["blchat", "blacklistchat"]) & SUDOERS)
@language
async def blacklist_chat_func(client, message: Message, _):
    if len(message.command) != 2:
        return await rich_reply(message, _["black_1"])
    chat_id = int(message.text.strip().split()[1])
    if chat_id in await blacklisted_chats():
        return await rich_reply(message, _["black_2"])
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        await rich_reply(message, _["black_3"])
    else:
        await rich_reply(message, _["black_9"])
    try:
        await app.leave_chat(chat_id)
    except:
        pass


@app.on_message(
    filters.command(["whitelistchat", "unblacklistchat", "unblchat"]) & SUDOERS
)
@language
async def white_funciton(client, message: Message, _):
    if len(message.command) != 2:
        return await rich_reply(message, _["black_4"])
    chat_id = int(message.text.strip().split()[1])
    if chat_id not in await blacklisted_chats():
        return await rich_reply(message, _["black_5"])
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await rich_reply(message, _["black_6"])
    await rich_reply(message, _["black_9"])


@app.on_message(filters.command(["blchats", "blacklistedchats"]) & ~BANNED_USERS)
@language
async def all_chats(client, message: Message, _):
    text = _["black_7"]
    j = 0
    for count, chat_id in enumerate(await blacklisted_chats(), 1):
        try:
            title = (await app.get_chat(chat_id)).title
        except:
            title = "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
        j = 1
        text += f"{count}. {title}[<code>{chat_id}</code>]\n"
    if j == 0:
        await rich_reply(message, _["black_8"].format(app.mention))
    else:
        await rich_reply(message, text)
