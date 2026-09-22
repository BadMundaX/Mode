from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from BADCLONE import app
import random
from pyrogram.enums import ButtonStyle


def random_style():
    return random.choice([
        ButtonStyle.SUCCESS,
        ButtonStyle.DANGER,
        ButtonStyle.PRIMARY
    ])


def help_pannel(_, START: Union[bool, int] = None):
    first = [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=random_style())]
    second = [
        InlineKeyboardButton(
            text=_["BACK_BUTTON"],
            callback_data="settingsback_helper",
         style=random_style()),
    ]
    mark = second if START else first
    
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=_["H_B_1"], callback_data="help_callback hb1", style=random_style()),
                InlineKeyboardButton(text=_["H_B_3"], callback_data="help_callback hb3", style=random_style()),
                InlineKeyboardButton(text=_["H_B_6"], callback_data="help_callback hb6", style=random_style()),
            ],
            [
                InlineKeyboardButton(text=_["H_B_7"], callback_data="help_callback hb7", style=random_style()),
                InlineKeyboardButton(text=_["H_B_10"], callback_data="help_callback hb10", style=random_style()),
                InlineKeyboardButton(text=_["H_B_11"], callback_data="help_callback hb11", style=random_style()),
            ],
            [
                InlineKeyboardButton(text=_["H_B_12"], callback_data="help_callback hb12", style=random_style()),
                InlineKeyboardButton(text=_["H_B_13"], callback_data="help_callback hb13", style=random_style()),
                InlineKeyboardButton(text=_["H_B_15"], callback_data="help_callback hb15", style=random_style()),
            ],
             [InlineKeyboardButton(text=_["C_B_3"], callback_data="help_callback cbot", style=random_style()),],
            mark,
        ]
    )
    return upl

def help_back_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="settings_back_helper",
                 style=random_style()),
            ]
        ]
    )
    return upl

def clone_help_markup(_, page: int, total: int = 5):
    nav = []
    if page > 1:
        nav.append(
            InlineKeyboardButton(
                text="๏ ʙᴀᴄᴋ ๏",
                callback_data=f"help_callback cbot{page - 1}" if page > 2 else "help_callback chelp",
             style=random_style())
        )
    if page < total:
        nav.append(
            InlineKeyboardButton(
                text="๏ ɴᴇxᴛ ๏",
                callback_data=f"help_callback cbot{page + 1}",
             style=random_style())
        )
    rows = []
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settings_back_helper", style=random_style())])
    rows.append([InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=random_style())])
    return InlineKeyboardMarkup(rows)

def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
             style=random_style()),
        ],
    ]
    return buttons


def first_page(_):
    controll_button = [
        InlineKeyboardButton(text="๏ ᴍᴇɴᴜ ๏", callback_data=f"settingsback_helper", style=random_style()),
        InlineKeyboardButton(text="๏ ɴᴇxᴛ ๏", callback_data=f"BadxBaby", style=random_style()),
    ]
    first_page_menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["H_B_1"], callback_data="help_callback hb1"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_2"], callback_data="help_callback hb2"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_3"], callback_data="help_callback hb3"
                , style=random_style()),
            ],
            [
                InlineKeyboardButton(
                    text=_["H_B_11"], callback_data="help_callback hb11"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_13"], callback_data="help_callback hb13"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_6"], callback_data="help_callback hb6"
                , style=random_style()),
            ],
            [
                InlineKeyboardButton(
                    text=_["H_B_12"], callback_data="help_callback hb12"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_10"], callback_data="help_callback hb10"
                , style=random_style()),
            ],
            [
                InlineKeyboardButton(
                    text=_["C_B_1"], callback_data="help_callback chelp"
                , style=random_style()),
            ],
            [
        InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=random_style())
    ]
        ]
    )
    return first_page_menu

def second_page(_):
    controll_button = [
        InlineKeyboardButton(text="๏ ʙᴀᴄᴋ ๏", callback_data=f"settings_back_helper", style=random_style())
    ]
    second_page_menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["H_B_7"], callback_data="help_callback hb7"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_19"], callback_data="help_callback hb19"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_14"], callback_data="help_callback hb14"
                , style=random_style()),
            ],
            [
                InlineKeyboardButton(
                    text=_["H_B_15"], callback_data="help_callback hb15"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_16"], callback_data="help_callback hb16"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_17"], callback_data="help_callback hb17"
                , style=random_style()),
            ],
            [
                InlineKeyboardButton(
                    text=_["H_B_18"], callback_data="help_callback hb18"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_13"], callback_data="help_callback hb13"
                , style=random_style()),
            ],
            [
                InlineKeyboardButton(
                    text=_["H_B_20"], callback_data="help_callback hb20"
                , style=random_style()),
                InlineKeyboardButton(
                    text=_["H_B_22"], callback_data="help_callback hb22"
                , style=random_style()),
            ],
            [
                InlineKeyboardButton(
                    text=_["H_B_21"], callback_data="help_callback hb21"
                , style=random_style())
            ],
            controll_button,
        ]
    )
    return second_page_menu
    
