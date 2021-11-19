# escpos_gen

## Description
Generator of printable binary files with helper methods based on ESC/POS protocol.

Methods to:
- Create tables providing data and table format.
- Set text format in ESC/POS protocol.
- Open drawer.
- Ring buzzer.
- Print text.
- Predefined horizontal lines.
- Get ESC/POS commands to print images.
- Generate ESC/POS printable binary file.

Supports spanish characters.

## Instalation

Run the following to install:
```python
pip install escpos_gen
```

## Usage

```python
from escpos_gen import escGenerator
a = escGenerator()

options = {
    "columns":[
        {
            "text": "Cant",
            "type": "data",
            "header_align": "center",
            "data_align": "left"
        },
        {
            "text": "Descripción",
            "type": "fill",
            "header_align": "center",
            "data_align": "left",
            "data_fill_car": " "
        },
        {
            "text": "Precio",
            "type": "data",
            "header_align": "center",
            "data_align": "right"
        }
    ],
    "show_headers": True,
    "show_data": True,
    "border_top" : False,
    "border_right" : False,
    "border_bottom" : True,
    "border_left" : False,
    "separate_header": True,
    "separate_cols": True,
    "separate_rows": False,
    "row_separator_style": "blank-dashed",
    "style": "blank-line",
    "table_align": "center"
}
data = [
    ["1", "Hamburguesa con papas y mucho aguacate porfavor", "$50.00"],
    ["1", "Cocacola ", "$10.00"],
    ["1", "Sprite", "$10.00"],
    ["2", "Tacos barbacoa", "$24.00"],
    ["1", "Torta ahogada", "$23.00"],
    ["2", "Torta ahogada", "$23.00"],
    ["3", "Torta ahogada", "$23.00"],
    ["4", "Torta ahogada", "$23.00"]
]


a.table(data, options)
data_to_print = a.generate()

str_dev_printer = f"/dev/usb/lp2"
dev_printer = open(str_dev_printer, 'wb')
dev_printer.write(data_to_print)
```