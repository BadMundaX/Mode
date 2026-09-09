import os
import random
import string
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall
from BADCLONE.utils.database import get_assistant
import config
from BADCLONE import Carbon, JioSaavn, Telegram, YouTube, app
from BADCLONE.core.call import PRO
from BADCLONE.misc import SUDOERS
from BADCLONE.utils.inline import panel_markup_clone
from BADCLONE.utils import seconds_to_min, time_to_seconds
from BADCLONE.utils.channelplay import get_channeplayCB
from BADCLONE.utils.decorators.language import languageCB
from BADCLONE.utils.decorators.play import CPlayWrapper
from BADCLONE.utils.formatters import formats
from BADCLONE.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from BADCLONE.utils.database import (
    add_served_chat_clone,
    add_served_user_clone,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from BADCLONE.utils.logger import play_logs
from config import BANNED_USERS, lyrical
from time import time
from BADCLONE.utils.extraction import extract_user

user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5


@Client.on_message(
    filters.command(
        ["play","vplay","cplay","cvplay","playforce","vplayforce","cplayforce","cvplayforce"],
        prefixes=["/", "!", "%", "", ".", "@", "#"],
    )
    & filters.group
    & ~BANNED_USERS
)
@CPlayWrapper
async def play_commnd(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):
    cuser = await client.get_me()
    user_id = message.from_user.id
    current_time = time()
    last_message_time = user_last_message_time.get(user_id, 0)

    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_last_message_time[user_id] = current_time
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            hu = await message.reply_text(f"**{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ**")
            await asyncio.sleep(3)
            await hu.delete()
            return
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    bot_id = cuser.id
    await add_served_user_clone(message.chat.id, bot_id)
    mystic = await message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])
    plist_id = None
    slider = None
    plist_type = None
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    audio_telegram = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message else None
    )
    video_telegram = (
        (message.reply_to_message.video or message.reply_to_message.document)
        if message.reply_to_message else None
    )

    if audio_telegram:
        if audio_telegram.file_size > 104857600:
            return await mystic.edit_text(_["play_5"])
        if (audio_telegram.duration) > config.DURATION_LIMIT:
            return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, cuser.mention))
        file_path = await Telegram.get_filepath(audio=audio_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(audio_telegram, audio=True)
            dur = await Telegram.get_duration(audio_telegram, file_path)
            details = {"title": file_name, "link": message_link, "path": file_path, "dur": dur}
            try:
                await stream(client, _, mystic, user_id, details, chat_id, user_name, message.chat.id, streamtype="telegram", forceplay=fplay)
            except Exception as e:
                ex_type = type(e).__name__
                return await mystic.edit_text(e if ex_type == "AssistantErr" else _["general_2"].format(ex_type))
            return await mystic.delete()
        return

    elif video_telegram:
        if message.reply_to_message.document:
            try:
                ext = video_telegram.file_name.split(".")[-1]
                if ext.lower() not in formats:
                    return await mystic.edit_text(_["play_7"].format(f"{' | '.join(formats)}"))
            except:
                return await mystic.edit_text(_["play_7"].format(f"{' | '.join(formats)}"))
        if video_telegram.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
            return await mystic.edit_text(_["play_8"])
        file_path = await Telegram.get_filepath(video=video_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(video_telegram)
            dur = await Telegram.get_duration(video_telegram, file_path)
            details = {"title": file_name, "link": message_link, "path": file_path, "dur": dur}
            try:
                await stream(client, _, mystic, user_id, details, chat_id, user_name, message.chat.id, video=True, streamtype="telegram", forceplay=fplay)
            except Exception as e:
                ex_type = type(e).__name__
                return await mystic.edit_text(e if ex_type == "AssistantErr" else _["general_2"].format(ex_type))
            return await mystic.delete()
        return

    elif url:
        if await JioSaavn.valid(url):
            if await JioSaavn.valid_playlist(url):
                try:
                    details, plist_id = await JioSaavn.playlist(url)
                except Exception as e:
                    print(e)
                    return await mystic.edit_text(_["general_2"].format(type(e).__name__))
                streamtype = "jiosaavn_playlist"
                plist_type = "jiosaavn"
                img = config.PLAYLIST_IMG_URL
                cap = _["play_10"].format(cuser.mention, message.from_user.mention)
            elif await JioSaavn.valid_album(url):
                try:
                    details, plist_id = await JioSaavn.album(url)
                except Exception as e:
                    print(e)
                    return await mystic.edit_text(_["general_2"].format(type(e).__name__))
                streamtype = "jiosaavn_playlist"
                plist_type = "jiosaavn"
                img = config.PLAYLIST_IMG_URL
                cap = _["play_10"].format(cuser.mention, message.from_user.mention)
            else:
                try:
                    details, track_id = await JioSaavn.track(url)
                except Exception as e:
                    print(e)
                    return await mystic.edit_text(_["general_2"].format(type(e).__name__))
                streamtype = "jiosaavn"
                img = details.get("thumb", config.YOUTUBE_IMG_URL)
                cap = _["play_10"].format(details["title"], details["duration_min"])
        else:
            try:
                await PRO.stream_call(url)
            except NoActiveGroupCall:
                await mystic.edit_text(_["black_9"])
                return await app.send_message(chat_id=config.CLONE_LOGGER, text=_["play_17"])
            except Exception as e:
                if "phone.CreateGroupCall" in str(e):
                    await mystic.edit_text(_["black_9"])
                    return await app.send_message(chat_id=config.CLONE_LOGGER, text=_["play_17"])
                else:
                    print(e)
                    return await mystic.edit_text(_["general_2"].format(type(e).__name__))
            await mystic.edit_text(_["str_2"])
            try:
                await stream(client, _, mystic, message.from_user.id, url, chat_id, message.from_user.first_name, message.chat.id, video=video, streamtype="index", forceplay=fplay)
            except Exception as e:
                ex_type = type(e).__name__
                return await mystic.edit_text(e if ex_type == "AssistantErr" else _["general_2"].format(ex_type))
            return await play_logs(message, streamtype="M3u8 or Index Link")

    else:
        if len(message.command) < 2:
            buttons = botplaylist_markup(_)
            return await mystic.edit_text(_["play_18"], reply_markup=InlineKeyboardMarkup(buttons))
        slider = True
        query = message.text.split(None, 1)[1]
        if "-v" in query:
            query = query.replace("-v", "")
        try:
            details, track_id = await JioSaavn.track_by_query(query)
        except Exception as e:
            print(e)
            return await mystic.edit_text(f"❌ Song not found on JioSaavn: {query}\n\nPlease try another song.")
        streamtype = "jiosaavn"

    if str(playmode) == "Direct":
        if not plist_type and details.get("duration_min"):
            duration_sec = time_to_seconds(details["duration_min"])
            if duration_sec > config.DURATION_LIMIT:
                return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, cuser.mention))
        try:
            await stream(client, _, mystic, user_id, details, chat_id, user_name, message.chat.id, video=video, streamtype=streamtype, forceplay=fplay)
        except Exception as e:
            ex_type = type(e).__name__
            return await mystic.edit_text(e if ex_type == "AssistantErr" else _["general_2"].format(ex_type))
        await mystic.delete()
        return await play_logs(message, streamtype=streamtype)
    else:
        if plist_type:
            ran_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
            lyrical[ran_hash] = plist_id
            buttons = playlist_markup(_, ran_hash, message.from_user.id, plist_type, "c" if channel else "g", "f" if fplay else "d")
            await mystic.delete()
            await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
            return await play_logs(message, streamtype="JioSaavn Playlist")
        else:
            if slider:
                buttons = slider_markup(_, track_id, message.from_user.id, query, 0, "c" if channel else "g", "f" if fplay else "d")
                await mystic.delete()
                await message.reply_photo(
                    photo=details.get("thumb", config.YOUTUBE_IMG_URL),
                    caption=_["play_10"].format(details["title"].title(), details["duration_min"]),
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                return await play_logs(message, streamtype="JioSaavn Search")
            else:
                buttons = track_markup(_, track_id, message.from_user.id, "c" if channel else "g", "f" if fplay else "d")
                await mystic.delete()
                await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
                return await play_logs(message, streamtype="JioSaavn URL")


@Client.on_callback_query(filters.regex("MusicStream") & ~BANNED_USERS)
@languageCB
async def play_music(client: Client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    vidid, user_id, mode, cplay, fplay = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
        except:
            return
    try:
        chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except:
        return
    user_name = CallbackQuery.from_user.first_name
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])
    try:
        details, track_id = await JioSaavn.track_by_query(vidid)
    except Exception as e:
        print(e)
        return await mystic.edit_text(_["general_2"].format(type(e).__name__))

    if details["duration_min"]:
        duration_sec = time_to_seconds(details["duration_min"])
        if duration_sec > config.DURATION_LIMIT:
            return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, CallbackQuery.from_user.mention))

    video = True if mode == "v" else None
    ffplay = True if fplay == "f" else None
    try:
        await stream(client, _, mystic, CallbackQuery.from_user.id, details, chat_id, user_name, CallbackQuery.message.chat.id, video, streamtype="jiosaavn", forceplay=ffplay)
    except Exception as e:
        ex_type = type(e).__name__
        return await mystic.edit_text(e if ex_type == "AssistantErr" else _["general_2"].format(ex_type))
    return await mystic.delete()


