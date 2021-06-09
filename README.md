# micropython-micro-gui

This is a lightweight, portable, MicroPython GUI library for displays with
drivers subclassed from `framebuf`. It allows input via pushbuttons or via a
switch joystick.

It is larger and more complex than `nano-gui` owing to the support for input.
It enables switching between screens and launching modal windows. In addition
to `nano-gui` widgets it supports listboxes, dropdown lists, various means of
entering or displaying floating point values, and other widgets.

It is compatible with all display drivers for
[nano-gui](https://github.com/peterhinch/micropython-nano-gui) so is portable
to a wide range of displays. It is also portable between hosts.

## This document is seriously incomplete.  
## It may be several weeks before it is usable.  
## Code is in a better state.  

# 0. Contents

**TODO**

# 1. Basic concepts

Internally `micro-gui` uses `uasyncio`. It presents a conventional callback
based interface; knowledge of `uasyncio` is not required for its use. Display
refresh is handled automatically. As in nano-gui, widgets are drawn using
graphics primitives rather than icons. This makes them efficiently scalable and
minimises RAM usage compared to icon-based graphics. It also facilitates the
provision of extra visual information. For example the color of all or part of
a widget may be changed programmatically, for example to highlight an overrange
condition.

## 1.1 Coordinates

These are defined as `row` and `col` values where `row==0` and `col==0`
corresponds to the top left most pixel. Rows increase downwards and columns
increase to the right. The graph plotting widget uses normal mathematical
conventions within graphs.

## 1.2 Screen, Window and Widget objects

A `Screen` is a window which occupies the entire display. A `Screen` can
overlay another, replacing all its contents. When closed, the `Screen` below is
re-displayed.

A `Window` is a subclass of `Screen` but is smaller, with size and location
attributes. It can overlay part of an underlying `Screen` and is typically used
for modal dialog boxes.

A `Widget` is an object capable of displaying data. Some are also capable of
data input. The latter can be capable of accepting focus, see
[navigation](./README.md#13-navigation). `Widget` objects have dimensions
defined as `height` and `width`. The space requred by them exceeds these by two
pixels all round, as a white border is drawn to show which object currently has
focus. Thus to place a `Widget` at the extreme top left, `row` and `col` values
should be 2.

## 1.3 Fonts

Python font files are in the `gui/fonts` directory. The easiest way to conserve
RAM is to freeze them which is highly recommended. In doing so the directory
structure must be maintained.

To create alternatives, Python fonts may be generated from industry standard
font files with
[font_to_py.py](https://github.com/peterhinch/micropython-font-to-py.git). The
`-x` option for horizontal mapping must be specified. If fixed pitch rendering
is required `-f` is also required. Supplied examples are:

 * `arial10.py` Variable pitch Arial. 10 pixels high.
 * `arial35.py` Arial 35 high.
 * `arial_50.py` Arial 50 high.
 * `courier20.py` Fixed pitch Courier, 20 high.
 * `font6.py` FreeSans 14 high.
 * `font10.py` FreeSans 17 high.
 * `freesans20.py` FreeSans 20 high.

## 1.4 Navigation

The GUI requires from 2 to 5 pushbuttons for control. These are:
 1. `Next` Move to the next widget.
 2. `Select` Operate the currently selected widget.
 3. `Prev` Move to the previous widget.
 4. `Increase` Move within the widget.
 5. `Decrease` Move within the widget.

Many widgets such as `Pushbutton` or `Checkbox` objects require only the
`Select` button to operate: it is possible to design an interface using only
the first two buttons.

Widgets such as `Listbox` objects, dropdown lists (`Dropdown`), and those for
floating point data entry require the `Increase` and `Decrease` buttons to move
within the widget or to adjust the linear value.

A `LinearIO` is a `Widget` that responds to the `increase` and `decrease`
buttons by running an `asyncio` task. These typically output floating point
values using an accelerating algorithm responding to the duration of the button
press. This enables floats with a wide dynamic range to be adjusted with
precision.

The currently selected `Widget` is identified by a white border: the focus
moves between widgets via `Next` and `Prev`. Only `Widget` instances that can
accept input can receive the focus; such widgets are defined as `active`. Some
widgets can be declared as `active` or not in the constructor. An `active`
widget can be disabled and re-enabled at runtime. While disabled a widget is
shown "greyed-out" and cannot accept the focus.

## 1.5 Hardware definition

A file `hardware_setup.py` must exist in the GUI root directory. This defines
the connections to the display, the display driver, and pins used for the
pushbuttons. Example files may be found in the `setup_examples` directory.

Display drivers are documented
[here](https://github.com/peterhinch/micropython-nano-gui/blob/master/DRIVERS.md).

## 1.6 Installation

The easy way to start is to use `mpremote` which allows a directory on your PC
to be mounted on the host. In this way the filesystem on the host is left
unchanged. This is at some cost in loading speed, especially on ESP32. If
adopting this approach, you will need to ensure the `hardware_setup.py` file on
the PC matches your hardware. Install `mpremote` with
```bash
$ pip3 install mpremote
```
Clone the repo to your PC with
```bash
$ git clone https://github.com/peterhinch/micropython-micro-gui
$ cd micropython-micro-gui
```
Edit `hardware_setup.py` then run:
```bash
$ mpremote mount .
```
This should provide a REPL. Run the minimal demo:
```python
>>> import gui.demos.simple
```
If installing to the device's filesystem it is necessary to maintain the
directory structure. The `drivers` and `gui` directories (with subdirectories
and contents) should be copied, along with `hardware_setup.py`. Filesystem
space may be conserved by copying only the display driver in use. Unused
widgets, fonts and demos can also be trimmed, but directory structure must be
kept.

There is scope for speeding loading and saving RAM by using frozen bytecode.
Once again, directory structure must be maintained.

## 1.7 Quick hardware check

The following may be pasted at the REPL to verify correct connection to the
display. It also confirms that `hardware_setup.py` is specifying a suitable
display driver.
```python
from hardware_setup import ssd  # Create a display instance
from gui.core.colors import *
ssd.fill(0)
ssd.line(0, 0, ssd.width - 1, ssd.height - 1, GREEN)  # Green diagonal corner-to-corner
ssd.rect(0, 0, 15, 15, RED)  # Red square at top left
ssd.rect(ssd.width -15, ssd.height -15, 15, 15, BLUE)  # Blue square at bottom right
ssd.show()
```

## 1.8 Performance and hardware notes

The largest supported display is a 320x240 ILI9341 unit. On a Pi Pico with no
use of frozen bytecode the demos run with over 74K of free RAM. Substantial
improvements could be achieved using frozen bytecode.

Snappy navigation benefits from several approaches:
 1. Clocking the SPI bus as fast as possible.
 2. Clocking the host fast (`machine.freq`).
 3. Device driver support for `uasyncio`. Currently this exists on ILI9341 and
    ST7789 (e.g. TTGO T-Display). I intend to extend this to other drivers.

On ESP32 I found it necessary to use physical pullup resistors on the
pushbutton GPIO lines.

## 1.9 Firmware and dependencies

Firmware should be V1.15 or later.

The source tree includes all dependencies. These are listed to enable users to
check for newer versions:

 * [writer.py](https://github.com/peterhinch/micropython-font-to-py/blob/master/writer/writer.py)
 Provides text rendering of Python font files.

A copy of the official driver for OLED displays using the SSD1306 chip is
provided. The official file is here:  
 * [SSD1306 driver](https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py).

Displays based on the Nokia 5110 (PCD8544 chip) require this driver. It is not
in this repo but may be found here:  
 * [PCD8544/Nokia 5110](https://github.com/mcauser/micropython-pcd8544.git)

Synchronisation primitives for `uasyncio` may be found here:  
 * [My async repo](https://github.com/peterhinch/micropython-async/tree/master/v3/primitives).

## 1.10 Supported hosts and displays

Development was done using a Raspberry Pi Pico connected to a cheap ILI9341
320x240 display. I have also tested a TTGO T-Display (an ESP32 host) and a
Pyboard. Code is written with portability as an aim, but MicroPython configs
vary between platforms and I can't guarantee that every widget will work on
every platform. For example, some use the `cmath` module which may be absent on
some builds.

Supported displays are as per
[the nano-gui list](https://github.com/peterhinch/micropython-nano-gui/blob/master/README.md#12-description).
In practice usage with ePaper displays is questionable because of their slow
refresh times. I haven't tested these, or the Sharp displays.

Display drivers are documented [here](https://github.com/peterhinch/micropython-nano-gui/blob/master/DRIVERS.md).

## 1.11 Files

Display drivers may be found in the `drivers` directory. These are copies of
those in `nano-gui`, included for convenience.

The system is organised as a Python package with the root being `gui`. Core
files in `gui/core` are:  
 * `colors.py` Constants including colors and shapes.
 * `ugui.py` The main GUI code.
 * `writer.py` Supports the `Writer` and `CWriter` classes.

The `gui/primitives` directory contains the following files:  
 * `switch.py` Interface to physical pushbuttons.
 * `delay_ms.py` A software triggerable timer.

The `gui/demos` directory contains a variety of demos and tests, some of which
require a large (320x240) display. Demos are run by issuing (fo example):
```python
>>> import gui.demos.simple
```
 * `simple.py` Minimal demo discussed below.
 * `active.py` Demonstrates `active` controls providing floating point input.
 * `plot.py` Graph plotting.
 * `screens.py` Listbox, dropdown and dialog boxes.
 * `tbox.py` Text boxes and user-controlled scrolling.
 * `various.py` Assorted widgets including the different types of pushbutton.
 * `vtest.py` Clock and compass styles of vector display.

# 2. Usage

## 2.1 Program structure and operation

The following is a minimal script (found in `gui.demos.simple.py`) which will
run on a minimal system with a small display and two pushbuttons. It provides
two `Button` widgets with "Yes" and "No" legends.

It may be run by issuing
```python
>>> import gui.demos.simple
```
at the REPL.

Note that the import of `hardware_setup.py` is the first line of code. This is
because the frame buffer is created here, with a need for a substantial block
of contiguous RAM.
```python
from hardware_setup import ssd  # Create a display instance
from gui.core.ugui import Screen

from gui.widgets.label import Label
from gui.widgets.buttons import Button, CloseButton
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):

        def my_callback(button, arg):
            print('Button pressed', arg)

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)

        col = 2
        row = 2
        Label(wri, row, col, 'Simple Demo')
        row = 20
        Button(wri, row, col, text='Yes', callback=my_callback, args=('Yes',))
        col += 60
        Button(wri, row, col, text='No', callback=my_callback, args=('No',))
        CloseButton(wri)  # Quit the application

def test():
    print('Testing micro-gui...')
    Screen.change(BaseScreen)

test()
```
Note how the `Next` pushbutton moves the focus between the two buttons and the
"X" close button. The focus does not move to the "Simple Demo" widget because
it is not `active`: a `Label` cannot accept user input. Pushing the `Select`
pushbutton while the focus is on a `Pushbutton` causes the callback to run.

Applications start by performing `Screen.change()` to a user-defined Screen
object. This must be subclassed from the GUI's `Screen` class. Note that
`Screen.change` accepts a class name, not a class instance.

The user defined `BaseScreen` class constructor instantiates all widgets to be
displayed and typically associates them with callback functions - which may be
bound methods. Screens typically have a `CloseButton` widget. This is a special
`Pushbutton` subclass which displays as an "X" at the top right corner of the
physical display and closes the current screen, showing the one below. If used
on the bottom level `Screen` (as above) it closes the application.

The `wri` `CWriter` instance associates a widget with a font. All widgets use
a `CWriter` instance followed by `row` and `col` as positional constructor args
followed typically by a number of optional keyword args. These have (hopefully)
sensible defaults enabling you to get started easily.

## 2.2 Callbacks

The interface is event driven. Widgets may have optional callbacks which will
be executed when a given event occurs. A callback function receives positional
arguments. The first is a reference to the object raising the callback.
Subsequent arguments are user defined, and are specified as a tuple or list of
items. Callbacks are optional, as are the argument lists - a default null
function and empty list are provided. Callbacks may optionally be written as
bound methods - see Screens below for a reason why this can be useful.

When writing callbacks take care to ensure that the number of arguments passed
is correct, bearing in mind the first arg listed above. Failure to do this will
result in tracebacks which implicate the GUI code rather than the buggy user
code: this is because the GUI runs the callbacks.

## 2.3 Colors

The file `gui/core/colors.py` defines standard color constants which may be
used with any display driver. This section describes how to change these or
to create additional colors.

Most of the color display drivers define colors as 8-bit or larger values.
In such cases colors may be created and assigned to variables as follows:
```python
from hardware_setup import ssd
PALE_YELLOW = ssd.rgb(150, 150, 0)
```
The GUI also provides drivers with 4-bit color to minimise RAM use. Colors are
assigned to a lookup table having 16 entries. The frame buffer stores 4-bit
color values, which are converted to the correct color depth for the hardware
when the display is refreshed.

Of the possible 16 colors 13 are assigned in `gui/core/colors.py`, leaving
color numbers 12, 13 and 14 free. Any color can be assigned as follows:
```python
from gui.core.colors import *  # Imports the create_color function
PALE_YELLOW = create_color(12, 150, 150, 0)
```
This creates a color `rgb(150, 150, 0)` assigns it to "spare" color number 12
then sets `PALE_YELLOW` to 12. Any color number in range `0 <= n <= 15` may be
used (implying that predefined colors may be reassigned). It is recommended
that `BLACK` (0) and `WHITE` (15) are not changed. If code is to be ported
between 4-bit and other drivers, use `create_color()` for all custom colors:
it will produce appropriate behaviour. For an example see the `nano-gui` demo
`color15.py` - in particular the `vari_fields` function.

### 2.3.1 Monochrome displays

Most widgets work on monochrome displays if color settings are left at default
values. If a color is specified, drivers in this repo will convert it to black
or white depending on its level of saturation. A low level will produce the
background color, a high level the foreground.

At the bit level `1` represents the foreground. This is white on an emitting
display such as an OLED. On a Sharp display it indicates reflection.

There is an issue regarding ePaper displays discussed
[here](https://github.com/peterhinch/micropython-nano-gui/blob/master/README.md#312-monochrome-displays).
I don't consider ePaper displays as suitable for I/O because of their slow
refresh time.

# 3. Class details

# 4. Screen class

The `Screen` class presents a full-screen canvas onto which displayable
objects are rendered. Before instantiating widgets a `Screen` instance must be
created. This will be current until another is instantiated. When a widget is
instantiated it is associated with the current screen.

All applications require the creation of at least one user screen. This is done
by subclassing the `Screen` class. Widgets are instantiated in the constructor.
Widgets may be assigned to bound variable: this facilitates communication
between them.

## 4.1 Class methods

In normal use the following methods only are required:  
 * `change` Change screen, refreshing the display. Mandatory positional
 argument: the new screen class name. This must be a class subclassed from
 `Screen`. The class will be instantiated and displayed. Optional keyword
 arguments: `args`, `kwargs`. These enable passing positional and keyword
 arguments to the constructor of the new screen.
 * `back` Restore previous screen.

These are uncommon:__
 * `shutdown` Clear the screen and shut down the GUI. Normally done by a
 `CloseButton` instance.
 * `show(cls, force)`. This causes the screen to be redrawn. If `force` is
 `False` unchanged widgets are not refreshed. If `True`, all visible widgets
 are re-drawn. Explicit calls to this should never be needed.

See `demos/plot.py` for an example of multi-screen design.

## 4.2 Constructor

This takes no arguments.

## 4.3 Callback methods

These are null functions which may be redefined in user subclasses.

 * `on_open` Called when a screen is instantiated but prior to display.
 * `after_open` Called after a screen has been displayed.
 * `on_hide` Called when a screen ceases to be current.

See `demos/plot.py` for examples of usage of `after_open`.

## 4.4 Method

 * `reg_task` args `task`, `on_change=False`. The first arg may be a `Task`
 instance or a coroutine. It is a convenience method which provides for the
 automatic cancellation of tasks. If a screen runs independent coros it can opt
 to register these. On shudown, any registered tasks of the base screen are
 cancelled. On screen change, registered tasks with `on_change` `True` are
 cancelled. For finer control applications can ignore this method and handle
 cancellation explicitly in code.

# 5. Window class

This is a `Screen` subclass providing for modal windows. As such it has
positional and dimension information. Usage consists of writing a user class
subclassed from `Window`. Example code is in `demos/screens.py`.

## 5.2 Constructor

This takes the following positional args:  
 * `row`
 * `col`
 * `height`
 * `width`

Followed by keyword-only args
 * `draw_border=True`
 * `bgcolor=None` Background color, default black.
 * `fgcolor=None` Foreground color, default white.

## 5.3 Class method

 * `value` This accepts a single arg which cane be any Python type. It allows
 widgets on a `Window` to store information in a way which can be accessed from
 the calling screen. This typically occurs after the window has closed and no
 longer exists as an instance.

Another approach, demonstrated in `demos/screens.py`, is to pass one or more
callbacks to the user window constructor args. These may be called by widgets
to send data to the calling screen. Note that widgets on the screen below will
not be updated until the window has closed.
