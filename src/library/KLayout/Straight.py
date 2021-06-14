import klayout.db as pya


class Straight(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide port
    """

    def __init__(self):
        # Important: initialize the super class
        super(Straight, self).__init__()

        # declare the parameters
        self.param("length", self.TypeDouble, "length of straight", default=200)
        self.param("width", self.TypeDouble, "width cpw", default=10)
        self.param("gap", self.TypeDouble, "gap cpw", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hole", self.TypeDouble, "hole mask", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Straight"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        length = self.length / dbu
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hole = self.hole / dbu
        # create shape

        create_straight(self, pya.DPoint(0, 0), 0, length, width, gap, ground, hole)


# angle in degrees
def create_straight(obj, start, rotation, length, width, gap, ground, hole):
    g_u_list = []
    g_l_list = []
    mask_list = []
    hole_u_list = []
    hole_l_list = []

    p_hole = width/2+gap+ground+hole
    p_mask = width/2+gap+ground
    p_g = width/2+gap

    hole_u_list.append(pya.DPoint(0, p_hole))
    mask_list.append(pya.DPoint(0, p_mask))
    g_u_list.append(pya.DPoint(0, p_g))
    g_l_list.append(pya.DPoint(0, -p_g))
    hole_l_list.append(pya.DPoint(0, -p_hole))

    hole_u_list.append(pya.DPoint(length, p_hole))
    mask_list.append(pya.DPoint(length, p_mask))
    g_u_list.append(pya.DPoint(length, p_g))
    g_l_list.append(pya.DPoint(length, -p_g))
    hole_l_list.append(pya.DPoint(length, -p_hole))

    p_hole = p_hole-hole
    p_mask = -p_mask
    p_g = p_g - gap

    hole_u_list.append(pya.DPoint(length, p_hole))
    mask_list.append(pya.DPoint(length, p_mask))
    g_u_list.append(pya.DPoint(length, p_g))
    g_l_list.append(pya.DPoint(length, -p_g))
    hole_l_list.append(pya.DPoint(length, -p_hole))

    hole_u_list.append(pya.DPoint(0, p_hole))
    mask_list.append(pya.DPoint(0, p_mask))
    g_u_list.append(pya.DPoint(0, p_g))
    g_l_list.append(pya.DPoint(0, -p_g))
    hole_l_list.append(pya.DPoint(0, -p_hole))

    shift = pya.ICplxTrans(1, rotation, False, start.x, start.y)
    # shift = pya.ICplxTrans(1, 0, False, 0, 0)

    l1 = obj.layout.layer(1, 0)
    l10 = obj.layout.layer(10, 0)
    l11 = obj.layout.layer(11, 0)

    obj.cell.shapes(l11).insert(pya.Polygon(hole_u_list).transformed(shift))
    obj.cell.shapes(l10).insert(pya.Polygon(mask_list).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Polygon(g_u_list).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Polygon(g_l_list).transformed(shift))
    obj.cell.shapes(l11).insert(pya.Polygon(hole_l_list).transformed(shift))

    return shift*pya.DPoint(length, 0)


def end_point(length):
    return pya.DPoint(length, 0)
