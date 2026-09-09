from BADCLONE.core.bot import PRO
from BADCLONE.core.dir import dirr
from BADCLONE.core.git import git
from BADCLONE.core.userbot import Userbot
from BADCLONE.misc import dbb, heroku
from pyrogram import Client
from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = PRO()
api = SafoneAPI()
userbot = Userbot()

from .platforms import *

Carbon = CarbonAPI()
JioSaavn = JioSaavnAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
