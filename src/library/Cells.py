import klayout.db as pya
import src.library.KLayout.Curve as KCurve
import src.library.KLayout.Straight as KStraight
import src.library.KLayout.Port as KPort
import src.library.KLayout.CustomPort as KCustomPort

"""
This File contains all necessary parameters for the cQED klayout library. Each class has an as_list() method which 
returns a dictionary for the corresponding PCell in the library.
"""

lib_name = "QCL"  # name of the klayout library


class CellObject:
    """
    Cell object for inheritance
    """
    def cell_name(self):
        """
        Cell name for the klayout library
        @return:
        """
        return ""

    def as_list(self):
        """
        Parameter list for the klayout library
        @return:
        """
        return {}


class Curve(CellObject):
    """
    CPW curve
    """
    def __init__(self, radius=101, angle=90, right_curve=1, width=10, gap=6, ground=50, hole=40):
        self.radius = radius
        self.angle = angle
        self.right_curve = right_curve
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole
        pass

    def end_point(self):
        """
        End point of the curve for chaining
        @return: end point of the curve
        """
        return KCurve.end_point(self.radius, self.angle, self.right_curve, self.width, self.gap, self.ground, self.hole)

    def rotation(self):
        """
        Rotation of the curve in degrees
        @return: rotation in degrees
        """
        return self.angle if self.right_curve == 0 else -self.angle

    def cell_name(self):
        """
        Name of the corresponding KLayout cell
        @return: cell name
        """
        return "Curve"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"radius": self.radius, "angle": self.angle, "right_curve": self.right_curve, "width": self.width,
                "gap": self.gap, "ground": self.ground, "hole": self.hole}


class Port(CellObject):
    def __init__(self, width_port=160, length_taper=300, length_port=140, spacing=0, width=10, gap=6, ground=50, hole=40):
        """
        Initializes smooth port parameters from the own KLayout library.
        :@param cp: Related chip params
        """
        self.spacing = spacing
        self.width_port = width_port
        self.length_taper = length_taper
        self.length_port = length_port
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole

    def end_point(self):
        """
        Calculates the x position for the (right, mirrored) port, i.e. -port_x is the start position for the left port
        @return: x position for the right mirrored port
        """
        return KPort.end_point(self.length_taper, self.length_port, self.width_port, self.spacing, self.width, self.gap,
                              self.ground, self.hole)

    def cell_name(self):
        return "Port"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"length_taper": self.length_taper, "length_port": self.length_port, "width_port": self.width_port,
                "spacing": self.spacing, "width": self.width, "gap": self.gap, "ground": self.ground, "hole": self.hole}


class CustomPort(CellObject):
    def __init__(self, width_port=160, gap_port=100, length_taper=300, length_port=140, spacing=0, width=10, gap=6, ground=50, hole=40):
        """
        Initializes smooth port parameters from the own KLayout library.
        :@param cp: Related chip params
        """
        self.spacing = spacing
        self.width_port = width_port
        self.gap_port = gap_port
        self.length_taper = length_taper
        self.length_port = length_port
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole

    def end_point(self):
        """
        Calculates the x position for the (right, mirrored) port, i.e. -port_x is the start position for the left port
        @return: x position for the right mirrored port
        """
        return KCustomPort.end_point(self.length_taper, self.length_port, self.width_port, self.gap_port, self.spacing, self.width, self.gap,
                                    self.ground, self.hole)

    def cell_name(self):
        return "CustomPort"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"length_taper": self.length_taper, "length_port": self.length_port, "width_port": self.width_port, "gap_port": self.gap_port,
                "spacing": self.spacing, "width": self.width, "gap": self.gap, "ground": self.ground, "hole": self.hole}


class Straight(CellObject):

    def __init__(self, length=100, width=10, gap=6, ground=50, hole=40):
        """
        Initializes transmission line parameters.
        :@param cp: Related chip params
        """
        self.length = length
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole

    def end_point(self):
        return KStraight.end_point(self.length)
    
    def cell_name(self):
        return "Straight"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"length": self.length, "width": self.width, "gap": self.gap, "ground": self.ground, "hole": self.hole}


