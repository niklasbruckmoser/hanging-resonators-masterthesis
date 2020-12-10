import klayout.db as pya
import numpy as np

"""
@deprecated
Use the new CPWLibrary instead
"""

# extracted data from txline for 50 ohm impedance for 525um substrate and 0.15um film, assuming ground beneath
x_data = [0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300]
y_data = [0,12,23,35,47,59,72,86,100,116,133,152,172,196,223,250]


def polyfit_with_fixed_points(x, y, xf, yf):
    """
    Method for fitting data and forcing through a point
    @param x: x data
    @param y: y data
    @param xf: forced x
    @param yf: forced y
    @return: params for a 3rd order fit
    """
    n = 3  # 3rd order polynomial fit is sufficient
    mat = np.empty((n + 1 + len(xf),) * 2)
    vec = np.empty((n + 1 + len(xf),))
    x_n = x**np.arange(2 * n + 1)[:, None]
    yx_n = np.sum(x_n[:n + 1] * y, axis=1)
    x_n = np.sum(x_n, axis=1)
    idx = np.arange(n + 1) + np.arange(n + 1)[:, None]
    mat[:n + 1, :n + 1] = np.take(x_n, idx)
    xf_n = xf**np.arange(n + 1)[:, None]
    mat[:n + 1, n + 1:] = xf_n / 2
    mat[n + 1:, :n + 1] = xf_n.T
    mat[n + 1:, n + 1:] = 0
    vec[:n + 1] = yx_n
    vec[n + 1:] = yf
    params = np.linalg.solve(mat, vec)
    return params[:n + 1]


