# __init__.py Common functions for uasyncio primitives used bu ugui

# Copyright (c) 2018-2022 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


async def _g():
    pass


type_coro = type(_g())

# If a callback is passed, run it and return.
# If a coro is passed initiate it and return.
# coros are passed by name i.e. not using function call syntax.
def launch(func, tup_args):
    res = func(*tup_args)
    if isinstance(res, type_coro):
        res = asyncio.create_task(res)
    return res


_attrs = {
    "Delay_ms": "delay_ms",
    "Encoder": "encoder",
    "Pushbutton": "pushbutton",
    "ESP32Touch": "pushbutton",
    "Switch": "switch",
    "VButton": "virt_button",
}

# Copied from uasyncio.__init__.py
# Lazy loader, effectively does:
#   global attr
#   from .mod import attr
def __getattr__(attr):
    mod = _attrs.get(attr, None)
    if mod is None:
        raise AttributeError(attr)
    value = getattr(__import__(mod, None, None, True, 1), attr)
    globals()[attr] = value
    return value
