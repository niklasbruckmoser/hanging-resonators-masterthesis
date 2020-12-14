import klayout.db as pya
import numpy as np


class EndHooks(pya.PCellDeclarationHelper):
    """
    Coplanar waveguide port
    """

    def __init__(self):
        # Important: initialize the super class
        super(EndHooks, self).__init__()


        # declare the parameters
        # self.param("l", self.TypeLayer, "Layer", default=pya.LayerInfo(1, 0))
        # self.param("lm", self.TypeLayer, "LayerMask", default=pya.LayerInfo(10, 0))
        # self.param("sh", self.TypeShape, "", default=pya.DPoint(0, 0))
        self.param("short", self.TypeInt, "shorted?", default=0)
        self.param("width", self.TypeDouble, "width cpw", default=10)
        self.param("gap", self.TypeDouble, "gap cpw", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hole", self.TypeDouble, "hole mask", default=40)
        self.param("hooks", self.TypeDouble, "hooks?", default=True)
        self.param("end_gap", self.TypeDouble, "gap at the end", default=6)
        self.param("hook_width", self.TypeDouble, "hook width", default=5)
        self.param("hook_length", self.TypeDouble, "hook length", default=2.5)
        self.param("hook_unit", self.TypeDouble, "hook unit", default=1)
        self.param("electrode_width", self.TypeDouble, "electrode width", default=0.5)
        self.param("bridge_width", self.TypeDouble, "bridge width", default=0.5)
        self.param("bridge_length", self.TypeDouble, "bridge length", default=1)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "End with hooks"

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
        end_gap = self.end_gap / dbu
        hook_width = self.hook_width / dbu
        hook_length = self.hook_length / dbu
        hook_unit = self.hook_unit / dbu
        electrode_width = self.electrode_width / dbu
        bridge_width = self.bridge_width / dbu
        bridge_length = self.bridge_length / dbu
        # create shape

        create_end_hooks(self, pya.DPoint(0, 0), 0, width, gap, ground, hole, self.hooks, end_gap, hook_width, hook_length, hook_unit, electrode_width, bridge_width, bridge_length)


# angle in degrees
def create_end_hooks(obj, start, rotation, width, gap, ground, hole, hooks, end_gap, hook_width, hook_length, hook_unit, electrode_width, bridge_width, bridge_length):
    g_list = []
    mask_list = []
    hole_list = []

    p_hole = width/2+gap+ground+hole
    p_mask = width/2+gap+ground
    p_g = width/2+gap

    hole_list.append(pya.DPoint(0, p_hole))
    hole_list.append(pya.DPoint(ground+hole, p_hole))
    hole_list.append(pya.DPoint(ground+hole, -p_hole))
    hole_list.append(pya.DPoint(0, -p_hole))
    hole_list.append(pya.DPoint(0, -p_mask))
    hole_list.append(pya.DPoint(ground, -p_mask))
    hole_list.append(pya.DPoint(ground, p_mask))
    hole_list.append(pya.DPoint(0, p_mask))

    mask_list.append(pya.DPoint(0, p_mask))
    mask_list.append(pya.DPoint(ground, p_mask))
    mask_list.append(pya.DPoint(ground, -p_mask))
    mask_list.append(pya.DPoint(0, -p_mask))

    g_list.append(pya.DPoint(0, p_g))
    g_list.append(pya.DPoint(end_gap, p_g))
    g_list.append(pya.DPoint(end_gap, -p_g))
    g_list.append(pya.DPoint(0, -p_g))

    shift = pya.ICplxTrans(1, rotation, False, start.x, start.y)
    # shift = pya.ICplxTrans(1, 0, False, 0, 0)

    l1 = obj.layout.layer(1, 0)
    l2 = obj.layout.layer(2, 0)
    l98 = obj.layout.layer(98, 0)
    l10 = obj.layout.layer(10, 0)
    l11 = obj.layout.layer(11, 0)

    obj.cell.shapes(l11).insert(pya.Polygon(hole_list).transformed(shift))
    obj.cell.shapes(l10).insert(pya.Polygon(mask_list).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Polygon(g_list).transformed(shift))

    if hooks is True:
        # define finger dimensions
        hook_list = [pya.DPoint(-hook_width / 2, 0),
                     pya.DPoint(-hook_width / 2, hook_length),
                     pya.DPoint(-hook_unit / 2,  hook_length),
                     pya.DPoint(-hook_unit / 2, hook_length - hook_unit),
                     pya.DPoint(-hook_width / 2 + hook_unit, hook_length - hook_unit),
                     pya.DPoint(-hook_width / 2 + hook_unit, 0),
                     pya.DPoint(hook_width / 2 - hook_unit, 0),
                     pya.DPoint(hook_width / 2 - hook_unit, hook_length - hook_unit),
                     pya.DPoint(hook_unit / 2, hook_length - hook_unit),
                     pya.DPoint(hook_unit / 2, hook_length),
                     pya.DPoint(hook_width / 2, hook_length),
                     pya.DPoint(hook_width / 2, 0)]
        L_hook_list = [pya.DPoint(hook_width / 2 + hook_unit, end_gap),
                       pya.DPoint(hook_width / 2 + 2 * hook_unit, end_gap),
                       pya.DPoint(hook_width / 2 + 2 * hook_unit, hook_length + 3 * hook_unit),
                       pya.DPoint(hook_width / 2 + 3 * hook_unit, hook_length + 3 * hook_unit),
                       pya.DPoint(hook_width / 2 + 3 * hook_unit, hook_length + 2 * hook_unit),
                       pya.DPoint(hook_width / 2 + hook_unit, hook_length + 2 * hook_unit)]
        Al_hook_list = [pya.DPoint(-hook_width/2 - hook_unit/2, -hook_unit/2),
                          pya.DPoint(-hook_width/2 - hook_unit/2, hook_length + hook_unit/2),
                          pya.DPoint(-hook_width/2 + hook_unit - electrode_width/2, hook_length + hook_unit/2),
                          pya.DPoint(-hook_width/2 + hook_unit - electrode_width/2, hook_length + hook_unit/2 + 2*hook_unit - 3*electrode_width/2 - bridge_width),
                          pya.DPoint(-hook_width/2 + hook_unit - bridge_length/2, hook_length + hook_unit/2 + 2*hook_unit - 3*electrode_width/2 - bridge_width),
                          pya.DPoint(-hook_width/2 + hook_unit - bridge_length/2, hook_length + hook_unit/2 + 2*hook_unit - electrode_width/2 - bridge_width),
                          pya.DPoint(-hook_width/2 + hook_unit + bridge_length/2, hook_length + hook_unit/2 + 2*hook_unit - electrode_width/2 - bridge_width),
                          pya.DPoint(-hook_width/2 + hook_unit + bridge_length/2, hook_length + hook_unit/2 + 2*hook_unit - 3*electrode_width/2 - bridge_width),
                          pya.DPoint(-hook_width/2 + hook_unit + electrode_width/2, hook_length + hook_unit/2 + 2*hook_unit - 3*electrode_width/2 - bridge_width),
                          pya.DPoint(-hook_width/2 + hook_unit + electrode_width/2, hook_length + hook_unit/2),
                          pya.DPoint(hook_width/2 - hook_unit - electrode_width/2, hook_length + hook_unit/2),
                          pya.DPoint(hook_width/2 - hook_unit - electrode_width/2, hook_length + hook_unit/2 + 2*hook_unit - 3*electrode_width/2 - bridge_width),
                          pya.DPoint(hook_width/2 - hook_unit - bridge_length/2, hook_length + hook_unit/2 + 2*hook_unit - 3*electrode_width/2 - bridge_width),
                          pya.DPoint(hook_width/2 - hook_unit - bridge_length/2, hook_length + hook_unit/2 + 2*hook_unit - electrode_width/2 - bridge_width),
                          pya.DPoint(hook_width/2 - hook_unit + bridge_length/2, hook_length + hook_unit/2 + 2*hook_unit - electrode_width/2 - bridge_width),
                          pya.DPoint(hook_width/2 - hook_unit + bridge_length/2, hook_length + hook_unit/2 + 2*hook_unit - 3*electrode_width/2 - bridge_width),
                          pya.DPoint(hook_width/2 - hook_unit + electrode_width/2, hook_length + hook_unit/2 + 2*hook_unit - 3*electrode_width/2 - bridge_width),
                          pya.DPoint(hook_width/2 - hook_unit + electrode_width/2, hook_length + hook_unit/2),
                          pya.DPoint(hook_width/2 + hook_unit/2, hook_length + hook_unit/2),
                          pya.DPoint(hook_width/2 + hook_unit/2, -hook_unit/2)]
        Al_L_hook_list = [pya.DPoint(hook_width / 2 + hook_unit/2, hook_length + 3*hook_unit + hook_unit/2),
                          pya.DPoint(hook_width / 2 + 3*hook_unit + hook_unit/2, hook_length + 3*hook_unit + hook_unit/2),
                          pya.DPoint(hook_width / 2 + 3*hook_unit + hook_unit/2, hook_length + 2*hook_unit - hook_unit/2),
                          pya.DPoint(hook_width / 2 + hook_unit/2, hook_length + 2*hook_unit - hook_unit/2),
                          pya.DPoint(hook_width / 2 + hook_unit/2, hook_length + 2*hook_unit + hook_unit/2 - electrode_width/2),
                          pya.DPoint(hook_width/2 - hook_unit - bridge_length/2, hook_length + 2*hook_unit + hook_unit/2 - electrode_width/2),
                          pya.DPoint(hook_width/2 - hook_unit - bridge_length/2, hook_length + 2*hook_unit + hook_unit/2 + electrode_width/2),
                          pya.DPoint(hook_width / 2 + hook_unit/2, hook_length + 2*hook_unit + hook_unit/2 + electrode_width/2)]

        hooks_shift = pya.ICplxTrans(1, -90, False, 0, 0)
        L_hook_shift_mirror = pya.ICplxTrans(1, 90, True, 0, 0)
        obj.cell.shapes(l2).insert(pya.Polygon(hook_list).transformed(shift * hooks_shift))
        obj.cell.shapes(l2).insert(pya.Polygon(L_hook_list).transformed(shift * hooks_shift))
        obj.cell.shapes(l2).insert(pya.Polygon(L_hook_list).transformed(shift * L_hook_shift_mirror))
        obj.cell.shapes(l98).insert(pya.Polygon(Al_hook_list).transformed(shift * hooks_shift))
        obj.cell.shapes(l98).insert(pya.Polygon(Al_L_hook_list).transformed(shift * hooks_shift))
        obj.cell.shapes(l98).insert(pya.Polygon(Al_L_hook_list).transformed(shift * L_hook_shift_mirror))

        # perform boolean operation
        processor = pya.ShapeProcessor()
        processor.boolean(obj.layout, obj.cell, l1, obj.layout, obj.cell, l2, obj.cell.shapes(l1),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        obj.layout.clear_layer(l2)

    return shift*pya.DPoint(ground+hole, 0)

