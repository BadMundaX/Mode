from BADCLONE.core.bot import Bad
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

app = Bad()
api = SafoneAPI()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
JioSaavn = JioSaavnAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
