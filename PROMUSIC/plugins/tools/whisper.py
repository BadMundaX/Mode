import aiohttp
from PROMUSIC import app as app
from config import BOT_USERNAME
from pyrogram import filters
from pyrogram.errors import Unauthorized
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)

whisper_db = {}

POSTER_IMG_LINK = "https://mxfly.in/blog/assets/poster/top-trending-anime.png"

WEB_LINK_NAME = "Visit Now"
WEB_LINK = "https://mxfly.in/blog/trending-anime-right-now"

WEB_BTN = InlineKeyboardMarkup([[InlineKeyboardButton(text=WEB_LINK_NAME, url=WEB_LINK)]])

switch_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔒 Start Whisper", switch_inline_query_current_chat="")]])


# Fetch JSON data from the website
async def fetch_json():
    url = "https://mxfly.in/assets/advertisement/json/bot-inline.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None  # Handle errors if the request fails

async def _whisper(_, inline_query):
    data = inline_query.query
    results = []
    
    if len(data.split()) < 2:
        mm = [
            InlineQueryResultArticle(
                title="🔒 Whisper",
                description=f"@{BOT_USERNAME} [ USERNAME | ID ] [ TEXT ]",
                input_message_content=InputTextMessageContent(f"🔒 Usage:\n\n@{BOT_USERNAME} [ USERNAME | ID ] [ TEXT ]"),
                thumb_url="https://i.ibb.co/0CZmTg8/istockphoto-1254403222-612x612.jpg",
                reply_markup=switch_btn
            )
        ]
    else:
        try:
            user_id = data.split()[0]
            msg = data.split(None, 1)[1]
        except IndexError as e:
            pass
        
        try:
            user = await _.get_users(user_id)
        except:
            mm = [
                InlineQueryResultArticle(
                    title="🔒 Whisper",
                    description="Invalid username or ID!",
                    input_message_content=InputTextMessageContent("Invalid username or ID!"),
                    thumb_url="https://i.ibb.co/0CZmTg8/istockphoto-1254403222-612x612.jpg",
                    reply_markup=switch_btn
                )
            ]
        
        try:
            whisper_btn = InlineKeyboardMarkup([[InlineKeyboardButton("show message 🔐", callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}")]])
            one_time_whisper_btn = InlineKeyboardMarkup([[InlineKeyboardButton("📩 One-Time Whisper", callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}_one")]])
            mm = [
                InlineQueryResultArticle(
                    title="🔒 Whisper",
                    description=f"Send a Whisper to {user.first_name}!",
                    input_message_content=InputTextMessageContent(f"🔒 A whisper message to {user.first_name}.\n\nOnly he/she can open it."),
                    thumb_url="https://i.ibb.co/0CZmTg8/istockphoto-1254403222-612x612.jpg",
                    reply_markup=whisper_btn
                ),
                InlineQueryResultArticle(
                    title="📩 One-Time Whisper",
                    description=f"Send a one-time whisper to {user.first_name}!",
                    input_message_content=InputTextMessageContent(f"📩 A one-time whisper message to {user.first_name}.\n\nOnly he/she can open it."),
                    thumb_url="https://i.ibb.co/0CZmTg8/istockphoto-1254403222-612x612.jpg",
                    reply_markup=one_time_whisper_btn
                )
            ]
        except:
            pass
        
        try:
            whisper_db[f"{inline_query.from_user.id}_{user.id}"] = msg
        except:
            pass
    
    results.append(mm)
    return results


@app.on_callback_query(filters.regex(pattern=r"fdaywhisper_(.*)"))
async def whispes_cb(_, query):
    data = query.data.split("_")
    from_user = int(data[1])
    to_user = int(data[2])
    user_id = query.from_user.id
    
    if user_id not in [from_user, to_user, 7355202884]:
        try:
            await _.send_message(from_user, f"{query.from_user.mention} is trying to open your whisper.")
        except Unauthorized:
            pass
        
        return await query.answer("This whisper is not for you 🚧", show_alert=True)
    
    search_msg = f"{from_user}_{to_user}"
    
    try:
        msg = whisper_db[search_msg]
    except:
        msg = "🚫 Error!\n\nWhisper has been deleted from the database!"
    
    SWITCH = InlineKeyboardMarkup([[InlineKeyboardButton("Go Inline 🪝", switch_inline_query_current_chat="")]])
    
    await query.answer(msg, show_alert=True)
    
    if len(data) > 3 and data[3] == "one":
        if user_id == to_user:
            await query.edit_message_text("🔓 Whisper has been read!\n\nPress the button below to send a whisper!", reply_markup=SWITCH)


async def in_help():

    # Fetch JSON data from the website
    blog_data = await fetch_json()

    if blog_data is None:
        # MAIN VALUE
        WEB_THUMB_URL = "https://mxfly.in/assets/advertisement/img/channel-logo.jpg"
        WEB_TITLE = "Watch Latest Anime."
        WEB_DESC = "Stream or download your favorite anime from MxFly.."
        ###################
        ADS_POSTER = "https://mxfly.in/blog/assets/poster/top-trending-anime.png"
        WEB_CAPTION = "[🏓]({0}) Top Trending Anime Right Now | trending anime 2025 | most trending anime right now"
        WEB_LINK_NAME = "Visit Now"
        WEB_LINK = "https://mxfly.in/blog/trending-anime-right-now"

    else:
        # MAIN VALUE
        WEB_THUMB_URL = blog_data["post_data"]["thumb_url"]
        WEB_TITLE = blog_data["post_data"]["web_title"]
        WEB_DESC = blog_data["post_data"]["web_desc"]
        ###################
        ADS_POSTER = blog_data["post_data"]["poster_img_link"]
        WEB_CAPTION = blog_data["post_data"]["caption"]
        WEB_LINK_NAME = blog_data["post_data"]["web_link_name"]
        WEB_LINK = blog_data["post_data"]["web_link"]

    ADS_WEB_BTN = InlineKeyboardMarkup([[InlineKeyboardButton(text=WEB_LINK_NAME, url=WEB_LINK)]])

    answers = [
        InlineQueryResultArticle(
            title="🔒 Whisper",
            description=f"@zmnrobot [USERNAME | ID] [TEXT]",
            input_message_content=InputTextMessageContent(f"**📍Usage:**\n\n@zmnrobot (Target Username or ID) (Your Message).\n\n**Example:**\n@zmnrobot @username I Wanna Phuck You"),
            thumb_url="https://i.ibb.co/0CZmTg8/istockphoto-1254403222-612x612.jpg",
            reply_markup=switch_btn
        ),
        InlineQueryResultArticle(
            title="End",
            description=f"End The Current Playing Stream",
            input_message_content=InputTextMessageContent(f"/end"),
            thumb_url="https://i.pinimg.com/1200x/50/ce/93/50ce93485d977cd21ef0e8265e8a7fe8.jpg"
        ),
        InlineQueryResultArticle(
            title="Watch Latest Anime",
            description=f"Stream or download your favorite anime from MxFly..",
            input_message_content=InputTextMessageContent(f"[🏓]({POSTER_IMG_LINK}) Top Trending Anime Right Now | trending anime 2025 | most trending anime right now"),
            thumb_url="https://mxfly.in/assets/advertisement/img/channel-logo.jpg",
            reply_markup=WEB_BTN
        ),
        InlineQueryResultArticle(
            title=WEB_TITLE,
            description=WEB_DESC,
            input_message_content=InputTextMessageContent(WEB_CAPTION.format(ADS_POSTER)),
            thumb_url=WEB_THUMB_URL,
            reply_markup=ADS_WEB_BTN
        )
    ]
    return answers


@app.on_inline_query()
async def bot_inline(_, inline_query):
    string = inline_query.query.lower()
    
    if string.strip() == "":
        answers = await in_help()
        await inline_query.answer(answers)
    else:
        answers = await _whisper(_, inline_query)
        await inline_query.answer(answers[-1], cache_time=0)
                                               
