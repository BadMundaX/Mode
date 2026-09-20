import math
import random
from config import SUPPORT_CHAT, OWNER_USERNAME
from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from BADCLONE import app
import config
from BADCLONE.utils.formatters import time_to_seconds
from BADCLONE.utils.stream.thumbnail import get_thumbnail_status
from BADCLONE.utils.database import get_autoplay_cached


def random_style():
    return random.choice([
        ButtonStyle.SUCCESS,
        ButtonStyle.DANGER,
        ButtonStyle.PRIMARY
    ])


def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style=random_style(),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style=random_style(),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}", style=ButtonStyle.DANGER,
            )
        ],
    ]
    return buttons


def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    ufff = math.floor(percentage)

    # Determine bar and color based on progress
    if 0 < ufff <= 10:
        bar = "┃┊♡—————————┊┃"
        bar_style = ButtonStyle.PRIMARY
    elif 10 < ufff < 20:
        bar = "┃┊—♡————————┊┃"
        bar_style = ButtonStyle.SUCCESS
    elif 20 <= ufff < 30:
        bar = "┃┊——♡———————┊┃"
        bar_style = ButtonStyle.DANGER
    elif 30 <= ufff < 40:
        bar = "┃┊———♡——————┊┃"
        bar_style = ButtonStyle.PRIMARY
    elif 40 <= ufff < 50:
        bar = "┃┊————♡—————┊┃"
        bar_style = ButtonStyle.SUCCESS
    elif 50 <= ufff < 60:
        bar = "┃┊—————♡————┊┃"
        bar_style = ButtonStyle.DANGER
    elif 60 <= ufff < 70:
        bar = "┃┊——————♡———┊┃"
        bar_style = ButtonStyle.PRIMARY
    elif 70 <= ufff < 80:
        bar = "┃┊———————♡——┊┃"
        bar_style = ButtonStyle.SUCCESS
    elif 80 <= ufff < 95:
        bar = "┃┊————————♡—┊┃"
        bar_style = ButtonStyle.DANGER
    else:
        bar = "┃┊—————————♡┊┃"
        bar_style = ButtonStyle.PRIMARY

    autoplay_status = get_autoplay_cached(chat_id)

    autoplay_text = "𝐀ᴜᴛᴏᴘʟᴀʏ | 𝐎‌ɴ" if autoplay_status else "𝐀ᴜᴛᴏᴘʟᴀʏ | 𝐎‌ғғ"
    autoplay_style = ButtonStyle.SUCCESS if autoplay_status else ButtonStyle.DANGER

    thumb_status = get_thumbnail_status(chat_id)

    thumb_text = (
        "𝐓‌ʜᴜᴍʙ | 𝐎‌ɴ"
        if thumb_status == "on"
        else "𝐓‌ʜᴜᴍʙ | 𝐎‌ғғ"
    )

    thumb_style = (
        ButtonStyle.SUCCESS
        if thumb_status == "on"
        else ButtonStyle.DANGER
    )
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
                style=bar_style,
            )
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=random_style()),
            #InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=random_style()),
        ],
        [
            InlineKeyboardButton(text=thumb_text, callback_data=f"THUMBTOGGLE|{chat_id}", style=thumb_style),
            InlineKeyboardButton(text=autoplay_text, callback_data=f"autoplay_from_player|{chat_id}", style=autoplay_style),
        ],
         [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=ButtonStyle.DANGER)],
    ]
    return buttons


def stream_markup(_, chat_id):
    autoplay_status = get_autoplay_cached(chat_id)

    autoplay_text = "𝐀ᴜᴛᴏᴘʟᴀʏ | 𝐎‌ɴ" if autoplay_status else "𝐀ᴜᴛᴏᴘʟᴀʏ | 𝐎‌ғғ"
    autoplay_style = ButtonStyle.SUCCESS if autoplay_status else ButtonStyle.DANGER

    thumb_status = get_thumbnail_status(chat_id)

    thumb_text = (
        "𝐓‌ʜᴜᴍʙ | 𝐎‌ɴ"
        if thumb_status == "on"
        else "𝐓‌ʜᴜᴍʙ | 𝐎‌ғғ"
    )

    thumb_style = (
        ButtonStyle.SUCCESS
        if thumb_status == "on"
        else ButtonStyle.DANGER
    )
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=random_style()),
            #InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=random_style()),
         ],
        [
            InlineKeyboardButton(text=thumb_text, callback_data=f"THUMBTOGGLE|{chat_id}", style=thumb_style),
            InlineKeyboardButton(text=autoplay_text, callback_data=f"autoplay_from_player|{chat_id}", style=autoplay_style),
        ],
        [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=ButtonStyle.DANGER)],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"BadPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}", style=random_style(),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"BadPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}", style=random_style(),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}", style=ButtonStyle.DANGER,
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}", style=random_style(),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}", style=ButtonStyle.DANGER,
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style=random_style(),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style=random_style(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}", style=random_style(),
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}", style=ButtonStyle.DANGER,
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}", style=random_style(),
            ),
        ],
    ]
    return buttons

## Telegram Markup

def telegram_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="Next",
                callback_data=f"PanelMarkup None|{chat_id}",
            ),
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


