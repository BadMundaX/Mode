import asyncio
import os
import re
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist
import aiohttp
from config import *


def time_to_seconds(time):
    if not time: return 0
    stringt = str(time)
    if stringt == "None": return 0
    try:
        return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))
    except Exception:
        return 0

async def download_song(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3: return None
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0: return file_path
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/download", params={"url": video_id, "type": "audio", "api_key": API_KEY}, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                if resp.status != 200: return None
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072): f.write(chunk)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0: return file_path
        return None
    except Exception:
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass
        return None

async def download_video(link: str) -> str:
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3: return None
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0: return file_path
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/download", params={"url": video_id, "type": "video", "api_key": API_KEY}, timeout=aiohttp.ClientTimeout(total=600)) as resp:
                if resp.status != 200: return None
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072): f.write(chunk)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0: return file_path
        return None
    except Exception:
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass
        return None

# ---------------------------------------------------------------------------
# "Up next" / related videos (used by autoplay)
# ---------------------------------------------------------------------------
_INNERTUBE_NEXT = (
    "https://www.youtube.com/youtubei/v1/next"
    "?prettyPrint=false&key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
)
_INNERTUBE_CLIENT_VERSION = "2.20250101.00.00"
_DURATION_RE = re.compile(r"^\d{1,2}(?::\d{2}){1,2}$")


def _yt_text(node) -> str:
    """Plain text of a YouTube text object (simpleText / runs / content)."""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        if "simpleText" in node:
            return str(node["simpleText"])
        if "runs" in node:
            return "".join(str(r.get("text", "")) for r in node["runs"] if isinstance(r, dict))
        if "content" in node:
            return str(node["content"])
    return ""


def _find_duration(node):
    """First 'm:ss' / 'h:mm:ss' string anywhere inside node."""
    if isinstance(node, str):
        return node if _DURATION_RE.match(node.strip()) else None
    if isinstance(node, dict):
        for v in node.values():
            found = _find_duration(v)
            if found:
                return found.strip()
    elif isinstance(node, list):
        for v in node:
            found = _find_duration(v)
            if found:
                return found.strip()
    return None


def _first_content(node):
    """First 'content' string inside node (used for the channel name)."""
    if isinstance(node, dict):
        if isinstance(node.get("content"), str) and node["content"].strip():
            return node["content"]
        for v in node.values():
            found = _first_content(v)
            if found:
                return found
    elif isinstance(node, list):
        for v in node:
            found = _first_content(v)
            if found:
                return found
    return None


