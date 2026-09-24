from pyrogram import filters

from BADCLONE import app
from BADCLONE.misc import SUDOERS
from BADCLONE.utils.database import add_off, add_on
from BADCLONE.utils.decorators.language import language
from BADCLONE.utils.rich_ui import rich_reply


@app.on_message(filters.command(["logger"]) & SUDOERS)
@language
async def logger(client, message, _):
    usage = _["log_1"]
    if len(message.command) != 2:
        return await rich_reply(message, usage)
    state = message.text.split(None, 1)[1].strip().lower()
    if state == "enable":
        await add_on(2)
        await rich_reply(message, _["log_2"])
    elif state == "disable":
        await add_off(2)
        await rich_reply(message, _["log_3"])
    else:
        await rich_reply(message, usage)
