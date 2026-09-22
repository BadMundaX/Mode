from typing import Union
from BADCLONE import app
from BADCLONE.utils.formatters import time_to_seconds
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
from pyrogram.enums import ButtonStyle


def random_style():
    return random.choice([
        ButtonStyle.SUCCESS,
        ButtonStyle.DANGER,
        ButtonStyle.PRIMARY
    ])



def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    not_dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
             style=random_style()),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
             style=random_style()),
        ]
    ]
    dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_2"].format(played, dur),
                callback_data="GetTimer",
             style=random_style())
        ],
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
             style=random_style()),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
             style=random_style()),
        ],
    ]
    upl = InlineKeyboardMarkup(not_dur if DURATION == "Unknown" else dur)
    return upl


def queue_back_markup(_, CPLAY):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"queue_back_timer {CPLAY}",
                 style=random_style()),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                 style=random_style()),
            ]
        ]
    )
    return upl


def aq_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=random_style()),
        ],
        [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=random_style())],
    ]
    return buttons

def queuemarkup(_, vidid, chat_id):

    buttons = [
        [
            InlineKeyboardButton(text=_["S_B_5"],url=f"https://t.me/{app.username}?startgroup=true", style=random_style()),
        ],
        [
            InlineKeyboardButton(text="II",callback_data=f"ADMIN Pause|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=random_style()),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style=random_style()),
        ],
    ]

    return buttons
