from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, Message
import config
import asyncio
from BADCLONE import app
import random
from pyrogram.enums import ButtonStyle


def random_style():
    return random.choice([
        ButtonStyle.SUCCESS,
        ButtonStyle.DANGER,
        ButtonStyle.PRIMARY
    ])



# Start panel for inline buttons
def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["SO_B_1"], url=f"https://t.me/{app.username}?startgroup=true"
            , style=random_style()),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT, style=random_style()),
        ],
    ]
    return buttons


# Private panel for inline buttons
def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
             style=random_style())
        ],
        [InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper", style=random_style())],
        [
            InlineKeyboardButton(text=_["S_B_6"], url=config.SUPPORT_CHANNEL, style=random_style()),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT, style=random_style()),
        ],
        [
            InlineKeyboardButton(text=_["S_B_5"], user_id=config.OWNER_ID, style=random_style()),
        ],
    ]
    return buttons
