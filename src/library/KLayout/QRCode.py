import klayout.db as pya
import numpy as np


class QRCode(pya.PCellDeclarationHelper):
    """
    QR Code
    """

    def __init__(self):
        # Important: initialize the super class
        super(QRCode, self).__init__()

        self.param("pixel_size", self.TypeInt, "size of a single pixel", default=10)
        self.param("text", self.TypeString, "qr text", default="https://gitlab.lrz.de/design-tools/hanging-resonators")

    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "QR Code"

    def coerce_parameters_impl(self):
        pass

    def produce_impl(self):
        # parameters in database units
        data = get_qr_data(self.text)
        pixel_size = self.pixel_size
        # create shape
        create_qr_code(self, pya.DPoint(0, 0), 0, data, pixel_size)


def create_qr_code(obj, start, rotation, data, pixel_size):

    box_list = []

    matrix_size = int(np.sqrt(len(data)))

    start_pos = -(matrix_size-1) / 2 * pixel_size

    for x in range(matrix_size):
        for y in range(matrix_size):
            if data[(matrix_size*x+y) % len(data)] == "1":
                pos = pya.DPoint(start_pos + x * pixel_size, start_pos + y * pixel_size)
                d = pixel_size/2
                box_list.append(pya.DBox(pya.DPoint(pos.x-d, pos.y-d), pya.DPoint(pos.x+d, pos.y+d)))

    shift = pya.DCplxTrans(1, rotation, False, start.x, start.y)

    l0 = obj.layout.layer(0, 0)
    l2 = obj.layout.layer(2, 0)

    obj.cell.shapes(l2).insert(pya.DBox(pya.DPoint(-matrix_size / 2 * pixel_size, -matrix_size / 2 * pixel_size),
                                        pya.DPoint(matrix_size / 2 * pixel_size, matrix_size / 2 * pixel_size))
                               .transformed(shift))

    for box in box_list:
        obj.cell.shapes(l0).insert(box.transformed(shift))

    return shift*pya.DPoint(0, 0)


def get_qr_data(text) -> str:
    """
    Get an array of zeros and ones as qr code data
    """
    from qrcode.main import QRCode
    qr = QRCode(1)
    qr.add_data(text)
    qr.make()
    string = ""
    for x in qr.modules:
        for y in x:
            if y:
                string += "1"
            else:
                string += "0"
    return string