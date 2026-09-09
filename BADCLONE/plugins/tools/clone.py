import re
import logging
import asyncio
import importlib
from sys import argv
from pyrogram import idle
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import (
    AccessTokenExpired,
    AccessTokenInvalid,
)
from BADCLONE.utils.database import get_assistant
from config import API_ID, API_HASH
from BADCLONE import app
from config import OWNER_ID
from BADCLONE.misc import SUDOERS
from BADCLONE.utils.database import get_assistant, clonebotdb
from BADCLONE.utils.database.clonedb import has_user_cloned_any_bot
from config import LOGGER_ID, CLONE_LOGGER
import requests
from BADCLONE.utils.decorators.language import language

from datetime import datetime
CLONES = set()

C_BOT_DESC = "Wᴀɴᴛ ᴀ ʙᴏᴛ ʟɪᴋᴇ ᴛʜɪs? Cʟᴏɴᴇ ɪᴛ ɴᴏᴡ! ✅\n\nVɪsɪᴛ: @Gaana_MusicBot ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ!\n\n - Uᴘᴅᴀᴛᴇ: @PBX_CHAT\n - Sᴜᴘᴘᴏʀᴛ: @PBX_UPDATE"

C_BOT_COMMANDS = [
                {"command": "/start", "description": "sᴛᴀʀᴛs ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ"},
                {"command": "/help", "description": "ɢᴇᴛ ʜᴇʟᴩ ᴍᴇɴᴜ ᴡɪᴛʜ ᴇxᴩʟᴀɴᴀᴛɪᴏɴ ᴏғ ᴄᴏᴍᴍᴀɴᴅs."},
                {"command": "/play", "description": "sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴛʀᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ."},
                {"command": "/pause", "description": "ᴩᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."},
                {"command": "/resume", "description": "ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ."},
                {"command": "/skip", "description": "ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛ sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ."},
                {"command": "/end", "description": "ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ᴇɴᴅ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."},
                {"command": "/ping", "description": "ᴛʜᴇ ᴩɪɴɢ ᴀɴᴅ sʏsᴛᴇᴍ sᴛᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ."},
                {"command": "/id", "description": "ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ɢʀᴏᴜᴘ ɪᴅ. ɪғ ᴜsᴇᴅ ʙʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ɢᴇᴛs ᴛʜᴀᴛ ᴜsᴇʀ's ɪᴅ."}

            ]


