from pathlib import Path

import klayout.db as pya
import numpy as np
import os


class WaferBuilder:

    def __init__(self, wafer_diameter=100000, spacing_x=10000, spacing_y=6000, x_constraint=None, right=True):
        """
        Initializes a WaferBuilder object, which can be used for generating wafers.
        @param wafer_diameter: Diameter of the wafer; by default 4 inch wafer
        @param spacing_x: x spacing of the chip grid
        @param spacing_y: y spacing of the chip grid
        @param x_constraint: x constraint for chip positions on the wafer
        @param right: if right, the grid will only contain slots greater than x_constraint. If not right, only slots
        smaller than the x_constraint will be created
        """
        self.wafer_diameter = wafer_diameter
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y

        x = -int(spacing_x/2)
        y = -int(spacing_y/2)

        self.chip_positions = [(x, y)]  # center positions

        fill_factor = 0.8  # 80% of the radius will be used (doesn't take chip dimensions into account)

        # init the chip positions (not optimized, but no need to)
        for i in range(1, int(wafer_diameter/min(spacing_x, spacing_y))):
            if i % 2 == 0:
                s = -1
            else:
                s = 1
            for _ in range(i):
                x += s*spacing_x
                if (x**2 + y**2) > (wafer_diameter/2*fill_factor)**2:
                    continue
                self.chip_positions.append((x, y))
            for _ in range(i):
                y += s*spacing_y
                if (x**2 + y**2) > (wafer_diameter/2*fill_factor)**2:
                    continue
                self.chip_positions.append((x, y))

        if x_constraint is not None:
            new_pos = []
            for pos in self.chip_positions:
                if right and pos[0] > x_constraint:
                    new_pos.append(pos)
                if not right and pos[0] < x_constraint:
                    new_pos.append(pos)

            self.chip_positions = new_pos

        # sort chip positions by ascending distance from origin
        self.chip_positions.sort(key=lambda r: r[0]**2+r[1]**2)

    def create_wafer(self, save_name: str, chip_list: [(str, int)]):
        """
        Create a wafer from a list containing name-amount tuples.
        @param save_name: Name for the wafer
        @param chip_list: List containing the chip names (+paths)
        """
        self._write_file(save_name, chip_list)

    def _write_file(self, save_name: str, chip_list: [(str, int)], write_wafer=True):
        """
        Creates a GDS wafer file from a given chip list.
        @param save_name: Name of the wafer
        @param chip_list: List containing the chip names (+paths)
        @param write_wafer: If true, adds a round wafer for reference
        """
        lay = pya.Layout()
        top = lay.create_cell("WAFER")
        dbu = lay.dbu

        print("Writing wafer...")

        # round wafer (for reference)
        if write_wafer:
            radius = 50000./dbu
            nr_points = 360
            angles = np.linspace(0, 2*np.pi, nr_points+1)[0:-1]
            points = []
            for ind, angle in enumerate(angles):
                points.append(pya.Point(radius*np.cos(angle), radius*np.sin(angle)))
            circle = pya.SimplePolygon(points)
            top.shapes(lay.layer(100, 0)).insert(circle)

        # mark structure for cutting
        mark = _mark(300/dbu, 30/dbu)

        # nested method to escape outer loop
        def write_chips():
            index = 0
            for chip, amount in chip_list:
                print("reading chip " + chip)
                lay.read(chip + ".gds")
                chip_cell = lay.cell_by_name("TOP")  # TODO: maybe change to first top cell in the future
                for _ in range(amount):
                    if index == len(self.chip_positions):
                        return
                    x, y = self.chip_positions[index]
                    trans = pya.DCplxTrans.new(1, 0, False, x, y)
                    top.insert(pya.DCellInstArray(chip_cell, trans))
                    mark_trans = pya.DCplxTrans.new(1, 0, False, (x-self.spacing_x/2)/dbu, (y-self.spacing_y/2)/dbu)
                    top.shapes(lay.layer(1, 0)).insert(pya.SimplePolygon(mark).transform(mark_trans))
                    index += 1

                top.flatten(1)  # flatten to remove the top cell of the resonator

        write_chips()
        print("Saving file...")
        Path("../../wafers/").mkdir(parents=True, exist_ok=True)
        lay.write("../../wafers/" + save_name + ".gds")

    @staticmethod
    def load_chips(path: str, amount: int):
        """
        Load all chips (i.e. all files having a .gds format) from a folder, each of them with the given amount.
        :@param path: Path to the folder
        :@param amount: Amount of each chip
        :@return: list that can be used for the wafer layout
        """
        chip_list = []
        for filename in os.listdir(path):
            if filename.endswith(".gds") or filename.endswith(".GDS"):
                chip_list.append((path + "/" + filename.split(".")[0], amount))
        return chip_list

    @staticmethod
    def load_prefixed_chips(path: str, prefix: str, amount: int):
        """
        Load all chips (i.e. all files having a .gds format) from a folder with a given prefix, each of them with the given
        amount.
        :@param path: Path to the folder
        :@param prefix: Given prefix for the gds files
        :@param amount: Amount of each chip
        :@return: list that can be used for the wafer layout
        """
        chip_list = []
        for filename in os.listdir(path):
            if filename.startswith(prefix) and (filename.endswith(".gds") or filename.endswith(".GDS")):
                chip_list.append((path + "/" + filename.split(".")[0], amount))
        return chip_list


def _mark(arm_length: float, arm_width: float):
    """
    Helper for creating marks.
    :@param arm_length: Arm length of the mark, measured from (0, 0)
    :@param arm_width: Arm width of the mark, measured from the axis
    :@return: A list containing the coordinates of the mark, centered around (0, 0)
    """
    return [pya.DPoint(-arm_width, -arm_width), pya.DPoint(-arm_width, -arm_length), pya.DPoint(arm_width, -arm_length),
            pya.DPoint(arm_width, -arm_width), pya.DPoint(arm_length, -arm_width), pya.DPoint(arm_length, arm_width),
            pya.DPoint(arm_width, arm_width), pya.DPoint(arm_width, arm_length), pya.DPoint(-arm_width, arm_length),
            pya.DPoint(-arm_width, arm_width), pya.DPoint(-arm_length, arm_width), pya.DPoint(-arm_length, -arm_width)]
