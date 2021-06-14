import klayout.db as pya
import numpy as np


class CustomPort(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide port with customizable width and gap for the pad (to deviate from 50 ohms impedance)
    """

    def __init__(self):
        # Important: initialize the super class
        super(CustomPort, self).__init__()

        self.param("length_taper", self.TypeDouble, "taper length", default=300)
        self.param("length_port", self.TypeDouble, "port length", default=200)
        self.param("width_port", self.TypeDouble, "width port", default=160)
        self.param("gap_port", self.TypeDouble, "gap port", default=100)
        self.param("spacing", self.TypeDouble, "spacing", default=0)
        self.param("width", self.TypeDouble, "width cpw", default=10)
        self.param("gap", self.TypeDouble, "gap cpw", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hole", self.TypeDouble, "hole mask", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "CPW Port Smoothed"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        length_taper = self.length_taper / dbu
        length_port = self.length_port /dbu
        width_port = self.width_port / dbu
        gap_port = self.gap_port / dbu
        spacing = self.spacing / dbu
        width_cpw = self.width / dbu
        gap_cpw = self.gap / dbu
        ground = self.ground / dbu
        hole = self.hole / dbu
        # create shape

        create_smooth_port(self, pya.DPoint(0, 0), length_taper, length_port, width_port, gap_port, spacing, width_cpw, gap_cpw, ground, hole)


def create_smooth_port(obj, start, length_taper, length_port, width_port, gap_port, spacing, width_cpw, gap_cpw, ground, hole):
    """
    Main method for creating the port - contains the geometry
    @param length_taper: taper length
    @param length_port: length of the port - not including taper length
    @param width_port: width of the port
    @param gap_port: gap of the port
    @param width_cpw: width of the CPW
    @param gap_cpw: gap of the CPW
    @param ground: ground size (area without holes)
    @param hole: high density hole mask
    """
    gap_list = []
    mask_list = []
    hole_list = []

    hole_list.append(pya.DPoint(0, width_port/2+gap_port+ground+hole))
    mask_list.append(pya.DPoint(hole, width_port/2+gap_port+ground))
    gap_list.append(pya.DPoint(hole+ground, width_port/2+gap_port))

    x_offset = hole + ground + gap_port + length_port

    res = 50

    for z in np.linspace(0, 1, res):
        h_w = get_height(z)*(width_port-width_cpw)/2+width_cpw/2
        h_g = get_height(z)*gap_port + (1-get_height(z))+gap_cpw

        hole_list.append(pya.DPoint(x_offset + z * length_taper, h_w + h_g + ground + hole))
        mask_list.append(pya.DPoint(x_offset + z * length_taper, h_w + h_g + ground))
        gap_list.append(pya.DPoint(x_offset + z * length_taper, h_w + h_g))

    for z in np.linspace(1, 0, res):
        h_w = get_height(z)*(width_port-width_cpw)/2+width_cpw/2
        h_g = get_height(z)*gap_port + (1-get_height(z))+gap_cpw

        hole_list.append(pya.DPoint(x_offset + z * length_taper, h_w + h_g + ground))
        mask_list.append(pya.DPoint(x_offset + z * length_taper, -(h_w + h_g + ground)))
        gap_list.append(pya.DPoint(x_offset + z * length_taper, h_w))

    hole_list.append(pya.DPoint(hole, width_port/2+gap_port+ground))
    mask_list.append(pya.DPoint(hole, -(width_port/2+gap_port+ground)))
    gap_list.append(pya.DPoint(hole+ground+gap_port, width_port/2))

    hole_list.append(pya.DPoint(hole, -(width_port/2+gap_port+ground)))
    gap_list.append(pya.DPoint(hole+ground+gap_port, -width_port/2))

    for z in np.linspace(0, 1, res):
        h_w = get_height(z)*(width_port-width_cpw)/2+width_cpw/2
        h_g = get_height(z)*gap_port + (1-get_height(z))+gap_cpw

        hole_list.append(pya.DPoint(x_offset + z * length_taper, -(h_w + h_g + ground)))
        gap_list.append(pya.DPoint(x_offset + z * length_taper, -h_w))

    for z in np.linspace(1, 0, res):
        h_w = get_height(z)*(width_port-width_cpw)/2+width_cpw/2
        h_g = get_height(z)*gap_port + (1-get_height(z))+gap_cpw

        hole_list.append(pya.DPoint(x_offset + z * length_taper, -(h_w + h_g + ground + hole)))
        gap_list.append(pya.DPoint(x_offset + z * length_taper, -(h_w + h_g)))

    hole_list.append(pya.DPoint(0, -(width_port/2+gap_port+ground+hole)))
    gap_list.append(pya.DPoint(hole+ground, -(width_port/2+gap_port)))

    shift = pya.ICplxTrans(1, 0, False, start.x+spacing, start.y)

    l1 = obj.layout.layer(1, 0)
    l10 = obj.layout.layer(10, 0)
    l11 = obj.layout.layer(11, 0)

    obj.cell.shapes(l1).insert(pya.Polygon(gap_list).transformed(shift))
    obj.cell.shapes(l10).insert(pya.Polygon(mask_list).transformed(shift))
    obj.cell.shapes(l11).insert(pya.Polygon(hole_list).transformed(shift))

    return shift*pya.DPoint(length_taper+length_port+gap_port+ground+hole, 0)

def get_height(z):
    """
    Calculates the height to a corresponding x value
    @param z: x coordinate normalized between 0 and 1
    @return: the height normalized between 0 and 1. Returns 1 for z=0 and 0 for z=1
    """
    if z < 0:
        return 1
    if z > 1:
        return 0
    return 2*z**3-3*z**2+1


def end_point(length_taper, length_port, width_port, gap_port, spacing, width_cpw, gap_cpw, ground, hole):
    return pya.DPoint(length_taper+length_port+gap_port+ground+hole+spacing, 0)
