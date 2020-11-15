from src.Blueprint import *
from src.WaferBuilder import *

"""
example usage of Blueprint and WaferBuilder
"""

bp = Blueprint(res_coupling_ground=7, silver_glue_port=False, port_spacing=200)
bp_finger = Blueprint(res_coupling_ground=7, silver_glue_port=False, port_spacing=200, res_fingers=8)

bp.create_chip("4to6-1", 4, 6, printed_text="ID: W1-1")
bp.create_chip("4to6-2", 4, 6, printed_text="ID: W1-2")
bp.create_chip("4to6-3", 4, 6, printed_text="ID: W1-3")
bp_finger.create_chip("4to6-f1", 4, 6, printed_text="ID: W1-4", markers=True)
bp_finger.create_chip("4to6-f2", 4, 6, printed_text="ID: W1-5", markers=True)
bp_finger.create_chip("4to6-f3", 4, 6, printed_text="ID: W1-6", markers=True)
bp.create_chip("6to8-1", 6, 8, printed_text="ID: W1-7")
bp.create_chip("6to8-2", 6, 8, printed_text="ID: W1-8")
bp.create_chip("6to8-3", 6, 8, printed_text="ID: W1-9")
bp_finger.create_chip("6to8-f1", 6, 8, printed_text="ID: W1-10", markers=True)
bp_finger.create_chip("6to8-f2", 6, 8, printed_text="ID: W1-11", markers=True)
bp_finger.create_chip("6to8-f3", 6, 8, printed_text="ID: W1-12", markers=True)
bp.create_chip("10to20-1", 10, 20, printed_text="ID: W1-13")
bp.create_chip("10to20-2", 10, 20, printed_text="ID: W1-14")
bp.create_chip("10to20-3", 10, 20, printed_text="ID: W1-15")
bp.create_chip("4to5-1", 4, 4.9, printed_text="ID: W1-16")
bp.create_chip("4to5-2", 4, 4.9, printed_text="ID: W1-17")
bp.create_chip("4to5-3", 4, 4.9, printed_text="ID: W1-18")
bp.create_chip("5to6-1", 5, 5.9, printed_text="ID: W1-19")
bp.create_chip("5to6-2", 5, 5.9, printed_text="ID: W1-20")
bp.create_chip("5to6-3", 5, 5.9, printed_text="ID: W1-21")
bp.create_chip("6to7-1", 6, 6.9, printed_text="ID: W1-22")
bp.create_chip("6to7-2", 6, 6.9, printed_text="ID: W1-23")
bp.create_chip("6to7-3", 6, 6.9, printed_text="ID: W1-24")
bp.create_chip("7to8-1", 7, 7.9, printed_text="ID: W1-25")
bp.create_chip("7to8-2", 7, 7.9, printed_text="ID: W1-26")
bp.create_chip("7to8-3", 7, 7.9, printed_text="ID: W1-27")

wafer = WaferBuilder(spacing_x=9900, spacing_y=5900)
wafer.create_wafer_from_folder("WaferLayout-W2", "../chips", 2)
