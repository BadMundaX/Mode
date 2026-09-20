import asyncio
from telegram import CallbackQuery
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from BADCLONE import YouTube, app
from BADCLONE.core.call import Bad, get_thumb_safe, send_now_playing
from BADCLONE.misc import SUDOERS, db
from BADCLONE.utils.database import (
    get_active_chats,
    get_lang,
    get_upvote_count,
    is_active_chat,
    is_music_playing,
    is_nonadmin_chat,
    music_off,
    music_on,
    set_loop,
)
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from BADCLONE.utils.database import get_assistant
from BADCLONE.utils.decorators.language import languageCB
from BADCLONE.utils.formatters import seconds_to_min
from BADCLONE.utils.inline import close_markup, stream_markup, stream_markup_timer
from BADCLONE.utils.stream.autoclear import auto_clean
from BADCLONE import app
from BADCLONE.utils.stream.autoplay import (
    autoplay_next,
    toggle_autoplay,
    user_can_control,
)
from BADCLONE.utils.stream.thumbnail import (
    toggle_thumbnail_status,
    get_thumbnail_status,
)

from BADCLONE.utils.inline.play import (
    stream_markup,
)
import config
from config import (
    BANNED_USERS,
    SOUNCLOUD_IMG_URL,
    STREAM_IMG_URL,
    TELEGRAM_AUDIO_URL,
    TELEGRAM_VIDEO_URL,
    adminlist,
    confirmer,
    votemode,
)
from strings import get_string

checker = {}
upvoters = {}


def _player_markup(_, chat_id: int, message_id: int):
    """Keyboard for the player message, so a button press refreshes it instantly."""
    playing = db.get(chat_id)
    if playing:
        cur = playing[0]
        mystic = cur.get("mystic")
        try:
            if mystic and mystic.id == message_id and int(cur.get("seconds", 0)) > 0:
                return stream_markup_timer(
                    _, chat_id, seconds_to_min(cur["played"]), cur["dur"]
                )
        except Exception:
            pass
    return stream_markup(_, chat_id)


async def _refresh_player_buttons(query, _, chat_id: int):
    try:
        markup = InlineKeyboardMarkup(_player_markup(_, chat_id, query.message.id))
        await query.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass  # e.g. "message not modified" / message deleted


@app.on_callback_query(filters.regex("^THUMBTOGGLE") & ~BANNED_USERS)
@languageCB
async def thumbnail_toggle_callback(client, query: CallbackQuery, _):
    try:
        chat_id = int(query.data.split("|")[1])
    except Exception:
        return await query.answer()

    new_status = toggle_thumbnail_status(chat_id)

    status_text = (
        "🖼 ᴛʜᴜᴍʙɴᴀɪʟ ᴇɴᴀʙʟᴇᴅ ғᴏʀ ɴᴇxᴛ sᴏɴɢs"
        if new_status == "on"
        else "🖼 ᴛʜᴜᴍʙɴᴀɪʟ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ɴᴇxᴛ sᴏɴɢs"
    )
    try:
        await query.answer(status_text, show_alert=False)
    except Exception:
        pass
    await _refresh_player_buttons(query, _, chat_id)


@app.on_callback_query(filters.regex("^autoplay_from_player") & ~BANNED_USERS)
@languageCB
async def autoplay_toggle_callback(client, query: CallbackQuery, _):
    try:
        chat_id = int(query.data.split("|")[1])
    except Exception:
        return await query.answer()

    if not await user_can_control(query.from_user.id, query.message.chat.id):
        return await query.answer(_["admin_14"], show_alert=True)

    enabled = await toggle_autoplay(chat_id)
    status_text = (
        "♬ ᴀᴜᴛᴏᴘʟᴀʏ ᴏɴ — ʀᴇʟᴀᴛᴇᴅ sᴏɴɢs ᴡɪʟʟ ᴋᴇᴇᴘ ᴘʟᴀʏɪɴɢ"
        if enabled
        else "♬ ᴀᴜᴛᴏᴘʟᴀʏ ᴏғғ"
    )
    try:
        await query.answer(status_text, show_alert=False)
    except Exception:
        pass
    await _refresh_player_buttons(query, _, chat_id)


