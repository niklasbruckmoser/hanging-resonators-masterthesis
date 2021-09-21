from __future__ import annotations

from pathlib import Path

import klayout.db as pya
import numpy as np
import os


class WaferBuilder:

    def __init__(self, wafer_diameter=100000, spacing_x=10000, spacing_y=6000, bounding_box=None):
        """
        Initializes a WaferBuilder object which can be used for generating wafers.
        @param wafer_diameter: Diameter of the wafer; by default 4 inch wafer
        @param spacing_x: x spacing of the chip grid
        @param spacing_y: y spacing of the chip grid
        @param bounding_box: bounding box constraint in the format [(ll_x, ll_y), (ur_x, ur_y)]
        """
        self.bounding_box = bounding_box
        self.wafer_diameter = wafer_diameter
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y

        self.chip_list = []

        x = -int(spacing_x/2)
        y = -int(spacing_y/2)

        self.chip_positions = [(x, y)]  # center positions of the grid

        fill_factor = 0.8  # 80% of the radius will be used (doesn't take chip dimensions into account)

        # init the chip positions (not really optimized, but also no need to)
        for i in range(1, int(wafer_diameter/min(spacing_x, spacing_y))):
            s = 1 if i % 2 else -1
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

        # constrain to positions inside the bounding box
        if bounding_box is not None:
            constraint_pos = []
            for pos in self.chip_positions:
                if bounding_box[0][0] <= pos[0] <= bounding_box[1][0] and \
                   bounding_box[0][1] <= pos[1] <= bounding_box[1][1]:  # x (^) and y (<) okay
                    constraint_pos.append(pos)
            self.chip_positions = constraint_pos

        # sort chip positions by ascending distance from origin
        self.chip_positions.sort(key=lambda r: r[0]**2+r[1]**2)

    def add_chip(self, path: str) -> WaferBuilder:
        """
        Add a single chip path to the chip list
        @param path: path to the chip
        """
        self.chip_list.append(f"{path}{'' if path.lower().endswith('.gds') else '.gds'}")
        return self

    def add_chip_folder(self, path: str, prefix=None) -> WaferBuilder:
        """
        Add all chips (i.e. all files having a .gds format) from a folder
        :@param path: Path to the folder
        :@return: self for chaining
        """
        if prefix is not None:
            return self._add_prefixed_chip_folder(path, prefix)
        for filename in os.listdir(path):
            if filename.lower().endswith(".gds"):
                self.chip_list.append(f"{path}/{filename.split('.')[0]}")
        return self

    def _add_prefixed_chip_folder(self, path: str, prefix: str) -> WaferBuilder:
        """
        Load all chips (i.e. all files having a .gds format) from a folder with a given prefix, each of them with the given
        amount.
        :@param path: Path to the folder
        :@param prefix: Given prefix for the gds files
        :@param amount: Amount of each chip
        :@return: list of paths to gds files that can be used for the wafer layout
        """
        for filename in os.listdir(path):
            if filename.startswith(prefix) and (filename.endswith(".gds") or filename.endswith(".GDS")):
                self.chip_list.append(f"{path}/{filename.split('.')[0]}")
        return self

    def create_wafer(self, save_name: str):
        """
        Creates a GDS wafer file from a given chip list.
        @param save_name: Name of the wafer
        """
        lay = pya.Layout()
        main_cell = lay.create_cell("WAFER")
        dbu = lay.dbu

        print(f"Writing wafer {save_name}...")

        # round wafer (for reference)
        radius = self.wafer_diameter/2/dbu
        nr_points = 360
        angles = np.linspace(0, 2*np.pi, nr_points+1)[0:-1]
        points = []
        for idx, angle in enumerate(angles):
            if 3/2*np.pi-0.3 < angle < 3/2*np.pi+0.3:  # make the circle more wafer-esque
                continue
            points.append(pya.Point(radius*np.cos(angle), radius*np.sin(angle)))
        circle = pya.SimplePolygon(points)
        main_cell.shapes(lay.layer(100, 0)).insert(circle)

        mark = _mark(300/dbu, 5/dbu)

        if len(self.chip_list) > len(self.chip_positions):
            # raise ValueError("Cannot fit all chips onto the wafer!")
            pass

        idx = 0
        for chip in self.chip_list:

            if idx == len(self.chip_positions):
                break

            print(f"reading chip '{chip}'")
            lay.read(chip + ".gds")
            chip_cell = lay.top_cells()[1].cell_index()
            x, y = self.chip_positions[idx]
            main_cell.insert(pya.DCellInstArray(chip_cell, pya.DCplxTrans.new(1, 0, False, x, y)))
            mark_trans = pya.DCplxTrans.new(1, 0, False, (x-self.spacing_x/2)/dbu, (y-self.spacing_y/2)/dbu)
            main_cell.shapes(lay.layer(1, 0)).insert(mark.transform(mark_trans))
            idx += 1

            main_cell.flatten(1)  # flatten to remove the top cell of the resonator

        print("Saving file...")
        Path("../../wafers/").mkdir(parents=True, exist_ok=True)
        lay.write(f"../../wafers/{save_name}.gds")


def _mark(l: float, w: float):
    """
    Helper for creating cutting marks.
    :@param l: Arm length of the mark, measured from (0, 0)
    :@param w: Arm width of the mark, measured from the axis (resulting in a total width of 2*w)
    :@return: A list containing the coordinates of the mark, centered around (0, 0)
    """
    return pya.SimplePolygon([pya.DPoint(-w, -w), pya.DPoint(-w, -l), pya.DPoint(w, -l),
                             pya.DPoint(w, -w), pya.DPoint(l, -w), pya.DPoint(l, w),
                             pya.DPoint(w, w), pya.DPoint(w, l), pya.DPoint(-w, l),
                             pya.DPoint(-w, w), pya.DPoint(-l, w), pya.DPoint(-l, -w)])