class StraightFingers(CellObject):

    def __init__(self, length=100, width=10, gap=6, ground=50, hole=40, n_fingers=4, finger_length=26, finger_end_gap=8,
                 finger_spacing=20, hook_width=5, hook_length=3, hook_unit=1, electrode_width=0.5, bridge_width=0.5,
                 bridge_length=1):
        """
        Initializes transmission line parameters.
        :@param cp: Related chip params
        """
        self.length = length
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole
        self.n_fingers = n_fingers
        self.finger_length = finger_length
        self.finger_end_gap = finger_end_gap
        self.finger_spacing = finger_spacing
        self.hook_width = hook_width
        self.hook_length = hook_length
        self.hook_unit = hook_unit
        self.electrode_width = electrode_width
        self.bridge_width = bridge_width
        self.bridge_length = bridge_length

    def end_point(self):
        return KStraight.end_point(self.length)
    
    def cell_name(self):
        return "StraightFingers"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"length": self.length, "width": self.width, "gap": self.gap, "ground": self.ground, "hole": self.hole,
                "n_fingers": self.n_fingers, "finger_length": self.finger_length, "finger_end_gap": self.finger_end_gap,
                "finger_spacing": self.finger_spacing, "hook_width": self.hook_width, "hook_length": self.hook_length,
                "hook_unit": self.hook_unit, "electrode_width": self.electrode_width, "bridge_width": self.bridge_width,
                "bridge_length": self.bridge_length}


class EndPart(CellObject):

    def __init__(self, short=0, width=10, gap=6, ground=50, hole=40):
        self.short = short
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole

    def cell_name(self):
        return "PEnd"

    def as_list(self):
        return {"short": self.short, "width": self.width, "gap": self.gap, "ground": self.ground, "hole": self.hole}

class HoleMask(CellObject):

    def __init__(self, width, height, spacing, sigma, size, hd_holes):
        """
        Initializes hole parameters.
        :@param cp: Related chip params
        :@param hole_dist: Distance between two holes
        :@param hole_sigma: Random position offset of the holes
        :@param hole_size: Size of the holes
        :@param hd_holes: True if params are used for high density holes
        """
        self.width = width
        self.height = height
        self.spacing = spacing
        self.sigma = sigma
        self.size = size

        self.lay = pya.LayerInfo(12, 0) if not hd_holes else pya.LayerInfo(13, 0)
        
    def cell_name(self):
        return "Hole"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"lay": self.lay, "width": self.width, "height": self.height, "spacing": self.spacing,
                "sigma": self.sigma, "size": self.size}


class Decorator(CellObject):
    '''
    Dummy class for resonator decorators
    '''
    pass


class Finger(Decorator):
    def __init__(self, amount=5, spacing=50, width=10, gap=6, ground=10, hole=40, f_len=20, f_w=16, notch_w=5,
                 notch_d=8, jj_len=12, jj_w=0.9, jj_d=0.5, b_d_f=0.4, b_d_jj=0.2):
        self.amount = amount
        self.spacing = spacing
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole
        self.f_len = f_len
        self.f_w = f_w
        self.notch_w = notch_w
        self.notch_d = notch_d
        self.jj_len = jj_len
        self.jj_w = jj_w
        self.jj_d = jj_d
        self.b_d_f = b_d_f
        self.b_d_jj = b_d_jj
        
    def cell_name(self):
        return "Finger"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"amount": self.amount, "spacing": self.spacing, "width": self.width, "gap": self.gap, "ground": self.ground, "hole": self.hole,
                "f_len": self.f_len, "f_w": self.f_w, "notch_w": self.notch_w, "notch_d": self.notch_d,
                "jj_len": self.jj_len, "jj_w": self.jj_w, "jj_d": self.jj_d, "b_d_f": self.b_d_f, "b_d_jj": self.b_d_jj}


class Airbridge(Decorator):

    def __init__(self, pad_width=100, pad_height=40, gap=35, bridge_pad_width=80, bridge_pad_height=20, bridge_width=40, spacing=500):
        self.pad_width = pad_width
        self.pad_height = pad_height
        self.gap = gap
        self.brigde_pad_width = bridge_pad_width
        self.brigde_pad_height = bridge_pad_height
        self.bridge_width = bridge_width
        self.spacing = spacing
        
    def cell_name(self):
        return "Airbridge"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"pad_width": self.pad_width, "pad_height": self.pad_height, "gap": self.gap,
                "bridge_pad_width": self.brigde_pad_width, "bridge_pad_height": self.brigde_pad_height,
                "bridge_width": self.bridge_width}


class AirbridgeRound(Airbridge):

    def __init__(self, pad_radius=60, gap=35, bridge_pad_radius=50, bridge_width=40, spacing=500):
        self.pad_radius = pad_radius
        self.pad_width = pad_radius
        self.pad_height = pad_radius
        self.gap = gap
        self.brigde_pad_radius = bridge_pad_radius
        self.brigde_pad_width = bridge_pad_radius
        self.bridge_pad_height = bridge_pad_radius
        self.bridge_width = bridge_width

        self.spacing = spacing
        
    def cell_name(self):
        return "AirbridgeRound"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"pad_radius": self.pad_radius, "gap": self.gap, "bridge_pad_radius": self.brigde_pad_radius,
                "bridge_width": self.bridge_width}


