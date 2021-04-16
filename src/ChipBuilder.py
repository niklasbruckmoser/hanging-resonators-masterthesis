from pathlib import Path

import numpy as np

import src.library.CPWLibrary.HangingResonator as HangingResonator
import src.library.CPWLibrary.Main
import src.library.TextGen as TextGen
from src.library.CPWLibrary.CellParams import *


class ChipBuilder:

    def __init__(self, chip_width=10000, chip_height=6000, width=10, gap=6, ground=50, hole=40):

        self.frequencies = []

        self.chip_width = chip_width
        self.chip_height = chip_height
        self.width = width
        self.gap = gap
        self.ground = ground
        self.hole = hole

        self.lay = None
        self.top = None
        self.dbu = None

    def create_chip(self, file_out, res_params, text=None, markers=False, hole_mask="hole_mask_50-10"):
        """
        Creates a chip from the blueprint in the given frequency range and saves it automatically as a .gds file.
        @param file_out: file name of the .gds file
        @param res_params: list of ResonatorParams, see @CellParams
        @param text: Written text on the chip. Supports \n
        @param markers: if True, writes nb5 markers onto the layout
        @param hole_mask: if True, writes hole mask onto the layout
        """
        print("Creating chip " + file_out + "...")

        self.lay = pya.Layout()
        self.top = self.lay.create_cell("TOP")
        self.dbu = self.lay.dbu

        if hole_mask is not False:
            self._write_fast_holes(hole_mask)
        self._write_structures(res_params)
        self._write_logos()
        if markers:
            self._write_markers_leo()
        self._write_text(text)
        self._perform_boolean_operations()
        self._write_file(file_out)

        self.frequencies = []

    def _write_structures(self, res_params):
        """
        Subroutine for writing the main structures.
        """

        print("Writing structures...")

        x_prog = -self.chip_width/2
        # Transmission line
        # port_params = PortParams(130, 200, 400, -300, 10, 6, 50, 40)
        port_params = PortParams(160, 200, 300, 0, 10, 6, 50, 40)
        port = self.lay.create_cell("Port", "QC", port_params.as_list())
        trans = pya.DCplxTrans.new(1, 0, False, x_prog, 0)
        self.top.insert(pya.DCellInstArray(port.cell_index(), trans))

        port_len = port_params.end_point().x
        x_prog += port_len

        tl_len = self.chip_width - 2*port_len

        straight_params = StraightParams(tl_len, 10, 6, 50, 40)
        straight = self.lay.create_cell("Straight", "QC", straight_params.as_list())
        trans = pya.DCplxTrans.new(1, 0, False, x_prog, 0)
        self.top.insert(pya.DCellInstArray(straight.cell_index(), trans))
        x_prog += straight_params.end_point().x

        port = self.lay.create_cell("Port", "QC", port_params.as_list())
        trans = pya.DCplxTrans.new(1, 180, False, x_prog+port_len, 0)
        self.top.insert(pya.DCellInstArray(port.cell_index(), trans))

        port = self.lay.create_cell("Port", "QC", port_params.as_list())
        trans = pya.DCplxTrans.new(1, 180, False, x_prog+port_params.end_point().x, 0)
        self.top.insert(pya.DCellInstArray(port.cell_index(), trans))

        safe_zone = 0
        for res in res_params:
            new_sz = res.segment_length + 2*(res.radius + res.ground + res.hole + res.gap + res.width/2)
            safe_zone = new_sz if new_sz > safe_zone else safe_zone

        residual = tl_len - safe_zone*(len(res_params)/2+0.5)

        safe_zone += residual / (len(res_params)/2+0.5)

        up = True

        x_prog = -tl_len/2

        for res in res_params:

            self.frequencies.append(HangingResonator.calc_f0(res.length*1000))

            x_prog += safe_zone/2
            if type(res) == HangingResonatorParams:
                res_cell = self.lay.create_cell("HangingResonator", "QC", res.as_list())
            else:
                res_cell = self.lay.create_cell("HangingResonatorFingers", "QC", res.as_list())
            trans = pya.DCplxTrans.new(1, 0, not up, x_prog, 0)
            self.top.insert(pya.DCellInstArray(res_cell.cell_index(), trans))

            up = not up

    def _write_fast_holes(self, name):
        """
        Subroutine for writing the logos on the chip.
        """
        print("Writing holes...")

        # hole files
        # TODO: auto generate if not existent?
        self.lay.read("../templates/" + name + ".gds")

        cell = self.lay.cell_by_name("HOLE")
        trans = pya.DCplxTrans.new(1, 0, False, 0, 0)
        self.top.insert(pya.DCellInstArray(cell, trans))
        self.top.flatten(1)

    def _write_logos(self):
        """
        Subroutine for writing the logos on the chip.
        """

        print("Writing logos...")

        size_multiplier = 0.5
        logo_spacing = 150

        # logo files
        self.lay.read("../templates/logo_mcqst.gds")
        self.lay.read("../templates/logo_wmi_new.gds")

        cell_mcqst = self.lay.cell_by_name("MCQST")
        trans = pya.DCplxTrans.new(size_multiplier, 0, False, self.chip_width / 2 - logo_spacing - 550,
                                   self.chip_height / 2 - logo_spacing - 325)
        self.top.insert(pya.DCellInstArray(cell_mcqst, trans))

        cell_wmi = self.lay.cell_by_name("WMI")
        trans = pya.DCplxTrans.new(size_multiplier, 0, False, -(self.chip_width / 2 - logo_spacing - 550),
                                   self.chip_height / 2 - logo_spacing - 325)
        self.top.insert(pya.DCellInstArray(cell_wmi, trans))

    def _write_markers_leo(self):
        """
        Subroutine for writing markers on the chip.
        """

        l0 = self.lay.layer(pya.LayerInfo(0, 0))
        l2 = self.lay.layer(pya.LayerInfo(2, 0))

        marker_width = 10 / self.dbu
        focus_width = 20 / self.dbu
        x_shift = 1015 / self.dbu - marker_width
        y_shift = x_shift
        marker = pya.Box(-marker_width/2, -marker_width/2,
                         marker_width/2, marker_width/2)
        focus = pya.Polygon([pya.DPoint(-focus_width, 0),
                             pya.DPoint(0, -focus_width),
                             pya.DPoint(0, focus_width),
                             pya.DPoint(focus_width, 0)])
        focus_trans = pya.ICplxTrans(1, 0, False, 10*marker_width + focus_width, 0)
        mask_trans = pya.ICplxTrans(30, 0, False, 0, 0)

        # top left
        top_left_trans = pya.ICplxTrans(1, 0, False, -self.chip_width / (2 * self.dbu) + x_shift, self.chip_height / (2 * self.dbu) - y_shift)
        self.top.shapes(l0).insert(marker.transformed(top_left_trans))
        self.top.shapes(l2).insert(marker.transformed(top_left_trans * mask_trans))
        self.top.shapes(l0).insert(focus.transformed(top_left_trans * focus_trans))
        self.top.shapes(l2).insert(marker.transformed(top_left_trans * focus_trans * mask_trans))
        # top right
        top_right_trans = pya.ICplxTrans(1, 0, False, self.chip_width / (2 * self.dbu) - x_shift, self.chip_height / (2 * self.dbu) - y_shift)
        self.top.shapes(l0).insert(marker.transformed(top_right_trans))
        self.top.shapes(l2).insert(marker.transformed(top_right_trans * mask_trans))
        self.top.shapes(l0).insert(focus.transformed(top_right_trans * focus_trans))
        self.top.shapes(l2).insert(marker.transformed(top_right_trans * focus_trans * mask_trans))
        # bottom left
        bottom_left_trans = pya.ICplxTrans(1, 0, False, -self.chip_width / (2 * self.dbu) + x_shift, -self.chip_height / (2 * self.dbu) + y_shift)
        self.top.shapes(l0).insert(marker.transformed(bottom_left_trans))
        self.top.shapes(l2).insert(marker.transformed(bottom_left_trans * mask_trans))
        self.top.shapes(l0).insert(focus.transformed(bottom_left_trans * focus_trans))
        self.top.shapes(l2).insert(marker.transformed(bottom_left_trans * focus_trans * mask_trans))
        # bottom right
        bottom_right_trans = pya.ICplxTrans(1, 0, False, self.chip_width / (2 * self.dbu) - x_shift, -self.chip_height / (2 * self.dbu) + y_shift)
        self.top.shapes(l0).insert(marker.transformed(bottom_right_trans))
        self.top.shapes(l2).insert(marker.transformed(bottom_right_trans * mask_trans))
        self.top.shapes(l0).insert(focus.transformed(bottom_right_trans * focus_trans))
        self.top.shapes(l2).insert(marker.transformed(bottom_right_trans * focus_trans * mask_trans))

    def _write_markers(self, inverted=False):
        """
        Subroutine for writing nanobeam markers on the chip
        """
        print("Writing markers...")

        if inverted:
            file = "nb5marker_inverted"
        else:
            file = "nb5marker"
        self.lay.read("../templates/" + file + ".gds")
        cell_marker = self.lay.cell_by_name("nb5marker")
        trans = pya.DCplxTrans.new(1, 0, False, 0, 0)
        self.top.insert(pya.DCellInstArray(cell_marker, trans))

    def _write_text(self, text=None, frequencies=True):
        """
        Subroutine for writing text on the chip.
        :@param text: Text that will be printed on the chip. Set to None for printing the resonance frequencies
        """
        print("Writing text...")

        if text is None:
            text = ""
        else:
            text += "\n"

        if frequencies is True:
            text += "´f0´ (GHz): "
            for i in range(len(self.frequencies)):
                if len(self.frequencies) > 16 and i == np.floor(len(self.frequencies) / 2):
                    text += "\n"
                text += "{:.2f}".format(self.frequencies[i])
                if i < len(self.frequencies) - 1:
                    text += ", "

        lines = text.splitlines()

        y_shift = (-self.chip_height/2 + len(lines)*150.) / self.dbu

        for line in lines:
            text = TextGen.write_text(self.lay, line)
            TextGen.place_cell_center(self.lay, self.top, text, 3, 0, y_shift*self.dbu)
            y_shift -= 150 / self.dbu

    def _perform_boolean_operations(self):
        """
        Subroutine for performing the boolean layer operations. This has to be the last step before saving the gds file.
        """

        print("performing boolean operations...")

        # define layers for convenience
        l0 = self.lay.layer(pya.LayerInfo(0, 0))  # logos and text
        l1 = self.lay.layer(pya.LayerInfo(1, 0))  # main structure
        l2 = self.lay.layer(pya.LayerInfo(2, 0))  # text mask
        l3 = self.lay.layer(pya.LayerInfo(3, 0))  # main structure
        l10 = self.lay.layer(pya.LayerInfo(10, 0))  # spacing
        l11 = self.lay.layer(pya.LayerInfo(11, 0))  # high density hole mask
        l12 = self.lay.layer(pya.LayerInfo(12, 0))  # periodic holes
        l13 = self.lay.layer(pya.LayerInfo(13, 0))  # high density holes
        l14 = self.lay.layer(pya.LayerInfo(14, 0))  # logo background for removing periodic holes

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
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l2, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)

        # place everything into a single layer (0, 12, 13 into 1)
        target_layer = self.top.shapes(l1)

        target_layer.insert(self.top.shapes(l13))
        target_layer.insert(self.top.shapes(l12))
        target_layer.insert(self.top.shapes(l0))

        # remove auxiliary layers
        self.lay.clear_layer(l10)
        self.lay.clear_layer(l11)
        self.lay.clear_layer(l14)
        self.lay.clear_layer(l2)

        self.lay.clear_layer(l0)
        self.lay.clear_layer(l12)
        self.lay.clear_layer(l13)

        self.top.shapes(l3).insert(pya.Box(-self.chip_width/2/self.dbu, -self.chip_height/2/self.dbu,
                                           self.chip_width/2/self.dbu, self.chip_height/2/self.dbu))
        processor.boolean(self.lay, self.top, l3, self.lay, self.top, l1, self.top.shapes(l1),
                          pya.EdgeProcessor.ModeAnd, True, True, True)

    def _write_file(self, file_out):
        """
        Subroutine for saving the file.
        :@param file_out: Name of the .gds file
        """

        print("Saving file...")
        Path("../chips/").mkdir(parents=True, exist_ok=True)
        self.lay.write("../chips/" + file_out + ".gds")

    def res_params(self, f_start, f_end, amount_resonators=11, segment_length=950, x_offset=950, y_offset=300,
                   q_ext=1e5, coupling_ground=10, radius=100, shorted=1, width_tl=10, gap_tl=6, width=10, gap=6,
                   ground=50, hole=40):
        """
        generate a list of resonator params for given parameters that are equally frequency-spaced
        @param f_start: start frequency
        @param f_end: end frequency
        @param amount_resonators: amount of resonators
        @param segment_length: x length of the straight
        @param x_offset: initial x offset (typically same as segment_length, not optimized for different lengths)
        @param y_offset: initial y offset
        @param q_ext: external coupling factor
        @param coupling_ground: distance from TL to resonator
        @param radius: meander radius (should be > 10*width)
        @param shorted: 1 = lambda/4, 0 = lambda/2 resonator
        @param width_tl: width of the TL (needed for q_ext calculation)
        @param gap_tl: gap of the TL (needed for q_ext calculation)
        @param width: width of the resonator
        @param gap: gap of the resonator
        @param ground: distance from gap to high density holes
        @param hole: width of high density holes
        @return: ResonatorParams for each resonator in a list
        """
        params = []

        interval = (f_end - f_start) / (amount_resonators - 1)
        for i in range(amount_resonators):
            f0 = f_start + i*interval
            length = HangingResonator.calc_length(f0) / 1000
            params.append(HangingResonatorParams(segment_length, length, x_offset, y_offset, q_ext, coupling_ground,
                                                 radius, shorted, width_tl, gap_tl, width, gap, ground, hole))

        return params

    def res_fingers_params(self, f_start, f_end, amount_resonators=11, segment_length=950, x_offset=950, y_offset=300,
                          q_ext=1e5, coupling_ground=10, radius=100, shorted=1, width_tl=10, gap_tl=6, width=10, gap=6,
                          ground=50, hole=40, n_fingers=20, finger_length=20, finger_end_gap=6, finger_spacing=20,
                          hook_width=5, hook_length=2, hook_unit=1, electrode_width=0.3, bridge_width=0.4, bridge_length=1):
        """
        generate a list of resonator params for given parameters
        @return: a list containing ResonatorParams
        """
        params = []

        interval = (f_end - f_start) / (amount_resonators - 1)
        for i in range(amount_resonators):
            f0 = f_start + i*interval
            length = HangingResonator.calc_length(f0) / 1000
            params.append(HangingResonatorFingersParams(segment_length, length, x_offset, y_offset, q_ext,
                                                        coupling_ground, radius, shorted, width_tl, gap_tl, width, gap,
                                                        ground, hole, n_fingers, finger_length, finger_end_gap,
                                                        finger_spacing, hook_width, hook_length, hook_unit,
                                                        electrode_width, bridge_width, bridge_length))

        return params
