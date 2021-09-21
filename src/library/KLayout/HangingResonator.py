import klayout.db as pya
import numpy as np
import src.library.Cells as Cells

from src.library.KLayout.Straight import create_straight
from src.library.KLayout.Curve import create_curve
from src.library.KLayout.End import create_end

from src.library.KLayout.Straight import end_point as straight_end
from src.library.KLayout.Curve import end_point as curve_end


class HangingResonator(pya.PCellDeclarationHelper):
    """
    Hanging resonator. The origin is centered in x direction and at the position of the transmission line in y direction
    """

    def __init__(self):
        # Important: initialize the super class
        super(HangingResonator, self).__init__()

        self.param("segment_length", self.TypeDouble, "segment length", default=700)
        self.param("length", self.TypeDouble, "resonator length", default=4000)
        self.param("x_offset", self.TypeDouble, "x offset", default=0)
        self.param("y_offset", self.TypeDouble, "y offset", default=100)
        self.param("coupling_length", self.TypeDouble, "coupling length", default=200)
        self.param("coupling_ground", self.TypeDouble, "coupling ground", default=10)
        self.param("radius", self.TypeDouble, "radius", default=70)
        self.param("shorted", self.TypeInt, "Lambda/4 resonator?", default=1)
        self.param("width_tl", self.TypeDouble, "width of transmission line", default=10)
        self.param("gap_tl", self.TypeDouble, "gap of transmission line", default=6)
        self.param("width", self.TypeDouble, "width cpw", default=10)
        self.param("gap", self.TypeDouble, "gap cpw", default=6)
        self.param("ground", self.TypeDouble, "ground", default=50)
        self.param("hole", self.TypeDouble, "hole mask", default=40)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Hanging Resonator"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        segment_length = self.segment_length / dbu
        length = self.length / dbu
        x_offset = self.x_offset / dbu
        y_offset = self.y_offset / dbu
        coupling_length = self.coupling_length / dbu
        coupling_ground = self.coupling_ground / dbu
        radius = self.radius / dbu
        shorted = self.shorted
        width_tl = self.width_tl / dbu
        gap_tl = self.gap_tl / dbu
        width = self.width / dbu
        gap = self.gap / dbu
        ground = self.ground / dbu
        hole = self.hole / dbu

        # create shape
        create_res(self, pya.DPoint(0, 0), 0, segment_length, length, x_offset, y_offset, coupling_length, coupling_ground, radius, shorted, width_tl, gap_tl, width, gap, ground, hole)


def create_res(obj, start, rotation, segment_length, length, x_offset, y_offset, coupling_length, coupling_ground, radius, shorted, width_tl, gap_tl, width, gap, ground, hole):

    dbu = obj.layout.dbu

    curr = pya.DPoint(start.x-segment_length/2+x_offset-coupling_length, start.y+width/2+width_tl/2+gap+gap_tl+coupling_ground)
    create_end(obj, curr, 180+rotation, 0, width, gap, ground, hole)

    curr = create_straight(obj, curr, rotation, coupling_length, width, gap, ground, hole)
    length -= coupling_length
    curr = create_curve(obj, curr, rotation, radius, 90, 0, width, gap, ground, hole)
    length -= np.pi/180*radius*90

    if length < y_offset:
        curr = create_straight(obj, curr, 90+rotation, length, width, gap, ground, hole)
        create_end(obj, curr, 90+rotation, shorted, width, gap, ground, hole)
        return
    curr = create_straight(obj, curr, 90+rotation, y_offset, width, gap, ground, hole)

    length -= y_offset

    if length < np.pi/180*radius*90:
        end_angle = 180*length/np.pi/radius
        curr = create_curve(obj, curr, 90+rotation, radius, end_angle, 0, width, gap, ground, hole)
        create_end(obj, curr, 360+end_angle+rotation, shorted, width, gap, ground, hole)
        return
    curr = create_curve(obj, curr, 90+rotation, radius, 90, 0, width, gap, ground, hole)
    length -= np.pi/180*radius*90

    if x_offset == 0:
        x_offset = segment_length
    if length < x_offset:
        curr = create_straight(obj, curr, 180+rotation, length, width, gap, ground, hole)
        create_end(obj, curr, 180+rotation, shorted, width, gap, ground, hole)
        return

    curr = create_straight(obj, curr, 180+rotation, x_offset, width, gap, ground, hole)
    length -= x_offset

    # begin meandering loop

    right = True

    while True:
        if length < np.pi/180*radius*180:
            end_angle = 180*length/np.pi/radius
            curr = create_curve(obj, curr, 180+rotation if right is True else rotation, radius, end_angle, right, width, gap, ground, hole)
            create_end(obj, curr, 180-end_angle+rotation if right else 360+end_angle+rotation, shorted, width, gap, ground, hole)
            return
        curr = create_curve(obj, curr, 180+rotation if right is True else rotation, radius, 180, right, width, gap, ground, hole)
        length -= np.pi/180*radius*180

        if length < segment_length:
            curr = create_straight(obj, curr, rotation if right is True else 180+rotation, length, width, gap, ground, hole)
            create_end(obj, curr, rotation if right else 180+rotation, shorted, width, gap, ground, hole)
            return

        curr = create_straight(obj, curr, rotation if right is True else 180+rotation, segment_length, width, gap, ground, hole)
        length -= segment_length

        right = not right


