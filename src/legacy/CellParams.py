import klayout.db as pya
import src.library.KLayout.Curve as Curve
import src.library.KLayout.Straight as Straight
import src.library.KLayout.Port as Port
import src.library.KLayout.CustomPort as CustomPort

"""
This File contains all necessary parameters for the cQED klayout library. Each class has an as_list() method which 
returns a dictionary for the corresponding PCell in the library.
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


class CurveParams:

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
        return Curve.end_point(self.radius, self.angle, self.right_curve, self.width, self.gap, self.ground, self.hole)

    def rotation(self):
        return self.angle if self.right_curve == 0 else -self.angle

    def as_list(self):
        return {"radius": self.radius, "angle": self.angle, "right_curve": self.right_curve, "width": self.width,
                "gap": self.gap, "ground": self.ground, "hole": self.hole}


class PortParams:
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
        return Port.end_point(self.length_taper, self.length_port, self.width_port, self.spacing, self.width, self.gap,
                              self.ground, self.hole)

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"length_taper": self.length_taper, "length_port": self.length_port, "width_port": self.width_port,
                "spacing": self.spacing, "width": self.width, "gap": self.gap, "ground": self.ground, "hole": self.hole}


class CustomPortParams:
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
        return CustomPort.end_point(self.length_taper, self.length_port, self.width_port, self.gap_port, self.spacing, self.width, self.gap,
                              self.ground, self.hole)

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"length_taper": self.length_taper, "length_port": self.length_port, "width_port": self.width_port, "gap_port": self.gap_port,
                "spacing": self.spacing, "width": self.width, "gap": self.gap, "ground": self.ground, "hole": self.hole}


class StraightParams:

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
        return Straight.end_point(self.length)

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"length": self.length, "width": self.width, "gap": self.gap, "ground": self.ground, "hole": self.hole}


class StraightFingersParams:

    def __init__(self, length=100, width=10, gap=6, ground=50, hole=40, n_fingers=4, finger_length=26, finger_end_gap=8, finger_spacing=20, hook_width=5, hook_length=3, hook_unit=1, electrode_width=0.5, bridge_width=0.5, bridge_length=1):
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
        return Straight.end_point(self.length)

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


class HoleParams:

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

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"lay": self.lay, "width": self.width, "height": self.height, "spacing": self.spacing,
                "sigma": self.sigma, "size": self.size}


class FingerParams:
    def __init__(self, amount=5, spacing=50, width=10, gap=6, ground=10, hole=40, f_len=20, f_w=16, notch_w=5, notch_d=8, jj_len=12, jj_w=0.9, jj_d=0.5, b_d_f=0.4, b_d_jj=0.2):
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

    def as_list(self):
        return {"amount": self.amount, "spacing": self.spacing, "width": self.width, "gap": self.gap, "ground": self.ground, "hole": self.hole,
                "f_len": self.f_len, "f_w": self.f_w, "notch_w": self.notch_w, "notch_d": self.notch_d,
                "jj_len": self.jj_len, "jj_w": self.jj_w, "jj_d": self.jj_d, "b_d_f": self.b_d_f, "b_d_jj": self.b_d_jj}


class AirbridgeParams:

    def __init__(self, pad_width=100, pad_height=40, gap=35, bridge_pad_width=80, bridge_pad_height=20, bridge_width=40, spacing = 500):
        self.pad_width = pad_width
        self.pad_height = pad_height
        self.gap = gap
        self.brigde_pad_width = bridge_pad_width
        self.brigde_pad_height = bridge_pad_height
        self.bridge_width = bridge_width
        self.spacing = spacing

    def as_list(self):
        return {"pad_width": self.pad_width, "pad_height": self.pad_height, "gap": self.gap,
                "bridge_pad_width": self.brigde_pad_width, "bridge_pad_height": self.brigde_pad_height,
                "bridge_width": self.bridge_width}


class AirbridgeRoundParams:

    def __init__(self, pad_radius=60, gap=35, bridge_pad_radius=50, bridge_width=40):
        self.pad_radius = pad_radius
        self.gap = gap
        self.brigde_pad_radius = bridge_pad_radius
        self.bridge_width = bridge_width

    def as_list(self):
        return {"pad_radius": self.pad_radius, "gap": self.gap, "bridge_pad_radius": self.brigde_pad_radius,
                "bridge_width": self.bridge_width}

class HangingResonatorOldParams:

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

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"segment_length": self.segment_length, "length": self.length, "x_offset": self.x_offset,
                "y_offset": self.y_offset, "q_ext": self.q_ext, "coupling_ground": self.coupling_ground,
                "radius": self.radius, "shorted": self.shorted, "width_tl": self.width_tl, "gap_tl": self.gap_tl, "width": self.width,
                "gap": self.gap, "ground": self.ground, "hole": self.hole}


class HangingResonatorParams:

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

    def as_list(self):
        """
        Returns a param dictionary for creating KLayout cells
        :@return: a dictionary containing all parameters
        """
        return {"segment_length": self.segment_length, "length": self.length, "x_offset": self.x_offset,
                "y_offset": self.y_offset, "coupling_length": self.coupling_length, "coupling_ground": self.coupling_ground,
                "radius": self.radius, "shorted": self.shorted, "width_tl": self.width_tl, "gap_tl": self.gap_tl, "width": self.width,
                "gap": self.gap, "ground": self.ground, "hole": self.hole}

class HangingResonatorFingersParams:

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