@app.on_message(filters.command("clone"))
@language
async def clone_txt(client, message, _):
    userbot = await get_assistant(message.chat.id)

    # check user has already clone bot ? -------
    userid = message.from_user.id
    has_already_cbot = await has_user_cloned_any_bot(userid)

    if has_already_cbot:
        if message.from_user.id != OWNER_ID:
            return await message.reply_text(_["C_B_H_0"])
    else:
        pass
    
    # check user has already clone bot ? -------

    if len(message.command) > 1:
        bot_token = message.text.split("/clone", 1)[1].strip()
        mi = await message.reply_text(_["C_B_H_2"])
        try:
            ai = Client(
                bot_token,
                API_ID,
                API_HASH,
                bot_token=bot_token,
                plugins=dict(root="BADCLONE.cplugin"), 
            )
            await ai.start()
            bot = await ai.get_me()
            bot_users = await ai.get_users(bot.username)
            bot_id = bot_users.id
            c_b_owner_fname = message.from_user.first_name
            c_bot_owner = message.from_user.id

        except (AccessTokenExpired, AccessTokenInvalid):
            await mi.edit_text(_["C_B_H_3"])
            return
        except Exception as e:
            if "database is locked" in str(e).lower():
                await message.reply_text(_["C_B_H_4"])
            else:
                await mi.edit_text(f"An error occurred: {str(e)}")
            return

        # Proceed with the cloning process
        await mi.edit_text(_["C_B_H_5"])
        try:

            await app.send_message(
                CLONE_LOGGER, f"**#NewClonedBot**\n\n**Bᴏᴛ:- {bot.mention}**\n**Usᴇʀɴᴀᴍᴇ:** @{bot.username}\n**Bᴏᴛ ID :** `{bot_id}`\n\n**Oᴡɴᴇʀ : ** [{c_b_owner_fname}](tg://user?id={c_bot_owner})"
            )
            await userbot.send_message(bot.username, "/start")

            details = {
                "bot_id": bot.id,
                "is_bot": True,
                "user_id": message.from_user.id,
                "name": bot.first_name,
                "token": bot_token,
                "username": bot.username,
                "channel": "PBX_UPDATE",
                "support": "PBX_CHAT",
                "premium" : False,
                "Date" : False,
            }
            clonebotdb.insert_one(details)
            CLONES.add(bot.id)

            #set bot info ----------------------------
            def set_bot_commands():
                url = f"https://api.telegram.org/bot{bot_token}/setMyCommands"
                
                params = {"commands": C_BOT_COMMANDS}
                response = requests.post(url, json=params)
                print(response.json())

            set_bot_commands()

            # Set bot's "Description" AutoMatically On Every Restart
            def set_bot_desc():
                url = f"https://api.telegram.org/bot{bot_token}/setMyDescription"
                params = {"description": C_BOT_DESC}
                response = requests.post(url, data=params)
                if response.status_code == 200:
                    logging.info(f"Successfully updated Description for bot: {bot_token}")
                else:
                    logging.error(f"Failed to update Description: {response.text}")

            set_bot_desc()

            #set bot info ----------------------------

            await mi.edit_text(_["C_B_H_6"].format(bot.username))
        except BaseException as e:
            logging.exception("Error while cloning bot.")
            await mi.edit_text(
                f"⚠️ <b>ᴇʀʀᴏʀ:</b>\n\n<code>{e}</code>\n\n**ᴋɪɴᴅʟʏ ғᴏᴡᴀʀᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ @PBX_CHAT ᴛᴏ ɢᴇᴛ ᴀssɪsᴛᴀɴᴄᴇ**"
            )
    else:
        await message.reply_text(_["C_B_H_1"])


@app.on_message(
    filters.command(
        [
            "delbot",
            "rmbot",
            "delcloned",
            "delclone",
            "deleteclone",
            "removeclone",
            "cancelclone",
        ]
    )
)
@language
async def delete_cloned_bot(client, message, _):
    try:
        if len(message.command) < 2:
            await message.reply_text(_["C_B_H_8"])
            return

        bot_token = " ".join(message.command[1:])
        await message.reply_text(_["C_B_H_9"])

        cloned_bot = clonebotdb.find_one({"token": bot_token})
        if cloned_bot:
            clonebotdb.delete_one({"token": bot_token})
            CLONES.remove(cloned_bot["bot_id"])
            await message.reply_text(_["C_B_H_10"])
            await app.send_message(
                CLONE_LOGGER, f"**#ClonedBotRemove**\n\n**Bᴏᴛ Tᴏᴋᴇɴ:- `{bot_token}`"
            )
            # await restart_bots()
            # Call restart function here after successful deletion
        else:
            await message.reply_text(_["C_B_H_11"])
    except Exception as e:
        await message.reply_text(_["C_B_H_12"])
        await app.send_message(
                CLONE_LOGGER, f"**#ClonedBotRemove**\n\n**Bᴏᴛ Tᴏᴋᴇɴ:- `{bot_token}`"
            )
        logging.exception(e)