def get_coord(z, start, rotation, params: Cells.Resonator) -> (float, float, float):
    """
    Get the coordinate depending on the progress (in percent, i.e. from 0 to 1)
    @param z: progress along the resonator, between 0 (start) and 1 (end)
    @param start: start position
    @param rotation: start rotation
    @param params: params for the hanging resonator
    @return:
    """
    # end -> coupling -> rotation -> y_off -> rotation -> x_off -> segment -> rotation -> ...

    length = z*params.length
    segment_length = params.segment_length
    x_offset = params.x_offset
    y_offset = params.y_offset
    coupling_length = params.coupling_length
    coupling_ground = params.coupling_ground
    width = params.width
    width_tl = params.width_tl
    gap = params.gap
    gap_tl = params.gap_tl
    radius = params.radius
    ground = params.ground
    hole = params.hole

    curr = pya.DPoint(start.x-segment_length/2+x_offset-coupling_length, start.y+width/2+width_tl/2+gap+gap_tl+coupling_ground)
    shift = pya.ICplxTrans(1, rotation, False, 0, 0)
    curr = pya.DPoint(shift*curr)

    # coupling
    if length < coupling_length:
        curr = curr + straight_end(length)
        return (curr.x, curr.y, rotation)
    curr = curr + straight_end(coupling_length)
    length -= coupling_length

    # first meander
    if length < np.pi*radius/2:
        end_angle = 180*length/np.pi/radius
        curr = curr + curve_end(radius, end_angle, 0, width, gap, ground, hole)
        return (curr.x, curr.y, rotation + end_angle)

    curr = curr + curve_end(radius, 90, 0, width, gap, ground, hole)
    rot = pya.ICplxTrans(1, 90, False, 0, 0)
    length -= np.pi*radius/2

    # y_offset
    if length < y_offset:
        curr = curr + pya.DPoint(rot*straight_end(length))
        return (curr.x, curr.y, rotation+90)

    curr = curr + pya.DPoint(rot*straight_end(y_offset))
    length -= y_offset

    # meander to x_offset
    if length < np.pi*radius/2:
        end_angle = 180*length/np.pi/radius
        curr = curr + pya.DPoint(rot*curve_end(radius, end_angle, 0, width, gap, ground, hole))
        return (curr.x, curr.y, rotation + 90 + end_angle)

    curr = curr + pya.DPoint(rot*curve_end(radius, 90, 0, width, gap, ground, hole))
    rot = pya.ICplxTrans(1, 90, False, 0, 0)*rot
    length -= np.pi*radius/2

    # x_offset
    if length < x_offset:
        curr = curr + pya.DPoint(rot*straight_end(length))
        return (curr.x, curr.y, rotation + 180)

    curr = curr + pya.DPoint(rot*straight_end(x_offset))
    length -= x_offset

    # begin meandering loop

    right = True

    while True:
        if length < np.pi/180*radius*180:
            end_angle = 180*length/np.pi/radius
            curr = curr + pya.DPoint(rot*curve_end(radius, end_angle, right, width, gap, ground, hole))
            return (curr.x, curr.y, 180-end_angle+rotation if right else 360+end_angle+rotation)

        curr = curr + pya.DPoint(rot*curve_end(radius, 180, right, width, gap, ground, hole))
        rot = rot*pya.ICplxTrans(1, 180, False, 0, 0)
        length -= np.pi/180*radius*180

        if length < segment_length:
            curr = curr + pya.DPoint(rot*straight_end(length))
            return (curr.x, curr.y, rotation)

        curr = curr + pya.DPoint(rot*straight_end(segment_length))
        length -= segment_length

        right = not right
