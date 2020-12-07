import klayout.db as pya
import numpy as np

class Curve(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide port
    """

    def __init__(self):
        # Important: initialize the super class
        super(Curve, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("radius", self.TypeDouble, "radius", default=0)
        self.param("angle", self.TypeDouble, "angle in degrees", default=200)
        self.param("right_curve", self.TypeInt, "right facing curve?", default=1)
        self.param("width", self.TypeDouble, "width cpw", default=10)
        self.param("gap", self.TypeDouble, "gap cpw", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hole", self.TypeDouble, "hole mask", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Curve"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        radius = self.radius / dbu
        angle = self.angle
        right_curve = self.right_curve
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hole = self.hole / dbu
        # create shape

        create_curve(self, pya.DPoint(0, 0), 0, radius, angle, right_curve, width, gap, ground, hole)


# angle in degrees
def create_curve(obj, start, rotation, radius, angle, right_curve, width, gap, ground, hole):
    dbu = obj.layout.dbu
    g_u_list = []
    g_l_list = []
    mask_list = []
    hole_u_list = []
    hole_l_list = []

    # min radius check
    # radius = max(radius, width/2+gap+ground+hole)

    # define outer radius as the full circle to the upper hd hole mask
    outer_radius = radius + width/2 + gap + ground + hole

    p_hu = outer_radius
    p_m = outer_radius-hole
    p_gu = outer_radius-hole-ground
    p_gl = outer_radius-hole-ground-gap-width
    p_hl = outer_radius-hole-2*ground-2*gap-width

    mag = radius

    for phi in np.linspace(0, angle, 100):

        ux = np.sin(phi*np.pi/180)
        uy = np.cos(phi*np.pi/180)

        hole_u_list.append(pya.DPoint(ux*p_hu, uy*p_hu-mag))
        mask_list.append(pya.DPoint(ux*p_m, uy*p_m-mag))
        g_u_list.append(pya.DPoint(ux*p_gu, uy*p_gu-mag))
        g_l_list.append(pya.DPoint(ux*p_gl, uy*p_gl-mag))
        hole_l_list.append(pya.DPoint(ux*p_hl, uy*p_hl-mag))

    p_hu = p_hu-hole
    p_m = p_m-2*ground-2*gap-width
    p_gu = p_gu-gap
    p_gl = p_gl-gap
    p_hl = p_hl-hole

    for phi in np.linspace(angle, 0, 100):

        ux = np.sin(phi*np.pi/180)
        uy = np.cos(phi*np.pi/180)

        hole_u_list.append(pya.DPoint(ux*p_hu, uy*p_hu-mag))
        mask_list.append(pya.DPoint(ux*p_m, uy*p_m-mag))
        g_u_list.append(pya.DPoint(ux*p_gu, uy*p_gu-mag))
        g_l_list.append(pya.DPoint(ux*p_gl, uy*p_gl-mag))
        hole_l_list.append(pya.DPoint(ux*p_hl, uy*p_hl-mag))

    shift = pya.ICplxTrans(1, rotation, not right_curve, start.x, start.y)

    l1 = obj.layout.layer(1, 0)
    l10 = obj.layout.layer(10, 0)
    l11 = obj.layout.layer(11, 0)

    obj.cell.shapes(l11).insert(pya.Polygon(hole_u_list).transformed(shift))
    obj.cell.shapes(l10).insert(pya.Polygon(mask_list).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Polygon(g_u_list).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Polygon(g_l_list).transformed(shift))
    obj.cell.shapes(l11).insert(pya.Polygon(hole_l_list).transformed(shift))

    return shift*pya.DPoint(mag*np.sin(angle*np.pi/180), mag*np.cos(angle*np.pi/180)-mag)


def end_point(radius, angle, right_curve, width, gap, ground, hole):
    mag = radius - width/2 - gap - ground - hole
    mag = radius
    shift = pya.ICplxTrans(1, 0, not right_curve, 0, 0)
    return shift*pya.DPoint(mag*np.sin(angle*np.pi/180), mag*np.cos(angle*np.pi/180)-mag)