def parse_related(data, exclude_id=None, limit: int = 30):
    """
    Pull the recommended videos out of a youtubei /next response.
    Works with both the old (compactVideoRenderer) and the new
    (lockupViewModel) layouts, so a small YouTube change won't break it.
    """
    out, seen = [], set()

    def add(vid, title, duration, channel):
        if not vid or not title or vid == exclude_id or vid in seen:
            return
        seen.add(vid)
        out.append({"id": vid, "title": title, "duration": duration or "", "channel": channel or ""})

    def walk(node):
        if isinstance(node, dict):
            cvr = node.get("compactVideoRenderer")
            if isinstance(cvr, dict):
                add(
                    cvr.get("videoId"),
                    _yt_text(cvr.get("title")),
                    _yt_text(cvr.get("lengthText")) or _find_duration(cvr.get("thumbnailOverlays")),
                    _yt_text(cvr.get("longBylineText") or cvr.get("shortBylineText")),
                )
            lvm = node.get("lockupViewModel")
            if isinstance(lvm, dict) and lvm.get("contentType") == "LOCKUP_CONTENT_TYPE_VIDEO":
                meta = (lvm.get("metadata") or {}).get("lockupMetadataViewModel") or {}
                add(
                    lvm.get("contentId"),
                    _yt_text(meta.get("title")),
                    _find_duration(lvm.get("contentImage")),
                    _first_content(meta.get("metadata")),
                )
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    return out[:limit]


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message: messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK: return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            results = VideosSearch(link, limit=1)
            res = await results.next()
            if not res.get("result"): return None, None, 0, None, None
            result = res["result"][0]
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = time_to_seconds(duration_min)
            return title, duration_min, duration_sec, thumbnail, vidid
        except Exception:
            return None, None, 0, None, None

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            results = VideosSearch(link, limit=1)
            res = await results.next()
            if not res.get("result"): return None
            return res["result"][0]["title"]
        except Exception: return None

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            results = VideosSearch(link, limit=1)
            res = await results.next()
            if not res.get("result"): return None
            return res["result"][0]["duration"]
        except Exception: return None

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            results = VideosSearch(link, limit=1)
            res = await results.next()
            if not res.get("result"): return None
            return res["result"][0]["thumbnails"][0]["url"].split("?")[0]
        except Exception: return None

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file: return 1, downloaded_file
            return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        if "&" in link: link = link.split("&")[0]
        try: plist = await Playlist.get(link)
        except Exception: return []
        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if not data: continue
            vid = data.get("id")
            if not vid: continue
            ids.append(vid)
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            results = VideosSearch(link, limit=1)
            res = await results.next()
            if not res.get("result"): return None, None
            result = res["result"][0]
            track_details = {
                "title": result["title"], "link": result["link"], "vidid": result["id"],
                "duration_min": result["duration"], "thumb": result["thumbnails"][0]["url"].split("?")[0],
            }
            return track_details, result["id"]
        except Exception:
            return None, None

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        try:
            with ydl:
                formats_available = []
                r = ydl.extract_info(link, download=False)
                for format in r["formats"]:
                    try:
                        if "dash" not in str(format["format"]).lower():
                            formats_available.append({
                                "format": format["format"], "filesize": format.get("filesize"),
                                "format_id": format["format_id"], "ext": format["ext"],
                                "format_note": format["format_note"], "yturl": link,
                            })
                    except Exception: continue
            return formats_available, link
        except Exception:
            return [], link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        if "&" in link: link = link.split("&")[0]
        try:
            a = VideosSearch(link, limit=10)
            res = await a.next()
            result = res.get("result")
            if not result or query_type >= len(result): return None, None, None, None
            title = result[query_type]["title"]
            duration_min = result[query_type]["duration"]
            vidid = result[query_type]["id"]
            thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
            return title, duration_min, thumbnail, vidid
        except Exception:
            return None, None, None, None

    async def download(self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None) -> str:
        if videoid: link = self.base + link
        try:
            if video: downloaded_file = await download_video(link)
            else: downloaded_file = await download_song(link)
            if downloaded_file: return downloaded_file, True
            return None, False
        except Exception: return None, False

    async def related_videos(self, video_id: str, limit: int = 30):
        """Videos YouTube itself suggests after `video_id` (best source for autoplay)."""
        payload = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": _INNERTUBE_CLIENT_VERSION,
                    "hl": "en",
                    "gl": "US",
                }
            },
            "videoId": video_id,
        }
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            ),
            "Content-Type": "application/json",
            "Origin": "https://www.youtube.com",
            "X-YouTube-Client-Name": "1",
            "X-YouTube-Client-Version": _INNERTUBE_CLIENT_VERSION,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    _INNERTUBE_NEXT,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=8),
                ) as resp:
                    if resp.status != 200:
                        return []
                    data = await resp.json(content_type=None)
            return parse_related(data, exclude_id=video_id, limit=limit)
        except Exception:
            return []

    async def get_related_streams(self, video_id: str):
        PIPED_INSTANCES = [
            "https://pipedapi.kavin.rocks",
            "https://pipedapi.adminforge.de",
            "https://api.piped.projectsegfau.lt",
            "https://pipedapi.in.projectsegfau.lt"
        ]
        for instance in PIPED_INSTANCES:
            try:
                url = f"{instance}/streams/{video_id}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            related = data.get("relatedStreams", [])
                            results = []
                            for item in related[:20]:
                                vid_url = item.get("url", "")
                                if "v=" in vid_url:
                                    vid_id = vid_url.split("v=")[-1].split("&")[0]
                                else:
                                    vid_id = vid_url.replace("/watch?v=", "").strip("/")
                                if vid_id:
                                    results.append({
                                        "id": vid_id,
                                        "title": item.get("title"),
                                        "duration": item.get("duration", 0),
                                        "thumb": item.get("thumbnail")
                                    })
                            if results: return results
            except Exception: continue
        
        try:
            details = await self.details(video_id, videoid=True)
            if details and details[0]:
                title = details[0]
                results = VideosSearch(f"{title} song", limit=10)
                res = await results.next()
                if res.get("result"):
                    return [{
                        "id": item["id"], "title": item["title"],
                        "duration": time_to_seconds(item.get("duration", "0:00")),
                        "thumb": item["thumbnails"][0]["url"].split("?")[0]
                    } for item in res["result"]]
        except Exception: pass
        return []

YouTube = YouTubeAPI()
