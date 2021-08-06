from ESCPOS import *
from math import *

a = escGenerator()

options = {
    "columns":[
        {
            "text": "Texto",
            "type": "data",
            "header_align": "center",
            "data_align": "center"
        }
    ],
    "show_headers": False,
    "show_data": True,
    "border_top" : True,
    "border_right" : True,
    "border_bottom" : True,
    "border_left" : True,
    "separate_header": False,
    "separate_cols": False,
    "separate_rows": False,
    "row_separator_style": "asterisk",
    "style": "asterisk",
    "table_align": "center"
}
data = [
    [" "],
    [" Gracias por su compra "],
    [" "]
]

a.table_normal(data, options)
data_to_print = a.generate()

str_dev_printer = f"/dev/usb/lp2"
dev_printer = open(str_dev_printer, 'wb')
dev_printer.write(data_to_print)