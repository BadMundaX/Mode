import logging

import config
from pyrogram import Client
from pytgcalls import PyTgCalls

LOGGER = logging.getLogger(__name__)

# bot_id -> PyTgCalls instance (already .start()-ed)
_clone_calls: dict[int, PyTgCalls] = {}
# bot_id -> underlying pyrogram Client (kept so we can .stop() it later)
_clone_clients: dict[int, Client] = {}


async def start_clone_assistant(bot_id: int, session_string: str) -> PyTgCalls:
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

    _clone_calls[bot_id] = pytgcalls
    _clone_clients[bot_id] = client
    LOGGER.info(f"clone_assistant: started dedicated assistant for bot_id={bot_id}")
    return pytgcalls


async def get_clone_assistant(bot_id: int):
    return _clone_calls.get(bot_id)


async def get_clone_client(bot_id: int):
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
            
