# micropython-micro-gui
Under development: will be released soon after further testing.

A lightweight MicroPython GUI library for display drivers based on framebuf, allows input via pushbuttons or via a switch joystick.

It is larger and more complex than nano-gui owing to the support for input. It enables switching between screens and launching modal windows. In addition to nano-gui widgets it supports listboxes, dropdown lists, various means of entering or displaying floating point values, and other widgets.

It uses display drivers for [nano-gui](https://github.com/peterhinch/micropython-nano-gui) providing portability to a wide range of displays. It is also portable between hosts. Currently running on RP2, but I intend to test on Pyboard and ESP32/TTGo TDisplay.
