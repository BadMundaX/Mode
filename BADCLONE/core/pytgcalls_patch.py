import logging

LOGGER = logging.getLogger(__name__)

try:
    from pyrogram.raw.types import UpdateGroupCall
    from pyrogram.utils import get_peer_id

    if "chat_id" not in UpdateGroupCall.__dict__:

        _original_getattr = getattr(UpdateGroupCall, "__getattr__", None)

        def _compat_getattr(self, name):
            if name == "chat_id":
                peer = self.__dict__.get("peer")
                if peer is not None:
                    return get_peer_id(peer)
                raise AttributeError(
                    "'UpdateGroupCall' object has no attribute 'chat_id' "
                    "(and no 'peer' to derive it from)"
                )
            if _original_getattr is not None:
                return _original_getattr(self, name)
            raise AttributeError(name)

        UpdateGroupCall.__getattr__ = _compat_getattr
        LOGGER.info("pytgcalls_patch: UpdateGroupCall.chat_id compat shim installed")

except Exception as e:  # never let a missing/renamed internal break startup
    LOGGER.warning(f"pytgcalls_patch: could not install compat shim ({e})")
    
