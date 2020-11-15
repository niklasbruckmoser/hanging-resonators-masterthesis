# $autorun

"""
This sample PCell implements a library called "CPW_pieces" containing basic elements for CPWs.
v1 - 6.7. 2018
(c) Stefan Filipp, IBM Research Zurich
v2 - updated and adapted for use with kLayout module, 20.11.2018 - Clemens Mueller, IBM Research Zurich
"""

## depending on if this is run in standalone python or kLayout python, module is called differently
import sys
if sys.version_info[0] == 2:  # v2 does not have importlib
    import pkgutil
    pyaLoad = pkgutil.find_loader('klayout')
else:
    import importlib
    pyaLoad = importlib.find_loader('klayout')
if pyaLoad is not None:
    import klayout.db as pya
    # import parts file, at same location as this library
    from src.library.CPW_parts import *
else:
    import pya
    # import parts file, at same location as this library - need to append library location to path first
    import os.path
    sys.path.append(os.path.dirname(__file__))
    from src.library.CPW_parts import *
## other required modules
# import math
# import numpy as np
import random as rd


## pCell class definitions following
class Hole_Pattern(pya.PCellDeclarationHelper):
    """
    Hole pattern
    """

    def __init__(self):
        # Important: initialize the super class
        super(Hole_Pattern, self).__init__()

        # declare the parameters
        self.param("lay", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("x", self.TypeDouble, "x size", default=2000)
        self.param("y", self.TypeDouble, "y size", default=2000)
        self.param("xd", self.TypeDouble, "x hole dist", default=50)
        self.param("yd", self.TypeDouble, "y hole dist", default=50)
        self.param("sigma", self.TypeDouble, "random sigma", default=0)
        self.param("hx", self.TypeDouble, "hole size x", default=5)
        self.param("hy", self.TypeDouble, "hole size y", default=5)
        self.param("logo", self.TypeInt, "logo?", default=0)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Hole Pattern (Pattern = " + ('%.2f' % self.xd) + " x " + ('%.2f' % self.yd) + \
               ", Size = " + ('%.2f' % self.hx) + "x" + ('%.2f' % self.hy) + ")"

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's bounding box width and layer
        # self.lay = self.layout.get_info(self.lay)
        self.x = self.shape.bbox().width() / self.layout.dbu
        self.y = self.shape.bbox().length() / self.layout.dbu

    def produce_impl(self):
        xu_dbu = self.x / self.layout.dbu
        yu_dbu = self.y / self.layout.dbu
        xdu_dbu = self.xd / self.layout.dbu
        ydu_dbu = self.yd / self.layout.dbu
        sigmau_dbu = self.sigma / self.layout.dbu
        hxu_dbu = self.hx / self.layout.dbu
        hyu_dbu = self.hy / self.layout.dbu

        # create the shape
        nrx = int(xu_dbu / xdu_dbu)
        nry = int(yu_dbu / ydu_dbu)

        for indexx in range(0, nrx):
            for indexy in range(0, nry):
                if sigmau_dbu != 0:
                    rx = rd.randrange(-sigmau_dbu, sigmau_dbu)
                    ry = rd.randrange(-sigmau_dbu, sigmau_dbu)
                    oInt = rd.randint(0, 3)
                else:
                    rx = 0
                    ry = 0
                    oInt = 0
                shift = pya.ICplxTrans(1, 0, False, indexx * xdu_dbu + rx, indexy * ydu_dbu + ry)
                if not self.logo:
                    self.cell.shapes(self.lay_layer).insert(pya.Box(0, 0, hxu_dbu, hyu_dbu).transformed(shift))
                else:
                    logo(self, self.lay_layer, hxu_dbu, shift.trans(pya.DPoint(0, 0)), oInt, False)


class CPW_Port(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide port
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_Port, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("width", self.TypeDouble, "width cpw", default=10)
        self.param("gap", self.TypeDouble, "gap cpw", default=6)
        self.param("ground", self.TypeDouble, "ground cpw", default=50)
        self.param("widthPort", self.TypeDouble, "width port", default=140)
        self.param("gapPort", self.TypeDouble, "gap port", default=60)
        self.param("groundPort", self.TypeDouble, "groundport", default=50)
        self.param("taperLength", self.TypeDouble, "taper length", default=300)
        self.param("padSize", self.TypeDouble, "pad size", default=140)
        self.param("hdHole", self.TypeDouble, "hd hole mask size", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW Port (TaperLength = " + ('%.2f' % self.taperLength) + ", PadSize = " + ('%.2f' % self.padSize) + ")"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        widthPort = self.widthPort / dbu
        groundPort = self.groundPort / dbu
        gapPort = self.gapPort / dbu
        widthCPW = self.width / dbu
        groundCPW = self.ground / dbu
        gapCPW = self.gap / dbu
        taperLength = self.taperLength / dbu
        padSize = self.padSize / dbu
        hdHole = self.hdHole / dbu

        # create shape
        create_cpw_port(self, widthPort, groundPort, gapPort, widthCPW, groundCPW, gapCPW, taperLength, padSize, hdHole, pya.DPoint(0, 0), 0, False)


class CPW_Simple(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide with ports at both ends
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_Simple, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "total length", default=5000)
        self.param("width", self.TypeDouble, "centre width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)
        self.param("widthPort", self.TypeDouble, "port width", default=140)
        self.param("gapPort", self.TypeDouble, "port gap", default=60)
        self.param("groundPort", self.TypeDouble, "port ground", default=50)
        self.param("taperLength", self.TypeDouble, "taper Length", default=300)
        self.param("padSize", self.TypeDouble, "port pad Size", default=140)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_Simple (width = " + ('%.2f' % self.width) + ", gap = " + ('%.2f' % self.gap) + ", length = " + ('%.2f' % self.length) + ")"

    def produce_impl(self):
        dbu = self.layout.dbu
        # fetch the parameters
        length = self.length / dbu
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hdHole = self.hdHole / dbu
        wPort = self.widthPort / dbu
        gPort = self.groundPort / dbu
        gapPort = self.gapPort / dbu
        taperLength = self.taperLength / dbu
        padSize = self.padSize / dbu

        # create the shape
        curr_point = create_cpw_port(self, wPort, gPort, gapPort, width, ground, gap, taperLength, padSize, hdHole, pya.DPoint(0, 0), 0, False)
        curr_point = create_cpw_straight(self, length, ground, width, gap, hdHole, curr_point, 0, False)
        create_cpw_port(self, wPort, gPort, gapPort, width, ground, gap, taperLength, padSize, hdHole, curr_point, 2, False)


class CPW_Res(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide with one resonator in the middle, offset from ends
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_Res, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "cpw segment length", default=2000)
        self.param("cLength", self.TypeDouble, "coupling length to CPW", default=80)
        self.param("midGround", self.TypeDouble, "groundplane between cpw segments", default=3)
        self.param("endGap", self.TypeDouble, "end capacitor gap", default=10)
        self.param("lRes", self.TypeDouble, "resonator length", default=8500)
        self.param("mirror", self.TypeInt, "mirror meander direction?", default=0)
        self.param("resType", self.TypeInt, "Lambda / 4 type?", default=0)
        self.param("wRes", self.TypeDouble, "resonator width", default=750)
        self.param("shiftRes", self.TypeDouble, "resonator meander shift", default=0)
        self.param("offRes", self.TypeDouble, "resonator initial length", default=500)
        self.param("width", self.TypeDouble, "centre width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)
        self.param("fingers", self.TypeInt, "number of fingers to add JJ", default=0)
        self.param("fingerLength", self.TypeDouble, "finger length", default=26)
        self.param("fingerEndGap", self.TypeDouble, "gap between end of finger and ground", default=8)
        self.param("hookWidth", self.TypeDouble, "hook width", default=5)
        self.param("hookLength", self.TypeDouble, "hook length", default=3)
        self.param("hookUnit", self.TypeDouble, "hook unit", default=1)
        self.param("holeLength", self.TypeDouble, "hole length", default = 1)
        # self.param("n", self.TypeInt, "Number of points in Arc", default=64)

        self.n = 64  # number of points in Arc
        self.numMeander = 0
        self.calclen = 0
        self.calclen_dbu = 0

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_Res (resonator length = " + ('%.2f' % self.calclen_dbu) \
            + ", coupling length = " + ('%.2f' % self.cLength) \
            + ", coupling distance = " + ('%.2f' % self.midGround) + ")"

    def produce_impl(self):
        dbu = self.layout.dbu
        # fetch the parameters
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hdHole = self.hdHole / dbu
        length = self.length /dbu
        endGap = self.endGap / dbu
        cLength = self.cLength / dbu
        midGround = self.midGround / dbu
        lengthRes = self.lRes / dbu
        widthRes = self.wRes / dbu
        offRes = self.offRes / dbu
        shiftRes = self.shiftRes / dbu
        fingerLength = self.fingerLength / dbu
        fingerEndGap = self.fingerEndGap / dbu
        hookWidth = self.hookWidth / dbu
        hookLength = self.hookLength / dbu
        hookUnit = self.hookUnit / dbu
        holeLength = self.holeLength/ dbu

        # length of lower cpw in coupler
        couplerLength = cLength + math.pi * (hdHole + ground + gap + width / 2) / 2
        # size of coupler element
        couplerSize = endGap + 3 * ground + 2 * gap + width + 2 * hdHole + cLength
        cpwLength = (length - couplerSize) / 2
        # lmabda /2 or lambda / 4 resonator?
        if self.resType:
            endGapRes = 0
        else:
            endGapRes = endGap
        # create the shape
        curr_point = pya.DPoint(0,0)
        curr_point = create_cpw_straight(self, cpwLength, ground, width, gap, hdHole, curr_point, 0, False)
        # resonator, pointing down, adjust length for coupler
        coup_point = create_cpw_rescoupler(self, cLength, ground, width, gap, endGap, midGround, self.n, hdHole, curr_point, 0, False)
        create_cpw_meander(self, ground, width, gap, hdHole, widthRes, lengthRes - couplerLength, offRes, shiftRes, endGapRes, coup_point['res'], 3, self.mirror, self.fingers, fingerLength, fingerEndGap, hookWidth, hookLength, hookUnit, holeLength)
        self.calclen_dbu = (self.calclen + couplerLength) * dbu
        curr_point = create_cpw_straight(self, cpwLength, ground, width, gap, hdHole, coup_point['cpw'], 0, False)


class CPW_ResInd(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide with one resonator in the middle, offset from ends, coupled inductively
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_ResInd, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "cpw segment length", default=2000)
        self.param("cLength", self.TypeDouble, "coupling length to CPW", default=80)
        # self.param("midGround", self.TypeDouble, "groundplane between cpw segments", default=3)
        self.param("endGap", self.TypeDouble, "end capacitor gap", default=10)
        self.param("lRes", self.TypeDouble, "resonator length", default=8500)
        # self.param("mirror", self.TypeInt, "mirror meander direction?", default=0)
        # self.param("resType", self.TypeInt, "Lambda / 4 type?", default=0)
        self.param("wRes", self.TypeDouble, "resonator width", default=750)
        self.param("shiftRes", self.TypeDouble, "resonator meander shift", default=0)
        self.param("offRes", self.TypeDouble, "resonator initial length", default=500)
        self.param("width", self.TypeDouble, "centre width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)
        # self.param("n", self.TypeInt, "Number of points in Arc", default=64)

        self.n = 64  # number of points in Arc
        self.numMeander = 0
        self.calclen = 0
        self.calclen_dbu = 0

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_ResInd (resonator length = " + ('%.2f' % self.calclen_dbu) \
            + ", coupling length = " + ('%.2f' % self.cLength) + ")"

    def produce_impl(self):
        dbu = self.layout.dbu
        # fetch the parameters
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hdHole = self.hdHole / dbu
        length = self.length /dbu
        endGap = self.endGap / dbu
        cLength = self.cLength / dbu
        lengthRes = self.lRes / dbu
        widthRes = self.wRes / dbu
        offRes = self.offRes / dbu
        shiftRes = self.shiftRes / dbu

        # length of lower cpw in coupler
        couplerLength = cLength + 2 * math.pi * (hdHole + ground + gap + width / 2) / 2
        # length of arc in x/y-plane
        lengthArc = 2 * ground + 2 * gap + width + 2 * hdHole
        # size of coupler element
        couplerSize = cLength + 2 * lengthArc
        cpwLength = (length - couplerSize) / 2
        # length of each resonator piece
        resLength = (lengthRes - couplerLength ) / 2

        # create the shape
        curr_point = pya.DPoint(0,0)
        curr_point = create_cpw_straight(self, cpwLength, ground, width, gap, hdHole, curr_point, 0, False)
        # resonator, pointing down, adjust length for coupler
        coup_point = create_cpw_indcoupler(self, cLength, ground, width, gap, self.n, hdHole, curr_point, 0, False)
        self.calclen_dbu += couplerLength * dbu
        create_cpw_meander(self, ground, width, gap, hdHole, widthRes, resLength, offRes, shiftRes, endGap, coup_point['res0'], 3, False)
        self.calclen_dbu += self.calclen * dbu
        create_cpw_meander(self, ground, width, gap, hdHole, widthRes, resLength, offRes, shiftRes, endGap, coup_point['res1'], 3, True)
        self.calclen_dbu += self.calclen * dbu
        curr_point = create_cpw_straight(self, cpwLength, ground, width, gap, hdHole, coup_point['cpw'], 0, False)


class CPW_OneRes(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide with ports at both ends, one resonator in the middle
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_OneRes, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "cpw segment length", default=2000)
        self.param("cLength", self.TypeDouble, "coupling length to CPW", default=80)
        self.param("midGround", self.TypeDouble, "groundplane between cpw segments", default=3)
        self.param("endGap", self.TypeDouble, "end capacitor gap", default=10)
        self.param("lRes", self.TypeDouble, "resonator length", default=8500)
        self.param("wRes", self.TypeDouble, "resonator width", default=500)
        self.param("mirror", self.TypeInt, "mirror meander direction?", default=0)
        self.param("resType", self.TypeInt, "Lambda / 4 type?", default=0)
        self.param("offRes", self.TypeDouble, "resonator initial length", default=500)
        self.param("shiftRes", self.TypeDouble, "resonator meander shift", default=0)
        self.param("width", self.TypeDouble, "centre width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)
        self.param("pStart", self.TypeInt, "Port at start point?", default=1)
        self.param("pEnd", self.TypeInt, "Port at end point?", default=1)
        self.param("widthPort", self.TypeDouble, "port width", default=140)
        self.param("gapPort", self.TypeDouble, "port gap", default=60)
        self.param("groundPort", self.TypeDouble, "port ground", default=50)
        self.param("taperLength", self.TypeDouble, "taper Length", default=300)
        self.param("padSize", self.TypeDouble, "port pad Size", default=140)
        # self.param("n", self.TypeInt, "Number of points in Arc", default=64)

        self.n = 64  # number of points in Arc
        self.numMeander = 0
        self.calclen = 0
        self.calclen_dbu = 0

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_OneRes (resonator length = " + ('%.2f' % self.calclen_dbu) \
            + ", coupling length = " + ('%.2f' % self.cLength) \
            + ", coupling distance = " + ('%.2f' % self.midGround) + ")"

    def produce_impl(self):
        dbu = self.layout.dbu
        # fetch the parameters
        length = self.length / dbu
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hdHole = self.hdHole / dbu
        wPort = self.widthPort / dbu
        gPort = self.groundPort / dbu
        gapPort = self.gapPort / dbu
        taperLength = self.taperLength / dbu
        padSize = self.padSize / dbu
        # posRes = self.posRes / dbu
        endGap = self.endGap / dbu
        cLength = self.cLength / dbu
        midGround = self.midGround / dbu
        lengthRes = self.lRes / dbu
        widthRes = self.wRes / dbu
        offRes = self.offRes / dbu
        shiftRes = self.shiftRes / dbu

        # length of lower cpw in coupler
        couplerLength = cLength + math.pi * (hdHole + ground + gap + width / 2) / 2
        # size of coupler element
        couplerSize = endGap + 3 * ground + 2 * gap + width + 2 * hdHole + cLength
        cpwLength = (length - couplerSize) / 2
        # Lambda / 2 or Lambda / 4 resonator
        if self.resType:
            endGapRes = 0
        else:
            endGapRes = endGap
        # create the shape
        curr_point = pya.DPoint(0, 0)
        if self.pStart:
            curr_point = create_cpw_port(self, wPort, gPort, gapPort, width, ground, gap, taperLength, padSize, hdHole, curr_point, 0, False)
        curr_point = create_cpw_straight(self, cpwLength, ground, width, gap, hdHole, curr_point, 0, False)
        # resonator, pointing down, adjust length for coupler
        coup_point = create_cpw_rescoupler(self, cLength, ground, width, gap, endGap, midGround, self.n, hdHole, curr_point, 0, False)
        create_cpw_meander(self, ground, width, gap, hdHole, widthRes, lengthRes - couplerLength, offRes, shiftRes, endGapRes, coup_point['res'], 3, self.mirror)
        self.calclen_dbu = (self.calclen + couplerLength) * dbu
        curr_point = create_cpw_straight(self, cpwLength, ground, width, gap, hdHole, coup_point['cpw'], 0, False)
        if self.pEnd:
            create_cpw_port(self, wPort, gPort, gapPort, width, ground, gap, taperLength, padSize, hdHole, curr_point, 2, False)


class CPW_TwoRes(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide with ports at both ends, one resonator in the middle
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_TwoRes, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "total length", default=2000)
        self.param("posRes", self.TypeDouble, "min resonator offset from ends", default=500)
        self.param("cLength1", self.TypeDouble, "coupling length Res1 to CPW", default=90)
        self.param("midGround1", self.TypeDouble, "groundplane between cpw segments Res1", default=3)
        self.param("cLength2", self.TypeDouble, "coupling length Res2 to CPW", default=80)
        self.param("midGround2", self.TypeDouble, "groundplane between cpw segments Res2", default=3)
        self.param("endGap", self.TypeDouble, "end capacitor gap", default=10)
        self.param("lRes1", self.TypeDouble, "resonator 1 length", default=8500)
        self.param("lRes2", self.TypeDouble, "resonator 2 length", default=9000)
        self.param("wRes", self.TypeDouble, "resonator width", default=750)
        self.param("mirror", self.TypeInt, "mirror resonators?", default=0)
        self.param("resType", self.TypeInt, "Lambda / 4 resonators?", default=0)
        self.param("offRes", self.TypeDouble, "resonator initial length", default=500)
        self.param("shiftRes", self.TypeDouble, "resonator meander shift", default=0)
        self.param("width", self.TypeDouble, "centre width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)
        self.param("pStart", self.TypeInt, "Port at start point?", default=1)
        self.param("pEnd", self.TypeInt, "Port at end point?", default=1)
        self.param("widthPort", self.TypeDouble, "port width", default=140)
        self.param("gapPort", self.TypeDouble, "port gap", default=60)
        self.param("groundPort", self.TypeDouble, "port ground", default=50)
        self.param("taperLength", self.TypeDouble, "taper Length", default=300)
        self.param("padSize", self.TypeDouble, "port pad Size", default=140)
        # self.param("n", self.TypeInt, "Number of points in Arc", default=64)

        self.n = 64  # number of points in Arc
        self.numMeander = 0
        self.calclen = 0
        self.resLen1 = 0
        self.resLen2 = 0

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_OneRes (resonator 1 length = " + ('%.2f' % self.resLen1) + ", resonator 2 length = " +  ('%.2f' % self.resLen2) + ")"

    def produce_impl(self):
        dbu = self.layout.dbu
        # fetch the parameters
        length = self.length / dbu
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hdHole = self.hdHole / dbu
        wPort = self.widthPort / dbu
        gPort = self.groundPort / dbu
        gapPort = self.gapPort / dbu
        taperLength = self.taperLength / dbu
        padSize = self.padSize / dbu
        posRes = self.posRes / dbu
        endGap = self.endGap / dbu
        cLength1 = self.cLength1 / dbu
        cLength2 = self.cLength2 / dbu
        midGround1 = self.midGround1 / dbu
        midGround2 = self.midGround2 / dbu
        lengthRes1 = self.lRes1 / dbu
        lengthRes2 = self.lRes2 / dbu
        widthRes = self.wRes / dbu
        offRes = self.offRes / dbu
        shiftRes = self.shiftRes / dbu

        # enforce minimal length of cpw
        if length < 3 * posRes:
            length = 3 * posRes

        # length of lower cpw in coupler, without coupling length
        couplerLength = math.pi * (hdHole + ground + gap + width / 2) / 2
        # size of coupler element, without coupling length
        couplerSize = endGap + 3 * ground + 2 * gap + width + 2 * hdHole # + cLength
        # distance of resonators
        resDist = length - 2 * posRes - 2 * couplerSize - cLength1 - cLength2
        # Lambda / 2 or Lambda / 4 resonator
        if self.resType:
            endGapRes = 0
        else:
            endGapRes = endGap
        # create the shape
        curr_point =  pya.DPoint(0, 0)
        if self.pStart:
            curr_point = create_cpw_port(self, wPort, gPort, gapPort, width, ground, gap, taperLength, padSize, hdHole, curr_point, 0, False)
        curr_point = create_cpw_straight(self, posRes, ground, width, gap, hdHole, curr_point, 0, False)
        # first resonator, pointing down, adjust length for coupler
        coup_point = create_cpw_rescoupler(self, cLength1, ground, width, gap, endGap, midGround1, self.n, hdHole, curr_point, 0, False)
        create_cpw_meander(self, ground, width, gap, hdHole, widthRes, lengthRes1 - couplerLength - cLength1, offRes, shiftRes, endGapRes, coup_point['res'], 3, self.mirror)
        self.resLen1 = (self.calclen + couplerLength + cLength1) * dbu
        curr_point = create_cpw_straight(self, resDist, ground, width, gap, hdHole, coup_point['cpw'], 0, False)
        # second resonator, pointing down, adjust length for coupler
        coup_point = create_cpw_rescoupler(self, cLength2, ground, width, gap, endGap, midGround2, self.n, hdHole, curr_point, 0, False)
        create_cpw_meander(self, ground, width, gap, hdHole, widthRes, lengthRes2 - couplerLength - cLength2, offRes, shiftRes, endGapRes, coup_point['res'], 3, self.mirror)
        self.resLen2 = (self.calclen + couplerLength + cLength2) * dbu
        curr_point = create_cpw_straight(self, posRes, ground, width, gap, hdHole, coup_point['cpw'], 0, False)
        if self.pEnd:
            create_cpw_port(self, wPort, gPort, gapPort, width, ground, gap, taperLength, padSize, hdHole, curr_point, 2, False)


class CPW_Straight(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide segment
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_Straight, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "length", default=100)
        self.param("width", self.TypeDouble, "width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_Straight (width = " + ('%.2f' % self.width) + ", gap = " + ('%.2f' % self.gap) + ", length = " + ('%.2f' % self.length) + ")"

    def produce_impl(self):
        # fetch the parameters
        lnu_dbu = self.length / self.layout.dbu
        wu_dbu = self.width / self.layout.dbu
        su_dbu = self.gap / self.layout.dbu
        gu_dbu = self.ground / self.layout.dbu
        hdu_dbu = self.hdHole / self.layout.dbu

        # create the shape
        create_cpw_straight(self, lnu_dbu, gu_dbu, wu_dbu, su_dbu, hdu_dbu, pya.DPoint(0, 0), 0, False)

class CPW_Straight_Fingers(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide segment
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_Straight_Fingers, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "length", default=100)
        self.param("width", self.TypeDouble, "width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)
        self.param("fingers", self.TypeInt, "number of fingers for JJ", default=0)
        self.param("fingerLength", self.TypeDouble, "finger length", default=26)
        self.param("fingerEndGap", self.TypeDouble, "gap at finger end", default=8)
        self.param("hookWidth", self.TypeDouble, "hook width", default=5)
        self.param("hookLength", self.TypeDouble, "hook length", default=3)
        self.param("hookUnit", self.TypeDouble, "hook unit", default=1)
        self.param("holeLength", self.TypeDouble, "hole length", default = 1)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_Straight_Fingers (width = " + ('%.2f' % self.width) + ", gap = " + ('%.2f' % self.gap) + ", length = " + ('%.2f' % self.length) + ")"

    def produce_impl(self):
        # fetch the parameters
        dbu = self.layout.dbu
        lnu_dbu = self.length / dbu
        wu_dbu = self.width / dbu
        su_dbu = self.gap / dbu
        gu_dbu = self.ground / dbu
        hdu_dbu = self.hdHole / dbu
        fl_dbu = self.fingerLength / dbu
        feg_dbu = self.fingerEndGap / dbu
        hookWidth = self.hookWidth / dbu
        hookLength = self.hookLength / dbu
        hookUnit = self.hookUnit / dbu
        holeLength = self.holeLength / dbu

        # create the shape
        create_cpw_straight_fingers(self, lnu_dbu, gu_dbu, wu_dbu, su_dbu, hdu_dbu, pya.DPoint(0, 0), 0, False, self.fingers, fl_dbu, feg_dbu, hookWidth, hookLength, hookUnit, holeLength)


class CPW_End(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide end segment - straight length ln, separated by endGap from groundplane
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_End, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "length", default=0)
        self.param("endGap", self.TypeDouble, "gap and end cap", default=10)
        self.param("width", self.TypeDouble, "width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_End (width = " + ('%.2f' % self.width) + ", gap = " + ('%.2f' % self.gap) + \
            ", length = " + ('%.2f' % self.length) + ", endGap = " + ('%.2f' % self.endGap) + ")"

    def produce_impl(self):
        dbu = self.layout.dbu
        # fetch the parameters
        lengthu = self.length / dbu
        widthu = self.width / dbu
        gapu = self.gap / dbu
        endGapu = self.endGap / dbu
        groundu = self.ground / dbu
        hdHoleu = self.hdHole / dbu

        # create the shape
        create_cpw_end(self, lengthu, groundu, widthu, gapu, endGapu, hdHoleu, pya.DPoint(0, 0), 0, False)


class CPW_Parallel(pya.PCellDeclarationHelper):
    """
    Two parallel coplanar waveguide segments - capacitive coupling element between two CPW segments
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_Parallel, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "length", default=80)
        self.param("midGround", self.TypeDouble, "groundplane between two segments", default=3)
        self.param("width", self.TypeDouble, "width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_Parallel (width = " + ('%.2f' % self.width) + ", gap = " + ('%.2f' % self.gap) + \
            ", length = " + ('%.2f' % self.length) + ", midGround = " + ('%.2f' % self.midGround) + ")"

    def produce_impl(self):
        # fetch the parameters
        dbu = self.layout.dbu
        length = self.length / dbu
        width = self.width /dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hdHole = self.hdHole / dbu
        midGround = self.midGround / dbu

        # create the shape
        create_cpw_parallel(self, length, ground, width, gap, midGround, hdHole, pya.DPoint(0, 0), 0, False)


class CPW_ResCoupler(pya.PCellDeclarationHelper):
    """
    Two parallel coplanar waveguide segments with the lower one bending down 90 degrees
        - capacitive coupling element between waveguide and resonator
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_ResCoupler, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "coupling length", default=80)
        self.param("midGround", self.TypeDouble, "groundplane width between segments", default=3)
        self.param("width", self.TypeDouble, "width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("endGap", self.TypeDouble, "end gap", default=10)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)
        # self.param("n", self.TypeInt, "Number of points in Arc", default=64)

        self.n = 64  # number of points in Arc
        self.radius = 0
        self.lengthLower =0

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_ResCoupler (width = " + ('%.2f' % self.width) + \
            ", gap = " + ('%.2f' % self.gap) + ", Endgap = " + ('%.2f' % self.endGap) + ", length = " + ('%.2f' % self.length) + \
            ", midGround = " + ('%.2f' % self.midGround) + \
            ", radius = " + ('%.2f' % self.radius) + ", length lower cpw = " + ('%.2f' % self.lengthLower) + ")"

    def produce_impl(self):
        # enforce minimum number of points in arc
        if self.n < 16:
            self.n = 16
        # define bend radius
        # self.radius = round((2 * self.g + self.w + 2 * self.s) / math.pi)
        self.radius = self.hdHole + self.ground + self.gap + self.width / 2
        self.lengthLower = self.length + math.pi * self.radius / 2
        # fetch the parameters
        dbu = self.layout.dbu
        length = self.length / dbu
        width = self.width /dbu
        gap = self.gap / dbu
        endGap = self.endGap / dbu
        ground = self.ground / dbu
        hdHole = self.hdHole / dbu
        midGround = self.midGround / dbu

        # create the shape
        create_cpw_rescoupler(self, length, ground, width, gap, endGap, midGround, self.n, hdHole, pya.DPoint(0, 0), 0, False)


class CPW_IndCoupler(pya.PCellDeclarationHelper):
    """
    inductive coupling element between waveguide and resonator
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_IndCoupler, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "coupling length", default=80)
        # self.param("midGround", self.TypeDouble, "groundplane width between segments", default=3)
        self.param("width", self.TypeDouble, "width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        # self.param("endGap", self.TypeDouble, "end gap", default=10)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)
        # self.param("n", self.TypeInt, "Number of points in Arc", default=64)

        self.n = 64  # number of points in Arc
        self.radius = 0

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_IndCoupler (width = " + ('%.2f' % self.width) + \
            ", gap = " + ('%.2f' % self.gap) + ", length = " + ('%.2f' % self.length) + ", radius = " + ('%.2f' % self.radius) + ")"

    def produce_impl(self):
        # enforce minimum number of points in arc
        if self.n < 16:
            self.n = 16
        # define bend radius
        # self.radius = round((2 * self.g + self.w + 2 * self.s) / math.pi)
        self.radius = self.hdHole + self.ground + self.gap + self.width / 2
        # self.lengthLower = self.length + math.pi * self.radius / 2
        # fetch the parameters
        dbu = self.layout.dbu
        length = self.length / dbu
        width = self.width /dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hdHole = self.hdHole / dbu

        # create the shape
        create_cpw_indcoupler(self, length, ground, width, gap, self.n, hdHole, pya.DPoint(0, 0), 0, False)


class CPW_Coupler(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide coupler = finger capacitor
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_Coupler, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("w", self.TypeDouble, "width", default=10)
        self.param("s", self.TypeDouble, "gap", default=6)
        self.param("g", self.TypeDouble, "ground", default=50)
        self.param("ln", self.TypeDouble, "length", default=100)
        self.param("fln", self.TypeDouble, "finger length", default=55)
        self.param("fs", self.TypeDouble, "finger gap", default=2)
        self.param("fw", self.TypeDouble, "finger width", default=1)
        self.param("ccg", self.TypeDouble, "center cond gap", default=7.5)
        self.param("fo", self.TypeDouble, "finger offset", default=30)
        self.param("hd", self.TypeDouble, "hd hole pattern", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_coupler (FingerLength = " + ('%.2f' % self.fln) + ",CenterGap = " + ('%.2f' % self.ccg) + ")"

    def produce_impl(self):
        # fetch the parameters
        ln = self.ln / self.layout.dbu
        w = self.w / self.layout.dbu
        s = self.s / self.layout.dbu
        g = self.g / self.layout.dbu
        fl = self.fln / self.layout.dbu
        fw = self.fw / self.layout.dbu
        fs = self.fs / self.layout.dbu
        ccg = self.ccg / self.layout.dbu
        fo = self.fo / self.layout.dbu
        hd = self.hd / self.layout.dbu

        # create the shape
        ep = pya.EdgeProcessor()
        self.cell.shapes(self.layout.layer(1, 0)).insert(pya.Box(0, -(2 * g + 2 * s + w) / 2, ln, -(2 * g + 2 * s + w) / 2 + g))
        self.cell.shapes(self.layout.layer(1, 0)).insert(pya.Box(0, (2 * g + 2 * s + w) / 2, ln, (2 * g + 2 * s + w) / 2 - g))
        centercond = [pya.Box(0, -w / 2, ln, +w / 2)]
        cutout = [pya.Box(ln - fo - ccg, w / 2, ln - fo, -w / 2), pya.Box(0, fw / 2 + fs, ln - fo, -fw / 2 - fs)]
        obj1 = ep.boolean_p2p(centercond, cutout, pya.EdgeProcessor.ModeANotB, False, False)
        for shapes in obj1:
            self.cell.shapes(self.layout.layer(1, 0)).insert(shapes)
        self.cell.shapes(self.layout.layer(1, 0)).insert(pya.Box(ln - fo, fw / 2, ln - fo - fl, -fw / 2))

        # cutout
        self.cell.shapes(self.layout.layer(10, 0)).insert(
            pya.Box(0, -(2 * g + 2 * s + w) / 2, ln, (2 * g + 2 * s + w) / 2))

        # high density mask
        self.cell.shapes(self.layout.layer(11, 0)).insert(
            pya.Box(0, -(2 * g + 2 * s + w) / 2 - hd, ln, -(2 * g + 2 * s + w) / 2))
        self.cell.shapes(self.layout.layer(11, 0)).insert(
            pya.Box(0, (2 * g + 2 * s + w) / 2, ln, (2 * g + 2 * s + w) / 2 + hd))


class CPW_90(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide segment
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_90, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        #self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("width", self.TypeDouble, "width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        # self.param("r", self.TypeDouble, "radius", default=39)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)
        # self.param("n", self.TypeInt, "Number of points in Arc", default=64)

        self.n = 64  # number of points in Arc
        self.radius = 0
        self.length = 0

    def display_text_impl(self):
        # radius = self.radius
        # length = self.length
        # Provide a descriptive text for the cell
        return "CPW_90 (radius = " + ('%.2f' % self.radius) + ", length = " + ('%.2f' % self.length) + ")"

    def produce_impl(self):
        # enforce minimum number of points in arc
        if self.n < 16:
            self.n = 16
        # define bend radius
        dbu = self.layout.dbu
        self.radius = self.hdHole + self.ground + self.gap + self.width / 2
        self.length = math.pi * self.radius / 2
        # self.r = self.hd
        # fetch the parameters
        widthu = self.width / dbu
        gapu = self.gap / dbu
        groundu = self.ground / dbu
        hdHoleu = self.hdHole / dbu

        # create the shape
        create_cpw_90(self, groundu, gapu, widthu, self.n, hdHoleu, pya.DPoint(0, 0), "else", False)


class CPW_MeanderSimple(pya.PCellDeclarationHelper):
    """
    Meandered coplanar waveguide
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_MeanderSimple, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        self.param("lengthTot", self.TypeDouble, "total length", default=4000)
        self.param("ioff", self.TypeDouble, "initial straight length", default=100)
        self.param("widthTot", self.TypeDouble, "total Width", default=1000)
        self.param("shiftTot", self.TypeDouble, "initial shift", default=100)
        self.param("width", self.TypeDouble, "width", default=10)
        self.param("mirror", self.TypeInt, "mirror meander direction?", default=0)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("endGap", self.TypeDouble, "gap at endcap", default=10)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)

        # # hidden parameters - do not appear in the pCell GUI
        # self.param("n", self.TypeInt, "number of points in arc", default=32, hidden=True)
        # self.param("numMeander", self.TypeInt, "number of meanders", default=0, hidden=True)
        # self.param("calclen", self.TypeDouble, "calculated length of meander", default=0, hidden=True)
        # self.param("calclen_dbu", self.TypeDouble, "calculated length in dbu", default=0, hidden=True)
        self.n = 64  # number of points in Arc
        self.numMeander = 0
        self.calclen = 0
        self.calclen_dbu = 0

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        # clen = self.calclen
        clen = self.calclen_dbu
        return "CPW_Meander (calculated length = " + ('%.2f' % clen) + ", number of meanders = " + str(int(self.numMeander)) + ")"

    def produce_impl(self):
        # enforce minimum number of points in arc
        if self.n < 16:
            self.n = 16

        dbu = self.layout.dbu
        # set the parameters
        ground = self.ground / dbu
        width = self.width / dbu
        gap = self.gap / dbu
        hdHole = self.hdHole / dbu
        widthTot = self.widthTot / dbu
        shiftTot = self.shiftTot / dbu
        lengthTot = self. lengthTot / dbu
        ioff = self.ioff / dbu
        endGap = self.endGap /dbu

        # create the shape
        create_cpw_meander(self, ground, width, gap, hdHole, widthTot, lengthTot, ioff, shiftTot, endGap, pya.DPoint(0, 0), 0, self.mirror)
        self.calclen_dbu = self.calclen * dbu


class CPW_S(pya.PCellDeclarationHelper):
    """
    S(igmoid) shaped coplanar waveguide - fixed final point with one bend
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_S, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("xfinal", self.TypeDouble, "final point x", default=1000)
        self.param("yfinal", self.TypeDouble, "final point y", default=1000)
        self.param("vStart", self.TypeInt, "start vertical?", default=0)
        self.param("vEndt", self.TypeInt, "end vertical? - not yet implemented", default=0)
        # self.param("pEnd", self.TypeInt, "Port at end point?", default=1)
        # self.param("r", self.TypeDouble, "radius", default=39)
        self.param("off", self.TypeDouble, "offset of bend", default=200)
        self.param("width", self.TypeDouble, "width", default=10)
        self.param("gap", self.TypeDouble, "gap", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        # self.param("n", self.TypeInt, "Number of points", default=64)
        self.param("hdHole", self.TypeDouble, "hd hole pattern", default=40)

        self.n = 64  # number of points in Arc
        self.length = 0
        self.length_dbu = 0

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_Sigmoid (Length = " + ('%.2f' % self.length_dbu) + ", initial offset = " + ('%.2f' % self.off) + ")"

    def produce_impl(self):
        # enforce minimum number of points in arc
        if self.n < 16:
            self.n = 16
        # define bend radius
        dbu = self.layout.dbu
        # fetch the parameters
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hdHole = self.hdHole / dbu
        off = self.off / dbu

        initial_point = pya.DPoint(0, 0)
        end_point = pya.DPoint(self.xfinal, self.yfinal)

        # distances in dbu
        dx = (end_point.x - initial_point.x) / dbu
        dy = (end_point.y - initial_point.y) / dbu

        create_cpw_S(self, ground, width, gap, hdHole, off, self.vStart, initial_point, dx, dy)
        self.length_dbu = self.length * dbu


class CPW_Cross(pya.PCellDeclarationHelper):
    """
    Cross-shaped dicing markers
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_Cross, self).__init__()

        # declare the parameters
        self.param("lay", self.TypeLayer, "Target Layer", default=pya.LayerInfo(114, 0))
        self.param("size", self.TypeDouble, "size of markers", default=400)
        self.param("width", self.TypeDouble, "width of markers", default=50)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW_Cross (Size = " + ('%.2f' % self.size) + ", width = " + ('%.2f' % self.width) + ")"

    def produce_impl(self):
        dbu = self.layout.dbu
        size = self.size / dbu
        width = self.width / dbu

        self.cell.shapes(self.lay_layer).insert(pya.Polygon(cross(size, width)))


class CPW_S_old(pya.PCellDeclarationHelper):
    """
    S(igmoid) shaped coplanar waveguide - fixed final point with one curve
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_S_old, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("w", self.TypeDouble, "width", default=10)
        self.param("g", self.TypeDouble, "ground", default=50)
        self.param("s", self.TypeDouble, "gap", default=6)
        # self.param("r", self.TypeDouble, "radius", default=39)
        self.param("ioff", self.TypeDouble, "initial offset", default=200)
        self.param("n", self.TypeInt, "Number of points", default=64)
        self.param("hd", self.TypeDouble, "hd hole pattern", default=40)
        self.param("pfinalx", self.TypeDouble, "final point x", default=1000)
        self.param("pfinaly", self.TypeDouble, "final point y", default=1000)

        self.radius = 0

    def display_text_impl(self):
        # radius = self.radius
        ioff = self.ioff
        # Provide a descriptive text for the cell
        return "CPW_Sigmoid (Radius = " + ('%.2f' % self.radius) + ", initial offset = " + ('%.2f' % ioff) + ")"

    def coerce_parameters_impl(self):
        pass

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    # def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's bounding box width and layer
        # self.ln = self.shape.bbox().width() / self.layout.dbu
        # self.l = self.layout.get_info(self.layer)

    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        # enforce minimum number of points in arc
        if self.n < 16:
            self.n = 16
        # define bend radius
        # self.r = round((2 * self.g + self.w + 2 * self.s) / math.pi)
        self.radius = self.hd + self.g + self.s + self.w / 2
        # fetch the parameters
        wu_dbu = self.w / self.layout.dbu
        su_dbu = self.s / self.layout.dbu
        gu_dbu = self.g / self.layout.dbu
        ru_dbu = self.hd / self.layout.dbu
        hdu_dbu = self.hd / self.layout.dbu
        ioffu_dbu = self.ioff / self.layout.dbu
        pfinalx_dbu = self.pfinalx / self.layout.dbu
        pfinaly_dbu = self.pfinaly / self.layout.dbu

        # determine number of bends
        bend_size_dbu = ru_dbu + gu_dbu + su_dbu + wu_dbu / 2
        # bend_len_dbu = (ru_dbu + gu_dbu + su_dbu + wu_dbu / 2) * math.pi / 2
        # nr_bend = 0

        segs = []
        # step 1: clarify if the vertical distance of the ports is less than 2* the bend radius
        if abs(pfinaly_dbu) >= 2 * (bend_size_dbu):  # situation I
            segs.append({'type': "cpw_straight", 'ln': ioffu_dbu, 'orientation': 0})
            # create the bent part
            if pfinaly_dbu > 0:
                segs.append({'type': "cpw_90", 'orientation': "rt"})
                segs.append({'type': "cpw_straight", 'ln': (pfinaly_dbu - 2 * bend_size_dbu), 'orientation': 1})
                segs.append({'type': "cpw_90", 'orientation': "tr"})
            elif pfinaly_dbu < 0:
                segs.append({'type': "cpw_90", 'orientation': "rb"})
                segs.append({'type': "cpw_straight", 'ln': (pfinaly_dbu - 2 * bend_size_dbu), 'orientation': 3})
                segs.append({'type': "cpw_90", 'orientation': "br"})
            else:
                segs.append({'type': "cpw_straight", 'ln': (2 * bend_size_dbu), 'orientation': 0})
                # create the last piece
            segs.append({'type': "cpw_straight", 'ln': (pfinalx_dbu - 2 * bend_size_dbu - ioffu_dbu), 'orientation': 0})

        elif abs(pfinaly_dbu) < 2 * bend_size_dbu:  # situation 2
            segs.append({'type': "cpw_straight", 'ln': ioffu_dbu, 'orientation': 0})
            if pfinaly_dbu > 0:
                segs.append({'type': "cpw_90", 'orientation': "rt"})
                segs.append({'type': "cpw_straight", 'ln': pfinaly_dbu, 'orientation': 1})
                segs.append({'type': "cpw_90", 'orientation': "tr"})
                segs.append({'type': "cpw_90", 'orientation': "rb"})
                segs.append({'type': "cpw_90", 'orientation': "br"})
            elif pfinaly_dbu < 0:
                segs.append({'type': "cpw_90", 'orientation': "rb"})
                segs.append({'type': "cpw_straight", 'ln': pfinaly_dbu, 'orientation': 3})
                segs.append({'type': "cpw_90", 'orientation': "br"})
                segs.append({'type': "cpw_90", 'orientation': "rt"})
                segs.append({'type': "cpw_90", 'orientation': "tr"})
            segs.append({'type': "cpw_straight", 'ln': (pfinalx_dbu - ioffu_dbu - 4 * bend_size_dbu), 'orientation': 0})

        # create the shape
        curr_point_dbu = pya.DPoint(0, 0)
        for elem in segs:
            if elem['type'] == "cpw_90":
                curr_point_dbu = create_cpw_90(self, gu_dbu, su_dbu, wu_dbu, self.n, hdu_dbu,
                                                    curr_point_dbu, elem['orientation'], False)
            elif elem['type'] == "cpw_straight":
                curr_point_dbu = create_cpw_straight(self, elem['ln'], gu_dbu, wu_dbu, su_dbu, hdu_dbu,
                                                     curr_point_dbu, elem['orientation'], False)


class CPW_Meander_old(pya.PCellDeclarationHelper):
    """
    Meandered coplanar waveguide
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_Meander_old, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("ln", self.TypeDouble, "total length", default=4000)
        self.param("w", self.TypeDouble, "width", default=10)
        self.param("g", self.TypeDouble, "ground", default=50)
        self.param("s", self.TypeDouble, "gap", default=6)
        # self.param("r", self.TypeDouble, "radius", default=39)
        self.param("hd", self.TypeDouble, "hd hole pattern", default=40)
        self.param("ioff", self.TypeDouble, "initial length", default=100)
        self.param("n", self.TypeInt, "Number of points", default=64)
        self.param("pfinalx", self.TypeDouble, "final point x", default=1000)
        self.param("pfinaly", self.TypeDouble, "final point y", default=1000)
        self.param("boxh", self.TypeDouble, "box height", default=2000)
        self.param("box0", self.TypeDouble, "box offset", default=0)

        self.calclen = 0
        self.calclen_dbu = 0

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        # clen = self.calclen
        clen = self.calclen_dbu
        return "CPW_Meander (calculated length = " + ('%.2f' % clen) + ")"

    def coerce_parameters_impl(self):
        pass

    def can_create_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we can use any shape which has a finite bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's bounding box width and layer
        self.ln = self.shape.bbox().width() / self.layout.dbu
        # self.l = self.layout.get_info(self.layer)
    #
    def transformation_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we use the center of the shape's bounding box to determine the transformation
        return pya.Trans(self.shape.bbox().center())

    def produce_impl(self):
        # enforce minimum number of points in arc
        if self.n < 16:
            self.n = 16
        # define bend radius
        # self.r = round((2 * self.g + self.w + 2 * self.s) / math.pi)
        self.r = self.hd
        # fetch the parameters
        dbu = self.layout.dbu
        lnu_dbu = self.ln / dbu
        wu_dbu = self.w / dbu
        su_dbu = self.s / dbu
        gu_dbu = self.g / dbu
        ru_dbu = self.r / dbu
        hdu_dbu = self.hd / dbu
        ioffu_dbu = self.ioff / dbu
        pfinalx_dbu = self.pfinalx / dbu
        pfinaly_dbu = self.pfinaly / dbu

        boxhu_dbu = self.boxh / dbu
        box0u_dbu = self.box0 / dbu

        # determine number of bends
        bend_size_dbu = ru_dbu + gu_dbu + su_dbu + wu_dbu / 2
        bend_len_dbu = (ru_dbu + gu_dbu + su_dbu + wu_dbu / 2) * math.pi / 2
        # nr_bend = 0

        segs = []

        if lnu_dbu < pfinalx_dbu:  # there is no way to draw this without curving space-time
            return
        if lnu_dbu < (pfinaly_dbu + 2 * bend_len_dbu + (pfinalx_dbu - 2 * (
                bend_size_dbu))):  # if there is an offset in y we need to add two bends and the total length must be at least of that size
            return

        # determine minimum and maximum length for a given number of bends constrained by a bounding box
        nr_units = -1  # one unit cell is a sigmoid shape (1 bend - 1 straight - 1 bend)
        # max_len = 0
        max_nrb = 10

        h = boxhu_dbu  # just a renaming
        pfy = abs(pfinaly_dbu)  # renaming and taking absolute value; idea is to mirror the meander in case pfy is negative afterwards
        di = box0u_dbu + pfy / 2  # distance from origin to center of bounding box
        df = box0u_dbu - pfy / 2  # distance from final point to center of bounding box
        mirror = False
        if pfinaly_dbu < 0: mirror = True
        pfx = pfinalx_dbu  # just a renaming
        bs = bend_size_dbu  # just a renaming
        bl = bend_len_dbu  # just a renaming

        # now we differentiate between the different cases of position of the bounding box relative to origin/final point

        # max_len = []
        if (di + h / 2) < 0:  # case 1
            max_len = [(pfy + (i + 1) * h + (2 * i + 2) * bl + pfx - 2 * (2 * i + 2) * bs) for i in range(0, max_nrb)]
            for nr in range(0, max_nrb):
                if lnu_dbu > max_len[nr] and (nr % 2) == 0:
                    nr_units = nr + 1

        elif (di - h / 2) <= 0 and (di + h / 2) >= 0 and (di + h / 2) < pfy:  # case 2
            max_len = [(pfy + i * h + (2 * i + 2) * bl + pfx - 2 * (2 * i + 2) * bs) for i in range(0, max_nrb)]
            for nr in range(0, max_nrb):
                if lnu_dbu > max_len[nr] and (nr % 2) == 1:
                    nr_units = nr + 1

        elif (di - h / 2) > 0 and (di + h / 2) < pfy:  # case 3
            max_len = [(pfy + i * h + (2 * i + 1) * bl + pfx - (2 * i + 1) * bs) for i in range(0, max_nrb)]
            for nr in range(0, max_nrb):
                if lnu_dbu > max_len[nr] and (nr % 2) == 1:
                    nr_units = nr + 1

        elif (di - h / 2) <= 0 and (di + h / 2) >= pfy:  # case 4
            max_len = [(pfy + i * h + (2 * i + 4) * bl + pfx - 2 * (2 * i + 4) * bs) for i in range(0, max_nrb)]
            for nr in range(0, max_nrb):
                if lnu_dbu > max_len[nr] and (nr % 2) == 1:
                    nr_units = nr + 1

        elif (di - h / 2) > 0 and (di - h / 2) < pfy and (di + h / 2) >= pfy:  # case 5
            max_len = [(pfy + i * h + (2 * i + 2) * bl + pfx - (2 * i + 2) * bs) for i in range(0, max_nrb)]
            for nr in range(0, max_nrb):
                if lnu_dbu > max_len[nr] and (nr % 2) == 1:
                    nr_units = nr + 1

        elif (di - h / 2) >= pfy:  # case 6
            max_len = [(pfy + (i - 1) * h + (2 * i + 2) * bl + pfx - (2 * i + 2) * bs) for i in range(0, max_nrb)]
            for nr in range(0, max_nrb):
                if lnu_dbu > max_len[nr] and (nr % 2) == 0:
                    nr_units = nr + 1

        acc_err = 0
        if (di + h / 2 + bs) < 0:  # case 1
            initpiecex = ioffu_dbu
            initpiecey = round((abs(di + h / 2) - bs) / 1000) * 1000
            endpiecex = round((pfx - ioffu_dbu - (2 * nr_units + 2) * bs) / 1000) * 1000
            endpiecey = round((pfy - bs + abs(di + h / 2)) / 1000) * 1000

            segs.append({'type': "cpw_straight", 'ln': initpiecex, 'orientation': 0})
            # if pfinaly_dbu > 0:
            dirsb = ["rb", "br", "rt", "tr"]
            dirss = [1, 3]
            # else:
            # dirsb = ["rt","tr","rb","br"] # directions of bends
            # dirss = [1,3] # direction of straights

            segs.append({'type': "cpw_90", 'orientation': dirsb[0]})
            segs.append({'type': "cpw_straight", 'ln': initpiecey, 'orientation': dirss[1]})
            self.calclen = initpiecex + bl + initpiecey
            rem_len = lnu_dbu - initpiecex - initpiecey - endpiecex - endpiecey - (2 * nr_units + 2) * bl

            for index in range(0, nr_units, 2):
                # segs.append({'type':"cpw_straight",'ln':round((h-bs)/1000)*1000,'orientation':dirss[0]})
                segs.append({'type': "cpw_straight", 'ln': round(rem_len / (nr_units + 1) / 1000) * 1000,
                             'orientation': dirss[1]})
                acc_err += rem_len / nr_units - round(rem_len / (nr_units) / 1000) * 1000
                segs.append({'type': "cpw_90", 'orientation': dirsb[1]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
                # segs.append({'type':"cpw_straight",'ln':round((h-bs)/1000)*1000,'orientation':dirss[1]})
                segs.append({'type': "cpw_straight", 'ln': round(rem_len / (nr_units + 1) / 1000) * 1000,
                             'orientation': dirss[0]})
                # self.calclen += 2* round((h-bs)/1000)*1000 + 2*bl
                self.calclen += 2 * round(rem_len / (nr_units + 1) / 1000) * 1000 + 2 * bl
                if index != (nr_units - 1):
                    segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
                    segs.append({'type': "cpw_90", 'orientation': dirsb[0]})
                    self.calclen += 2 * bl
            # last straight piece
            # segs.append({'type':"cpw_straight",'ln':round((pfy-bs+abs(di+h/2))/1000)*1000,'orientation':dirss[1]})
            segs.append({'type': "cpw_straight", 'ln': endpiecey, 'orientation': dirss[0]})
            segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
            self.calclen += endpiecey + bl + round(acc_err / 1000) * 1000
            segs.append({'type': "cpw_straight", 'ln': endpiecex, 'orientation': 0})
            self.calclen += endpiecex

        elif (di - h / 2) <= 0 and (di + h / 2) >= 0 and (di + h / 2) < pfy:  # case 2
            initpiecex = ioffu_dbu
            initpiecey = round((abs(di + h / 2) - bs) / 1000) * 1000
            endpiecex = round((pfx - ioffu_dbu - (2 * nr_units + 1) * bs) / 1000) * 1000
            endpiecey = round((pfy - bs - abs(di + h / 2)) / 1000) * 1000

            segs.append({'type': "cpw_straight", 'ln': initpiecex, 'orientation': 0})
            # if pfinaly_dbu > 0:
            dirsb = ["rb", "br", "rt", "tr"]
            dirss = [1, 3]
            # else:
            # dirsb = ["rt","tr","rb","br"] # directions of bends
            # dirss = [1,3] # direction of straights

            segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
            segs.append({'type': "cpw_straight", 'ln': initpiecey, 'orientation': dirss[0]})
            self.calclen = initpiecex + bl + initpiecey
            rem_len = lnu_dbu - initpiecex - initpiecey - endpiecex - endpiecey - (2 * nr_units + 2) * bl
            acc_err = 0
            for index in range(0, nr_units - 1, 2):
                # segs.append({'type':"cpw_straight",'ln':round((h-bs)/1000)*1000,'orientation':dirss[0]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[0]})
                # segs.append({'type':"cpw_straight",'ln':round((h-bs)/1000)*1000,'orientation':dirss[1]})
                segs.append(
                    {'type': "cpw_straight", 'ln': round(rem_len / (nr_units) / 1000) * 1000, 'orientation': dirss[1]})
                acc_err += rem_len / nr_units - round(rem_len / (nr_units) / 1000) * 1000
                # self.calclen += 2* round((h-bs)/1000)*1000 + 2*bl
                self.calclen += round(rem_len / (nr_units) / 1000) * 1000 + 2 * bl
                if index != (nr_units):
                    segs.append({'type': "cpw_90", 'orientation': dirsb[1]})
                    segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
                    segs.append({'type': "cpw_straight", 'ln': round(rem_len / (nr_units) / 1000) * 1000,
                                 'orientation': dirss[0]})
                    acc_err += (rem_len / (nr_units) - round(rem_len / (nr_units) / 1000) * 1000)
                    self.calclen += round(rem_len / (nr_units) / 1000) * 1000 + 2 * bl
            # last straight piece
            # segs.append({'type':"cpw_straight",'ln':round((pfy-bs+abs(di+h/2))/1000)*1000,'orientation':dirss[1]})
            segs.append(
                {'type': "cpw_straight", 'ln': endpiecey - round(acc_err / 1000) * 1000, 'orientation': dirss[0]})
            segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
            self.calclen += endpiecey - round(acc_err / 1000 * 1000) + bl
            segs.append({'type': "cpw_straight", 'ln': endpiecex, 'orientation': 0})
            self.calclen += endpiecex

        elif (di - h / 2) > 0 and (di + h / 2) < pfy:  # case 3
            acc_err = 0
            initpiecex = ioffu_dbu
            initpiecey = (abs(di - h / 2) - bs)
            rnd_initpiecey = math.floor(initpiecey / 1000) * 1000
            err_initpiecey = initpiecey - rnd_initpiecey
            endpiecex = (pfx - ioffu_dbu - (2 * nr_units + 2) * bs)
            rnd_endpiecex = math.floor(endpiecex / 1000) * 1000
            err_endpiecex = endpiecex - rnd_endpiecex
            endpiecey = (pfy - bs - abs(di - h / 2))
            rnd_endpiecey = math.floor(endpiecey / 1000) * 1000
            err_endpiecey = endpiecey - rnd_endpiecey

            segs.append({'type': "cpw_straight", 'ln': initpiecex, 'orientation': 0})
            dirsb = ["rb", "br", "rt", "tr"]
            dirss = [1, 3]

            segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
            segs.append({'type': "cpw_straight", 'ln': rnd_initpiecey, 'orientation': dirss[0]})
            acc_err += err_initpiecey
            self.calclen = initpiecex + bl + rnd_initpiecey
            calcy = rnd_initpiecey
            rem_len = lnu_dbu - initpiecex - rnd_initpiecey - rnd_endpiecex - rnd_endpiecey - (2 * nr_units + 2) * bl
            unit_size = rem_len / nr_units
            rnd_unit_size = math.floor(unit_size / 1000) * 1000
            err_unit_size = unit_size - rnd_unit_size

            for index in range(0, nr_units, 2):
                segs.append({'type': "cpw_straight", 'ln': rnd_unit_size, 'orientation': dirss[0]})
                acc_err += err_unit_size

                segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[0]})
                segs.append({'type': "cpw_straight", 'ln': rnd_unit_size, 'orientation': dirss[1]})
                acc_err -= err_unit_size
                segs.append({'type': "cpw_90", 'orientation': dirsb[1]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
                self.calclen += 2 * rnd_unit_size + 4 * bl
                # last straight piece
            # segs.append({'type':"cpw_straight",'ln':round((pfy-bs+abs(di+h/2))/1000)*1000,'orientation':dirss[1]})
            segs.append({'type': "cpw_straight", 'ln': rnd_endpiecey + math.ceil(acc_err), 'orientation': dirss[0]})
            segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
            segs.append({'type': "cpw_straight", 'ln': rnd_endpiecex, 'orientation': 0})
            self.calclen += rnd_endpiecex + rnd_endpiecey + bl + acc_err

        elif (di - h / 2) <= 0 and (di + h / 2) >= pfy:  # case 4
            initpiecex = ioffu_dbu
            initpiecey = ((abs(di - h / 2) - 2 * bs) / 1000) * 1000
            endpiecex = math.ceil((pfx - ioffu_dbu - (2 * nr_units + 4) * bs) / 1000) * 1000
            endpiecey = math.ceil((pfy + abs(di - h / 2) - 2 * bs) / 1000) * 1000

            segs.append({'type': "cpw_straight", 'ln': initpiecex, 'orientation': 0})
            dirsb = ["rb", "br", "rt", "tr"]
            dirss = [1, 3]

            segs.append({'type': "cpw_90", 'orientation': dirsb[0]})
            segs.append({'type': "cpw_straight", 'ln': initpiecey, 'orientation': dirss[1]})
            segs.append({'type': "cpw_90", 'orientation': dirsb[1]})
            segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
            self.calclen = initpiecex + initpiecey + 3 * bl
            rem_len = lnu_dbu - initpiecex - initpiecey - endpiecex - endpiecey - (2 * nr_units + 4) * bl
            acc_err = 0
            for index in range(0, nr_units, 2):
                segs.append({'type': "cpw_straight", 'ln': math.ceil(rem_len / (nr_units) / 1000) * 1000,
                             'orientation': dirss[0]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[0]})
                self.calclen += 2 * math.ceil(rem_len / (nr_units) / 1000) * 1000 + 4 * bl
                segs.append({'type': "cpw_straight", 'ln': math.ceil(rem_len / (nr_units) / 1000) * 1000,
                             'orientation': dirss[1]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[1]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
            # last straight piece
            # segs.append({'type':"cpw_straight",'ln':math.ceil((pfy-bs+abs(di+h/2))/1000)*1000,'orientation':dirss[1]})
            segs.append(
                {'type': "cpw_straight", 'ln': endpiecey - math.ceil(acc_err / 1000) * 1000, 'orientation': dirss[0]})
            segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
            segs.append({'type': "cpw_straight", 'ln': endpiecex, 'orientation': 0})
            self.calclen += endpiecex + endpiecey + bl - math.ceil(acc_err / 1000) * 1000

        elif (di - h / 2) > 0 and (di - h / 2) < pfy and (di + h / 2) >= pfy:  # case 5
            initpiecex = ioffu_dbu
            initpiecey = math.ceil((abs(di - h / 2) - bs) / 1000) * 1000
            endpiecex = math.ceil((pfx - ioffu_dbu - (2 * nr_units + 2) * bs) / 1000) * 1000
            endpiecey = math.ceil((pfy - bs - abs(di - h / 2)) / 1000) * 1000

            segs.append({'type': "cpw_straight", 'ln': initpiecex, 'orientation': 0})
            dirsb = ["rb", "br", "rt", "tr"]
            dirss = [1, 3]

            segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
            segs.append({'type': "cpw_straight", 'ln': initpiecey, 'orientation': dirss[0]})
            self.calclen = initpiecex + bl + initpiecey
            rem_len = lnu_dbu - initpiecex - initpiecey - endpiecex - endpiecey - (2 * nr_units + 2) * bl
            for index in range(0, nr_units, 2):
                segs.append({'type': "cpw_straight", 'ln': math.ceil(rem_len / (nr_units) / 1000) * 1000,
                             'orientation': dirss[0]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[0]})
                segs.append({'type': "cpw_straight", 'ln': math.ceil(rem_len / (nr_units) / 1000) * 1000,
                             'orientation': dirss[1]})
                self.calclen += 2 * math.ceil(rem_len / (nr_units) / 1000) * 1000 + 4 * bl
                segs.append({'type': "cpw_90", 'orientation': dirsb[1]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
            # last straight piece
            # segs.append({'type':"cpw_straight",'ln':math.ceil((pfy-bs+abs(di+h/2))/1000)*1000,'orientation':dirss[1]})
            segs.append({'type': "cpw_straight", 'ln': endpiecey, 'orientation': dirss[0]})
            segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
            segs.append({'type': "cpw_straight", 'ln': endpiecex, 'orientation': 0})
            self.calclen += endpiecex + endpiecey + bl

        elif (di - h / 2) >= pfy:  # case 6
            initpiecex = ioffu_dbu
            initpiecey = math.ceil((abs(di - h / 2) - bs) / 1000) * 1000
            endpiecex = math.ceil((pfx - ioffu_dbu - (2 * nr_units + 2) * bs) / 1000) * 1000
            endpiecey = math.ceil((abs(df - h / 2) - bs) / 1000) * 1000

            segs.append({'type': "cpw_straight", 'ln': initpiecex, 'orientation': 0})
            # if pfinaly_dbu > 0:
            dirsb = ["rb", "br", "rt", "tr"]
            dirss = [1, 3]
            # else:
            # dirsb = ["rt","tr","rb","br"] # directions of bends
            # dirss = [1,3] # direction of straights

            segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
            segs.append({'type': "cpw_straight", 'ln': initpiecey, 'orientation': dirss[0]})
            self.calclen = initpiecex + bl + initpiecey
            rem_len = lnu_dbu - initpiecex - initpiecey - endpiecex - endpiecey - (2 * nr_units + 2) * bl
            for index in range(0, nr_units, 2):
                segs.append({'type': "cpw_straight", 'ln': math.ceil(rem_len / (nr_units + 1) / 1000) * 1000,
                             'orientation': dirss[0]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[3]})
                segs.append({'type': "cpw_90", 'orientation': dirsb[0]})
                segs.append({'type': "cpw_straight", 'ln': math.ceil(rem_len / (nr_units + 1) / 1000) * 1000,
                             'orientation': dirss[1]})
                self.calclen += 2 * math.ceil(rem_len / (nr_units + 1) / 1000) * 1000 + 2 * bl
                if index != (nr_units - 1):
                    segs.append({'type': "cpw_90", 'orientation': dirsb[1]})
                    segs.append({'type': "cpw_90", 'orientation': dirsb[2]})
                    self.calclen += 2 * bl
            # last straight piece
            # segs.append({'type':"cpw_straight",'ln':round((pfy-bs+abs(di+h/2))/1000)*1000,'orientation':dirss[1]})
            segs.append({'type': "cpw_straight", 'ln': endpiecey, 'orientation': dirss[1]})
            segs.append({'type': "cpw_90", 'orientation': dirsb[1]})
            segs.append({'type': "cpw_straight", 'ln': endpiecex, 'orientation': 0})
            self.calclen += endpiecex + endpiecey + bl

        # final length in micrometers
        self.calclen_dbu = self.calclen * dbu

        # create the shape
        curr_point_dbu = pya.DPoint(0, 0)
        for elem in segs:
            if elem['type'] == "cpw_90":
                curr_point_dbu = create_cpw_90(self, gu_dbu, su_dbu, wu_dbu, self.n, hdu_dbu, curr_point_dbu, elem['orientation'], mirror)
            elif elem['type'] == "cpw_straight":
                curr_point_dbu = create_cpw_straight(self, elem['ln'], gu_dbu, wu_dbu, su_dbu, hdu_dbu, curr_point_dbu, elem['orientation'], mirror)

        # self.cell.transform(self,pya.CplxTrans.M0)
        if mirror:
            t = pya.ICplxTrans.M0
        else:
            t = pya.ICplxTrans.R0

        for inst in self.cell.each_inst():
            inst.transform(t)

        for layer_index in self.layout.layer_indexes():
            for shape in self.cell.each_shape(layer_index):
                shape.transform(t)


class Mask(pya.Library):
    """
    The library containing elements for creating a superconducting circuit mask.
    """

    def __init__(self):
        # Set the description
        self.description = "Circuit Elements Library"

        # Create the PCell declarations
        self.layout().register_pcell("CPW_Straight", CPW_Straight())
        self.layout().register_pcell("CPW_90", CPW_90())
        self.layout().register_pcell("CPW_End", CPW_End())
        self.layout().register_pcell("CPW_Simple", CPW_Simple())
        self.layout().register_pcell("CPW_Res", CPW_Res())
        self.layout().register_pcell("CPW_ResInd", CPW_ResInd())
        self.layout().register_pcell("CPW_OneRes", CPW_OneRes())
        self.layout().register_pcell("CPW_TwoRes", CPW_TwoRes())
        self.layout().register_pcell("CPW_ResCoupler", CPW_ResCoupler())
        self.layout().register_pcell("CPW_IndCoupler", CPW_IndCoupler())
        self.layout().register_pcell("CPW_MeanderSimple", CPW_MeanderSimple())
        self.layout().register_pcell("CPW_Port", CPW_Port())
        self.layout().register_pcell("CPW_Coupler", CPW_Coupler())
        self.layout().register_pcell("CPW_S", CPW_S())
        self.layout().register_pcell("CPW_Cross", CPW_Cross())
        self.layout().register_pcell("Hole_Pattern", Hole_Pattern())
        self.layout().register_pcell("CPW_Parallel", CPW_Parallel())
        self.layout().register_pcell("CPW_S_old", CPW_S_old())
        self.layout().register_pcell("CPW_Meander_old", CPW_Meander_old())
        self.layout().register_pcell("CPW_Straight_Fingers", CPW_Straight_Fingers())
        # Register the library with the name "cQED".
        # If a library with that name already existed, it will be replaced
        self.register("cQED")


# Instantiate and register the library
Mask()