@Client.on_callback_query(filters.regex("BrandedmousAdmin") & ~BANNED_USERS)
async def Brandedmous_check(client: Client, CallbackQuery):
    try:
        await CallbackQuery.answer("» ʀᴇᴠᴇʀᴛ ʙᴀᴄᴋ ᴛᴏ ᴜsᴇʀ ᴀᴄᴄᴏᴜɴᴛ :\n\nᴏᴘᴇɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs.\n-> ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs\n-> ᴄʟɪᴄᴋ ᴏɴ ʏᴏᴜʀ ɴᴀᴍᴇ\n-> ᴜɴᴄʜᴇᴄᴋ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs.", show_alert=True)
    except:
        pass


@Client.on_callback_query(filters.regex("BrandedPlaylists") & ~BANNED_USERS)
@languageCB
async def play_playlists_command(client: Client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    (videoid, user_id, ptype, mode, cplay, fplay) = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
        except:
            return
    try:
        chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except:
        return
    user_name = CallbackQuery.from_user.first_name
    await CallbackQuery.message.delete()
    try:
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])
    videoid = lyrical.get(videoid)
    video = True if mode == "v" else None
    ffplay = True if fplay == "f" else None

    if ptype == "jiosaavn":
        try:
            result, _ = await JioSaavn.playlist(videoid)
        except Exception as e:
            print(e)
            return await mystic.edit_text(_["general_2"].format(type(e).__name__))
        stream_type = "jiosaavn_playlist"
    else:
        return await mystic.edit_text("❌ Playlist type supported nahi hai.")

    try:
        await stream(client, _, mystic, user_id, result, chat_id, user_name, CallbackQuery.message.chat.id, video, streamtype=stream_type, forceplay=ffplay)
    except Exception as e:
        ex_type = type(e).__name__
        return await mystic.edit_text(e if ex_type == "AssistantErr" else _["general_2"].format(ex_type))
    return await mystic.delete()