async def restart_bots():
    global CLONES
    try:
        logging.info("Restarting all cloned bots........")
        bots = list(clonebotdb.find())
        for bot in bots:
            bot_token = bot["token"]

            # Check if the bot token is valid
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            response = requests.get(url)
            if response.status_code != 200:
                logging.error(f"Invalid or expired token for bot: {bot_token}")
                clonebotdb.delete_one({"token": bot_token})
                continue  # Skip this bot and move to the next one

            ai = Client(
                f"{bot_token}",
                API_ID,
                API_HASH,
                bot_token=bot_token,
                plugins=dict(root="BADCLONE.cplugin"),
            )
            await ai.start()

            # Set bot's "Description" AutoMatically On Every Restart
            def set_bot_desc():
                url = f"https://api.telegram.org/bot{bot_token}/setMyDescription"
                params = {"description": C_BOT_DESC}
                response = requests.post(url, data=params)
                if response.status_code == 200:
                    logging.info(f"Successfully updated Description for bot: {bot_token}")
                else:
                    logging.error(f"Failed to update Description: {response.text}")

            # set_bot_desc()

            bot = await ai.get_me()
            if bot.id not in CLONES:
                try:
                    CLONES.add(bot.id)
                except Exception:
                    pass
            await asyncio.sleep(5)

        await app.send_message(
                CLONE_LOGGER, f"All Cloned Bots Started !"
            )
    except Exception as e:
        logging.exception("Error while restarting bots.")


@app.on_message(filters.command("clonedinfo") & filters.user(OWNER_ID))
@language
async def list_cloned_bots_info(client, message, _):
    try:
        cloned_bots = list(clonebotdb.find())
        if not cloned_bots:
            await message.reply_text(_["C_B_H_13"])
            return

        total_clones = len(cloned_bots)
        text = f"**Tᴏᴛᴀʟ Cʟᴏɴᴇᴅ Bᴏᴛs: {total_clones}**\n\n"

        for bot in cloned_bots:
            text += f"**Bᴏᴛ ID:** `{bot['bot_id']}`\n"
            text += f"**Bᴏᴛ Nᴀᴍᴇs:** {bot['name']}\n"
            text += f"**Bᴏᴛ Usᴇʀɴᴀᴍᴇ:** @{bot['username']}\n"
            text += f"**Bᴏᴛ Tᴏᴋᴇɴ:** `{bot['token']}`\n\n"

        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while listing cloned bots.")


@app.on_message(filters.command("delallclone") & filters.user(OWNER_ID))
@language
async def delete_all_cloned_bots(client, message, _):
    try:
        await message.reply_text(_["C_B_H_14"])

        # Delete all cloned bots from the database
        clonebotdb.delete_many({})

        # Clear the CLONES set
        CLONES.clear()

        await message.reply_text(_["C_B_H_15"])
    except Exception as e:
        await message.reply_text("An error occurred while deleting all cloned bots.")
        logging.exception(e)


@app.on_message(filters.command(["mybot", "mybots"], prefixes=["/", "."]))
@language
async def my_cloned_bots(client, message, _):
    try:
        user_id = message.from_user.id
        cloned_bots = list(clonebotdb.find({"user_id": user_id}))
        
        if not cloned_bots:
            await message.reply_text(_["C_B_H_16"])
            return
        
        total_clones = len(cloned_bots)
        text = f"**Yᴏᴜʀ Cʟᴏɴᴇᴅ Bᴏᴛs: {total_clones}**\n\n"
        
        for bot in cloned_bots:
            text += f"**Bᴏᴛ Nᴀᴍᴇs:** {bot['name']}\n"
            text += f"**Bᴏᴛ Usᴇʀɴᴀᴍᴇ:** @{bot['username']}\n\n"
        
        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while fetching your cloned bots.")

# Premium Users ------------------------

@app.on_message(filters.command("addpremium") & filters.user(OWNER_ID))
@language
async def add_premium(client, message, _):
    if len(message.command) < 2:
        await message.reply_text("Please provide the bot ID.")
        return
    
    bot_id = int(message.command[1])
    result = clonebotdb.update_one(
        {"bot_id": bot_id},
        {"$set": {"premium": True, "Date": datetime.now().strftime("%d-%m-%Y")}}
    )
    
    if result.matched_count:
        await message.reply_text(f"Premium access granted to bot ID {bot_id}.")
    else:
        await message.reply_text("Bot ID not found in the database.")


