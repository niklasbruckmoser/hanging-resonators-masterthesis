import klayout.db as pya
import math
import numpy as np


class StraightFingers(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide with fingers
    """

    def __init__(self):
        # Important: initialize the super class
        super(StraightFingers, self).__init__()

        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("length", self.TypeDouble, "length of straight", default=200)
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
        return "StraightFingers"

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
        finger_length = self.finger_length / dbu
        finger_end_gap = self.finger_end_gap / dbu
        finger_spacing = self.finger_spacing / dbu
        hook_width = self.hook_width / dbu
        hook_length = self.hook_length / dbu
        hook_unit = self.hook_unit / dbu

        # create shape
        create_straight_fingers(self, pya.DPoint(0, 0), 0, length, width, gap, ground, hole, self.n_fingers,
                                finger_length, finger_end_gap, finger_spacing, hook_width, hook_length, hook_unit)


# angle in degrees
def create_straight_fingers(obj, start, rotation, length, width, gap, ground, hole, n_fingers, finger_length,
                            finger_end_gap, finger_spacing, hook_width, hook_length, hook_unit):
    g_u_list = []
    g_l_list = []
    mask_list = []
    hole_u_list = []
    hole_l_list = []

    p_hole = width / 2 + gap + ground + finger_length + finger_end_gap + hole
    p_mask = width / 2 + gap + ground + finger_length + finger_end_gap
    p_g = width / 2 + gap

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

    p_hole = p_hole - hole
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
    l2 = obj.layout.layer(2, 0)
    l10 = obj.layout.layer(10, 0)
    l11 = obj.layout.layer(11, 0)

    obj.cell.shapes(l11).insert(pya.Polygon(hole_u_list).transformed(shift))
    obj.cell.shapes(l10).insert(pya.Polygon(mask_list).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Polygon(g_u_list).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Polygon(g_l_list).transformed(shift))
    obj.cell.shapes(l11).insert(pya.Polygon(hole_l_list).transformed(shift))

    # define finger dimensions
    hook_y = width / 2 + finger_length
    finger_list = [pya.DPoint(-width / 2, width / 2),
                   pya.DPoint(-width / 2, width / 2 + finger_length),
                   pya.DPoint(-hook_width / 2, hook_y),
                   pya.DPoint(-hook_width / 2, hook_y + hook_length),
                   pya.DPoint(-hook_unit / 2, hook_y + hook_length),
                   pya.DPoint(-hook_unit / 2, hook_y + hook_length - hook_unit),
                   pya.DPoint(-hook_width / 2 + hook_unit, hook_y + hook_length - hook_unit),
                   pya.DPoint(-hook_width / 2 + hook_unit, hook_y),
                   pya.DPoint(hook_width / 2 - hook_unit, hook_y),
                   pya.DPoint(hook_width / 2 - hook_unit, hook_y + hook_length - hook_unit),
                   pya.DPoint(hook_unit / 2, hook_y + hook_length - hook_unit),
                   pya.DPoint(hook_unit / 2, hook_y + hook_length),
                   pya.DPoint(hook_width / 2, hook_y + hook_length),
                   pya.DPoint(hook_width / 2, hook_y),
                   pya.DPoint(width / 2, width / 2 + finger_length),
                   pya.DPoint(width / 2, width / 2)]
    L_hook_list = [pya.DPoint(hook_width / 2 + hook_unit, hook_y + finger_end_gap),
                   pya.DPoint(hook_width / 2 + 2 * hook_unit, hook_y + finger_end_gap),
                   pya.DPoint(hook_width / 2 + 2 * hook_unit, hook_y + hook_length + 2 * hook_unit),
                   pya.DPoint(hook_width / 2 + 3 * hook_unit, hook_y + hook_length + 2 * hook_unit),
                   pya.DPoint(hook_width / 2 + 3 * hook_unit, hook_y + hook_length + 1 * hook_unit),
                   pya.DPoint(hook_width / 2 + hook_unit, hook_y + hook_length + 1 * hook_unit)]

    # calc maximum number of fingers
    n_fingers_max = 2 * int((length - finger_spacing) / (finger_spacing + 2 * gap + width))
    if n_fingers > n_fingers_max:
        n_fingers = n_fingers_max
    x_start = length / 2 - (finger_spacing + math.ceil(n_fingers / 2) * (finger_spacing + 2 * gap + width)) / 2 + finger_spacing + gap + width/2

    # place each finger
    for i in range(n_fingers):
        x_shift = x_start + math.ceil((i - 1) / 2) * (2 * gap + width + finger_spacing)
        angle = 0
        if i % 2 == 1:
            angle = 180
        finger_shift = pya.ICplxTrans(1, angle, False, x_shift, 0)
        L_hook_shift_mirror = pya.ICplxTrans(1, angle + 180, True, x_shift, 0)
        obj.cell.shapes(l1).insert(pya.Box(-width / 2 - gap, width / 2 + gap, width / 2 + gap, width / 2 + finger_length + finger_end_gap).transformed(shift * finger_shift))
        obj.cell.shapes(l2).insert(pya.Polygon(finger_list).transformed(shift * finger_shift))
        obj.cell.shapes(l2).insert(pya.Polygon(L_hook_list).transformed(shift * finger_shift))
        obj.cell.shapes(l2).insert(pya.Polygon(L_hook_list).transformed(shift * L_hook_shift_mirror))

    # perform boolean operation
    processor = pya.ShapeProcessor()
    processor.boolean(obj.layout, obj.cell, l1, obj.layout, obj.cell, l2, obj.cell.shapes(l1),
                      pya.EdgeProcessor.ModeANotB, True, True, True)
    obj.layout.clear_layer(l2)

    return shift * pya.DPoint(length, 0)


def end_point(length):
    return pya.DPoint(length, 0)
