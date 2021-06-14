import klayout.db as pya


class Hallbar(pya.PCellDeclarationHelper):
    """
    Hallbar
    """

    def __init__(self):
        # Important: initialize the super class
        super(Hallbar, self).__init__()

        self.param("padsize", self.TypeDouble, "pad size", default=10)
        self.param("length", self.TypeDouble, "length of lines", default=6)
        self.param("width", self.TypeDouble, "width of lines", default=50)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Hallbar"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        dbu = self.layout.dbu

        # parameters in database units
        padsize = self.padsize / dbu
        length = self.length / dbu
        width = self.width / dbu
        # create shape

        create_hallbar(self, pya.DPoint(0, 0), 0, padsize, length, width)


# angle in degrees
def create_hallbar(obj, start, rotation, padsize, length, width):

    bar_length = 2*padsize + 4*length
    bar_height = 2*padsize + 2*length

    # start as center

    l1 = obj.layout.layer(1, 0)
    l10 = obj.layout.layer(10, 0)

    shift = pya.ICplxTrans(1, rotation, False, start.x, start.y)

    obj.cell.shapes(l10).insert(pya.Box(-bar_length/2*1.2, -bar_height/2*1.2, bar_length/2*1.2, bar_height/2*1.2).transformed(shift))

    obj.cell.shapes(l1).insert(pya.Box(-bar_length/2, -padsize/2, -bar_length/2+padsize, padsize/2).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Box(bar_length/2-padsize, -padsize/2, bar_length/2, padsize/2).transformed(shift))

    obj.cell.shapes(l1).insert(pya.Box(-length-padsize/2, -length-padsize, -length+padsize/2, -length).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Box(length-padsize/2, -length-padsize, length+padsize/2, -length).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Box(-length-padsize/2, length, -length+padsize/2, length+padsize).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Box(length-padsize/2, length, length+padsize/2, length+padsize).transformed(shift))

    obj.cell.shapes(l1).insert(pya.Box(-2*length, -width/2, 2*length, width/2).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Box(-length-width/2, -length, -length+width/2, length).transformed(shift))
    obj.cell.shapes(l1).insert(pya.Box(length-width/2, -length, length+width/2, length).transformed(shift))

    return shift*pya.DPoint(0, 0)

