"""
Per-clone dedicated assistant manager.

By default every clone bot joins voice chats using the shared 5-userbot
pool (self.one..self.five in core/call.py, picked by group_assistant()).
This module lets an individual clone owner register their OWN pyrogram
session string (via /setassistant in cplugin/setinfo.py) so THEIR clone
joins calls with their own userbot instead of the shared pool.

Everything here is in-memory (a running Client + PyTgCalls per bot_id).
On restart, call load_all_clone_assistants() once at startup to
reconnect every session already saved in the database.

The stream-end / kicked / closed-voice-chat / left callbacks that the
shared pool gets from Call.decorators() are wired up here individually
for each custom assistant (see _register_callbacks below), so
pause/resume/skip/next-queue-song work exactly the same way they do on
the shared pool.
"""

import logging
import time

import config
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.stream import StreamAudioEnded

LOGGER = logging.getLogger(__name__)

# bot_id -> PyTgCalls instance (already .start()-ed)
_clone_calls: dict[int, PyTgCalls] = {}
# bot_id -> underlying pyrogram Client (kept so we can .stop() it later)
_clone_clients: dict[int, Client] = {}

# chat_id -> unix time of the last successful join/song-change on this
# chat. Used only to debounce a known py-tgcalls==0.9.7 flakiness: a
# freshly-connected custom Client can fire a spurious on_kicked/on_left/
# on_closed_voice_chat right as a stream naturally ends and the next
# song starts, even though nothing actually kicked it. The long-running
# shared pool assistants don't show this because they've been connected
# for a while. If a leave/kick event lands within this window of a
# change, we treat it as noise once instead of tearing down a call that
# just successfully started its next song.
_last_change_at: dict[int, float] = {}
_LEAVE_DEBOUNCE_SECONDS = 4


def _register_callbacks(pytgcalls: PyTgCalls):
    """Mirrors Call.decorators() for a single dynamically-created
    assistant, so it behaves like a 6th pool member instead of a
    second-class citizen that never gets told a stream ended."""

    @pytgcalls.on_kicked()
    @pytgcalls.on_closed_voice_chat()
    @pytgcalls.on_left()
    async def _clone_left_handler(_, chat_id: int):
        last = _last_change_at.get(chat_id, 0)
        if time.time() - last < _LEAVE_DEBOUNCE_SECONDS:
            LOGGER.warning(
                f"clone_assistant: ignoring kicked/left/closed_voice_chat for "
                f"chat_id={chat_id} — fired within {_LEAVE_DEBOUNCE_SECONDS}s "
                f"of a song change, treating as a spurious event."
            )
            return
        try:
            from BADCLONE.core.call import Bad
            await Bad.stop_stream(chat_id)
        except Exception:
            LOGGER.exception(
                f"clone_assistant: error handling kicked/left for chat_id={chat_id}"
            )

    @pytgcalls.on_stream_end()
    async def _clone_stream_end_handler(client, update):
        if not isinstance(update, StreamAudioEnded):
            return
        try:
            from BADCLONE.core.call import Bad
            _last_change_at[update.chat_id] = time.time()
            await Bad.change_stream(client, update.chat_id)
        except Exception:
            LOGGER.exception(
                f"clone_assistant: error advancing queue for chat_id={update.chat_id}"
            )


async def start_clone_assistant(bot_id: int, session_string: str) -> PyTgCalls:
    """Validate + connect a session string as bot_id's dedicated assistant.
    Raises on failure (bad/expired session, etc.) — caller should catch
    and show the user a clear error rather than silently failing.
    """
    # Replace any existing one first
    await stop_clone_assistant(bot_id)

    client = Client(
        name=f"CloneAss{bot_id}",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=session_string,
        in_memory=True,
    )
    pytgcalls = PyTgCalls(client, cache_duration=100)
    await pytgcalls.start()  # starts the underlying pyrogram client too
    _register_callbacks(pytgcalls)

    _clone_calls[bot_id] = pytgcalls
    _clone_clients[bot_id] = client
    LOGGER.info(f"clone_assistant: started dedicated assistant for bot_id={bot_id}")
    return pytgcalls


async def get_clone_assistant(bot_id: int):
    """Returns the running PyTgCalls instance for this bot_id, or None if
    it doesn't have one registered/running. Never raises."""
    return _clone_calls.get(bot_id)


def mark_recent_change(chat_id: int):
    """Call this whenever a chat's stream is freshly joined/changed, so
    the debounce in _clone_left_handler above knows not to treat an
    immediately-following kicked/left event as real. Safe to call even
    for chats not using a custom assistant — it's a no-op cost either way."""
    _last_change_at[chat_id] = time.time()


async def get_clone_client(bot_id: int):
    """Returns the underlying pyrogram Client for this bot_id's assistant
    (e.g. to show which account got connected), or None."""
    return _clone_clients.get(bot_id)


async def stop_clone_assistant(bot_id: int):
    pytgcalls = _clone_calls.pop(bot_id, None)
    client = _clone_clients.pop(bot_id, None)
    if pytgcalls is not None:
        try:
            await client.stop()
        except Exception as e:
            LOGGER.warning(f"clone_assistant: error stopping bot_id={bot_id}: {e}")


async def load_all_clone_assistants():
    """Call once at startup: reconnects every custom assistant session
    already saved in the database, so a restart doesn't lose them."""
    from BADCLONE.utils.database.clonedb import get_all_clone_assistant_sessions

    sessions = await get_all_clone_assistant_sessions()
    for entry in sessions:
        bot_id = entry["bot_id"]
        session_string = entry["assistant_session"]
        try:
            await start_clone_assistant(bot_id, session_string)
        except Exception as e:
            LOGGER.warning(
                f"clone_assistant: could not reconnect bot_id={bot_id} at startup: {e}"
            )
            
