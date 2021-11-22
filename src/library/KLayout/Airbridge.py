import klayout.db as pya


class Airbridge(pya.PCellDeclarationHelper):
    """
    Vertical air bridge, with origin in the center
    """

    def __init__(self):
        # Important: initialize the super class
        super(Airbridge, self).__init__()

        self.param("pad_width", self.TypeDouble, "width of the pad", default=100)
        self.param("pad_height", self.TypeDouble, "height of the pad", default=40)
        self.param("gap", self.TypeDouble, "gap between the pads", default=30)
        self.param("bridge_pad_width", self.TypeDouble, "width of the bridge pad", default=80)
        self.param("bridge_pad_height", self.TypeDouble, "height of the bridge pad", default=20)
        self.param("bridge_width", self.TypeDouble, "width of the bridge", default=40)
        self.param("positive_mask", self.TypeInt, "write bridges with positive resist?", default=0)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Airbridge"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        pad_width = self.pad_width / dbu
        pad_height = self.pad_height / dbu
        gap = self.gap / dbu
        bridge_pad_width = self.bridge_pad_width / dbu
        bridge_pad_height = self.bridge_pad_height / dbu
        bridge_width = self.bridge_width / dbu
        positive_mask = self.positive_mask
        positive_mask_buffer = 20 / dbu
        # create shape

        create_airbridge(self, pya.DPoint(0, 0), 0, pad_width, pad_height, gap, bridge_pad_width, bridge_pad_height, bridge_width, positive_mask, positive_mask_buffer)


def create_airbridge(obj, start, rotation, pad_width, pad_height, gap, bridge_pad_width, bridge_pad_height, bridge_width, positive_mask, positive_mask_buffer):

    p_u_list = []
    p_l_list = []
    b_list = []

    x = -pad_width/2
    y = pad_height + gap/2

    bridge_gap = gap + 2*(pad_height-bridge_pad_height)/2

    p_u_list.append(pya.DPoint(x, y))
    p_u_list.append(pya.DPoint(x+pad_width, y))
    p_u_list.append(pya.DPoint(x+pad_width, y-pad_height))
    p_u_list.append(pya.DPoint(x, y-pad_height))

    y = -gap/2

    p_l_list.append(pya.DPoint(x, y))
    p_l_list.append(pya.DPoint(x+pad_width, y))
    p_l_list.append(pya.DPoint(x+pad_width, y-pad_height))
    p_l_list.append(pya.DPoint(x, y-pad_height))

    x = -bridge_pad_width/2
    y = gap/2 + bridge_pad_height + (pad_height-bridge_pad_height)/2

    b_list.append(pya.DPoint(x, y))
    b_list.append(pya.DPoint(x+bridge_pad_width, y))
    b_list.append(pya.DPoint(x+bridge_pad_width, y-bridge_pad_height))
    b_list.append(pya.DPoint(x+bridge_pad_width-(bridge_pad_width-bridge_width)/2, y-bridge_pad_height))
    b_list.append(pya.DPoint(x+bridge_pad_width-(bridge_pad_width-bridge_width)/2, y-bridge_pad_height-bridge_gap))
    b_list.append(pya.DPoint(x+bridge_pad_width, y-bridge_pad_height-bridge_gap))
    b_list.append(pya.DPoint(x+bridge_pad_width, y-2*bridge_pad_height-bridge_gap))
    b_list.append(pya.DPoint(x, y-2*bridge_pad_height-bridge_gap))
    b_list.append(pya.DPoint(x, y-bridge_pad_height-bridge_gap))
    b_list.append(pya.DPoint(x+(bridge_pad_width-bridge_width)/2, y-bridge_pad_height-bridge_gap))
    b_list.append(pya.DPoint(x+(bridge_pad_width-bridge_width)/2, y-bridge_pad_height))
    b_list.append(pya.DPoint(x, y-bridge_pad_height))

    shift = pya.ICplxTrans(1, rotation, False, start.x, start.y)

    l15 = obj.layout.layer(15, 0)
    l16 = obj.layout.layer(16, 0)
    l17 = obj.layout.layer(17, 0)

    obj.cell.shapes(l15).insert(pya.Polygon(p_u_list).transformed(shift))
    obj.cell.shapes(l15).insert(pya.Polygon(p_l_list).transformed(shift))

    if positive_mask:


        x_buffer = pad_width + positive_mask_buffer*2
        y_buffer = 2*pad_height+gap + positive_mask_buffer*2

        mask = []
        mask.append(pya.DPoint(-x_buffer/2, y_buffer/2))
        mask.append(pya.DPoint(x_buffer/2, y_buffer/2))
        mask.append(pya.DPoint(x_buffer/2, -y_buffer/2))
        mask.append(pya.DPoint(-x_buffer/2, -y_buffer/2))

        obj.cell.shapes(l16).insert(pya.Polygon(b_list).transformed(shift))
        obj.cell.shapes(l17).insert(pya.Polygon(mask).transformed(shift))

        processor = pya.ShapeProcessor()
        processor.boolean(obj.layout, obj.cell, l17, obj.layout, obj.cell, l16, obj.cell.shapes(l16),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        obj.layout.clear_layer(l17)

    else:
        obj.cell.shapes(l16).insert(pya.Polygon(b_list).transformed(shift))

    return shift*pya.DPoint(0, 0)


def end_point():
    return pya.DPoint(0, 0)
