import klayout.db as pya

"""
This File contains all necessary parameters for the cQED klayout library. Each class has a list() method which returns
a dictionary for the corresponding PCell in the library.
"""


class ChipParams:

    def __init__(self, chip_w=10000, chip_h=6000, gap=6, width=10, ground=50, hd_holes=40):
        """
        Initializes basic chip parameters.
        :@param chip_w: The width of the chip
        :@param chip_h: The height of the chip
        :@param gap: The gap between the transmission line and ground
        :@param width: The width of the transmission line
        :@param ground: Spacing between the gap and high density holes
        :@param hd_holes: width of the high density hole mask
        """
        self.w = chip_w
        self.h = chip_h

        self.gap = gap
        self.width = width
        self.ground = ground
        self.hd_holes = hd_holes


class PortParams:

    def __init__(self, cp, silver_glue_port=True, spacing=0):
        """
        Initializes port parameters.
        :@param cp: Related chip params
        :@param silver_glue_port:  True if using the silver glue port layout, False for bonding
        :@param spacing: Shifts the params on the x axis towards the center
        """
        self.cp = cp
        self.spacing = spacing

        if silver_glue_port:
            self.port_width = 514
            self.port_gap = 264
            self.port_ground = 50
            self.taper_length = 700
            self.pad_size = 500

        else:
            self.port_width = 140
            self.port_gap = 60
            self.port_ground = 50
            self.taper_length = 300
            self.pad_size = 140

    def port_x(self):
        """
        Calculates the x position for the (right mirrored) port, i.e. -port_x is the start position for the left port
        @return: x position for the right mirrored port
        """
        return self.cp.w/2 - self.taper_length - self.pad_size - self.port_gap - self.spacing

    def list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"width": self.cp.width, "gap": self.cp.gap, "ground": self.cp.ground, "widthPort": self.port_width,
                "gapPort": self.port_gap, "groundPort": self.port_ground, "taperLength": self.taper_length,
                "padSize": self.pad_size, "hdHole": self.cp.hd_holes}


class StraightParams:

    def __init__(self, cp):
        """
        Initializes transmission line parameters.
        :@param cp: Related chip params
        """
        self.cp = cp
        self.length = self.cp.w

    def list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"length": self.length, "width": self.cp.width, "gap": self.cp.gap, "ground": self.cp.ground,
                "hdHole": self.cp.hd_holes}


class HoleParams:

    def __init__(self, cp, hole_dist, hole_sigma, hole_size, hd_holes):
        """
        Initializes hole parameters.
        :@param cp: Related chip params
        :@param hole_dist: Distance between two holes
        :@param hole_sigma: Random position offset of the holes
        :@param hole_size: Size of the holes
        :@param hd_holes: True if params are used for high density holes
        """
        self.cp = cp
        self.dist = hole_dist
        self.sigma = hole_sigma
        self.size = hole_size
        self.layer = pya.LayerInfo(12, 0) if hd_holes is False else pya.LayerInfo(13, 0)

    def list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"lay": self.layer, "x": self.cp.w, "y": self.cp.h, "xd": self.dist, "yd": self.dist,
                "sigma": self.sigma, "hx": self.size, "hy": self.size, "logo": 0}


class ResonatorParams:

    def __init__(self, cp, res_segment_w, res_coupling_ground, res_length, res_mirror, res_lambda_4, res_shift_y,
                 fingers=0, finger_length=26, finger_endgap=8, hook_width=5, hook_length=3, hook_unit=1, hole_length=1):
        """
        Initialize resonator parameters.
        :@param cp: Related chip params
        :@param res_segment_w: Segment width of the resonator (i.e. the length it uses in the TL)
        :@param res_length: Length of the meandering resonator, determines f0
        :@param res_mirror: True, if the design should be mirrored
        :@param res_lambda_4: True, if using lambda/4 resonator design
        :@param res_shift_y: Y-shift of the resonator away from the TL
        :@param fingers: number of fingers to add JJ
        :@param finger_length: length of the fingers
        :@param fingerEndGap: gap between ground and the end of the fingers
        """
        self.cp = cp
        self.segment_w = res_segment_w
        self.coupling_w = 80  # cpw coupling length, will be set dynamic to keep Q_ext in critical coupling region
        self.coupling_ground = res_coupling_ground  # keep fixed - reasonably large for easy fabrication
        self.end_gap = 10  # end capacitor gap, probably fixed
        self.length = res_length
        self.mirror = res_mirror
        self.lambda_4 = res_lambda_4
        self.w = 2*self.segment_w*0.95  # resonator width, 2*res_length seems good for dense packaging
        self.shift_x = self.w/2 - self.cp.ground - self.cp.hd_holes  # initial shift - res_wRes/2

        necessary_shift_y = 2*self.cp.width+(int(fingers/2)+fingers % 2)*(2*self.cp.gap+3*self.cp.width)
        if necessary_shift_y > res_shift_y:
            self.shift_y = necessary_shift_y
        else:
            self.shift_y = res_shift_y

        self.fingers = fingers
        self.fingerLength = finger_length
        self.fingerEndGap = finger_endgap
        self.hookWidth = hook_width
        self.hookLength = hook_length
        self.hookUnit = hook_unit
        self.holeLength = hole_length

    def list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"length": self.segment_w, "cLength": self.coupling_w, "midGround": self.coupling_ground,
                "endGap": self.end_gap, "lRes": self.length, "mirror": self.mirror, "resType": self.lambda_4,
                "wRes": self.w, "shiftRes": self.shift_x, "offRes": self.shift_y, "width": self.cp.width,
                "gap": self.cp.gap, "ground": self.cp.ground, "hdHole": self.cp.hd_holes, "fingers": self.fingers,
                "fingerLength": self.fingerLength, "fingerEndGap": self.fingerEndGap, "hookWidth": self.hookWidth,
                "hookLength": self.hookLength, "hookUnit": self.hookUnit, "holeLength": self.holeLength}
