import src.library.KLayout.Main
from pathlib import Path
from src.library.Cells import *


class HoleGenerator:

    def __init__(self):
        self.lay = None
        self.top = None
        self.dbu = None

    def create_hole_mask(self, file_out, width=10000, height=6000, l_spacing=50, l_sigma=3, l_size=2, hd_spacing=10, hd_sigma=2, hd_size=2):
        """
        Creates a hole mask saves it automatically as a .gds file.
        :@param file_out: Name of the gds file
        """

        self.lay = pya.Layout()
        self.top = self.lay.create_cell("HOLE")
        self.dbu = self.lay.dbu

        self._write_holes(width, height, l_spacing, l_sigma, l_size, hd_spacing, hd_sigma, hd_size)
        self._write_file(file_out)

    def _write_holes(self, width, height, l_spacing, l_sigma, l_size, hd_spacing, hd_sigma, hd_size):
        """
        Subroutine for writing the main structures.
        """

        # periodic holes
        print("writing low density holes...")
        hole_pattern = HoleMask(width=width, height=height, spacing=l_spacing, sigma=l_sigma, size=l_size, hd_holes=0)
        hole_cell = self.lay.create_cell(hole_pattern.cell_name(), lib_name, hole_pattern.as_list())
        trans = pya.DCplxTrans.new(1, 0, False, 0, 0)
        self.top.insert(pya.DCellInstArray(hole_cell.cell_index(), trans))

        # high density holes
        print("writing high density holes...")
        hole_pattern = HoleMask(width=width, height=height, spacing=hd_spacing, sigma=hd_sigma, size=hd_size, hd_holes=1)
        hole_cell = self.lay.create_cell(hole_pattern.cell_name(), lib_name, hole_pattern.as_list())
        trans = pya.DCplxTrans.new(1, 0, False, 0, 0)
        self.top.insert(pya.DCellInstArray(hole_cell.cell_index(), trans))

        self.top.flatten(1)

    def _write_file(self, file_out):
        """
        Subroutine for saving the file.
        :@param file_out: Name of the .gds file
        """

        print("Saving file...")
        Path("../../chips/").mkdir(parents=True, exist_ok=True)
        self.lay.write("../../chips/" + file_out + ".gds")

# # Example usage:
# hg = HoleGenerator()
# hg.create_hole_mask("hole_mask_small_full", width=14300, height=14300, l_spacing=50, l_sigma=2, l_size=2, hd_spacing=10, hd_sigma=2, hd_size=2)
