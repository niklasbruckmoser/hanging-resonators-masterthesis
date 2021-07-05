import klayout.db as pya
from src.library.KLayout.Port import *
from src.library.KLayout.CustomPort import *
from src.library.KLayout.Curve import *
from src.library.KLayout.Straight import *
from src.library.KLayout.End import *
from src.library.KLayout.Hole import *
from src.library.KLayout.StraightFingers import *
from src.library.KLayout.HangingResonatorFingers import *
from src.library.KLayout.HangingResonator import *
from src.library.KLayout.EndHooks import *
from src.library.KLayout.Hallbar import *
from src.library.KLayout.Airbridge import *
from src.library.KLayout.AirbridgeRound import *
from src.legacy.HangingResonatorOld import *
from src.library.KLayout.Finger import *


class Main(pya.Library):
    """
    The library containing elements for creating a superconducting circuit mask.
    """

    def __init__(self):
        self.description = "CPW Library"

        self.layout().register_pcell("Port", Port())
        self.layout().register_pcell("CustomPort", CustomPort())
        self.layout().register_pcell("Curve", Curve())
        self.layout().register_pcell("Straight", Straight())
        self.layout().register_pcell("PEnd", End())
        self.layout().register_pcell("Hole", Hole())
        self.layout().register_pcell("HangingResonator", HangingResonator())
        self.layout().register_pcell("HangingResonatorOld", HangingResonatorOld())
        self.layout().register_pcell("StraightFingers", StraightFingers())
        self.layout().register_pcell("HangingResonatorFingers", HangingResonatorFingers())
        self.layout().register_pcell("EndHooks", EndHooks())
        self.layout().register_pcell("Hallbar", Hallbar())
        self.layout().register_pcell("Airbridge", Airbridge())
        self.layout().register_pcell("AirbridgeRound", AirbridgeRound())
        self.layout().register_pcell("Finger", Finger())

        self.register("QC")


# Instantiate and register the library
Main()












