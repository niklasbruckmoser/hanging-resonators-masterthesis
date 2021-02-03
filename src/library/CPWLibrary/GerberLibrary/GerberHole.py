import klayout.db as pya
import numpy as np

class GHole(pya.PCellDeclarationHelper):
    """
    Hole pattern
    """

    def __init__(self):
        # Important: initialize the super class
        super(GHole, self).__init__()

        # declare the parameters
        self.param("lay", self.TypeLayer, "Layer", default=pya.LayerInfo(12, 0))
        self.param("width", self.TypeDouble, "width", default=10000)
        self.param("height", self.TypeDouble, "height", default=6000)
        self.param("spacing", self.TypeDouble, "hole spacing", default=50)
        self.param("sigma", self.TypeDouble, "random sigma", default=0)
        self.param("size", self.TypeDouble, "hole size", default=5)

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Hole Pattern"

    def parameters_from_shape_impl(self):
        # Implement the "Create PCell from shape" protocol: we set r and l from the shape's bounding box width and layer
        # self.lay = self.layout.get_info(self.lay)
        self.x = self.shape.bbox().width() / self.layout.dbu
        self.y = self.shape.bbox().length() / self.layout.dbu

    def produce_impl(self):
        dbu = self.layout.dbu
        width = self.width / dbu
        height = self.height / dbu
        spacing = self.spacing / dbu
        sigma = self.sigma / dbu
        size = self.size / dbu

        # create the shape
        nx = int(width / spacing)
        ny = int(height / spacing)

        spot = 250

        path_list = []
        path_list.append(pya.DPoint(size/2, size/2))
        path_list.append(pya.DPoint(size/2, -size/2))
        path_list.append(pya.DPoint(-size/2, -size/2))
        path_list.append(pya.DPoint(-size/2, size/2))

        i = 0.5
        down = True
        while i*spot < size:
            path_list.append(pya.DPoint(-size/2 + i*spot, size/2-spot if down is True else -size/2+spot))
            path_list.append(pya.DPoint(-size/2 + i*spot, -size/2+spot if down is True else size/2-spot))
            down = not down
            i += 1

        # if not down:
        #     path_list.append(path_list[-2])
        path_list.append(path_list[3])
        path_list.append(path_list[0])

        for x in range(0, nx):
            x += 1/2
            for y in range(0, ny):
                y += 1/2

                if sigma != 0:
                    rx = sigma*(2*np.random.random()-1)
                    ry = sigma*(2*np.random.random()-1)
                else:
                    rx = 0
                    ry = 0

                shift = pya.ICplxTrans(1, 0, False, (x*spacing+rx)-width/2, (y*spacing+ry)-height/2)

                # self.cell.shapes(self.lay_layer).insert(pya.Box(-size/2, -size/2, size/2, size/2).transformed(shift))
                self.cell.shapes(self.lay_layer).insert(pya.Polygon(path_list).transformed(shift))


