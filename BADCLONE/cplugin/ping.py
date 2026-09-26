import time
from datetime import datetime

import psutil
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import SUPPORT_CHAT, PING_IMG_URL
from .utils import StartTime
from BADCLONE.utils import get_readable_time
from BADCLONE.utils.database.clonedb import get_owner_id_from_db, get_cloned_support_chat, get_cloned_support_channel
import random
from pyrogram.enums import ButtonStyle
from BADCLONE.utils.rich_ui import rich_edit, rich_send, rich_img


def random_style():
    return random.choice([
        ButtonStyle.SUCCESS,
        ButtonStyle.DANGER,
        ButtonStyle.PRIMARY
    ])



@Client.on_message(filters.command("ping"))
async def ping_clone(client: Client, message: Message):
    bot = await client.get_me()

    C_BOT_OWNER_ID = await get_owner_id_from_db(bot.id)

    #Cloned Bot Support Chat and channel
    C_BOT_SUPPORT_CHAT = await get_cloned_support_chat(bot.id)
    C_SUPPORT_CHAT = f"https://t.me/{C_BOT_SUPPORT_CHAT}"
    C_BOT_SUPPORT_CHANNEL = await get_cloned_support_channel(bot.id)
    C_SUPPORT_CHANNEL = f"https://t.me/{C_BOT_SUPPORT_CHANNEL}"

    hmm = await rich_send(
        client, message.chat.id,
        f"❍ {bot.mention} ɪs ᴘɪɴɢɪɴɢ...",
    )
    upt = int(time.time() - StartTime)
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    start = datetime.now()
    resp = (datetime.now() - start).microseconds / 1000
    uptime = get_readable_time((upt))

    await rich_edit(hmm, 
        f"""➻ ᴘᴏɴɢ : `{resp}ᴍs`

{rich_img(PING_IMG_URL)}
<b><u>{bot.mention} sʏsᴛᴇᴍ sᴛᴀᴛs :</u></b>

๏ **ᴜᴘᴛɪᴍᴇ :** {uptime}
๏ **ʀᴀᴍ :** {mem}
๏ **ᴄᴘᴜ :** {cpu}
๏ **ᴅɪsᴋ :** {disk}""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("❄ sᴜᴘᴘᴏʀᴛ ❄", url=C_SUPPORT_CHAT, style=random_style()),
                    InlineKeyboardButton(
                        "✨ ᴀᴅᴅ ᴍᴇ ✨",
                        url=f"https://t.me/{bot.username}?startgroup=true",
                     style=random_style()),
                ],
            ]
        ),
    )
    
