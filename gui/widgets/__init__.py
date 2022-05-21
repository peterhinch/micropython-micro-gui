_attrs = {
    "Adjuster": "adjuster",
    "FloatAdj": "adjuster",
    "Button": "buttons",
    "CloseButton": "buttons",
    "ButtonList": "buttons",
    "RadioButtons": "buttons",
    "Checkbox": "checkbox",
    "Dial": "dial",
    "Pointer": "dial",
    "DialogBox": "dialog",
    "Dropdown": "dropdown",
    "Knob": "knob",
    "Label": "label",
    "LED": "led",
    "Listbox": "listbox",
    "SubMenu": "menu",
    "Menu": "menu",
    "Meter": "meter",
    "Region": "region",
    "ScaleLog": "scale_log",
    "Scale": "scale",
    "Slider": "sliders",
    "HorizSlider": "sliders",
    "Textbox": "textbox",
    "BitMap": "bitmap",
    "QRMap": "qrcode",
    }

# Lazy loader, effectively does:
#   global attr
#   from .mod import attr
# Filched from uasyncio.__init__.py

def __getattr__(attr):
    mod = _attrs.get(attr, None)
    if mod is None:
        raise AttributeError(attr)
    value = getattr(__import__(mod, None, None, True, 1), attr)
    globals()[attr] = value
    return value
