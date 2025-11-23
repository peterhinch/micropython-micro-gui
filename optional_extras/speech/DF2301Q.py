# DF2301Q.py Driver for speech recognition module.

# Product:
# https://www.dfrobot.com/product-2665.html
# Wiki:
# https://wiki.dfrobot.com/SKU_SEN0539-EN_Gravity_Voice_Recognition_Module_I2C_UART#Command%20Words
# Ported from CircuitPython code:
# https://github.com/DFRobot/DFRobot_DF2301Q/tree/master/python/circuitpython
# Original python code written by qsjhyy(yihuan.huang@dfrobot.com), 2022.
# Copyright 2010 DFRobot Co.
# Released under the MIT License (MIT). See LICENSE.

import time

# GUI operation ID's
# PREVIOUS = 0  Move to previous widget
# NEXT = 1  Move to next widget
# OK = 2  Like OK button: push button, check checkbox etc.
# DO_PRECISION = 3  Enter precision mode
# CANCEL = 4  Stop continuous motion
# INCREASE = 5  Small increase of an "analog" control
# KEEP_INCREASING = 6  Keep increasing until cancelled
# DECREASE = 7  Small decrease
# KEEP_DECREASING = 8  # keep decreasing

# Button class calls .gui_op_id() every poll_interval ms.
# NOTE Device crashes, locking up the I2C bus, if polled too frequently.
class Device:  # Instantiated in hardware_setup.py
    poll_interval = 800  # ms

    def __init__(self, i2c):
        self._i2c = i2c
        self._addr = 0x64

    def _read_reg(self, reg: int) -> int:  # Read a single byte
        buf = self._i2c.readfrom_mem(self._addr, reg, 1)
        return int.from_bytes(buf)  # Convert to int

    # **** Interface to Button. ****
    # Return None if no valid result, else
    # return value from hardware converted to a GUI operation ID
    def gui_op_id(self):
        x = self._read_reg(2)
        return None if not x else x - 5

    # **** The following methods are not used by GUI. ****

    def _write_reg(self, reg: int, data: int):
        self._i2c.writeto_mem(self._addr, reg, int.to_bytes(data, 1, "little"))

    # See https://github.com/DFRobot/DFRobot_DF2301Q/tree/master/python/circuitpython
    # This is supposed to make it speak the passed command, or go into listen mode
    # if passed 1. Not sure it does...
    def play_by_cmdid(self, cmdid: int):
        self._write_reg(3, cmdid)
        time.sleep(1)

    def get_wake_time(self) -> int:  # Current wake time (secs)
        return self._read_reg(6)

    def set_wake_time(self, wake_time: int):  # Set wake time (secs)
        if not 0 <= wake_time <= 255:
            raise ValueError(f"Invalid wake time {wake_time}")
        self._write_reg(6, wake_time)

    def set_volume(self, vol: int):  # Set voice voulme 1..7
        if not 1 <= vol <= 7:
            raise ValueError(f"Invalid volume level {vol}")
        self._write_reg(5, vol)

    def set_mute_mode(self, mode: bool):  # Mute/unmute
        self._write_reg(4, int(mode))
