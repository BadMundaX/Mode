
import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from BADCLONE import LOGGER, app, userbot
from BADCLONE.core.call import Bad
from BADCLONE.misc import sudo
from BADCLONE.plugins import ALL_MODULES
from BADCLONE.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS
from BADCLONE.plugins.tools.clone import restart_bots


async def init():
    if not config.STRING1:
        LOGGER(__name__).error("sᴛʀɪɴɢ sᴇssɪᴏɴ ɴᴏᴛ ғɪʟʟᴇᴅ, ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ sᴇssɪᴏɴ.")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("BADCLONE.plugins" + all_module)
    LOGGER("BADCLONE.plugins").info("ᴀʟʟ ғᴇᴀᴛᴜʀᴇs ʟᴏᴀᴅᴇᴅ ʙᴀʙʏ🥳")
    await userbot.start()
    await Bad.start()
    try:
        await Bad.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("BADCLONE").error(
            "ᴘʟᴢ sᴛᴀʀᴛ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇᴄʜᴀᴛ\ᴄʜᴀɴɴᴇʟ \n\n ᴍᴜsɪᴄ ʙᴏᴛ sᴛᴏᴘ.."
        )
        exit()
    except:
        pass
    await Bad.decorators()
    await restart_bots()
    LOGGER("BADCLONE").info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ☠︎︎ᴍᴀᴅᴇ ʙʏ ʙᴀᴅ ᴍᴜɴᴅᴀ☠︎︎\n╚═════ஜ۩۞۩ஜ════╝"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("BADCLONE").info("sᴛᴏᴘ ᴍᴜsɪᴄ ʙᴏᴛ")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
    
