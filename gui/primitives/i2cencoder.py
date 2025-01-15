# encoder.py Asynchronous driver for incremental quadrature encoder.
# This is minimised for micro-gui. Derived from
# https://github.com/peterhinch/micropython-async/blob/master/v3/primitives/encoder.py

# Copyright (c) 2021-2024 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file

# Thanks are due to @ilium007 for identifying the issue of tracking detents,
# https://github.com/peterhinch/micropython-async/issues/82.
# Also to Mike Teachman (@miketeachman) for design discussions and testing
# against a state table design
# https://github.com/miketeachman/micropython-rotary/blob/master/rotary.py

# Now uses ThreadSafeFlag.clear()

import asyncio
from machine import Pin


class I2CEncoder:
    delay = 100  # Debounce/detent delay (ms)

    def __init__(self, encoder, callback):
        self._v = 0  # Encoder value set by ISR
        self._tsf = asyncio.ThreadSafeFlag()
        trig = Pin.IRQ_RISING | Pin.IRQ_FALLING
        try:
            xirq = pin_x.irq(trigger=trig, handler=self._x_cb, hard=True)
            yirq = pin_y.irq(trigger=trig, handler=self._y_cb, hard=True)
        except TypeError:  # hard arg is unsupported on some hosts
            xirq = pin_x.irq(trigger=trig, handler=self._x_cb)
            yirq = pin_y.irq(trigger=trig, handler=self._y_cb)
        asyncio.create_task(self._run(div, callback))

    def _x_cb(self, pin_x):
        if (x := pin_x()) != self._x:
            self._x = x
            self._v += 1 if x ^ self._pin_y() else -1
            self._tsf.set()

    def _y_cb(self, pin_y):
        if (y := pin_y()) != self._y:
            self._y = y
            self._v -= 1 if y ^ self._pin_x() else -1
            self._tsf.set()

    async def _run(self, div, cb):
        pv = 0  # Prior hardware value
        pcv = 0  # Prior divided value passed to callback
        while True:
            self._tsf.clear()
            await self._tsf.wait()  # Wait for an edge
            await asyncio.sleep_ms(Encoder.delay)  # Wait for motion/bounce to stop.
            hv = self._v  # Sample hardware (atomic read).
            if hv == pv:  # A change happened but was negated before
                continue  # this got scheduled. Nothing to do.
            pv = hv
            cv = round(hv / div)  # cv is divided value.
            if (cv - pcv) != 0:  # dv is change in divided value.
                cb(cv, cv - pcv)  # Run user CB in uasyncio context
                pcv = cv
