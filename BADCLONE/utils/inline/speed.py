from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
from pyrogram.enums import ButtonStyle


def random_style():
    return random.choice([
        ButtonStyle.SUCCESS,
        ButtonStyle.DANGER,
        ButtonStyle.PRIMARY
    ])



def speed_markup(_, chat_id):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🕒 0.5x",
                    callback_data=f"SpeedUP {chat_id}|0.5",
                 style=random_style()),
                InlineKeyboardButton(
                    text="🕓 0.75x",
                    callback_data=f"SpeedUP {chat_id}|0.75",
                 style=random_style()),
            ],
            [
                InlineKeyboardButton(
                    text=_["P_B_4"],
                    callback_data=f"SpeedUP {chat_id}|1.0",
                 style=random_style()),
            ],
            [
                InlineKeyboardButton(
                    text="🕤 1.5x",
                    callback_data=f"SpeedUP {chat_id}|1.5",
                 style=random_style()),
                InlineKeyboardButton(
                    text="🕛 2.0x",
                    callback_data=f"SpeedUP {chat_id}|2.0",
                 style=random_style()),
            ],
            [
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                 style=random_style()),
            ],
        ]
    )
    return upl
    
