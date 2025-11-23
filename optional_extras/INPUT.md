# Alternative micro-gui input devices

These comprise external hardware such as speech recognition modules, gesture
recognition via cameras or inertial measurement units and so forth. The GUI
provides visual feedback that the input has been recognised and interacts with
external hardware or code in the usual way. There are various circumstances
where a "hands off" approach is desirable: wearing heavy gloves, contaminated
hands/gloves etc.

# User code

The user writes a device driver which maps data from the device onto an integer
in range 0 to 8 (or `Null`). These represent GUI operations according to the
following table:

| Value | Operation                                                        |
|:-----:|:-----------------------------------------------------------------|
| None  | No data received.                                                |
| 0     | Move to previous widget (next button).                           |
| 1     | Move to next widget (previous button).                           |
| 2     | Operate current widget (select button).                          |
| 3     | Enter precision mode (long press of select).                     |
| 4     | Cancel continuous motion (release increase or decrease button).  |
| 5     | Increase the value of a numeric widget (increase button).        |
| 6     | Continuously increase until cancelled (long press of increase).  |
| 7     | Decrease the value of a numeric widget (decrease button).        |
| 8     | Continuously decrease until cancelled (long press of decrease).  |

The device driver must provide a single method `gui_op_id`. This is polled
periodically with the interval defined by the class variable `poll_interval`.
Typically this might be 100ms. The following is an example of such a driver for
the speech recognition module DF2301Q (see below).
```python
class Device:
    poll_interval = 800  # ms

    def __init__(self, i2c):
        self._i2c = i2c
        self._addr = 0x64

    def _read_reg(self, reg: int) -> int:  # Read a single byte
        buf = self._i2c.readfrom_mem(self._addr, reg, 1)
        return int.from_bytes(buf)  # Convert to int

    # **** Interface to VButton. ****
    def gui_op_id(self):
        x = self._read_reg(2)
        return None if not x else x - 5
```
The interface between the driver and nano-gui is provided by the `VButton`
primitive. This polls the device and emulates a control button. The
`hardware_setup.py` creates a `Display` with five `VButton` objects as follows:
```python
# Set up ssd as usual, then instantiate the device
i2c = SoftI2C(Pin(27, Pin.OUT), Pin(26, Pin.OUT))
dfr = Device(i2c)
# Create and export a Display instance with five virtual control buttons
display = Display(ssd, *(VButton(dfr) for x in range(5)))
```
# Managing expectations

This was developed with the [DFRobot DF2301Q](https://www.dfrobot.com/product-2665.html)
speech recognition module. Issues encountered may apply to other input devices.
Compared to a pushbutton or encoder, speech or gesture recognition is slow - it
takes time to utter a phrase. This makes moving between large numbers of widgets
a little laborious. Simple screen layouts with few widgets may be best. Accuracy
of the device is imperfect; this can probably be improved by choosing a set of
nine custom words with very distinct sounds. The operation of floating point
widgets is tricky because if "cancel" is not recognised quickly the control will
overshoot.

Clearly input device types vary. Even with the limitations of the DF2301Q it
works well with non-FP widgets. It may be worth characterising the device before
designing the application so that the GUI design works well with the device's
limitations.

# DF2301Q

[Product home page](https://www.dfrobot.com/product-2665.html). This requires
training to recognise custom words. The procedure is described
[here](https://wiki.dfrobot.com/SKU_SEN0539-EN_Gravity_Voice_Recognition_Module_I2C_UART#Connection%20Diagram%20-%20UART).
Custom phrases are assigned integers in turn starting at 5. If the chosen
phrases are entered in the order of the above table, mapping is simply a matter
of subtracting 5. While training a speaker or headphones must be connected, but
once running with the GUI this is no longer required as the GUI provides
feedback.

As described above, care should be taken in the choice of words/phrases. For
example it could not reliably distinguish "keep increasing" and
"keep decreasing" - "raise" and "lower" might be better choices.

The DF2301Q does not like being polled too frequently: it expresses its
displeasure by crashing and locking up the I2C bus, requiring a power cycle. The
DFRobot examples poll it with a 3s interval.

See [DF2301Q driver](https://github.com/peterhinch/micropython-micro-gui/blob/main/optional_extras/speech/DF2301Q.py)
which expands on the above code sample to add features such as setting the wake
time.

# The VButton class

This describes the operation of the class for anyone wishing to modify the code.
**TODO**