class CPW_Port_Smoothed(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide port
    """

    def __init__(self):
        # Important: initialize the super class
        super(CPW_Port_Smoothed, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length_taper", self.TypeDouble, "taper length", default=300)
        self.param("length_port", self.TypeDouble, "port length", default=200)
        self.param("width_port", self.TypeDouble, "width port", default=140)  # 140
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
        width_cpw = self.width / dbu
        gap_cpw = self.gap / dbu
        ground = self.ground / dbu
        hole = self.hole / dbu
        # create shape

        create_smooth_port(self, length_taper, length_port, width_port, width_cpw, gap_cpw, ground, hole)


def create_smooth_port(obj, length_taper, length_port, width_port, width_cpw, gap_cpw, ground, hole):
    """
    Main method for creating the port - contains the geometry
    @param length_taper: taper length
    @param length_port: length of the port - not including taper length
    @param width_port: width of the port
    @param width_cpw: width of the CPW
    @param gap_cpw: gap of the CPW
    @param ground: ground size (area without holes)
    @param hole: high density hole mask
    """
    dbu = obj.layout.dbu
    w_list = []
    gap_list = []
    ground_list = []
    mask_list = []
    hole_list = []

    get_gap = np.polynomial.Polynomial(polyfit_with_fixed_points(np.array(x_data), np.array(y_data),
                                                                    np.array([width_cpw*dbu]), np.array([gap_cpw*dbu])))

    gap_max = int(get_gap(width_port*dbu) / dbu)


    hole_list.append(pya.DPoint(0, width_port/2+gap_max+ground+hole))
    mask_list.append(pya.DPoint(hole, width_port/2+gap_max+ground))
    ground_list.append(pya.DPoint(hole, width_port/2+gap_max+ground))
    gap_list.append(pya.DPoint(hole+ground, width_port/2+gap_max))
    w_list.append(pya.DPoint(hole+ground+gap_max, width_port/2))

    x_offset = hole + ground + gap_max + length_port

    for z in np.linspace(0, 1, 100):
        h_w = get_height(z)*(width_port-width_cpw)/2+width_cpw/2
        h_g = int(get_gap(2*h_w*dbu) / dbu)

        w_list.append(pya.DPoint(x_offset + z * length_taper, h_w))
        gap_list.append(pya.DPoint(x_offset + z * length_taper, h_w + h_g))
        ground_list.append(pya.DPoint(x_offset + z * length_taper, h_w + h_g + ground))
        mask_list.append(pya.DPoint(x_offset + z * length_taper, h_w + h_g + ground))
        hole_list.append(pya.DPoint(x_offset + z * length_taper, h_w + h_g + ground + hole))

    for z in np.linspace(1, 0, 100):
        h_w = get_height(z)*(width_port-width_cpw)/2+width_cpw/2
        h_g = int(get_gap(2*h_w*dbu) / dbu)

        w_list.append(pya.DPoint(x_offset + z * length_taper, -h_w))
        gap_list.append(pya.DPoint(x_offset + z * length_taper, -(h_w + h_g)))
        ground_list.append(pya.DPoint(x_offset + z * length_taper, -(h_w + h_g + ground)))
        mask_list.append(pya.DPoint(x_offset + z * length_taper, -(h_w + h_g + ground)))
        hole_list.append(pya.DPoint(x_offset + z * length_taper, -(h_w + h_g + ground + hole)))

    hole_list.append(pya.DPoint(0, -(width_port/2+gap_max+ground+hole)))
    mask_list.append(pya.DPoint(hole, -(width_port/2+gap_max+ground)))
    ground_list.append(pya.DPoint(hole, -(width_port/2+gap_max+ground)))
    gap_list.append(pya.DPoint(hole+ground, -(width_port/2+gap_max)))
    w_list.append(pya.DPoint(hole+ground+gap_max, -(width_port/2)))

    shift = pya.ICplxTrans(1, 0, False, -(length_taper+length_port+gap_max+ground+hole), 0)

    l1 = obj.layout.layer(1, 0)
    l2 = obj.layout.layer(2, 0)
    l3 = obj.layout.layer(3, 0)
    l10 = obj.layout.layer(10, 0)
    l11 = obj.layout.layer(11, 0)

    obj.cell.shapes(l1).insert(pya.Polygon(w_list).transformed(shift))
    obj.cell.shapes(l2).insert(pya.Polygon(gap_list).transformed(shift))
    obj.cell.shapes(l3).insert(pya.Polygon(ground_list).transformed(shift))
    obj.cell.shapes(l10).insert(pya.Polygon(mask_list).transformed(shift))
    obj.cell.shapes(l11).insert(pya.Polygon(hole_list).transformed(shift))

    processor = pya.ShapeProcessor()

    processor.boolean(obj.layout, obj.cell, l3, obj.layout, obj.cell, l2, obj.cell.shapes(l2),
                      pya.EdgeProcessor.ModeANotB, True, True, True)

    processor.boolean(obj.layout, obj.cell, l11, obj.layout, obj.cell, l10, obj.cell.shapes(l11),
                      pya.EdgeProcessor.ModeANotB, True, True, True)

    obj.cell.shapes(l1).insert(obj.cell.shapes(l2))
    obj.layout.clear_layer(l2)
    obj.layout.clear_layer(l3)


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


# TODO better structure?
def max_port_gap(width_port, width_cpw, gap_cpw):
    """
    Get the port gap for a corresponding port width. Needs the width and gap of the CPW, because the gap value is
    extracted from a fit that matches the CPW sizes.
    @param width_port: width of the port
    @param width_cpw: width of the CPW
    @param gap_cpw: gap of the CPW
    @return:
    """
    get_gap = np.polynomial.Polynomial(polyfit_with_fixed_points(np.array(x_data), np.array(y_data),
                                                                 np.array([width_cpw]), np.array([gap_cpw])))
    return get_gap(width_port)


class Mask(pya.Library):
    """
    The library containing elements for creating a superconducting circuit mask.
    """

    def __init__(self):
        # Set the description
        self.description = "CPW Library"

        # Create the PCell declarations
        self.layout().register_pcell("CPW_Port_Smooth", CPW_Port_Smoothed())
        # Register the library with the name "cQED".
        # If a library with that name already existed, it will be replaced
        self.register("qCPW")


# Instantiate and register the library
Mask()