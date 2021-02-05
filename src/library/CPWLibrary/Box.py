import klayout.db as pya
import numpy as np





def create_box(obj, start, rotation, lengthlength, widthwidth,  hole,l_w,l_g,l_gr,l_h):
    #width, gap, ground, hole
    g_list = []
    mask_list = []
    hole_list = []
    dist = l_w/2+l_g+l_gr+l_h
    p_mask = widthwidth/2
    p_mask2= lengthlength
    p_hole = hole+widthwidth/2
    p_hole2= p_mask2+hole

##########
    hole_list.append(pya.DPoint(0, dist))
    hole_list.append(pya.DPoint(0, p_mask))
    hole_list.append(pya.DPoint(p_mask2, p_mask))
    hole_list.append(pya.DPoint(p_mask2, -p_mask))
    hole_list.append(pya.DPoint(0, -p_mask))
    hole_list.append(pya.DPoint(0, -dist))
    hole_list.append(pya.DPoint(-hole, -dist))
    hole_list.append(pya.DPoint(-hole, -p_hole))
    hole_list.append(pya.DPoint(p_hole2, -p_hole))
    hole_list.append(pya.DPoint(p_hole2, p_hole))
    hole_list.append(pya.DPoint(-hole, p_hole))
    hole_list.append(pya.DPoint(-hole, dist))



    mask_list.append(pya.DPoint(0, p_mask))
    mask_list.append(pya.DPoint(p_mask2, p_mask))
    mask_list.append(pya.DPoint(p_mask2, -p_mask))
    mask_list.append(pya.DPoint(0, -p_mask))

    '''
    if not short:
        g_list.append(pya.DPoint(0, p_g))
        g_list.append(pya.DPoint(gap, p_g))
        g_list.append(pya.DPoint(gap, -p_g))
        g_list.append(pya.DPoint(0, -p_g))
    '''

    shift = pya.ICplxTrans(1, rotation, False, start.x, start.y)
    # shift = pya.ICplxTrans(1, 0, False, 0, 0)

    #l1 = obj.layout.layer(1, 0)
    l10 = obj.layout.layer(10, 0)
    l11 = obj.layout.layer(11, 0)

    obj.cell.shapes(l11).insert(pya.Polygon(hole_list).transformed(shift))
    obj.cell.shapes(l10).insert(pya.Polygon(mask_list).transformed(shift))
    #obj.cell.shapes(l1).insert(pya.Polygon(g_list).transformed(shift))

    return shift*pya.DPoint(hole, 0)