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

    def create_chip(self, file_out):
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


        self._write_structures()

        self._perform_boolean_operations()
        self._write_file(file_out)

        self.frequencies = []

    def _write_structures(self):
        """
        Subroutine for writing the main structures.
        """

        print("Writing structures...")

        straight_len = 40
        straight_w = 20
        straight_g = 10

        x_prog = 0

        values = [(5, 30), (5, 40), (5, 50), (5, 70)]  # amount

        max_y = values[-1][0]*(values[-1][1]+straight_len)

        m_ul_x = -200
        m_ul_y = max_y + 700



        m_lr_x = m_ul_x + 2600
        m_lr_y = m_ul_y - 2200

        self._place_marker(m_ul_x, m_ul_y)
        self._place_marker(m_lr_x, m_lr_y)
        self._place_marker(m_ul_x, m_ul_y)
        self._place_marker(m_lr_x, m_lr_y)
        self._place_marker(m_ul_x, m_ul_y)
        self._place_marker(m_lr_x, m_lr_y)

        text = TextGen.write_text(self.lay, f"2.6 2.2")
        TextGen.place_cell_center(self.lay, self.top, text, 1.5, m_ul_x+250, m_ul_y-70)

        # self._place_marker(-200, max_y + 700)
        # self._place_marker(300*len(values)*2 + 100, -200)

        # print(-200 - (300*len(values)*2 + 100))
        # print(max_y + 700 - (-200))

        for x in range(len(values)):

            y_prog = 0

            straight = Straight(straight_len, straight_w, straight_g, 0, 0)
            straight_cell = self.lay.create_cell(straight.cell_name(), lib_name, straight.as_list())

            port = CustomPort(200, 50, 50, 200, 0, straight_w, straight_g, 0, 0)
            port_cell = self.lay.create_cell(port.cell_name(), lib_name, port.as_list())
            trans = pya.DCplxTrans.new(1, 90, False, x_prog, 0)
            self.top.insert(pya.DCellInstArray(port_cell.cell_index(), trans))

            y_prog += 300

            amount, bridge_len = values[x]

            for y in range(amount):

                trans = pya.DCplxTrans.new(1, 90, False, x_prog, y_prog)
                self.top.insert(pya.DCellInstArray(straight_cell.cell_index(), trans))
                y_prog += straight_len

                self.top.shapes(self.lay.layer(pya.LayerInfo(1, 0))).insert(
                    pya.Box((x_prog-straight_g-straight_w/2)/self.dbu, y_prog/self.dbu, (x_prog+straight_g+straight_w/2)/self.dbu, (y_prog+bridge_len)/self.dbu))
                y_prog += bridge_len

                bridge = Airbridge(straight_w, straight_w*0.75, bridge_len, straight_w*0.75, straight_w*0.75*0.75, straight_w*0.65, 0)
                bridge_cell = self.lay.create_cell(bridge.cell_name(), lib_name, bridge.as_list())
                trans = pya.DCplxTrans.new(1, 0, False, x_prog, y_prog-bridge_len/2)
                self.top.insert(pya.DCellInstArray(bridge_cell.cell_index(), trans))

            trans = pya.DCplxTrans.new(1, 90, False, x_prog, y_prog)
            self.top.insert(pya.DCellInstArray(straight_cell.cell_index(), trans))
            y_prog += straight_len

            trans = pya.DCplxTrans.new(1, 270, False, x_prog, y_prog+300)
            self.top.insert(pya.DCellInstArray(port_cell.cell_index(), trans))

            text = TextGen.write_text(self.lay, f"{amount} bridges, l={bridge_len}")
            TextGen.place_cell_center(self.lay, self.top, text, 0.5, x_prog, y_prog + 320)

            x_prog += 300

            # dummy without bridges

            y_prog = 0

            trans = pya.DCplxTrans.new(1, 90, False, x_prog, 0)
            self.top.insert(pya.DCellInstArray(port_cell.cell_index(), trans))

            y_prog += 300

            amount, bridge_len = values[x]

            total_len = amount*(bridge_len+straight_len) + straight_len

            long_straight = straight
            long_straight.length = total_len
            long_straight = self.lay.create_cell(long_straight.cell_name(), lib_name, long_straight.as_list())
            trans = pya.DCplxTrans.new(1, 90, False, x_prog, y_prog)
            self.top.insert(pya.DCellInstArray(long_straight.cell_index(), trans))
            y_prog += total_len

            trans = pya.DCplxTrans.new(1, 270, False, x_prog, y_prog+300)
            self.top.insert(pya.DCellInstArray(port_cell.cell_index(), trans))

            text = TextGen.write_text(self.lay, f"comparison structure")
            TextGen.place_cell_center(self.lay, self.top, text, 0.5, x_prog, y_prog + 320)

            x_prog += 300

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
        self.lay.read("../../templates/logo_mcqst.gds")
        self.lay.read("../../templates/logo_wmi.gds")

        cell_mcqst = self.lay.cell_by_name("MCQST")
        trans = pya.DCplxTrans.new(size_multiplier, 0, False, self.chip_width / 2 - logo_spacing - 550,
                                   self.chip_height / 2 - logo_spacing - 325)
        self.top.insert(pya.DCellInstArray(cell_mcqst, trans))

        cell_wmi = self.lay.cell_by_name("WMI")
        trans = pya.DCplxTrans.new(size_multiplier, 0, False, -(self.chip_width / 2 - logo_spacing - 550),
                                   self.chip_height / 2 - logo_spacing - 325)
        self.top.insert(pya.DCellInstArray(cell_wmi, trans))


    def _place_marker(self, x, y):
        """
        Subroutine for writing nanobeam markers on the chip
        """
        print("Writing markers...")

        self.lay.read(f"../../templates/marker_AB_manual.gds")
        cell = self.lay.top_cells()[1].cell_index()

        # index = self.lay.layer(pya.LayerInfo(layer, 0))  # create new layer
        # self.lay.top_cells()[1].swap(0, index)

        trans = pya.DCplxTrans.new(1, 0, False, x, y)
        self.top.insert(pya.DCellInstArray(cell, trans))
        self.top.flatten(1)

    def _write_text(self, text):
        """
        Subroutine for writing text on the chip.
        :@param text: Text that will be printed on the chip.
        """
        print("Writing text...")

        lines = text.splitlines()

        y_shift = (-self.chip_height/2) / self.dbu

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
        # l15 = self.lay.layer(pya.LayerInfo(15, 0))  # first step for airbridges
        # l16 = self.lay.layer(pya.LayerInfo(16, 0))  # second step for airbridges (with negative resist)

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
        # target_layer.insert(self.top.shapes(l15))

        # remove auxiliary layers
        self.lay.clear_layer(l10)
        self.lay.clear_layer(l11)
        self.lay.clear_layer(l14)
        self.lay.clear_layer(l2)

        self.lay.clear_layer(l0)
        self.lay.clear_layer(l12)
        self.lay.clear_layer(l13)
        # self.lay.clear_layer(l15)

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
        self.lay.write("../../chips/" + file_out + ".gds")


ab = AirbridgeBuilder()
ab.create_chip("airbridge_array_30to70")