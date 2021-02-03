import numpy as np
# import src.library.CPW_pieces
# import src.library.CPWLib
import src.library.CPWLibrary.Main
import src.library.TextGen as TextGen
import src.library.CPW_pieces
import src.library.CPWLibrary.HangingResonator as HangingResonator
from pathlib import Path
from src.library.CPWLibrary.CellParams import *


class SimulationBuilder:

    def __init__(self, chip_width=3000, chip_height=3000, width=10, gap=6, ground=50, hole=40):

        self.chip_width = chip_width
        self.chip_height = chip_height
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole

        self.lay = None
        self.top = None
        self.dbu = None

    def create_chip(self, file_out, res_params, hole_mask="hole_mask_50-10"):
        """
        Creates a chip from the blueprint in the given frequency range and saves it automatically as a .gds file.
        @param file_out: file name of the .gds file
        @param res_params: list of ResonatorParams, see @CellParams
        @param hole_mask: if True, writes hole mask onto the layout
        """
        print("Creating chip " + file_out + "...")

        self.lay = pya.Layout()
        self.top = self.lay.create_cell("TOP")
        self.dbu = self.lay.dbu

        if hole_mask is not False:
            self._write_fast_holes(hole_mask)
        self._write_structures(res_params)
        self._perform_boolean_operations()
        self._write_file(file_out)
        self._write_tech_file(file_out)

    def _write_structures(self, res_params):
        """
        Subroutine for writing the main structures.
        """

        print("Writing structures...")

        x_prog = -self.chip_width/2
        # Transmission line
        tl_len = self.chip_width

        straight_params = StraightParams(tl_len, 10, 6, 50, 40)
        straight = self.lay.create_cell("Straight", "QC", straight_params.as_list())
        trans = pya.DCplxTrans.new(1, 0, False, x_prog, -self.chip_height/2 + self.chip_height/10)
        self.top.insert(pya.DCellInstArray(straight.cell_index(), trans))
        x_prog += straight_params.end_point().x

        # print("Frequency: " + str(HangingResonator.calc_f0(res_params.length*1000)) + " GHz")

        if type(res_params) == HangingResonatorParams:
            res_cell = self.lay.create_cell("HangingResonator", "QC", res_params.as_list())
        else:
            res_cell = self.lay.create_cell("HangingResonatorFingers", "QC", res_params.as_list())
        trans = pya.DCplxTrans.new(1, 0, False, 0, -self.chip_height/2 + self.chip_height/10)
        self.top.insert(pya.DCellInstArray(res_cell.cell_index(), trans))

        # create ports
        self.top.shapes(self.lay.layer(pya.LayerInfo(4, 0))).insert(pya.DPath([
            pya.DPoint(-self.chip_width/2, -self.width/2 - 2 * self.gap - self.chip_height/2 + self.chip_height/10),
            pya.DPoint(-self.chip_width/2, self.width/2 + 2 * self.gap - self.chip_height/2 + self.chip_height/10)], 0))
        self.top.shapes(self.lay.layer(pya.LayerInfo(4, 0))).insert(pya.DPath([
            pya.DPoint(self.chip_width/2, -self.width/2 - 2 * self.gap - self.chip_height/2 + self.chip_height/10),
            pya.DPoint(self.chip_width/2, self.width/2 + 2 * self.gap - self.chip_height/2 + self.chip_height/10)], 0))

    def _write_fast_holes(self, name):
        """
        Subroutine for writing the logos on the chip.
        """
        print("Writing holes...")

        # hole files
        self.lay.read("../templates/" + name + ".gds")

        cell = self.lay.cell_by_name("HOLE")
        trans = pya.DCplxTrans.new(1, 0, False, 0, 0)
        self.top.insert(pya.DCellInstArray(cell, trans))
        self.top.flatten(1)

    def _perform_boolean_operations(self):
        """
        Subroutine for performing the boolean layer operations. This has to be the last step before saving the gds file.
        """

        print("performing boolean operations...")

        # define layers for convenience
        l1 = self.lay.layer(pya.LayerInfo(1, 0))  # main structure
        l2 = self.lay.layer(pya.LayerInfo(2, 0))  # ground
        l3 = self.lay.layer(pya.LayerInfo(3, 0))  # main structure
        l10 = self.lay.layer(pya.LayerInfo(10, 0))  # spacing
        l11 = self.lay.layer(pya.LayerInfo(11, 0))  # high density hole mask
        l12 = self.lay.layer(pya.LayerInfo(12, 0))  # periodic holes
        l13 = self.lay.layer(pya.LayerInfo(13, 0))  # high density holes
        l14 = self.lay.layer(pya.LayerInfo(14, 0))  # logo background for removing periodic holes
        l98 = self.lay.layer(pya.LayerInfo(98, 0))  # Al structures

        # flatten, otherwise boolean operations won't work
        self.top.flatten(1)

        # prepare a shape processor
        processor = pya.ShapeProcessor()

        # preprocessing
        processor.boolean(self.lay, self.top, l11, self.lay, self.top, l10, self.top.shapes(l11),
                          pya.EdgeProcessor.ModeANotB, True, True, True)

        # hole boolean operations
        processor.boolean(self.lay, self.top, l13, self.lay, self.top, l11, self.top.shapes(l13),
                          pya.EdgeProcessor.ModeAnd, True, True, True)
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l11, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l10, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l14, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)

        # place everything into a single layer (0, 12, 13 into 1)
        target_layer = self.top.shapes(l1)

        target_layer.insert(self.top.shapes(l13))
        target_layer.insert(self.top.shapes(l12))

        # remove auxiliary layers
        self.lay.clear_layer(l10)
        self.lay.clear_layer(l11)
        self.lay.clear_layer(l14)
        self.lay.clear_layer(l12)
        self.lay.clear_layer(l13)
        self.lay.clear_layer(l98)

        self.top.shapes(l3).insert(pya.Box(-self.chip_width/2/self.dbu, -self.chip_height/2/self.dbu,
                                           self.chip_width/2/self.dbu, self.chip_height/2/self.dbu))
        processor.boolean(self.lay, self.top, l3, self.lay, self.top, l1, self.top.shapes(l1),
                          pya.EdgeProcessor.ModeAnd, True, True, True)

        # create ground layer
        processor.boolean(self.lay, self.top, l3, self.lay, self.top, l1, self.top.shapes(l2),
                          pya.EdgeProcessor.ModeANotB, True, True, True)

    def _write_file(self, file_out):
        """
        Subroutine for saving the file.
        :@param file_out: Name of the .gds file
        """

        print("Saving GDS file...")
        Path("../chips/").mkdir(parents=True, exist_ok=True)
        self.lay.write("../chips/" + file_out + ".gds")

    def _write_tech_file(self, file_out):
        print("Saving TECH file...")
        f = open("../chips/" + file_out + ".tech", "w")
        f.write("UNITS um\n/\n")
        f.write("/ ----------------------------------------------------------\n")
        f.write("/ import#	destination		Color	Elevation	Thickness\n")
        f.write("/ ----------------------------------------------------------\n")
        f.write("1			gap		        blue	0		    0\n")
        f.write("2			Nb       		orange	0   		0\n")
        f.write("3			substrate   	gray	-525   		525\n")
        f.write("4			port           	red 	-34   		34\n")
        f.close()

    def res_params(self, f, segment_length=950, x_offset=950, y_offset=300, q_ext=1e5, coupling_ground=10, radius=100,
                   shorted=1, width_tl=10, gap_tl=6, width=10, gap=6, ground=50, hole=40):
        """
        generate resonator params for given parameters
        @return: a list containing ResonatorParams
        """

        length = HangingResonator.calc_length(f) / 1000
        return HangingResonatorParams(segment_length, length, x_offset, y_offset, q_ext, coupling_ground,
                                      radius, shorted, width_tl, gap_tl, width, gap, ground, hole)


    def res_fingers_params(self, f, segment_length=950, x_offset=950, y_offset=300, q_ext=1e5, coupling_ground=10,
                           radius=100, shorted=1, width_tl=10, gap_tl=6, width=10, gap=6, ground=50, hole=40,
                           n_fingers=20, finger_length=20, finger_end_gap=6, finger_spacing=20, hook_width=5,
                           hook_length=2, hook_unit=1, electrode_width=0.3, bridge_width=0.4, bridge_length=1):
        """
        generate resonator params for given parameters
        @return: a list containing ResonatorParams
        """

        length = HangingResonator.calc_length(f) / 1000
        return HangingResonatorFingersParams(segment_length, length, x_offset, y_offset, q_ext,
                                                    coupling_ground, radius, shorted, width_tl, gap_tl, width, gap,
                                                    ground, hole, n_fingers, finger_length, finger_end_gap,
                                                    finger_spacing, hook_width, hook_length, hook_unit,
                                                    electrode_width, bridge_width, bridge_length)