@app.on_callback_query(filters.regex("unban_assistant"))
async def unban_assistant(_, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    userbot = await get_assistant(chat_id)
    
    try:
        await app.unban_chat_member(chat_id, userbot.id)
        await callback.answer("My assistant id unbanned successfully\n\nNow you can play song🔉\n\nThank you", show_alert=True)
    except Exception as e:
        await callback.answer(f"Failed to unban my assistant because i don't have ban power\n\nPlease provide me ban power so that i can unban my assistant id", show_alert=True)


@app.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    command, chat = callback_request.split("|")
    if "_" in str(chat):
        bet = chat.split("_")
        chat = bet[0]
        counter = bet[1]
    chat_id = int(chat)
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)
    mention = CallbackQuery.from_user.mention
    if command == "UpVote":
        if chat_id not in votemode:
            votemode[chat_id] = {}
        if chat_id not in upvoters:
            upvoters[chat_id] = {}

        voters = (upvoters[chat_id]).get(CallbackQuery.message.id)
        if not voters:
            upvoters[chat_id][CallbackQuery.message.id] = []

        vote = (votemode[chat_id]).get(CallbackQuery.message.id)
        if not vote:
            votemode[chat_id][CallbackQuery.message.id] = 0

        if CallbackQuery.from_user.id in upvoters[chat_id][CallbackQuery.message.id]:
            (upvoters[chat_id][CallbackQuery.message.id]).remove(
                CallbackQuery.from_user.id
            )
            votemode[chat_id][CallbackQuery.message.id] -= 1
        else:
            (upvoters[chat_id][CallbackQuery.message.id]).append(
                CallbackQuery.from_user.id
            )
            votemode[chat_id][CallbackQuery.message.id] += 1
        upvote = await get_upvote_count(chat_id)
        get_upvotes = int(votemode[chat_id][CallbackQuery.message.id])
        if get_upvotes >= upvote:
            votemode[chat_id][CallbackQuery.message.id] = upvote
            try:
                exists = confirmer[chat_id][CallbackQuery.message.id]
                current = db[chat_id][0]
            except:
                return await CallbackQuery.edit_message_text(f"ғᴀɪʟᴇᴅ.")
            try:
                if current["vidid"] != exists["vidid"]:
                    return await CallbackQuery.edit_message.text(_["admin_35"])
                if current["file"] != exists["file"]:
                    return await CallbackQuery.edit_message.text(_["admin_35"])
            except:
                return await CallbackQuery.edit_message_text(_["admin_36"])
            try:
                await CallbackQuery.edit_message_text(_["admin_37"].format(upvote))
            except:
                pass
            command = counter
            mention = "ᴜᴘᴠᴏᴛᴇs"
        else:
            if (
                CallbackQuery.from_user.id
                in upvoters[chat_id][CallbackQuery.message.id]
            ):
                await CallbackQuery.answer(_["admin_38"], show_alert=True)
            else:
                await CallbackQuery.answer(_["admin_39"], show_alert=True)
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"👍 {get_upvotes}",
                            callback_data=f"ADMIN  UpVote|{chat_id}_{counter}",
                        )
                    ]
                ]
            )
            await CallbackQuery.answer(_["admin_40"], show_alert=True)
            return await CallbackQuery.edit_message_reply_markup(reply_markup=upl)
    else:
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            if CallbackQuery.from_user.id not in SUDOERS:
                admins = adminlist.get(CallbackQuery.message.chat.id)
                if not admins:
                    return await CallbackQuery.answer(_["admin_13"], show_alert=True)
                else:
                    if CallbackQuery.from_user.id not in admins:
                        return await CallbackQuery.answer(
                            _["admin_14"], show_alert=True
                        )
    if command == "Pause":
        if not await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_1"], show_alert=True)
        await CallbackQuery.answer()
        await music_off(chat_id)
        await Bad.pause_stream(chat_id)
        await CallbackQuery.message.reply_text(
            _["admin_2"].format(mention), reply_markup=close_markup(_)
        )
    elif command == "Resume":
        if await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_3"], show_alert=True)
        await CallbackQuery.answer()
        await music_on(chat_id)
        await Bad.resume_stream(chat_id)
        await CallbackQuery.message.reply_text(
            _["admin_4"].format(mention), reply_markup=close_markup(_)
        )
    elif command == "Stop" or command == "End":
        await CallbackQuery.answer()
        await Bad.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        await CallbackQuery.message.reply_text(
            _["admin_5"].format(mention), reply_markup=close_markup(_)
        )
        await CallbackQuery.message.delete()
    elif command == "Skip" or command == "Replay":
        check = db.get(chat_id)
        if command == "Skip":
            txt = f"{mention}\n Skiped"
            popped = None
            try:
                popped = check.pop(0)
                if popped:
                    await auto_clean(popped)
                if not check and not await autoplay_next(chat_id, popped):
                    await CallbackQuery.edit_message_text(
                        f"{mention}\n Skiped"
                    )
                    await CallbackQuery.message.reply_text(
                        text=_["admin_6"].format(
                            mention, CallbackQuery.message.chat.title
                        ),
                        reply_markup=close_markup(_),
                    )
                    try:
                        return await Bad.stop_stream(chat_id)
                    except:
                        return
                check = db.get(chat_id)
            except:
                try:
                    await CallbackQuery.edit_message_text(
                        f"{mention}\n Skiped"
                    )
                    await CallbackQuery.message.reply_text(
                        text=_["admin_6"].format(
                            mention, CallbackQuery.message.chat.title
                        ),
                        reply_markup=close_markup(_),
                    )
                    return await Bad.stop_stream(chat_id)
                except:
                    return
        else:
            txt = f"{mention}\n playing"
        await CallbackQuery.answer()
        queued = check[0]["file"]
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        duration = check[0]["dur"]
        streamtype = check[0]["streamtype"]
        videoid = check[0]["vidid"]
        thumb_on = get_thumbnail_status(chat_id) == "on"
        status = True if str(streamtype) == "video" else None
        db[chat_id][0]["played"] = 0
        exis = (check[0]).get("old_dur")
        if exis:
            db[chat_id][0]["dur"] = exis
            db[chat_id][0]["seconds"] = check[0]["old_second"]
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0
        if "live_" in queued:
            n, link = await YouTube.video(videoid, True)
            if n == 0:
                return await CallbackQuery.message.reply_text(
                    text=_["admin_7"].format(title),
                    reply_markup=close_markup(_),
                )
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
            try:
                await Bad.skip_stream(chat_id, link, video=status, image=image)
            except:
                return await CallbackQuery.message.reply_text(_["call_6"])
            button = stream_markup(_, chat_id)
            run = await send_now_playing(
                CallbackQuery.message.chat.id,
                thumb_on,
                await get_thumb_safe(videoid) if thumb_on else None,
                _["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    title[:23],
                    duration,
                    user,
                ),
                button,
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
            await CallbackQuery.edit_message_text(txt, reply_markup=close_markup(_))
        elif "vid_" in queued:
            mystic = await CallbackQuery.message.reply_text(
                _["call_7"], disable_web_page_preview=True
            )
            try:
                file_path, direct = await YouTube.download(
                    videoid,
                    mystic,
                    videoid=True,
                    video=status,
                )
            except:
                return await mystic.edit_text(_["call_6"])
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
            try:
                await Bad.skip_stream(chat_id, file_path, video=status, image=image)
            except:
                return await mystic.edit_text(_["call_6"])
            button = stream_markup(_, chat_id)
            run = await send_now_playing(
                CallbackQuery.message.chat.id,
                thumb_on,
                await get_thumb_safe(videoid) if thumb_on else None,
                _["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    title[:23],
                    duration,
                    user,
                ),
                button,
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
            await CallbackQuery.edit_message_text(txt, reply_markup=close_markup(_))
            await mystic.delete()
        elif "index_" in queued:
            try:
                await Bad.skip_stream(chat_id, videoid, video=status)
            except:
                return await CallbackQuery.message.reply_text(_["call_6"])
            button = stream_markup(_, chat_id)
            run = await send_now_playing(
                CallbackQuery.message.chat.id,
                thumb_on,
                STREAM_IMG_URL,
                _["stream_2"].format(user),
                button,
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
            await CallbackQuery.edit_message_text(txt, reply_markup=close_markup(_))
        else:
            if videoid == "telegram":
                image = None
            elif videoid == "soundcloud":
                image = None
            else:
                try:
                    image = await YouTube.thumbnail(videoid, True)
                except:
                    image = None
            try:
                await Bad.skip_stream(chat_id, queued, video=status, image=image)
            except:
                return await CallbackQuery.message.reply_text(_["call_6"])
            if videoid == "telegram":
                button = stream_markup(_, chat_id)
                run = await send_now_playing(
                    CallbackQuery.message.chat.id,
                    thumb_on,
                    TELEGRAM_AUDIO_URL
                    if str(streamtype) == "audio"
                    else TELEGRAM_VIDEO_URL,
                    _["stream_1"].format(
                        config.SUPPORT_CHAT, title[:23], duration, user
                    ),
                    button,
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif videoid == "soundcloud":
                button = stream_markup(_, chat_id)
                run = await send_now_playing(
                    CallbackQuery.message.chat.id,
                    thumb_on,
                    SOUNCLOUD_IMG_URL
                    if str(streamtype) == "audio"
                    else TELEGRAM_VIDEO_URL,
                    _["stream_1"].format(
                        config.SUPPORT_CHAT, title[:23], duration, user
                    ),
                    button,
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                button = stream_markup(_, chat_id)
                run = await send_now_playing(
                    CallbackQuery.message.chat.id,
                    thumb_on,
                    await get_thumb_safe(videoid) if thumb_on else None,
                    _["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        duration,
                        user,
                    ),
                    button,
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            await CallbackQuery.edit_message_text(txt, reply_markup=close_markup(_))


async def markup_timer():
    while not await asyncio.sleep(7):
        active_chats = await get_active_chats()
        for chat_id in active_chats:
            try:
                if not await is_music_playing(chat_id):
                    continue
                playing = db.get(chat_id)
                if not playing:
                    continue
                duration_seconds = int(playing[0]["seconds"])
                if duration_seconds == 0:
                    continue
                try:
                    mystic = playing[0]["mystic"]
                except:
                    continue
                try:
                    check = checker[chat_id][mystic.id]
                    if check is False:
                        continue
                except:
                    pass
                try:
                    language = await get_lang(chat_id)
                    _ = get_string(language)
                except:
                    _ = get_string("en")
                try:
                    buttons = stream_markup_timer(
                        _,
                        chat_id,
                        seconds_to_min(playing[0]["played"]),
                        playing[0]["dur"],
                    )
                    await mystic.edit_reply_markup(
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
                except:
                    continue
            except:
                continue


asyncio.create_task(markup_timer())
