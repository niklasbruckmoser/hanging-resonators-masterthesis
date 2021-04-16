import klayout.db as pya
from src.library.CPWLibrary.Port import *
from src.library.CPWLibrary.Curve import *
from src.library.CPWLibrary.Straight import *
from src.library.CPWLibrary.End import *
from src.library.CPWLibrary.Hole import *
from src.library.CPWLibrary.HangingResonator import *
from src.library.CPWLibrary.StraightFingers import *
from src.library.CPWLibrary.HangingResonatorFingers import *
from src.library.CPWLibrary.EndHooks import *
from src.library.CPWLibrary.Hallbar import *


class Main(pya.Library):
    """
    The library containing elements for creating a superconducting circuit mask.
    """

    def __init__(self):
        self.description = "CPW Library"

        self.layout().register_pcell("Port", Port())
        self.layout().register_pcell("Curve", Curve())
        self.layout().register_pcell("Straight", Straight())
        self.layout().register_pcell("PEnd", End())
        self.layout().register_pcell("Hole", Hole())
        self.layout().register_pcell("HangingResonator", HangingResonator())
        self.layout().register_pcell("StraightFingers", StraightFingers())
        self.layout().register_pcell("HangingResonatorFingers", HangingResonatorFingers())
        self.layout().register_pcell("EndHooks", EndHooks())
        self.layout().register_pcell("Hallbar", Hallbar())

        self.register("QC")


# Instantiate and register the library
Main()












