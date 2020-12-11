import klayout.db as pya
import numpy as np
import os
import pickle
import src.coplanar_coupler as coupler

from src.library.CPWLibrary.Straight import create_straight
from src.library.CPWLibrary.StraightFingers import create_straight_fingers
from src.library.CPWLibrary.Curve import create_curve
from src.library.CPWLibrary.End import create_end


class HangingResonatorFingers(pya.PCellDeclarationHelper):
    """
    Hanging Resonator with Fingers
    """

    def __init__(self):
        # Important: initialize the super class
        super(HangingResonatorFingers, self).__init__()

        # declare the parameters
        self.param("segment_length", self.TypeDouble, "segment length", default=700)
        self.param("length", self.TypeDouble, "resonator length", default=4000)
        self.param("x_offset", self.TypeDouble, "x offset", default=0)
        self.param("y_offset", self.TypeDouble, "y offset", default=100)
        self.param("q_ext", self.TypeDouble, "external quality factor", default=1e5)
        self.param("coupling_ground", self.TypeDouble, "coupling ground", default=10)
        self.param("radius", self.TypeDouble, "radius", default=70)
        self.param("shorted", self.TypeInt, "Lambda/4 resonator?", default=1)
        self.param("width_tl", self.TypeDouble, "width of transmission line", default=10)
        self.param("gap_tl", self.TypeDouble, "gap of transmission line", default=6)
        self.param("width", self.TypeDouble, "width cpw", default=10)
        self.param("gap", self.TypeDouble, "gap cpw", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hole", self.TypeDouble, "hole mask", default=40)
        self.param("n_fingers", self.TypeInt, "number of fingers", default=4)
        self.param("finger_length", self.TypeDouble, "finger length", default=26)
        self.param("finger_end_gap", self.TypeDouble, "gap at finger end", default=6)
        self.param("finger_spacing", self.TypeDouble, "spacing between fingers", default=20)
        self.param("hook_width", self.TypeDouble, "hook width", default=5)
        self.param("hook_length", self.TypeDouble, "hook length", default=2.5)
        self.param("hook_unit", self.TypeDouble, "hook unit", default=1)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Hanging Resonator with Fingers"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        segment_length = self.segment_length / dbu
        length = self.length / dbu
        x_offset = self.x_offset / dbu
        y_offset = self.y_offset / dbu
        q_ext = self.q_ext
        coupling_ground = self.coupling_ground / dbu
        radius = self.radius / dbu
        shorted = self.shorted
        width_tl = self.width_tl / dbu
        gap_tl = self.gap_tl / dbu
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hole = self.hole / dbu
        finger_length = self.finger_length / dbu
        finger_end_gap = self.finger_end_gap / dbu
        finger_spacing = self.finger_spacing / dbu
        hook_width = self.hook_width / dbu
        hook_length = self.hook_length / dbu
        hook_unit = self.hook_unit / dbu

        # create shape
        create_res_fingers(self, pya.DPoint(0, 0), 0, segment_length, length, x_offset, y_offset, q_ext,
                           coupling_ground, radius, shorted, width_tl, gap_tl, width, gap, ground, hole, self.n_fingers,
                           finger_length, finger_end_gap, finger_spacing, hook_width, hook_length, hook_unit)


def create_res_fingers(obj, start, rotation, segment_length, length, x_offset, y_offset, q_ext, coupling_ground, radius,
                       shorted, width_tl, gap_tl, width, gap, ground, hole, n_fingers, finger_length, finger_end_gap,
                       finger_spacing, hook_width, hook_length, hook_unit):

    coupling_length = calc_coupling_length(width_tl, gap_tl, width, gap, coupling_ground, length, q_ext)
    # curr = pya.DPoint(start.x-radius-coupling_length, start.y+width+2*gap+coupling_ground)

    curr = pya.DPoint(-segment_length/2+x_offset-coupling_length, start.y+width/2+width_tl/2+gap+gap_tl+coupling_ground)
    create_end(obj, curr, 180+rotation, 0, width, gap, ground, hole)

    curr = create_straight(obj, curr, rotation, coupling_length, width, gap, ground, hole)
    length -= coupling_length
    curr = create_curve(obj, curr, rotation, radius, 90, 0, width, gap, ground, hole)
    length -= np.pi/180*radius*90

    if length < y_offset:
        curr = create_straight_fingers(obj, curr, 90+rotation, length, width, gap, ground, hole, n_fingers, finger_length, finger_end_gap, finger_spacing, hook_width, hook_length, hook_unit)
        create_end(obj, curr, 90+rotation, shorted, width, gap, ground, hole)
        return
    curr = create_straight_fingers(obj, curr, 90+rotation, y_offset, width, gap, ground, hole, n_fingers, finger_length, finger_end_gap, finger_spacing, hook_width, hook_length, hook_unit)
    length -= y_offset

    if length < np.pi/180*radius*90:
        end_angle = 180*length/np.pi/radius
        curr = create_curve(obj, curr, 90+rotation, radius, end_angle, 0, width, gap, ground, hole)
        create_end(obj, curr, 360+end_angle+rotation, shorted, width, gap, ground, hole)
        return
    curr = create_curve(obj, curr, 90+rotation, radius, 90, 0, width, gap, ground, hole)
    length -= np.pi/180*radius*90

    if x_offset == 0:
        x_offset = segment_length
    if length < x_offset:
        curr = create_straight(obj, curr, 180+rotation, length, width, gap, ground, hole)
        create_end(obj, curr, 180+rotation, shorted, width, gap, ground, hole)
        return
    curr = create_straight(obj, curr, 180+rotation, x_offset, width, gap, ground, hole)
    length -= x_offset

    # begin meandering loop

    right = True

    while True:
        if length < np.pi/180*radius*180:
            end_angle = 180*length/np.pi/radius
            curr = create_curve(obj, curr, 180+rotation if right is True else rotation, radius, end_angle, right, width, gap, ground, hole)
            create_end(obj, curr, 180-end_angle+rotation if right else 360+end_angle+rotation, shorted, width, gap, ground, hole)
            return
        curr = create_curve(obj, curr, 180+rotation if right is True else rotation, radius, 180, right, width, gap, ground, hole)
        length -= np.pi/180*radius*180

        if length < segment_length:
            curr = create_straight(obj, curr, rotation if right is True else 180+rotation, length, width, gap, ground, hole)
            create_end(obj, curr, rotation if right else 180+rotation, shorted, width, gap, ground, hole)
            return
        curr = create_straight(obj, curr, rotation if right is True else 180+rotation, segment_length, width, gap, ground, hole)
        length -= segment_length
        right = not right

def calc_coupling_length(width_cpw, gap_cpw, width_res, gap_res, coupling_ground, length, q_ext=1e5):
    """
    Calculates the needed coupling length for achieving a given Q factor. Assuming all lengths in nanometres
     and epsilon_eff = 6.45.
    For reference, see https://doi.org/10.1140/epjqt/s40507-018-0066-3
    :@param l_res: length of the resonator
    :@param intended_q: external Q one wishes to achieve
    :@return: The calculated coupling length
    """
    key = (width_cpw, gap_cpw, width_res, gap_res,
           coupling_ground, 6.45)

    kappa_dict = _load_kappa_dict()

    if key in kappa_dict:
        kappa = kappa_dict[key]
    else:
        print("No value for kappa detected. Calculating new value for determining Q_ext...")
        cpw_c = coupler.coplanar_coupler()
        cpw_c.w1 = width_cpw
        cpw_c.s1 = gap_cpw
        cpw_c.w2 = width_res
        cpw_c.s2 = gap_res
        cpw_c.w3 = coupling_ground
        cpw_c.epsilon_eff = 6.45
        Cl, Ll, Zl = cpw_c.coupling_matrices(mode='notch')
        kappa = Zl[0, 1] / (np.sqrt(Zl[0, 0] * Zl[1, 1]))

        kappa_dict[key] = kappa
        _save_kappa_dict(kappa_dict)

    return int((_v_ph() / (2 * np.pi * calc_f0(length) * 1e9) * np.arcsin(
        np.sqrt(np.pi / (2 * kappa ** 2 * q_ext)))) * 1e9)


def calc_f0(length):
    """
    Calculate a rough estimate for f0. Assuming Si-Air boundary and a lambda/4 resonator.
    :@param length: The length of the resonator in nanometres
    :@return: The resonance frequency in GHz
    """
    return _v_ph() / (4 * length * 1e-9) * 1e-9


def calc_length(f0):
    """
    Calculate a rough estimate for the length. Assuming Si-Air boundary and a lambda/4 resonator.
    :@param f0: The resonance frequency in GHz
    :@return: The length of the resonator in nanometres
    """
    return _v_ph() / (4 * f0 * 1e9) * 1e9


def _v_ph():
    """
    Get the phase velocity for Si-Air
    @return: Approximate phase velocity of light
    """
    return 3e8 / np.sqrt(6.45)



def _load_kappa_dict():
    """
    Load the kappa dictionary for fast calculation of the Quality factor
    @return: Dictionary containing the parameters and associated kappa value
    """
    if not os.path.exists('../kappaValues.txt'):
        _save_kappa_dict({(10, 6, 10, 6, 3, 6.45): 0.11358238085799895})
    with open('../kappaValues.txt', 'rb') as handle:
        return pickle.loads(handle.read())


def _save_kappa_dict(kappa_dict):
    """
    Save the kappa dictionary into a binary (non-readable) file
    @param kappa_dict: Dictionary to save
    """
    with open('../kappaValues.txt', 'wb') as handle:
        pickle.dump(kappa_dict, handle)



