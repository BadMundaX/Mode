import asyncio
import aiohttp
import os
import re
from typing import Union, Tuple, Optional

# JioSaavn API base URL (self-hosted from sumitkolhe/jiosaavn-api)
JIOSAAVN_API = "http://54.179.88.9:8080/api"


class JioSaavnAPI:
    def __init__(self):
        self.base = JIOSAAVN_API
        # JioSaavn song/album/playlist URL patterns
        self.song_regex = re.compile(
            r"jiosaavn\.com/song/|jiosaavn\.com/s/song/"
        )
        self.album_regex = re.compile(r"jiosaavn\.com/album/")
        self.playlist_regex = re.compile(r"jiosaavn\.com/(featured|s/playlist)/")

    # ─────────────────────── URL Validators ───────────────────────

    async def valid(self, link: str) -> bool:
        return bool(
            self.song_regex.search(link)
            or self.album_regex.search(link)
            or self.playlist_regex.search(link)
        )

    async def valid_song(self, link: str) -> bool:
        return bool(self.song_regex.search(link))

    async def valid_album(self, link: str) -> bool:
        return bool(self.album_regex.search(link))

    async def valid_playlist(self, link: str) -> bool:
        return bool(self.playlist_regex.search(link))

    # ─────────────────────── Helper ───────────────────────────────

    async def _get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                return await resp.json()

    def _best_audio_url(self, download_urls: list) -> str:
        """downloadUrl list mein se highest quality URL do."""
        for quality in ["320kbps", "160kbps", "96kbps", "48kbps"]:
            for item in download_urls:
                if item.get("quality") == quality and item.get("url"):
                    return item["url"]
        if download_urls:
            return download_urls[-1].get("url", "")
        return ""

    def _duration_min(self, seconds) -> str:
        try:
            secs = int(seconds)
            return f"{secs // 60}:{secs % 60:02d}"
        except Exception:
            return "0:00"

    # ─────────────────────── Search ───────────────────────────────

    async def search(self, query: str) -> Optional[dict]:
        """Query se pehla song result do."""
        try:
            data = await self._get("/search/songs", {"query": query, "limit": 1})
            results = data.get("data", {}).get("results", [])
            if not results:
                return None
            return results[0]
        except Exception as e:
            print(f"[JioSaavn] search error: {e}")
            return None

    # ─────────────────────── Track (by URL) ───────────────────────

    async def track(self, link: str) -> Tuple[dict, str]:
        """JioSaavn song URL se track details do. Returns (details_dict, track_id)."""
        try:
            data = await self._get("/songs", {"link": link})
            songs = data.get("data", [])
            if not songs:
                raise Exception("No song found for this URL")
            song = songs[0] if isinstance(songs, list) else songs
            return self._build_track_details(song)
        except Exception as e:
            print(f"[JioSaavn] track error: {e}")
            raise

    # ─────────────────────── Track by Query ───────────────────────

    async def track_by_query(self, query: str) -> Tuple[dict, str]:
        """Text search se track details do. Returns (details_dict, track_id)."""
        song = await self.search(query)
        if not song:
            raise Exception(f"JioSaavn pe '{query}' nahi mila")
        return self._build_track_details(song)

    # ─────────────────────── Album ────────────────────────────────

    async def album(self, link: str) -> Tuple[list, str]:
        """Album URL se songs list do. Returns (song_query_list, album_id)."""
        try:
            data = await self._get("/albums", {"link": link})
            album_data = data.get("data", {})
            album_id = str(album_data.get("id", "album"))
            songs = album_data.get("songs", [])
            song_queries = [
                f"{s.get('name', '')} {s.get('artists', {}).get('primary', [{}])[0].get('name', '')}".strip()
                for s in songs
            ]
            return song_queries, album_id
        except Exception as e:
            print(f"[JioSaavn] album error: {e}")
            raise

    # ─────────────────────── Playlist ─────────────────────────────

    async def playlist(self, link: str) -> Tuple[list, str]:
        """Playlist URL se songs list do. Returns (song_query_list, playlist_id)."""
        try:
            data = await self._get("/playlists", {"link": link})
            pl_data = data.get("data", {})
            pl_id = str(pl_data.get("id", "playlist"))
            songs = pl_data.get("songs", [])
            song_queries = [
                f"{s.get('name', '')} {s.get('artists', {}).get('primary', [{}])[0].get('name', '')}".strip()
                for s in songs
            ]
            return song_queries, pl_id
        except Exception as e:
            print(f"[JioSaavn] playlist error: {e}")
            raise

    # ─────────────────────── Details (for playlist stream loop) ───

    async def details(self, query: str, spotify: bool = False) -> Tuple[str, str, int, str, str]:
        """
        Playlist streaming loop ke liye use hota hai.
        Returns: (title, duration_min, duration_sec, thumbnail, track_id)
        """
        try:
            song = await self.search(query)
            if not song:
                raise Exception("Song not found")
            title = song.get("name", query)
            duration_sec = int(song.get("duration", 0))
            duration_min = self._duration_min(duration_sec)
            thumbnail = self._get_thumbnail(song)
            track_id = str(song.get("id", query))
            return title, duration_min, duration_sec, thumbnail, track_id
        except Exception as e:
            print(f"[JioSaavn] details error: {e}")
            raise

    # ─────────────────────── Download ─────────────────────────────

    async def download(self, query: str, mystic=None, video: bool = False,
                       videoid: bool = False) -> Tuple[str, bool]:
        """
        Audio URL do JioSaavn se.
        Returns (audio_url, True)

        Fix: Jado query already ek direct CDN URL hai (saavncdn.com)
        taan seedha return karo - dobara search mat karo.
        """
        try:
            query = str(query)

            # ✅ FIX: Already direct audio URL hai - seedha return karo
            if "saavncdn.com" in query:
                return query, True

            # JioSaavn page URL hai - API se song info lo
            if "jiosaavn.com" in query:
                data = await self._get("/songs", {"link": query})
                songs = data.get("data", [])
                song = songs[0] if songs else None

            # Text query hai - search karo
            else:
                song = await self.search(query)

            if not song:
                raise Exception(f"JioSaavn pe song nahi mila: {query}")

            download_urls = song.get("downloadUrl", [])
            audio_url = self._best_audio_url(download_urls)
            if not audio_url:
                raise Exception("Download URL nahi mili")

            return audio_url, True

        except Exception as e:
            print(f"[JioSaavn] download error: {e}")
            raise

    # ─────────────────────── Slider / Search Results ──────────────

    async def slider(self, query: str, query_type: int) -> Tuple[str, str, str, str]:
        """Slider ke liye multiple results. Returns (title, duration_min, thumbnail, track_id)"""
        try:
            data = await self._get("/search/songs", {"query": query, "limit": 10})
            results = data.get("data", {}).get("results", [])
            if not results:
                raise Exception("No results")
            idx = min(query_type, len(results) - 1)
            song = results[idx]
            title = song.get("name", "Unknown")
            duration_sec = int(song.get("duration", 0))
            duration_min = self._duration_min(duration_sec)
            thumbnail = self._get_thumbnail(song)
            track_id = str(song.get("id", ""))
            return title, duration_min, thumbnail, track_id
        except Exception as e:
            print(f"[JioSaavn] slider error: {e}")
            raise

    # ─────────────────────── Internal Helpers ─────────────────────

    def _get_thumbnail(self, song: dict) -> str:
        images = song.get("image", [])
        if images:
            return images[-1].get("url", "") or images[0].get("url", "")
        return ""

    def _build_track_details(self, song: dict) -> Tuple[dict, str]:
        title = song.get("name", "Unknown")
        track_id = str(song.get("id", ""))
        duration_sec = int(song.get("duration", 0))
        duration_min = self._duration_min(duration_sec)
        thumbnail = self._get_thumbnail(song)
        download_urls = song.get("downloadUrl", [])
        audio_url = self._best_audio_url(download_urls)

        artists = song.get("artists", {})
        primary = artists.get("primary", [])
        artist_name = primary[0].get("name", "") if primary else ""

        track_details = {
            "title": title,
            "link": audio_url,       # ← direct CDN audio URL
            "vidid": track_id,
            "duration_min": duration_min,
            "duration_sec": duration_sec,
            "thumb": thumbnail,
            "artist": artist_name,
        }
        return track_details, track_id
