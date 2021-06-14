import klayout.db as pya


class End(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide end, for resonators
    """

    def __init__(self):
        # Important: initialize the super class
        super(End, self).__init__()

        self.param("short", self.TypeInt, "shorted?", default=0)
        self.param("width", self.TypeDouble, "width cpw", default=10)
        self.param("gap", self.TypeDouble, "gap cpw", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hole", self.TypeDouble, "hole mask", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "End"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        short = self.short
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hole = self.hole / dbu
        # create shape

        create_end(self, pya.DPoint(0, 0), 0, short, width, gap, ground, hole)


# angle in degrees
def create_end(obj, start, rotation, short, width, gap, ground, hole):
    g_list = []
    mask_list = []
    hole_list = []

    p_hole = width/2+gap+ground+hole
    p_mask = width/2+gap+ground
    p_g = width/2+gap

    hole_list.append(pya.DPoint(0, p_hole))
    hole_list.append(pya.DPoint(ground+hole+gap, p_hole))
    hole_list.append(pya.DPoint(ground+hole+gap, -p_hole))
    hole_list.append(pya.DPoint(0, -p_hole))
    hole_list.append(pya.DPoint(0, -p_mask))
    hole_list.append(pya.DPoint(ground+gap, -p_mask))
    hole_list.append(pya.DPoint(ground+gap, p_mask))
    hole_list.append(pya.DPoint(0, p_mask))

    mask_list.append(pya.DPoint(0, p_mask))
    mask_list.append(pya.DPoint(ground+gap, p_mask))
    mask_list.append(pya.DPoint(ground+gap, -p_mask))
    mask_list.append(pya.DPoint(0, -p_mask))

    if not short:
        g_list.append(pya.DPoint(0, p_g))
        g_list.append(pya.DPoint(gap, p_g))
        g_list.append(pya.DPoint(gap, -p_g))
        g_list.append(pya.DPoint(0, -p_g))

    shift = pya.ICplxTrans(1, rotation, False, start.x, start.y)
    # shift = pya.ICplxTrans(1, 0, False, 0, 0)

    l1 = obj.layout.layer(1, 0)
    l10 = obj.layout.layer(10, 0)
    l11 = obj.layout.layer(11, 0)

    obj.cell.shapes(l11).insert(pya.Polygon(hole_list).transformed(shift))
    obj.cell.shapes(l10).insert(pya.Polygon(mask_list).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Polygon(g_list).transformed(shift))

    return shift*pya.DPoint(ground+hole, 0)

