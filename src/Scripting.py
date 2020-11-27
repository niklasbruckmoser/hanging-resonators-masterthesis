from src.Blueprint import *
from src.WaferBuilder import *

"""
example script for creating 54 chips and a wafer containing all of them once
"""


def name():
    return w_name + "-" + str(res_id)


def next_name():
    global res_id
    res_id += 1
    return name()


w_name = "WaferName"
res_id = 0


bp = Blueprint(res_coupling_ground=7, silver_glue_port=False, port_spacing=200, res_segment_w=750)
bpf = Blueprint(res_coupling_ground=7, silver_glue_port=False, port_spacing=200, res_fingers=8)


bp.create_chip(next_name(), 4, 5, printed_text=name())
bp.create_chip(next_name(), 4, 5, printed_text=name())
bp.create_chip(next_name(), 4, 5, printed_text=name())

bpf.create_chip(next_name(), 4, 5, printed_text=name(), markers=True)
bpf.create_chip(next_name(), 4, 5, printed_text=name(), markers=True)
bpf.create_chip(next_name(), 4, 5, printed_text=name(), markers=True)

bp.create_chip(next_name(), 5, 6, printed_text=name())
bp.create_chip(next_name(), 5, 6, printed_text=name())
bp.create_chip(next_name(), 5, 6, printed_text=name())

bp.create_chip(next_name(), 6, 7, printed_text=name())
bp.create_chip(next_name(), 6, 7, printed_text=name())
bp.create_chip(next_name(), 6, 7, printed_text=name())

bp.create_chip(next_name(), 7, 8, printed_text=name())
bp.create_chip(next_name(), 7, 8, printed_text=name())
bp.create_chip(next_name(), 7, 8, printed_text=name())

bp.create_chip(next_name(), 8, 9, printed_text=name())
bp.create_chip(next_name(), 8, 9, printed_text=name())
bp.create_chip(next_name(), 8, 9, printed_text=name())

bp.create_chip(next_name(), 4, 6, printed_text=name())
bp.create_chip(next_name(), 4, 6, printed_text=name())
bp.create_chip(next_name(), 4, 6, printed_text=name())

bp.create_chip(next_name(), 6, 8, printed_text=name())
bp.create_chip(next_name(), 6, 8, printed_text=name())
bp.create_chip(next_name(), 6, 8, printed_text=name())

bp.create_chip(next_name(), 6, 6.1, printed_text=name())
bp.create_chip(next_name(), 6, 6.1, printed_text=name())
bp.create_chip(next_name(), 6, 6.1, printed_text=name())

bp.create_chip(next_name(), 6.1, 6.2, printed_text=name())
bp.create_chip(next_name(), 6.1, 6.2, printed_text=name())
bp.create_chip(next_name(), 6.1, 6.2, printed_text=name())

bp.create_chip(next_name(), 6.2, 6.3, printed_text=name())
bp.create_chip(next_name(), 6.2, 6.3, printed_text=name())
bp.create_chip(next_name(), 6.2, 6.3, printed_text=name())

bp.create_chip(next_name(), 6.3, 6.4, printed_text=name())
bp.create_chip(next_name(), 6.3, 6.4, printed_text=name())
bp.create_chip(next_name(), 6.3, 6.4, printed_text=name())

bp.create_chip(next_name(), 6.4, 6.5, printed_text=name())
bp.create_chip(next_name(), 6.4, 6.5, printed_text=name())
bp.create_chip(next_name(), 6.4, 6.5, printed_text=name())

bp.create_chip(next_name(), 6.5, 6.6, printed_text=name())
bp.create_chip(next_name(), 6.5, 6.6, printed_text=name())
bp.create_chip(next_name(), 6.5, 6.6, printed_text=name())

bp.create_chip(next_name(), 6.6, 6.7, printed_text=name())
bp.create_chip(next_name(), 6.6, 6.7, printed_text=name())
bp.create_chip(next_name(), 6.6, 6.7, printed_text=name())

bp.create_chip(next_name(), 6.7, 6.8, printed_text=name())
bp.create_chip(next_name(), 6.7, 6.8, printed_text=name())
bp.create_chip(next_name(), 6.7, 6.8, printed_text=name())

bp.create_chip(next_name(), 6.8, 6.9, printed_text=name())
bp.create_chip(next_name(), 6.8, 6.9, printed_text=name())
bp.create_chip(next_name(), 6.8, 6.9, printed_text=name())

bp.create_chip(next_name(), 6.9, 7, printed_text=name())
bp.create_chip(next_name(), 6.9, 7, printed_text=name())
bp.create_chip(next_name(), 6.9, 7, printed_text=name())


wafer = WaferBuilder(spacing_x=9900, spacing_y=5900)
chip_list = wafer.load_prefixed_chips("../chips", w_name, 1)
# sorting by chip ID
chip_list = sorted(chip_list, key=lambda x: int(x[0].split("-")[1]))
wafer.create_wafer("WaferLayout-" + w_name, chip_list)