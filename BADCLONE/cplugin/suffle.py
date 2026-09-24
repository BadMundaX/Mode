import random

from pyrogram import filters, Client
from pyrogram.types import Message

from BADCLONE import app
from BADCLONE.misc import db
from BADCLONE.utils.decorators import AdminRightsCheck
from BADCLONE.utils.inline import close_markup
from config import BANNED_USERS
from BADCLONE.utils.rich_ui import rich_reply


@Client.on_message(
    filters.command(["shuffle", "cshuffle"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def admins(Client, message: Message, _, chat_id):
    check = db.get(chat_id)
    if not check:
        return await rich_reply(message, _["queue_2"])
    try:
        popped = check.pop(0)
    except:
        return await rich_reply(message, _["admin_15"], reply_markup=close_markup(_))
    check = db.get(chat_id)
    if not check:
        check.insert(0, popped)
        return await rich_reply(message, _["admin_15"], reply_markup=close_markup(_))
    random.shuffle(check)
    check.insert(0, popped)
    await rich_reply(message, 
        _["admin_16"].format(message.from_user.mention), reply_markup=close_markup(_)
    )