## Queue Markup


def queue_markup(_, videoid, chat_id):

    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(
                text="II ᴘᴀᴜsᴇ",
                callback_data=f"ADMIN Pause|{chat_id}",
            ),
            InlineKeyboardButton(text="▢ sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(
                text="sᴋɪᴘ ‣‣I", callback_data=f"ADMIN Skip|{chat_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"
            ),
            InlineKeyboardButton(
                text="ʀᴇᴘʟᴀʏ ↺", callback_data=f"ADMIN Replay|{chat_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="ᴍᴏʀᴇ",
                callback_data=f"PanelMarkup None|{chat_id}",
            ),
        ],
    ]

    return buttons


def stream_markup2(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
[
            InlineKeyboardButton(
                text="ᴏᴡɴᴇʀ", url=f"https://t.me/BadMundaXD"
            ),
            InlineKeyboardButton(
                text="ᴄʜᴀᴛ", url=f"https://t.me/PBXCHATS"
            ),
        ],

        [
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def stream_markup_timer2(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 40:
        bar = "◉——————————"
    elif 10 < umm < 20:
        bar = "—◉—————————"
    elif 20 < umm < 30:
        bar = "——◉————————"
    elif 30 <= umm < 40:
        bar = "———◉———————"
    elif 40 <= umm < 50:
        bar = "————◉——————"
    elif 50 <= umm < 60:
        bar = "——————◉————"
    elif 50 <= umm < 70:
        bar = "———————◉———"
    else:
        bar = "——————————◉"

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def panel_markup_1(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(
                text="sᴜғғʟᴇ",
                callback_data=f"ADMIN Shuffle|{chat_id}",
            ),
            InlineKeyboardButton(text="ʟᴏᴏᴘ ↺", callback_data=f"ADMIN Loop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="◁ 10 sᴇᴄ",
                callback_data=f"ADMIN 1|{chat_id}",
            ),
            InlineKeyboardButton(
                text="10 sᴇᴄ ▷",
                callback_data=f"ADMIN 2|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʜᴏᴍᴇ",
                callback_data=f"Pages Back|2|{videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="ɴᴇxᴛ",
                callback_data=f"Pages Forw|2|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_2(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🕒 0.5x",
                callback_data=f"SpeedUP {chat_id}|0.5",
            ),
            InlineKeyboardButton(
                text="🕓 0.75x",
                callback_data=f"SpeedUP {chat_id}|0.75",
            ),
            InlineKeyboardButton(
                text="🕤 1.0x",
                callback_data=f"SpeedUP {chat_id}|1.0",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🕤 1.5x",
                callback_data=f"SpeedUP {chat_id}|1.5",
            ),
            InlineKeyboardButton(
                text="🕛 2.0x",
                callback_data=f"SpeedUP {chat_id}|2.0",
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʙᴀᴄᴋ",
                callback_data=f"Pages Back|1|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_5(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(text="sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"
            ),
            InlineKeyboardButton(
                text="ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʜᴏᴍᴇ",
                callback_data=f"MainMarkup {videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="ɴᴇxᴛ",
                callback_data=f"Pages Forw|1|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_3(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="🕒 0.5x",
                callback_data=f"SpeedUP {chat_id}|0.5",
            ),
            InlineKeyboardButton(
                text="🕓 0.75x",
                callback_data=f"SpeedUP {chat_id}|0.75",
            ),
            InlineKeyboardButton(
                text="🕤 1.0x",
                callback_data=f"SpeedUP {chat_id}|1.0",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🕤 1.5x",
                callback_data=f"SpeedUP {chat_id}|1.5",
            ),
            InlineKeyboardButton(
                text="🕛 2.0x",
                callback_data=f"SpeedUP {chat_id}|2.0",
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʙᴀᴄᴋ",
                callback_data=f"Pages Back|2|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_4(_, vidid, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 40:
        bar = "◉——————————"
    elif 10 < umm < 20:
        bar = "—◉—————————"
    elif 20 < umm < 30:
        bar = "——◉————————"
    elif 30 <= umm < 40:
        bar = "———◉———————"
    elif 40 <= umm < 50:
        bar = "————◉——————"
    elif 50 <= umm < 60:
        bar = "——————◉————"
    elif 50 <= umm < 70:
        bar = "———————◉———"
    else:
        bar = "——————————◉"

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(
                text="II ᴘᴀᴜsᴇ",
                callback_data=f"ADMIN Pause|{chat_id}",
            ),
            InlineKeyboardButton(
                text="▢ sᴛᴏᴘ ▢", callback_data=f"ADMIN Stop|{chat_id}"
            ),
            InlineKeyboardButton(
                text="sᴋɪᴘ ‣‣I", callback_data=f"ADMIN Skip|{chat_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"
            ),
            InlineKeyboardButton(
                text="ʀᴇᴘʟᴀʏ ↺", callback_data=f"ADMIN Replay|{chat_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʜᴏᴍᴇ",
                callback_data=f"MainMarkup {vidid}|{chat_id}",
            ),
        ],
    ]

    return buttons


def panel_markup_clone(_, vidid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")],
    ]

    return buttons


         