@Client.on_callback_query(filters.regex("slider") & ~BANNED_USERS)
@languageCB
async def slider_queries(client: Client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    (what, rtype, query, user_id, cplay, fplay) = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
        except:
            return
    what = str(what)
    rtype = int(rtype)
    if what == "F":
        if rtype == 9:
            query_type = 0
        else:
            query_type = int(rtype + 1)
        try:
            await CallbackQuery.answer(_["playcb_2"])
        except:
            pass
        title, duration_min, thumbnail, vidid = await JioSaavn.slider(query, query_type)
        buttons = slider_markup(_, vidid, user_id, query, query_type, cplay, fplay)
        med = InputMediaPhoto(media=thumbnail, caption=_["play_10"].format(title.title(), duration_min))


# ─────────────────────── STREAM ─────────────────────────

import os
from random import randint
from typing import Union
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup

import config
from BADCLONE import Carbon, YouTube
from BADCLONE.core.call import PRO
from BADCLONE.misc import db
from BADCLONE.utils.database import add_active_video_chat, is_active_chat
from BADCLONE.utils.exceptions import AssistantErr
from BADCLONE.utils.inline import (
    aq_markup,
    queuemarkup,
    close_markup,
    stream_markup,
    stream_markup2,
    panel_markup_4,
)
from BADCLONE.utils.pastebin import PROBin
from BADCLONE.utils.stream.queue import put_queue, put_queue_index
from youtubesearchpython.__future__ import VideosSearch
from BADCLONE.utils.database.clonedb import get_owner_id_from_db, get_cloned_support_chat, get_cloned_support_channel


async def stream(
    client, _, mystic, user_id, result, chat_id, user_name, original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    a = await client.get_me()
    C_BOT_OWNER_ID = get_owner_id_from_db(a.id)
    C_BOT_SUPPORT_CHAT = await get_cloned_support_chat(a.id)
    C_SUPPORT_CHAT = f"https://t.me/{C_BOT_SUPPORT_CHAT}"

    if not result:
        return
    if forceplay:
        await PRO.force_stop_stream(chat_id)

    # ── JioSaavn Playlist ──
    if streamtype in ("jiosaavn_playlist", "playlist"):
        msg = f"{_['play_19']}\n\n"
        count = 0
        for search in result:
            if int(count) == config.PLAYLIST_FETCH_LIMIT:
                continue
            try:
                title, duration_min, duration_sec, thumbnail, vidid = await JioSaavn.details(search)
            except:
                continue
            if str(duration_min) == "None" or duration_sec > config.DURATION_LIMIT:
                continue
            try:
                audio_url, is_direct = await JioSaavn.download(search)
            except:
                continue
            if await is_active_chat(chat_id):
                await put_queue(chat_id, original_chat_id, audio_url, title, duration_min, user_name, vidid, user_id, "audio")
                position = len(db.get(chat_id)) - 1
                count += 1
                msg += f"{count}. {title[:70]}\n"
                msg += f"{_['play_20']} {position}\n\n"
            else:
                if not forceplay:
                    db[chat_id] = []
                await PRO.join_call(chat_id, original_chat_id, audio_url, video=None, image=thumbnail)
                await put_queue(chat_id, original_chat_id, audio_url, title, duration_min, user_name, vidid, user_id, "audio", forceplay=forceplay)
                img = thumbnail or config.YOUTUBE_IMG_URL
                button = panel_markup_clone(_, vidid, chat_id)
                run = await client.send_photo(
                    original_chat_id, photo=img,
                    caption=_["stream_1"].format(C_SUPPORT_CHAT, title[:18], duration_min, user_name),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
        if count == 0:
            return
        link = await PROBin(msg)
        lines = msg.count("\n")
        car = os.linesep.join(msg.split(os.linesep)[:17]) if lines >= 17 else msg
        carbon = await Carbon.generate(car, randint(100, 10000000))
        upl = close_markup(_)
        return await client.send_photo(original_chat_id, photo=carbon, caption=_["play_21"].format(position, link), reply_markup=upl)

    # ── JioSaavn Single Track ──
    elif streamtype == "jiosaavn":
        link = result.get("link", "")
        vidid = result.get("vidid", "")
        title = result.get("title", "Unknown").title()
        duration_min = result.get("duration_min