@app.on_message(filters.command("removepremium") & filters.user(OWNER_ID))
@language
async def remove_premium(client, message, _):
    if len(message.command) < 2:
        await message.reply_text("Please provide the bot ID.")
        return
    
    bot_id = int(message.command[1])
    result = clonebotdb.update_one(
        {"bot_id": bot_id},
        {"$set": {"premium": False}}
    )
    
    if result.matched_count:
        await message.reply_text(f"Premium access removed for bot ID {bot_id}.")
    else:
        await message.reply_text("Bot ID not found in the database.")


@app.on_message(filters.command("premiumbots") & filters.user(OWNER_ID))
@language
async def premium_bots(client, message, _):
    # Find all bots with premium set to True
    premium_bots = list(clonebotdb.find({"premium": True}))
    
    # If no premium bots exist
    if len(premium_bots) == 0:
        await message.reply_text("Nᴏ ᴘʀᴇᴍɪᴜᴍ ʙᴏᴛs ғᴏᴜɴᴅ.")
        return
    
    # Collecting and sending bot information
    reply_text = "Lɪsᴛ ᴏғ Pʀᴇᴍɪᴜᴍ Bᴏᴛs:\n\n"
    
    for bot in premium_bots:
        # Fetch the bot owner's details using their user_id
        owner = await client.get_users(bot['user_id'])
        
        # Prepare the profile link and first name
        owner_name = owner.first_name
        owner_profile_link = f"tg://user?id={bot['user_id']}"
        
        bot_info = f"**Bᴏᴛ Nᴀᴍᴇ**: {bot['name']}\n" \
                   f"**Bot ID**: `{bot['bot_id']}`\n" \
                   f"**Usᴇʀɴᴀᴍᴇ**: @{bot['username']}\n" \
                   f"**Pʀᴇᴍɪᴜᴍ Sɪɴᴄᴇ**: `{bot['Date']}`\n" \
                   f"**Oᴡɴᴇʀ**: [{owner_name}]({owner_profile_link})\n\n"
        
        reply_text += bot_info
    
    await message.reply_text(reply_text)

# Premium Users ------------------------


@app.on_message(filters.command("cloned") & SUDOERS)
@language
async def list_cloned_bots(client, message, _):
    try:
        cloned_bots = list(clonebotdb.find())
        if not cloned_bots:
            await message.reply_text("No bots have been cloned yet.")
            return

        total_clones = len(cloned_bots)
        text = f"**Tᴏᴛᴀʟ Cʟᴏɴᴇᴅ Bᴏᴛs: `{total_clones}`**\n\n"

        for bot in cloned_bots:

            # Fetch the bot owner's details using their user_id
            owner = await client.get_users(bot['user_id'])
            
            # Prepare the profile link and first name
            owner_name = owner.first_name
            owner_profile_link = f"tg://user?id={bot['user_id']}"

            text += f"**Bᴏᴛ ID:** `{bot['bot_id']}`\n"
            text += f"**Bᴏᴛ Nᴀᴍᴇ:** {bot['name']}\n"
            text += f"**Bᴏᴛ Usᴇʀɴᴀᴍᴇ:** @{bot['username']}\n"
            text += f"**Oᴡɴᴇʀ:** [{owner_name}]({owner_profile_link})\n\n"

        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while listing cloned bots.")


#total clone
@app.on_message(filters.command("totalbots") & SUDOERS)
@language
async def list_cloned_bots(client, message, _):
    try:
        cloned_bots = list(clonebotdb.find())
        if not cloned_bots:
            await message.reply_text("No bots have been cloned yet.")
            return

        total_clones = len(cloned_bots)
        text = f"**Tᴏᴛᴀʟ Cʟᴏɴᴇᴅ Bᴏᴛs: `{total_clones}`**\n\n"         

        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while listing cloned bots.")
