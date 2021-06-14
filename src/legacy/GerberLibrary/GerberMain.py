from src.legacy.GerberLibrary.GerberCurve import *
from src.legacy.GerberLibrary.GerberStraight import *
from src.legacy.GerberLibrary.GerberHangingResonator import *
from src.legacy.GerberLibrary.GerberEnd import *
from src.legacy.GerberLibrary.GerberHole import *
from src.legacy.GerberLibrary.GerberPort import *


class Main(pya.Library):
    """
    The library containing elements for creating a superconducting circuit mask.
    """

    def __init__(self):
        self.description = "Gerber CPW Library"

        self.layout().register_pcell("Port", GPort())
        self.layout().register_pcell("Curve", GCurve())
        self.layout().register_pcell("Straight", GStraight())
        self.layout().register_pcell("End", GEnd())
        self.layout().register_pcell("Hole", GHole())
        self.layout().register_pcell("HangingResonator", GHangingResonator())
        # self.layout().register_pcell("StraightFingers", StraightFingers())
        # self.layout().register_pcell("HangingResonatorFingers", HangingResonatorFingers())
        # self.layout().register_pcell("EndHooks", EndHooks())

        self.register("gerQC")


# Instantiate and register the library
Main()












