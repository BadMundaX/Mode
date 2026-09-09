import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram import filters, Client
from PROMUSIC import app
from PROMUSIC.misc import SUDOERS
from PROMUSIC.utils.decorators.language import language

from PROMUSIC.utils.database.clonedb import get_owner_id_from_db, get_cloned_support_chat, get_cloned_support_channel, check_bot_premium
from config import SUPPORT_CHAT, OWNER_ID

from PROMUSIC.utils.database import clonebotdb


#set clone bot support channel
@Client.on_message(filters.command("setchannel"))
@language
async def set_channel(client: Client, message: Message, _):

    bot = await client.get_me()
    bot_id = bot.id

    # premium check --------------
    # get owner info
    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))
    
    # Check if bot has premium
    premium_status = check_bot_premium(bot_id)
    if premium_status is None:
        return await message.reply_text(_["C_B_P_1"])
    elif not premium_status:
        if message.from_user.id != OWNER_ID:
            return await message.reply_text(_["C_B_P_2"])
        else:
            pass

    # premium check ---------------

    if len(message.command) != 2:
        await message.reply_text(_["C_P_I_2"])
        return
    
    channel = message.command[1]
    if channel.startswith("@"):
        channel = channel[1:] 

    result = clonebotdb.update_one({"bot_id": bot_id}, {"$set": {"channel": channel}})
    if result.modified_count > 0:
        await message.reply_text(_["C_P_I_4"].format(channel))
    else:
        await message.reply_text(_["C_P_I_6"])


#set clone bot support chat
@Client.on_message(filters.command("setsupport"))
@language
async def set_support(client: Client, message: Message, _):

    bot = await client.get_me()
    bot_id = bot.id

    # premium check --------------
    # get owner info
    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))
    
    # Check if bot has premium
    premium_status = check_bot_premium(bot_id)
    if premium_status is None:
        return await message.reply_text(_["C_B_P_1"])
    elif not premium_status:
        if message.from_user.id != OWNER_ID:
            return await message.reply_text(_["C_B_P_2"])
        else:
            pass

    # premium check ---------------

    if len(message.command) != 2:
        await message.reply_text(_["C_P_I_1"])
        return

    support = message.command[1]
    if support.startswith("@"):
        support = support[1:] 

    result = clonebotdb.update_one({"bot_id": bot_id}, {"$set": {"support": support}})
    if result.modified_count > 0:
        await message.reply_text(_["C_P_I_3"].format(support))
    else:
        await message.reply_text(_["C_P_I_5"])



#check bot info -------------------
@Client.on_message(filters.command("botinfo"))
@language
async def bot_info(client: Client, message: Message, _):

    bot = await client.get_me()
    bot_id = bot.id

    # premium check --------------
    # get owner info
    C_OWNER = get_owner_id_from_db(bot_id)
    OWNERS = [OWNER_ID, C_OWNER]

    if message.from_user.id not in OWNERS:
        return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))

    # premium check ---------------

    channel = await get_cloned_support_channel(bot_id)
    support = await get_cloned_support_chat(bot_id)
    premium_status = check_bot_premium(bot_id)
    if premium_status == True:
        bot_status = "Premium"
    else:
        bot_status = "Free"
    
     # Format and send the response
    await message.reply_text(
        f"**Bᴏᴛ Iɴғᴏ:**\n"
        f"➤ **Bᴏᴛ ID:** `{bot_id}`\n"
        f"➤ **Cʜᴀɴɴᴇʟ:** @{channel}\n"
        f"➤ **Sᴜᴘᴘᴏʀᴛ Cʜᴀᴛ:** @{support}\n"
        f"➤ **Bᴏᴛ Sᴛᴀᴛᴜs:** {bot_status}"
    )
