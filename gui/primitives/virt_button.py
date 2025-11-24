# virt_button.py Emulate Pushbutton objects for micro_gui.
# Device independent.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2025 Peter Hinch

from collections import namedtuple
import asyncio


# Virtual buttons defined by index in .buttons
_NXT = const(0)
_SEL = const(1)
_PREV = const(2)
_INCR = const(3)
_DECR = const(4)
_ALL = const(5)

# dest: index of virtual button in .buttons.
# Other args:
# Delay in ms before executing pushbutton callback.
# 0: never
# 1: effectively immediate
Instruction = namedtuple("Instruction", ("dest", "press", "long", "release"))
# Map GUI operation ID from superclass to instructions
cmd = (
    Instruction(_PREV, 1, 0, 100),  # move to previous
    Instruction(_NXT, 1, 0, 100),  # move to next
    Instruction(_SEL, 1, 0, 100),  # ok
    Instruction(_SEL, 0, 1000, 0),  # do precison
    Instruction(_ALL, 0, 0, 1),  # cancel precision
    Instruction(_INCR, 1, 0, 100),  # increase
    Instruction(_INCR, 1, 0, 0),  # keep increasing
    Instruction(_DECR, 1, 0, 100),  # decrease
    Instruction(_DECR, 1, 0, 0),  # keep decreasing
)

# Virtual button. Has a subset of Pushbutton API sufficient for micro_gui.
# Has a Device object which supplies GUI operation IDs in response to user actions.
# hardware_setup must instantiate five of these.
class VButton:
    buttons = []  # nxt, sel, prev, incr, decr
    device = None

    def __init__(self, device):

        if self.device is None:  # First instance
            self.device = device
        self.poll_interval = self.device.poll_interval
        self.state = False
        self._pf = False
        self._rf = False
        self._lf = False
        self.buttons.append(self)
        if len(self.buttons) == 5:  # Last instance
            asyncio.create_task(self.poll())

    # Args: Virtual button instance, Instruction.
    # Run button callbacks as defined by Instruction.
    async def process(self, dest, ins):
        if ins.press:
            await asyncio.sleep_ms(ins.press)
            dest._press()
        if ins.long:
            await asyncio.sleep_ms(ins.long)
            dest._long()
        if ins.release:  # Only release active buttons
            await asyncio.sleep_ms(ins.release)
            if dest.state:  # Check state after delay (ins may also press)
                dest._release()

    # Poll the device
    async def poll(self):
        await asyncio.sleep(1)
        while True:
            op_id = self.device.gui_op_id()  # Get GUI operation ID from device (or None)
            if op_id is not None and 0 <= op_id < len(cmd):
                ins = cmd[op_id]  # Get Instruction
                if ins.dest == _ALL:
                    for b in self.buttons:
                        await self.process(b, ins)
                else:
                    await self.process(self.buttons[ins.dest], ins)

            await asyncio.sleep_ms(self.poll_interval)

    def _press(self):
        self.state = True
        if self._pf:
            self._pf(*self._pa)

    def _long(self):
        self.state = True
        if self._lf:
            self._lf(*self._la)

    def _release(self):
        if self._rf:
            self._rf(*self._ra)
        self.state = False

    # API
    def press_func(self, func=False, args=()):
        self._pf = func
        if func:  # next, prev, incr, decr  - takes arg
            self._pa = args

    def release_func(self, func=False, args=()):
        self._rf = func
        if func:  # sel only, no arg
            self._ra = args

    def double_func(self, func=False, args=()):
        pass  # Only in 3-button and encoder modes

    def long_func(self, func=False, args=()):
        self._lf = func
        if func:  # sel only: enter precision mode - takes arg
            self._la = args

    def __call__(self):
        return self.state
