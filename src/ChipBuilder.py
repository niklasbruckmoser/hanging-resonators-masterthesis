import numpy as np
# import src.library.CPW_pieces
# import src.library.CPWLib
import src.library.CPWLibrary.Main
import src.library.TextGen as TextGen
import src.library.CPW_pieces
import src.library.CPWLibrary.HangingResonator as HangingResonator
from pathlib import Path
from src.library.CPWLibrary.CellParams import *

class PadTest:

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

    def create_chip(self, file_out, text=None):
        """
        Creates a chip from the blueprint in the given frequency range and saves it automatically as a .gds file.
        :@param file_out: Name of the gds file
        :@param f_start: Start frequency
        :@param f_end: End frequency
        :@param amount_resonators: Amount of resonators on the chip. Set to 0 for a dense filling
        :@param frequencies: A list containing the frequencies of the resonators, in GHz (replaces f_start, f_end and
                amount_resonators)
        :@param printed_text: Can be used for displaying custom text on the chip
        :@param print_frequencies: In addition to the text, print the frequencies of the resonators
        :@param markers: Add nb5 markers (6x10) to the chip layout
        """
        print("Creating chip " + file_out + "...")

        self.lay = pya.Layout()
        self.top = self.lay.create_cell("TOP")
        self.dbu = self.lay.dbu

        res_params = [
            HangingResonatorParams(950, 1600, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
            HangingResonatorParams(950, 1700, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
            HangingResonatorParams(950, 2000, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
            HangingResonatorParams(950, 2500, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
            HangingResonatorParams(950, 3000, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
            HangingResonatorParams(950, 3500, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
            HangingResonatorParams(950, 4000, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
            HangingResonatorParams(950, 4500, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
            HangingResonatorParams(950, 5000, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
            HangingResonatorParams(950, 5500, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
            HangingResonatorParams(950, 6000, 950, 100, 1e5, 12, 80, 1, 10, 6, 10, 6, 50, 40),
        ]

        self._write_structures(res_params)
        self._write_logos()
        self._write_text(text)
        # self._perform_boolean_operations()
        self._write_file(file_out)

        self.frequencies = []

    def _write_structures(self, res_params):
        """
        Subroutine for writing the main structures.
        """

        self._write_fast_holes()

        print("Writing structures...")

        x_prog = -self.chip_width/2
        # Transmission line

        port_params = PortParams(100, 200, 400, -300, 10, 6, 50, 40)
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

        residual = tl_len - (safe_zone*np.ceil(len(res_params)/2))

        safe_zone += residual / np.ceil(len(res_params)/2)

        x_up = -tl_len/2
        x_down = -tl_len/2 + safe_zone/2
        up = True

        for res in res_params:

            self.frequencies.append(HangingResonator.calc_f0(res.length*1000))

            if up:
                x_up += safe_zone/2
                res_cell = self.lay.create_cell("HangingResonator", "QC", res.as_list())
                trans = pya.DCplxTrans.new(1, 0, not up, x_up, 0)
                self.top.insert(pya.DCellInstArray(res_cell.cell_index(), trans))
                x_up += safe_zone/2
            else:
                x_down += safe_zone/2
                res_cell = self.lay.create_cell("HangingResonator", "QC", res.as_list())
                trans = pya.DCplxTrans.new(1, 0, not up, x_down, 0)
                self.top.insert(pya.DCellInstArray(res_cell.cell_index(), trans))
                x_down += safe_zone/2

            up = not up


    def _write_fast_holes(self):
        """
        Subroutine for writing the logos on the chip.
        """
        print("Writing holes...")

        # hole files
        # TODO: auto generate if not existent?
        self.lay.read("../templates/hole_mask_50-10.gds")

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
        self.lay.read("../templates/logo_wmi.gds")

        cell_mcqst = self.lay.cell_by_name("MCQST")
        trans = pya.DCplxTrans.new(size_multiplier, 0, False, self.chip_width / 2 - logo_spacing - 550,
                                   self.chip_height / 2 - logo_spacing - 325)
        self.top.insert(pya.DCellInstArray(cell_mcqst, trans))

        cell_wmi = self.lay.cell_by_name("WMI")
        trans = pya.DCplxTrans.new(size_multiplier, 0, False, -(self.chip_width / 2 - logo_spacing - 550),
                                   self.chip_height / 2 - logo_spacing - 325)
        self.top.insert(pya.DCellInstArray(cell_wmi, trans))


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
            text += "f0 (GHz): "
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
        l120 = self.lay.layer(pya.LayerInfo(120, 0))  # ? ? ?

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
        self.lay.clear_layer(l120)  # not really sure why this layer even exists... maybe rewrite the CPW_pieces class
        self.lay.clear_layer(l14)
        self.lay.clear_layer(l2)

        self.lay.clear_layer(l0)
        self.lay.clear_layer(l12)
        self.lay.clear_layer(l13)

        self.top.shapes(l3).insert(pya.Box(-5000/self.dbu, -3000/self.dbu, 5000/self.dbu, 3000/self.dbu))
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
        generate a list of resonator params for given parameters
        @param f_start:
        @param f_end:
        @param amount_resonators:
        @param segment_length:
        @param x_offset:
        @param y_offset:
        @param q_ext:
        @param coupling_ground:
        @param radius:
        @param shorted:
        @param width_tl:
        @param gap_tl:
        @param width:
        @param gap:
        @param ground:
        @param hole:
        @return:
        """
        params = []

        if x_offset == 0:
            x_offset = segment_length/2-radius/2

        interval = (f_end - f_start) / (amount_resonators - 1)
        for i in range(amount_resonators):
            f0 = f_start + i*interval
            length = HangingResonator.calc_length(f0) / 1000
            params.append(HangingResonatorParams(segment_length, length, x_offset, y_offset, q_ext, coupling_ground,
                                                 radius, shorted, width_tl, gap_tl, width, gap, ground, hole))

        return params


pd = PadTest()
pd.create_chip("curve")