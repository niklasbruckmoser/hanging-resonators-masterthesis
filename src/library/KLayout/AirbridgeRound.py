import klayout.db as pya
import numpy as np


class AirbridgeRound(pya.PCellDeclarationHelper):
    """
    Round air bridge, except for the pads identical to the default air bridge
    """

    def __init__(self):
        # Important: initialize the super class
        super(AirbridgeRound, self).__init__()

        self.param("pad_radius", self.TypeDouble, "width of the pad", default=80)
        self.param("gap", self.TypeDouble, "gap between the pads", default=30)
        self.param("bridge_pad_radius", self.TypeDouble, "width of the bridge pad", default=80)
        self.param("bridge_width", self.TypeDouble, "width of the bridge", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Airbridge"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        pad_radius = self.pad_radius / dbu
        gap = self.gap / dbu
        bridge_pad_radius = self.bridge_pad_radius / dbu
        bridge_width = self.bridge_width / dbu
        # create shape

        create_airbridge(self, pya.DPoint(0, 0), 0, pad_radius, gap, bridge_pad_radius, bridge_width)


# angle in degrees
def create_airbridge(obj, start, rotation, pad_radius, gap, bridge_pad_radius, bridge_width):

    p_u_list = []  # upper pad list
    p_l_list = []  # lower pad list
    b_u_list = []  # upper bridge list
    b_l_list = []  # lower bridge list
    b_m_list = []  # mid bridge list

    negative_mask = []

    x = 0
    y = gap/2 + pad_radius/1.5

    for i in range(100):
        phi = i*2*np.pi/100
        p_u_list.append(pya.DPoint(x + np.sin(phi)*pad_radius, y + np.cos(phi)*pad_radius))
        p_l_list.append(pya.DPoint(x + np.sin(phi)*pad_radius, -y + np.cos(phi)*pad_radius))

        b_u_list.append(pya.DPoint(x + np.sin(phi)*bridge_pad_radius, y + np.cos(phi)*bridge_pad_radius))
        b_l_list.append(pya.DPoint(x + np.sin(phi)*bridge_pad_radius, -y + np.cos(phi)*bridge_pad_radius))

    b_m_list.append(pya.DPoint(-bridge_width/2, y))
    b_m_list.append(pya.DPoint(bridge_width/2, y))
    b_m_list.append(pya.DPoint(bridge_width/2, -y))
    b_m_list.append(pya.DPoint(-bridge_width/2, -y))


    y = gap/2

    negative_mask.append(pya.DPoint(-pad_radius, y))
    negative_mask.append(pya.DPoint(pad_radius, y))
    negative_mask.append(pya.DPoint(pad_radius, -y))
    negative_mask.append(pya.DPoint(-pad_radius, -y))


    shift = pya.ICplxTrans(1, rotation, False, start.x, start.y)
    # shift = pya.ICplxTrans(1, 0, False, 0, 0)

    l15 = obj.layout.layer(15, 0)
    l16 = obj.layout.layer(16, 0)
    l17 = obj.layout.layer(17, 0)

    obj.cell.shapes(l17).insert(pya.Polygon(negative_mask).transformed(shift))

    obj.cell.shapes(l15).insert(pya.Polygon(p_u_list).transformed(shift))
    obj.cell.shapes(l15).insert(pya.Polygon(p_l_list).transformed(shift))
    obj.cell.shapes(l16).insert(pya.Polygon(b_u_list).transformed(shift))
    obj.cell.shapes(l16).insert(pya.Polygon(b_l_list).transformed(shift))
    obj.cell.shapes(l16).insert(pya.Polygon(b_m_list).transformed(shift))

    processor = pya.ShapeProcessor()
    processor.boolean(obj.layout, obj.cell, l15, obj.layout, obj.cell, l17, obj.cell.shapes(l15),
                      pya.EdgeProcessor.ModeANotB, True, True, True)
    processor.boolean(obj.layout, obj.cell, l16, obj.layout, obj.cell, l16, obj.cell.shapes(l16),
                      pya.EdgeProcessor.ModeAnd, True, True, True)
    obj.layout.clear_layer(l17)

    return shift*pya.DPoint(0, 0)


def end_point():
    return pya.DPoint(0, 0)
