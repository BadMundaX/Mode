from pyrogram import filters
from pyrogram.types import Message

from BADCLONE import app
from BADCLONE.utils.database import get_loop, set_loop
from BADCLONE.utils.decorators import AdminRightsCheck
from BADCLONE.utils.inline import close_markup
from config import BANNED_USERS
from BADCLONE.utils.rich_ui import rich_reply


@app.on_message(filters.command(["loop", "cloop"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def admins(cli, message: Message, _, chat_id):
    usage = _["admin_17"]
    if len(message.command) != 2:
        return await rich_reply(message, usage)
    state = message.text.split(None, 1)[1].strip()
    if state.isnumeric():
        state = int(state)
        if 1 <= state <= 10:
            got = await get_loop(chat_id)
            if got > 0:
                state = got + state
            if int(state) > 10:
                state = 10
            await set_loop(chat_id, state)
            return await rich_reply(message, 
                text=_["admin_18"].format(state, message.from_user.mention),
                reply_markup=close_markup(_),
            )
        else:
            return await rich_reply(message, _["admin_17"])
    elif state.lower() == "enable":
        await set_loop(chat_id, 10)
        return await rich_reply(message, 
            text=_["admin_18"].format(state, message.from_user.mention),
            reply_markup=close_markup(_),
        )
    elif state.lower() == "disable":
        await set_loop(chat_id, 0)
        return await rich_reply(message, 
            _["admin_19"].format(message.from_user.mention),
            reply_markup=close_markup(_),
        )
    else:
        return await rich_reply(message, usage)
