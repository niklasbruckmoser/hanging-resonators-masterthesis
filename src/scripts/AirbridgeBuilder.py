from pathlib import Path

import src.library.KLayout.Main
import src.library.TextGen as TextGen
from src.library.Cells import *


class AirbridgeBuilder:

    def __init__(self, chip_width=4500, chip_height=21000, width=10, gap=6, ground=50, hole=40):

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

    def create_chip(self, file_out, hole_mask=False):
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
        self._write_structures()
        self._perform_boolean_operations()
        self._write_file(file_out)

        self.frequencies = []

    def _write_structures(self):
        """
        Subroutine for writing the main structures.
        """

        print("Writing structures...")

        pad_gaps = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]


        bridge_width=30
        bridge_pad_width=bridge_width*2.5
        bridge_pad_height=20
        pad_width=bridge_pad_width + 20
        pad_height= bridge_pad_height + 20



        max_pad_gap = pad_gaps[-1]

        arr_size = (5, 4)

        prog_x = -2100
        prog_y = -9000

        spacing_x = 60
        spacing_y = 60

        block_spacing_x = 400
        block_spacing_y = 400

        for pad_gap in pad_gaps:
            for x in range(arr_size[0]):
                for y in range(arr_size[1]):

                    bridge = Airbridge(pad_width, pad_height, pad_gap, bridge_pad_width, bridge_pad_height, bridge_width)
                    bridge_cell = self.lay.create_cell(bridge.cell_name(), lib_name, bridge.as_list())
                    trans = pya.DCplxTrans.new(1, 0, False, prog_x, prog_y)
                    self.top.insert(pya.DCellInstArray(bridge_cell.cell_index(), trans))

                    prog_y += max_pad_gap+2*pad_height + spacing_y

                prog_x += pad_width + spacing_x
                prog_y -= arr_size[1]*(max_pad_gap+2*pad_height + spacing_y)

            prog_x -= arr_size[0]*(pad_width + spacing_x)
            prog_y += arr_size[1]*(max_pad_gap+2*pad_height + spacing_y) + block_spacing_y

            text = TextGen.write_text(self.lay, f"{bridge_width}x{pad_gap}")
            TextGen.place_cell(self.lay, self.top, text, 2, prog_x, prog_y - block_spacing_y - 80)

        prog_x += arr_size[0]*(pad_width + spacing_x) + block_spacing_x
        prog_y = -9000

        bridge_width=20
        bridge_pad_width=bridge_width*2.5
        bridge_pad_height=20
        pad_width=bridge_pad_width + 20
        pad_height= bridge_pad_height + 20

        for pad_gap in pad_gaps:
            for x in range(arr_size[0]):
                for y in range(arr_size[1]):
                    bridge = Airbridge(pad_width, pad_height, pad_gap, bridge_pad_width, bridge_pad_height, bridge_width)
                    bridge_cell = self.lay.create_cell(bridge.cell_name(), lib_name, bridge.as_list())
                    trans = pya.DCplxTrans.new(1, 0, False, prog_x, prog_y)
                    self.top.insert(pya.DCellInstArray(bridge_cell.cell_index(), trans))

                    prog_y += max_pad_gap+2*pad_height + spacing_y

                prog_x += pad_width + spacing_x
                prog_y -= arr_size[1]*(max_pad_gap+2*pad_height + spacing_y)

            prog_x -= arr_size[0]*(pad_width + spacing_x)
            prog_y += arr_size[1]*(max_pad_gap+2*pad_height + spacing_y) + block_spacing_y

            text = TextGen.write_text(self.lay, f"{bridge_width}x{pad_gap}")
            TextGen.place_cell(self.lay, self.top, text, 2, prog_x, prog_y - block_spacing_y - 80)

        prog_x += arr_size[0]*(pad_width + spacing_x) + block_spacing_x
        prog_y = -9000

        bridge_width = 10
        bridge_pad_width=bridge_width*2.5
        bridge_pad_height=20
        pad_width=bridge_pad_width + 20
        pad_height= bridge_pad_height + 20

        for pad_gap in pad_gaps:
            for x in range(arr_size[0]):
                for y in range(arr_size[1]):
                    bridge = Airbridge(pad_width, pad_height, pad_gap, bridge_pad_width, bridge_pad_height, bridge_width)
                    bridge_cell = self.lay.create_cell(bridge.cell_name(), lib_name, bridge.as_list())
                    trans = pya.DCplxTrans.new(1, 0, False, prog_x, prog_y)
                    self.top.insert(pya.DCellInstArray(bridge_cell.cell_index(), trans))

                    prog_y += max_pad_gap+2*pad_height + spacing_y

                prog_x += pad_width + spacing_x
                prog_y -= arr_size[1]*(max_pad_gap+2*pad_height + spacing_y)

            prog_x -= arr_size[0]*(pad_width + spacing_x)
            prog_y += arr_size[1]*(max_pad_gap+2*pad_height + spacing_y) + block_spacing_y

            text = TextGen.write_text(self.lay, f"{bridge_width}x{pad_gap}")
            TextGen.place_cell(self.lay, self.top, text, 2, prog_x, prog_y - block_spacing_y - 80)

        prog_x += arr_size[0]*(pad_width + spacing_x) + block_spacing_x
        prog_y = -9000

        bridge_width = 20

        for pad_gap in pad_gaps:
            for x in range(arr_size[0]):
                for y in range(arr_size[1]):
                    bridge = AirbridgeRound(35, pad_gap, 22, bridge_width)
                    bridge_cell = self.lay.create_cell(bridge.cell_name(), lib_name, bridge.as_list())
                    trans = pya.DCplxTrans.new(1, 0, False, prog_x, prog_y)
                    self.top.insert(pya.DCellInstArray(bridge_cell.cell_index(), trans))

                    prog_y += max_pad_gap+2*pad_height + spacing_y

                prog_x += pad_width + spacing_x
                prog_y -= arr_size[1]*(max_pad_gap+2*pad_height + spacing_y)

            prog_x -= arr_size[0]*(pad_width + spacing_x)
            prog_y += arr_size[1]*(max_pad_gap+2*pad_height + spacing_y) + block_spacing_y

            text = TextGen.write_text(self.lay, f"{bridge_width}x{pad_gap}")
            TextGen.place_cell(self.lay, self.top, text, 2, prog_x, prog_y - block_spacing_y - 80)


        prog_x += arr_size[0]*(pad_width + spacing_x) + block_spacing_x
        prog_y = -9000
        pad_width=12
        pad_height=12
        bridge_pad_width=9
        bridge_pad_height=9
        bridge_width=9

        arr_size = (5, 5)

        for pad_gap in pad_gaps:
            for x in range(arr_size[0]):
                for y in range(arr_size[1]):
                    bridge = Airbridge(pad_width, pad_height, pad_gap, bridge_pad_width, bridge_pad_height, bridge_width)
                    bridge_cell = self.lay.create_cell(bridge.cell_name(), lib_name, bridge.as_list())
                    trans = pya.DCplxTrans.new(1, 0, False, prog_x, prog_y)
                    self.top.insert(pya.DCellInstArray(bridge_cell.cell_index(), trans))

                    prog_y += max_pad_gap+2*pad_height + spacing_y

                prog_x += pad_width + spacing_x
                prog_y -= arr_size[1]*(max_pad_gap+2*pad_height + spacing_y)

            prog_x -= arr_size[0]*(pad_width + spacing_x)
            prog_y += arr_size[1]*(max_pad_gap+2*pad_height + spacing_y) + block_spacing_y

            text = TextGen.write_text(self.lay, f"{bridge_width}x{pad_gap}")
            TextGen.place_cell(self.lay, self.top, text, 2, prog_x, prog_y - block_spacing_y - 80)

        prog_x += arr_size[0]*(pad_width + spacing_x) + block_spacing_x
        prog_y = -9000

        pad_width=120
        pad_height=120
        bridge_pad_width=100
        bridge_pad_height=100
        bridge_width=20

        arr_size = (5, 2)

        for pad_gap in pad_gaps:
            for x in range(arr_size[0]):
                for y in range(arr_size[1]):
                    bridge = Airbridge(pad_width, pad_height, pad_gap, bridge_pad_width, bridge_pad_height, bridge_width)
                    bridge_cell = self.lay.create_cell(bridge.cell_name(), lib_name, bridge.as_list())
                    trans = pya.DCplxTrans.new(1, 0, False, prog_x, prog_y)
                    self.top.insert(pya.DCellInstArray(bridge_cell.cell_index(), trans))

                    prog_y += max_pad_gap+2*pad_height + spacing_y

                prog_x += pad_width + spacing_x
                prog_y -= arr_size[1]*(max_pad_gap+2*pad_height + spacing_y)

            prog_x -= arr_size[0]*(pad_width + spacing_x)
            prog_y += arr_size[1]*(max_pad_gap+2*pad_height + spacing_y) + block_spacing_y

            text = TextGen.write_text(self.lay, f"{bridge_width}x{pad_gap}")
            TextGen.place_cell(self.lay, self.top, text, 2, prog_x, prog_y - block_spacing_y - 80)

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
        if self.chip_height < 5900:
            logo_spacing = 50

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

    def _write_text(self, text):
        """
        Subroutine for writing text on the chip.
        :@param text: Text that will be printed on the chip.
        """
        print("Writing text...")

        lines = text.splitlines()

        y_shift = (-self.chip_height/2)  / self.dbu

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
        l15 = self.lay.layer(pya.LayerInfo(15, 0))  # first step for airbridges
        l16 = self.lay.layer(pya.LayerInfo(16, 0))  # second step for airbridges (with negative resist)

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
        target_layer.insert(self.top.shapes(l15))

        # remove auxiliary layers
        self.lay.clear_layer(l10)
        self.lay.clear_layer(l11)
        self.lay.clear_layer(l14)
        self.lay.clear_layer(l2)

        self.lay.clear_layer(l0)
        self.lay.clear_layer(l12)
        self.lay.clear_layer(l13)
        self.lay.clear_layer(l15)

        # self.top.shapes(l3).insert(pya.Box(-self.chip_width/2/self.dbu, -self.chip_height/2/self.dbu,
        #                                    self.chip_width/2/self.dbu, self.chip_height/2/self.dbu))
        # processor.boolean(self.lay, self.top, l3, self.lay, self.top, l1, self.top.shapes(l1),
        #                   pya.EdgeProcessor.ModeAnd, True, True, True)

    def _write_file(self, file_out):
        """
        Subroutine for saving the file.
        :@param file_out: Name of the .gds file
        """

        print("Saving file...")
        Path("../../chips/").mkdir(parents=True, exist_ok=True)
        self.lay.write("../chips/" + file_out + ".gds")


ab = AirbridgeBuilder()
ab.create_chip("airbridge_v6")