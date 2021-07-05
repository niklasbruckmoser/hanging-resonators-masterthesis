import klayout.db as pya


class Finger(pya.PCellDeclarationHelper):
    """
    Vertical fingers, with origin in the center
    """

    def __init__(self):
        # Important: initialize the super class
        super(Finger, self).__init__()

        self.param("width", self.TypeDouble, "width cpw", default=10)
        self.param("gap", self.TypeDouble, "gap cpw", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hole", self.TypeDouble, "hole mask", default=40)
        self.param("f_len", self.TypeDouble, "length of the finger", default=20)
        self.param("f_w", self.TypeDouble, "width of the finger", default=16)
        self.param("notch_w", self.TypeDouble, "width of the notch", default=5)
        self.param("notch_d", self.TypeDouble, "depth of the notch", default=8)
        self.param("jj_len", self.TypeDouble, "length of the JJ electrode", default=12)
        self.param("jj_w", self.TypeDouble, "width of the JJ electrode", default=0.9)
        self.param("jj_d", self.TypeDouble, "distance of the JJ to notch", default=0.5)
        self.param("b_d_f", self.TypeDouble, "distance of the bandage to finger borders", default=0.4)
        self.param("b_d_jj", self.TypeDouble, "distance of the bandage to JJ borders", default=0.2)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Finger"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hole = self.hole / dbu
        f_len = self.f_len / dbu
        f_w = self.f_w / dbu
        notch_w = self.notch_w / dbu
        notch_d = self.notch_d / dbu
        jj_len = self.jj_len / dbu
        jj_w = self.jj_w / dbu
        jj_d = self.jj_d / dbu
        b_d_f = self.b_d_f / dbu
        b_d_jj = self.b_d_jj /dbu

        # create shape

        create_finger(self, pya.DPoint(0, 0), 0, width, gap, ground, hole, f_len, f_w, notch_w, notch_d, jj_len, jj_w, jj_d, b_d_f, b_d_jj)


def create_finger(obj, start, rotation, width, gap, ground, hole, f_len, f_w, notch_w, notch_d, jj_len, jj_w, jj_d, b_d_f, b_d_jj):
    f_list = []  # finger
    jj_list = []    # jj
    b_list = []   # bandage

    gap_list = []     # gap
    ground_list = []    # ground
    hole_list = []      # hole

    f_list.append(pya.DPoint(-f_w/2, -width/2-f_len))
    f_list.append(pya.DPoint(-f_w/2, width/2+f_len))
    f_list.append(pya.DPoint(-notch_w/2, width/2+f_len))
    f_list.append(pya.DPoint(-notch_w/2, width/2+f_len-notch_d))
    f_list.append(pya.DPoint(notch_w/2, width/2+f_len-notch_d))
    f_list.append(pya.DPoint(notch_w/2, width/2+f_len))
    f_list.append(pya.DPoint(f_w/2, width/2+f_len))
    f_list.append(pya.DPoint(f_w/2, -width/2-f_len))
    f_list.append(pya.DPoint(notch_w/2, -width/2-f_len))
    f_list.append(pya.DPoint(notch_w/2, -width/2-f_len+notch_d))
    f_list.append(pya.DPoint(-notch_w/2, -width/2-f_len+notch_d))
    f_list.append(pya.DPoint(-notch_w/2, -width/2-f_len))

    gap_list.append(pya.DPoint(-f_w/2-gap, width/2+gap/2))
    gap_list.append(pya.DPoint(-f_w/2-gap, width/2+f_len+gap))
    gap_list.append(pya.DPoint(f_w/2+gap, width/2+f_len+gap))
    gap_list.append(pya.DPoint(f_w/2+gap, width/2+gap/2))

    ground_list.append(pya.DPoint(-f_w/2-gap-ground, width/2+gap+2*gap/3))
    ground_list.append(pya.DPoint(-f_w/2-gap-ground, width/2+f_len+gap+ground))
    ground_list.append(pya.DPoint(f_w/2+gap+ground, width/2+f_len+gap+ground))
    ground_list.append(pya.DPoint(f_w/2+gap+ground, width/2+gap+2*gap/3))

    hole_list.append(pya.DPoint(-f_w/2-gap-ground, width/2+f_len+gap+ground))
    hole_list.append(pya.DPoint(-f_w/2-gap-ground, width/2+f_len+gap+ground+hole))
    hole_list.append(pya.DPoint(f_w/2+gap+ground, width/2+f_len+gap+ground+hole))
    hole_list.append(pya.DPoint(f_w/2+gap+ground, width/2+f_len+gap+ground))

    jj_list.append(pya.DPoint(-notch_w/2+jj_d, width/2+f_len-notch_d+jj_d))
    jj_list.append(pya.DPoint(-notch_w/2+jj_d, width/2+f_len-notch_d+jj_d+jj_len))
    jj_list.append(pya.DPoint(-notch_w/2+jj_d+jj_w, width/2+f_len-notch_d+jj_d+jj_len))
    jj_list.append(pya.DPoint(-notch_w/2+jj_d+jj_w, width/2+f_len-notch_d+jj_d))

    b_list.append(pya.DPoint(-f_w/2+b_d_f, width/2+f_len-notch_d+jj_d+b_d_jj))
    b_list.append(pya.DPoint(-f_w/2+b_d_f, width/2+f_len-b_d_f))
    b_list.append(pya.DPoint(-notch_w/2+jj_d+jj_w-b_d_jj, width/2+f_len-b_d_f))
    b_list.append(pya.DPoint(-notch_w/2+jj_d+jj_w-b_d_jj, width/2+f_len-notch_d+jj_d+b_d_jj))

    shift = pya.ICplxTrans(1, rotation, False, start.x, start.y)

    l1 = obj.layout.layer(1, 0)
    l5 = obj.layout.layer(5, 0)
    l6 = obj.layout.layer(6, 0)
    l10 = obj.layout.layer(10, 0)
    l11 = obj.layout.layer(11, 0)
    l110 = obj.layout.layer(110, 0)

    rot = pya.ICplxTrans(1, 180, False, 0, 0)
    mirror = pya.ICplxTrans(1, 180, True, 0, 0)

    obj.cell.shapes(l110).insert(pya.Polygon(f_list).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Polygon(gap_list).transformed(shift))    # upper
    obj.cell.shapes(l1).insert(pya.Polygon(gap_list).transformed(shift*rot))    # lower
    obj.cell.shapes(l10).insert(pya.Polygon(ground_list).transformed(shift))    # upper
    obj.cell.shapes(l10).insert(pya.Polygon(ground_list).transformed(shift*rot))    # lower
    obj.cell.shapes(l11).insert(pya.Polygon(hole_list).transformed(shift))  # upper
    obj.cell.shapes(l11).insert(pya.Polygon(hole_list).transformed(shift*rot))  # lower
    obj.cell.shapes(l5).insert(pya.Polygon(jj_list).transformed(shift))     # upper
    obj.cell.shapes(l5).insert(pya.Polygon(jj_list).transformed(shift*rot*mirror))     # lower
    obj.cell.shapes(l6).insert(pya.Polygon(b_list).transformed(shift))  # upper
    obj.cell.shapes(l6).insert(pya.Polygon(b_list).transformed(shift*rot*mirror))  # lower

    return shift * pya.DPoint(0, 0)


def end_point():
    return pya.DPoint(0, 0)
