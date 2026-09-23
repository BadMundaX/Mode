from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
from pyrogram.enums import ButtonStyle


def random_style():
    return random.choice([
        ButtonStyle.SUCCESS,
        ButtonStyle.DANGER,
        ButtonStyle.PRIMARY
    ])


buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="▷", callback_data="resume_cb", style=random_style()),
            InlineKeyboardButton(text="II", callback_data="pause_cb", style=random_style()),
            InlineKeyboardButton(text="‣‣I", callback_data="skip_cb", style=random_style()),
            InlineKeyboardButton(text="▢", callback_data="end_cb", style=random_style()),
        ]
    ]
)

close_key = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text="✯ ᴄʟᴏsᴇ ✯", callback_data="close", style=random_style())]]
)
