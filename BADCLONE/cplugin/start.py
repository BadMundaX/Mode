import time
import random
from pyrogram import filters, Client
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch
from PROMUSIC import app

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import config
# from PROMUSIC import app
from PROMUSIC.misc import _boot_
from PROMUSIC.plugins.sudo.sudoers import sudoers_list
from PROMUSIC.utils.database import get_served_chats, get_served_users, get_sudoers
from PROMUSIC.utils import bot_sys_stats
from PROMUSIC.utils.database import (
    add_served_chat_clone,
    add_served_user_clone,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from PROMUSIC.utils.decorators.language import LanguageStart
from PROMUSIC.utils.formatters import get_readable_time
from PROMUSIC.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS, OWNER_ID
from strings import get_string

from PROMUSIC.utils.database.clonedb import get_owner_id_from_db, get_cloned_support_chat, get_cloned_support_channel

#--------------------------

NEXI_VID = [
"https://telegra.ph/file/1a3c152717eb9d2e94dc2.mp4",
"https://graph.org/file/ba7699c28dab379b518ca.mp4",
"https://graph.org/file/83ebf52e8bbf138620de7.mp4",
"https://graph.org/file/82fd67aa56eb1b299e08d.mp4",
"https://graph.org/file/318eac81e3d4667edcb77.mp4",
"https://graph.org/file/7c1aa59649fbf3ab422da.mp4",
"https://graph.org/file/2a7f857f31b32766ac6fc.mp4",

]

YUMI_PICS = [
"https://graph.org/file/f76fd86d1936d45a63c64.jpg",
"https://graph.org/file/69ba894371860cd22d92e.jpg",
"https://graph.org/file/67fde88d8c3aa8327d363.jpg",
"https://graph.org/file/3a400f1f32fc381913061.jpg",
"https://graph.org/file/a0893f3a1e6777f6de821.jpg",
"https://graph.org/file/5a285fc0124657c7b7a0b.jpg",
"https://graph.org/file/25e215c4602b241b66829.jpg",
"https://graph.org/file/a13e9733afdad69720d67.jpg",
"https://graph.org/file/692e89f8fe20554e7a139.jpg",
"https://graph.org/file/db277a7810a3f65d92f22.jpg",
"https://graph.org/file/a00f89c5aa75735896e0f.jpg",
"https://graph.org/file/f86b71018196c5cfe7344.jpg",
"https://graph.org/file/a3db9af88f25bb1b99325.jpg",
"https://graph.org/file/5b344a55f3d5199b63fa5.jpg",
"https://graph.org/file/84de4b440300297a8ecb3.jpg",
"https://graph.org/file/84e84ff778b045879d24f.jpg",
"https://graph.org/file/a4a8f0e5c0e6b18249ffc.jpg",
"https://graph.org/file/ed92cada78099c9c3a4f7.jpg",
"https://graph.org/file/d6360613d0fa7a9d2f90b.jpg",
"https://graph.org/file/37248e7bdff70c662a702.jpg",
"https://graph.org/file/0bfe29d15e918917d1305.jpg",
"https://graph.org/file/16b1a2828cc507f8048bd.jpg",
"https://graph.org/file/e6b01f23f2871e128dad8.jpg",
"https://graph.org/file/cacbdddee77784d9ed2b7.jpg",
"https://graph.org/file/ddc5d6ec1c33276507b19.jpg",
"https://graph.org/file/39d7277189360d2c85b62.jpg",
"https://graph.org/file/5846b9214eaf12c3ed100.jpg",
"https://graph.org/file/ad4f9beb4d526e6615e18.jpg",
"https://graph.org/file/3514efaabe774e4f181f2.jpg",  
"https://graph.org/file/eaa3a2602e43844a488a5.jpg",
"https://graph.org/file/b129e98b6e5c4db81c15f.jpg",
"https://graph.org/file/3ccb86d7d62e8ee0a2e8b.jpg",
"https://graph.org/file/df11d8257613418142063.jpg",
"https://graph.org/file/9e23720fedc47259b6195.jpg",
"https://graph.org/file/826485f2d7db6f09db8ed.jpg",
"https://graph.org/file/ff3ad786da825b5205691.jpg",
"https://graph.org/file/52713c9fe9253ae668f13.jpg",
"https://graph.org/file/8f8516c86677a8c91bfb1.jpg",
"https://graph.org/file/6603c3740378d3f7187da.jpg",
"https://graph.org/file/66cb6ec40eea5c4670118.jpg",
"https://graph.org/file/2e3cf4327b169b981055e.jpg",   

]

@Client.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    a = await client.get_me()
    C_BOT_OWNER_ID = get_owner_id_from_db(a.id)

    #Cloned Bot Support Chat and channel
    C_BOT_SUPPORT_CHAT = await get_cloned_support_chat(a.id)
    C_SUPPORT_CHAT = f"https://t.me/{C_BOT_SUPPORT_CHAT}"
    C_BOT_SUPPORT_CHANNEL = await get_cloned_support_channel(a.id)
    C_SUPPORT_CHANNEL = f"https://t.me/{C_BOT_SUPPORT_CHANNEL}"

    #new ------
    # await add_served_user_clone(message.from_user.id)
    bot_id = a.id
    await add_served_user_clone(message.from_user.id, bot_id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_photo(
                random.choice(YUMI_PICS),
                caption=_["help_1"].format(C_SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)

            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, a.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=C_SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            await client.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
    
    else:
        out = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{a.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text=_["C_B_2"], user_id=C_BOT_OWNER_ID),
            InlineKeyboardButton(text=_["S_B_6"], url=C_SUPPORT_CHANNEL),
        ],
        [
            InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper"),
        ],
    ]
        
        app_name = app.name
        app_link = f"https://t.me/{app.username}"

        # out = private_panel(_)
        await message.reply_photo(
            random.choice(YUMI_PICS),
            caption=_["c_start_2"].format(message.from_user.mention, a.mention, app_name, app_link, app_name, app_link, C_SUPPORT_CHANNEL, C_SUPPORT_CHAT),
            reply_markup=InlineKeyboardMarkup(out),
        )


@Client.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    a = await client.get_me()
    #Cloned Bot Support Chat and channel
    C_BOT_SUPPORT_CHAT = await get_cloned_support_chat(a.id)
    C_SUPPORT_CHAT = f"https://t.me/{C_BOT_SUPPORT_CHAT}"
    C_BOT_SUPPORT_CHANNEL = await get_cloned_support_channel(a.id)
    C_SUPPORT_CHANNEL = f"https://t.me/{C_BOT_SUPPORT_CHANNEL}"
    # out = start_panel(_)
    out = [
                    [
                        InlineKeyboardButton(
                            text=_["S_B_1"], url=f"https://t.me/{a.username}?startgroup=true"
                        ),
                        InlineKeyboardButton(text=_["S_B_2"], url=C_SUPPORT_CHAT),
                    ],
                ]
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        random.choice(YUMI_PICS),
        caption=_["start_1"].format(a.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    # return await add_served_chat_clone(message.chat.id)
    bot_id = a.id
    return await add_served_chat_clone(message.chat.id, bot_id)