class Resonator(CellObject):
    """
    Dummy super class for resonators
    """
    def __init__(self):
        """
        Constructor for defining geometry variables
        """
        self.segment_length = None
        self.length = None
        self.x_offset = None
        self.y_offset = None
        self.coupling_length = None
        self.coupling_ground = None
        self.radius = None
        self.width_tl = None
        self.gap_tl = None
        self.width = None
        self.gap = None
        self.ground = None
        self.hole = None


class HangingResonatorOld(Resonator):

    def __init__(self, segment_length, length, x_offset, y_offset, q_ext, coupling_ground, radius, shorted, width_tl,
                 gap_tl, width, gap, ground, hole):

        self.segment_length = segment_length
        self.length = length
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.q_ext = q_ext
        self.coupling_ground = coupling_ground
        self.radius = radius
        self.shorted = shorted
        self.width_tl = width_tl
        self.gap_tl = gap_tl
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole
    
    def cell_name(self):
        return "HangingResonatorOld"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"segment_length": self.segment_length, "length": self.length, "x_offset": self.x_offset,
                "y_offset": self.y_offset, "q_ext": self.q_ext, "coupling_ground": self.coupling_ground,
                "radius": self.radius, "shorted": self.shorted, "width_tl": self.width_tl, "gap_tl": self.gap_tl, "width": self.width,
                "gap": self.gap, "ground": self.ground, "hole": self.hole}


class HangingResonator(Resonator):

    def __init__(self, segment_length, length, x_offset, y_offset, coupling_length, coupling_ground, radius, shorted, width_tl,
                 gap_tl, width, gap, ground, hole):

        self.segment_length = segment_length
        self.length = length
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.coupling_length = coupling_length
        self.coupling_ground = coupling_ground
        self.radius = radius
        self.shorted = shorted
        self.width_tl = width_tl
        self.gap_tl = gap_tl
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole
        
    def cell_name(self):
        return "HangingResonator"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"segment_length": self.segment_length, "length": self.length, "x_offset": self.x_offset,
                "y_offset": self.y_offset, "coupling_length": self.coupling_length, "coupling_ground": self.coupling_ground,
                "radius": self.radius, "shorted": self.shorted, "width_tl": self.width_tl, "gap_tl": self.gap_tl, "width": self.width,
                "gap": self.gap, "ground": self.ground, "hole": self.hole}

class HangingResonatorFingers(Resonator):
    """
    deprecated
    """

    def __init__(self, segment_length, length, x_offset, y_offset, q_ext, coupling_ground, radius, shorted, width_tl,
                 gap_tl, width, gap, ground, hole, n_fingers, finger_length, finger_end_gap, finger_spacing, hook_width,
                 hook_length, hook_unit, electrode_width, bridge_width, bridge_length):

        self.segment_length = segment_length
        self.length = length
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.q_ext = q_ext
        self.coupling_ground = coupling_ground
        self.radius = radius
        self.shorted = shorted
        self.width_tl = width_tl
        self.gap_tl = gap_tl
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole
        self.n_fingers = n_fingers
        self.finger_length = finger_length
        self.finger_end_gap = finger_end_gap
        self.finger_spacing = finger_spacing
        self.hook_width = hook_width
        self.hook_length = hook_length
        self.hook_unit = hook_unit
        self.electrode_width = electrode_width
        self.bridge_width = bridge_width
        self.bridge_length = bridge_length
        
    def cell_name(self):
        return "HangingResonatorFingers"

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"segment_length": self.segment_length, "length": self.length,
                "x_offset": self.x_offset, "y_offset": self.y_offset, "q_ext": self.q_ext,
                "coupling_ground": self.coupling_ground, "radius": self.radius, "shorted": self.shorted,
                "width_tl": self.width_tl, "gap_tl": self.gap_tl, "width": self.width, "gap": self.gap,
                "ground": self.ground, "hole": self.hole, "n_fingers": self.n_fingers,
                "finger_length": self.finger_length, "finger_end_gap": self.finger_end_gap,
                "finger_spacing": self.finger_spacing, "hook_width": self.hook_width, "hook_length": self.hook_length,
                "hook_unit": self.hook_unit, "electrode_width": self.electrode_width, "bridge_width": self.bridge_width,
                "bridge_length": self.bridge_length}
