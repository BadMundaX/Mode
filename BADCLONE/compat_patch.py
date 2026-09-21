"""
Newer Kurigram versions removed the old `disable_web_page_preview=` argument
(it is now `link_preview_options=LinkPreviewOptions(is_disabled=True)`).
Old code that still passes `disable_web_page_preview` then crashes with
"TypeError: ... got an unexpected keyword argument 'disable_web_page_preview'".

This patch converts the old argument to the new one, so both old and new
Kurigram versions work with the same code. It does nothing on versions that
still understand `disable_web_page_preview`.
"""
import functools
import inspect

try:
    from pyrogram import Client
    from pyrogram.types import CallbackQuery, Message

    try:
        from pyrogram.types import LinkPreviewOptions
    except ImportError:  # old pyrogram: nothing to patch
        LinkPreviewOptions = None
except Exception:  # pragma: no cover
    Client = CallbackQuery = Message = LinkPreviewOptions = None


def _wrap(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if "disable_web_page_preview" in kwargs:
            disable = kwargs.pop("disable_web_page_preview")
            if disable and "link_preview_options" not in kwargs:
                kwargs["link_preview_options"] = LinkPreviewOptions(is_disabled=True)
        return fn(*args, **kwargs)

    wrapper._preview_patched = True
    return wrapper


def apply():
    if LinkPreviewOptions is None:
        return 0
    patched = 0
    for cls in (Client, Message, CallbackQuery):
        for name in dir(cls):
            if name.startswith("_"):
                continue
            try:
                fn = getattr(cls, name)
                if not callable(fn) or getattr(fn, "_preview_patched", False):
                    continue
                params = inspect.signature(fn).parameters
            except Exception:
                continue
            if "link_preview_options" in params and "disable_web_page_preview" not in params:
                setattr(cls, name, _wrap(fn))
                patched += 1
    return patched


apply()
