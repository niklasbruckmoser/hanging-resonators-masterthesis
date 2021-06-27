from __future__ import annotations

from pathlib import Path

import numpy as np

import src.library.KLayout.HangingResonator as HangingResonator
import src.library.KLayout.Main
import src.library.TextGen as TextGen
from src.library.KLayout.CellParams import *
import src.library.ResonatorUtil as Util


"""
Class for creating resonator chips. All length units are assumed to be in µm, frequencies in GHz
"""


class ChipBuilder():

    def __init__(self, template=None):
        """
        Initialize the chip builder with an optional template
        @param template: if not None, this will initialize the chip builder with a given template. For templates, see
                         templates/ChipTemplates.py
        """
        # parameter declaration
        self.chip_size = (10000, 6000)
        self.width = 10
        self.gap = 6
        self.ground = 10
        self.hole = 40
        self.eps_eff = 6.45
        self.port_params = PortParams(160, 200, 300, 100, self.width, self.gap, self.ground, self.hole)
        self.hole_mask = "hole_mask_small"
        self.resonator_list = []
        self.logo_list = {}
        self.marker_list = {}
        self.text = "´f0´ (GHz): $FREQUENCIES$"
        self.global_rotation = 0

        self.airbridge_params = None
        self.default_resonator_params = HangingResonatorParams(950, 5000, 950, 300, 5e5, 20, 100, 1, 10, 6, 10, 6, 10,
                                                               40)

        # init from template
        if template is not None:
            import templates.ChipTemplates as CT
            getattr(CT, f"{template}")(self)


        self.lay = None
        self.top = None
        self.dbu = None

    def set_airbridge_parameters(self, pad_width=40, pad_height=30, gap=35, bridge_pad_width=30, bridge_pad_height=20,
                                 bridge_width=15, spacing=500) -> ChipBuilder:
        """
        Set the parameters for the air bridges
        @param pad_width: width of the reflow pad
        @param pad_height: height of the reflow pad
        @param gap: airbridge gap
        @param bridge_pad_width: width of the contact pad
        @param bridge_pad_height: height of the contact pad
        @param bridge_width: width of the air bridge
        @param spacing: spacing between individual air bridges at a resonator
        @return: ChipBuilder object for chaining
        """
        self.airbridge_params = AirbridgeParams(pad_width, pad_height, gap, bridge_pad_width, bridge_pad_height,
                                                bridge_width, spacing)
        return self

    def set_airbridges(self, boolean: bool) -> ChipBuilder:
        """
        Enable or disable air bridges
        @param boolean: True for enabling airbridges
        @return: ChipBuilder object for chaining
        """
        if boolean is False:
            self.airbridge_params = None
        else:
            if self.airbridge_params is None:
                self.set_airbridge_parameters()
        return self

    def set_port_parameters(self, width_port=160, length_taper=200, length_port=300, spacing=100) -> ChipBuilder:
        """
        Set the parameters for the transmission line ports
        @param width_port: width of the port
        @param length_taper: length of the narrowing cpw
        @param length_port: length of the port (with the full width)
        @param spacing: spacing to the borders (without ground and holes)
        @return: ChipBuilder object for chaining
        """
        self.port_params = PortParams(width_port, length_taper, length_port, spacing, self.width, self.gap,
                                      self.ground, self.hole)
        return self

    def _re_init_port_parameters(self):
        """
        Reinitialize the port parameters after changing width, gap, ground or hole
        """
        width_port = self.port_params.width_port
        length_taper = self.port_params.length_taper
        length_port = self.port_params.length_port
        spacing = self.port_params.spacing
        self.set_port_parameters(width_port, length_taper, length_port, spacing)

    def set_TL_width(self, width: float) -> ChipBuilder:
        """
        Set the width of the transmission line
        @param width: transmission line width
        @return: ChipBuilder object for chaining
        """
        self.width = width
        self._re_init_port_parameters()
        return self

    def set_TL_gap(self, gap: float) -> ChipBuilder:
        """
        Set the gap of the transmission line
        @param gap: transmission line gap to ground
        @return: ChipBuilder object for chaining
        """
        self.gap = gap
        self._re_init_port_parameters()
        return self

    def set_TL_ground(self, ground: float) -> ChipBuilder:
        """
        Set the ground of the transmission line, i.e. the width without flux trap holes
        @param ground: transmission line ground width
        @return: ChipBuilder object for chaining
        """
        self.ground = ground
        self._re_init_port_parameters()
        return self

    def set_TL_hole(self, hole: float) -> ChipBuilder:
        """
        Set the hole width of the transmission line, i.e. the width of high density holes
        @param hole: width of high density flux trap holes
        @return: ChipBuilder object for chaining
        """
        self.hole = hole
        self._re_init_port_parameters()
        return self

    def set_chip_size(self, width: float, height: float) -> ChipBuilder:
        """
        Define the size of the chip
        @param width: chip width
        @param height: chip height
        @return: ChipBuilder object for chaining
        """
        self.chip_size = (width, height)
        return self

    def set_hole_mask(self, mask: str) -> ChipBuilder:
        """
        Set the hole mask template
        @param mask: file name (without .gdx suffix) of the mask, see folder "templates"
        @return: ChipBuilder object for chaining
        """
        self.hole_mask = mask
        return self

    def remove_hole_mask(self) -> ChipBuilder:
        """
        Remove the hole mask, i.e. don't write any flux trap holes
        @return: ChipBuilder object for chaining
        """
        self.hole_mask = None
        return self

    def set_eps_eff(self, eps_eff: float) -> ChipBuilder:
        """
        Set the effective dielectric constant for the chip
        @param eps_eff: effective dielectric constant
        @return: ChipBuilder object for chaining
        """
        self.eps_eff = eps_eff
        return self

    def set_global_rotation(self, rotation: float) -> ChipBuilder:
        """
        Set the global rotation of the chip
        @param rotation: rotation in degrees. -90 for Laserwriter chips
        @return: ChipBuilder object for chaining
        """
        self.global_rotation = rotation
        return self

    def set_logo(self, position: str, name: str, size: float, spacing: float) -> ChipBuilder:
        """
        Set a logo at a given position
        @param position: position of the logo on the chip - either 'ul', 'ur', 'll' or 'lr'
        @param name: file name (without .gds suffix) of the logo, see folder "templates"
        @param size: size multiplier for the logo
        @param spacing: spacing to the closest chip borders
        @return: ChipBuilder object for chaining
        """
        if position not in ['ul', 'ur', 'll', 'lr']:
            raise ValueError(f"Logo position '{position}' not valid! Use 'ul', 'ur', 'll' or 'lr'.")
        self.logo_list[position] = (name, size, spacing)
        return self

    def remove_logos(self) -> ChipBuilder:
        """
        Remove all logos from the chip
        @return: ChipBuilder object for chaining
        """
        return self.remove_logo('all')

    def remove_logo(self, position) -> ChipBuilder:
        """
        Remove a logo at a given position
        @param position: either one of the four corners or 'all' for all positions
        @return: ChipBuilder object for chaining
        """
        if position not in ['ul', 'ur', 'll', 'lr', 'all']:
            raise ValueError(f"Logo position '{position}' not valid! Use 'ul', 'ur', 'll', 'lr' or 'all'.")
        if position != 'all':
            self.logo_list.pop(position, None)
        else:
            self.logo_list.pop('ul', None)
            self.logo_list.pop('ur', None)
            self.logo_list.pop('ll', None)
            self.logo_list.pop('lr', None)
        return self

    def set_marker(self, position: str, name: str, spacing: float, layers=[1], rotation=None) -> ChipBuilder:
        """
        Set an alignment marker at a given position
        @param position: position of the marker on the chip - either 'ul', 'ur', 'll', 'lr' or 'all'
        @param name: file name (without .gds suffix) of the marker, see folder "templates"
        @param spacing: spacing from the middle of the marker to the closest chip borders
        @param layers: list of layers for the marker. By default [1] (main layer)
        @param rotation: marker rotation (relevant for single chips, as they are typically being rotated by 90 degrees).
                         A rotation of "None" (default) rotates the markers accordingly to the global rotation
        @return: ChipBuilder object for chaining
        """
        if position not in ['ul', 'ur', 'll', 'lr', 'all']:
            raise ValueError(f"Marker position '{position}' not valid! Use 'ul', 'ur', 'll', 'lr' or 'all'.")
        if position != 'all':
            self.marker_list[position] = (name, spacing, layers, rotation)
        else:
            self.marker_list['ul'] = (name, spacing, layers, rotation)
            self.marker_list['ur'] = (name, spacing, layers, rotation)
            self.marker_list['ll'] = (name, spacing, layers, rotation)
            self.marker_list['lr'] = (name, spacing, layers, rotation)
        return self

    def remove_markers(self) -> ChipBuilder:
        """
        Remove all markers of the chip
        @return: ChipBuilder object for chaining
        """
        return self.remove_marker('all')

    def remove_marker(self, position) -> ChipBuilder:
        """
        Remove an alignment marker at a given position
        @param position: position of the marker on the chip - either 'ul', 'ur', 'll', 'lr' or 'all'
        @return: ChipBuilder object for chaining
        """
        if position not in ['ul', 'ur', 'll', 'lr', 'all']:
            raise ValueError(f"Marker position '{position}' not valid! Use 'ul', 'ur', 'll', 'lr' or 'all'.")
        if position != 'all':
            self.marker_list.pop(position, None)
        else:
            self.marker_list.pop('ul', None)
            self.marker_list.pop('ur', None)
            self.marker_list.pop('ll', None)
            self.marker_list.pop('lr', None)
        return self

    def set_text(self, text: str, write_frequencies: bool) -> ChipBuilder:
        """
        Set a text that will be displayed at the bottom of the chip
        @param text: String containing the text, multiple lines are supported (\n)
        @param write_frequencies: if True, the text will contain the frequencies on a separate line
        @return: ChipBuilder object for chaining
        """
        if write_frequencies:
            self.text = f"{text}\n´f0´ (GHz): $FREQUENCIES$"
        else:
            self.text = text
        return self

    def set_default_resonator_parameters(self, segment_length=950, y_offset=300, q_ext=4e5, coupling_ground=20,
                                         radius=100, shorted=1, width=10, gap=6, ground=10, hole=40) -> ChipBuilder:
        """
        Set default fallback resonator parameters
        @param segment_length: length of the x straight
        @param y_offset: length of the y offset
        @param q_ext: external coupling to the resonator
        @param coupling_ground: ground distance between the resonator and the transmission line
        @param radius: meander radius
        @param shorted: if 1, the end will be shorted (lambda/4 resonator)
        @param width: width of the resonator cpw
        @param gap: gap of the resonator cpw
        @param ground: ground width of the resonator cpw
        @param hole: high density hole width of the resonator cpw
        @return: ChipBuilder object for chaining
        """
        # save q_ext in coupling length - dirty, but more compact than saving a new variable
        self.default_resonator_params = HangingResonatorParams(segment_length, 5000, segment_length, y_offset, q_ext,
                                                                 coupling_ground, radius, shorted, self.width, self.gap,
                                                                 width, gap, ground, hole)
        return self

    def add_resonator(self, res_params: HangingResonatorParams) -> ChipBuilder:
        """
        Add a resonator to the chip
        @param res_params: a ResonatorParams object containing all the parameters
        @return: ChipBuilder object for chaining
        """
        self.resonator_list.append(res_params)
        return self

    def set_resonator_list(self, res_param_list: [HangingResonatorParams]) -> ChipBuilder:
        """
        Set the whole list of resonators for the chip
        @param res_param_list: a list containing all ResonatorParams objects
        @return: ChipBuilder object for chaining
        """
        self.resonator_list = res_param_list
        return self

    def get_resonator(self, f0: float, segment_length=None, y_offset=None, q_ext=None, coupling_ground=None,
                      radius=None, shorted=None, width=None, gap=None, ground=None,
                      hole=None) -> HangingResonatorParams:
        """
        Create a ResonatorParams object
        @param f0: the resonance frequency (assuming lambda/4 resonator) TODO change in the future? prob. not necessary
        @param segment_length: length of the x straight
        @param y_offset: length of the y offset
        @param q_ext: external coupling to the resonator
        @param coupling_ground: ground distance between the resonator and the transmission line
        @param radius: meander radius
        @param shorted: if 1, the end will be shorted (lambda/4 resonator)
        @param width: width of the resonator cpw
        @param gap: gap of the resonator cpw
        @param ground: ground width of the resonator cpw
        @param hole: high density hole width of the resonator cpw
        @return: a ResonatorParams object
        """
        # initialize values from default resonator params
        segment_length = segment_length or self.default_resonator_params.segment_length
        y_offset = y_offset or self.default_resonator_params.y_offset
        q_ext = q_ext or self.default_resonator_params.coupling_length  # q_ext is being saved in coupling length
        coupling_ground = coupling_ground or self.default_resonator_params.coupling_ground
        radius = radius or self.default_resonator_params.radius
        shorted = shorted or self.default_resonator_params.shorted
        width = width or self.default_resonator_params.width
        gap = gap or self.default_resonator_params.gap
        ground = ground or self.default_resonator_params.ground
        hole = hole or self.default_resonator_params.hole

        length = Util.calc_length(f0, self.eps_eff) / 1000
        coupling_length = Util.calc_coupling_length(self.width, self.gap, width, gap, coupling_ground, length, q_ext,
                                                    self.eps_eff)

        return HangingResonatorParams(segment_length, length, segment_length, y_offset, coupling_length,
                                        coupling_ground, radius, shorted, self.width, self.gap, width, gap, ground,
                                        hole)

    def get_resonator_list(self, f0_start: float, f0_end: float, amount_resonators: int, segment_length=None,
                           y_offset=None, q_ext=None, coupling_ground=None, radius=None, shorted=None, width=None,
                           gap=None, ground=None, hole=None) -> [HangingResonatorParams]:
        """
        Get a list of resonator params
        @param f0_start: the start resonance frequency (assuming lambda/4)
        @param f0_end: the end resonance frequency (assuming lambda/4)
        @param amount_resonators: amount of resonators
        @param segment_length: length of the x straight
        @param y_offset: length of the y offset
        @param q_ext: external coupling to the resonator
        @param coupling_ground: ground distance between the resonator and the transmission line
        @param radius: meander radius
        @param shorted: if 1, the end will be shorted (lambda/4 resonator)
        @param width: width of the resonator cpw
        @param gap: gap of the resonator cpw
        @param ground: ground width of the resonator cpw
        @param hole: high density hole width of the resonator cpw
        @return:
        """
        param_list = []
        interval = (f0_end - f0_start) / (amount_resonators - 1)
        for i in range(amount_resonators):
            f0 = f0_start + i*interval
            param_list.append(self.get_resonator(f0, segment_length, y_offset, q_ext, coupling_ground, radius,
                                                 shorted, width, gap, ground, hole))

        return param_list

    #####################
    ###               ###
    ### Template list ###
    ###               ###
    #####################

    # shifted to ChipTemplates

    #######################
    ###                 ###
    ### Generation part ###
    ###                 ###
    #######################

    def build_chip(self, save_name: str, file_format='gds'):
        """
        Build a chip from all the parameters previously set
        @param save_name: name that will be used for the file
        @param file_format: format of the file, by default 'gds'
        """
        print(f"Creating chip {save_name}.{file_format}...")

        self.lay = pya.Layout()
        self.top = self.lay.create_cell("TOP")
        self.dbu = self.lay.dbu

        self._write_structures()
        self._write_markers()
        self._write_logos()
        self._write_text()
        self._perform_boolean_operations()
        self._rotate_design()
        self._save_chip(save_name, file_format)

    ########################
    ###                  ###
    ### Internal methods ###
    ###                  ###
    ########################

    def _write_structures(self):
        """
        Write the transmission line, resonators and airbridges
        """
        if self.hole_mask is not None:
            self._write_holes()

        print("Writing structures...")

        ### TL

        x_prog = -self.chip_size[0]/2
        port = self.lay.create_cell("Port", "QC", self.port_params.as_list())
        trans = pya.DCplxTrans.new(1, 0, False, x_prog, 0)
        self.top.insert(pya.DCellInstArray(port.cell_index(), trans))

        port_len = self.port_params.end_point().x
        x_prog += port_len

        tl_len = self.chip_size[0] - 2*port_len

        straight_params = StraightParams(tl_len, self.width, self.gap, self.ground, self.hole)
        straight = self.lay.create_cell("Straight", "QC", straight_params.as_list())
        trans = pya.DCplxTrans.new(1, 0, False, x_prog, 0)
        self.top.insert(pya.DCellInstArray(straight.cell_index(), trans))
        x_prog += straight_params.end_point().x

        port = self.lay.create_cell("Port", "QC", self.port_params.as_list())
        trans = pya.DCplxTrans.new(1, 180, False, x_prog+port_len, 0)
        self.top.insert(pya.DCellInstArray(port.cell_index(), trans))

        ### Resonators

        safe_zone = 0
        for res in self.resonator_list:
            new_sz = res.segment_length + 2*(res.radius + res.ground + res.hole + res.gap + res.width/2)
            safe_zone = new_sz if new_sz > safe_zone else safe_zone

        residual = tl_len - safe_zone*(len(self.resonator_list)/2+0.5)

        safe_zone += residual / (len(self.resonator_list)/2+0.5)

        up = True

        x_prog = -tl_len/2

        for res in self.resonator_list:

            x_prog += safe_zone/2
            if type(res) == HangingResonatorParams:
                res_cell = self.lay.create_cell("HangingResonator", "QC", res.as_list())
            elif type(res) == HangingResonatorFingersParams:
                res_cell = self.lay.create_cell("HangingResonatorFingers", "QC", res.as_list())
            elif type(res) == HangingResonatorOldParams:
                res_cell = self.lay.create_cell("HangingResonatorOld", "QC", res.as_list())
            else:
                raise ValueError(f"Unknown type {type(res)} as resonator parameters")
            trans = pya.DCplxTrans.new(1, 0, not up, x_prog, 0)
            self.top.insert(pya.DCellInstArray(res_cell.cell_index(), trans))

            # air bridges

            if self.airbridge_params is not None:

                # TL airbridges
                ab_pos = x_prog + res.radius + res.segment_length/2 + 100
                ab_cell = self.lay.create_cell("Airbridge", "QC", self.airbridge_params.as_list())
                trans = pya.DCplxTrans.new(1, 0, False, ab_pos, 0)
                self.top.insert(pya.DCellInstArray(ab_cell.cell_index(), trans))

                # resonator airbridges
                len_start = res.coupling_length + np.pi*res.radius/2 + res.y_offset/2
                amount_bridges = int(np.floor((res.length-len_start)/self.airbridge_params.spacing))

                for z in np.linspace(len_start/res.length,
                                     (len_start+self.airbridge_params.spacing*amount_bridges)/res.length,
                                     amount_bridges):

                    if res.length*(1-z) < 200:  # too close to end of resonator
                        continue

                    x, y, rot = HangingResonator.get_coord(z, pya.DPoint(0, 0), 0, res)
                    trans = pya.DCplxTrans.new(1, 0, not up, 0, 0)*pya.DCplxTrans.new(1, rot, 0, x+x_prog, y)
                    self.top.insert(pya.DCellInstArray(ab_cell.cell_index(), trans))

            up = not up

    def _write_holes(self):
        """
        Write the hole mask for both the periodic and the high density holes
        """
        print("Writing holes...")

        self.lay.read(f"../../templates/{self.hole_mask}.gds")

        cell = self.lay.top_cells()[1].cell_index()
        trans = pya.DCplxTrans.new(1, 0, False, 0, 0)
        self.top.insert(pya.DCellInstArray(cell, trans))
        self.top.flatten(1)

    def _write_markers(self):
        """
        Write the alignment markers
        """
        print("Writing markers...")

        x_sign = -1
        y_sign = 1

        for position, data in self.marker_list.items():
            if position == 'ul':
                x_sign = -1
                y_sign = 1
            elif position == 'ur':
                x_sign = 1
                y_sign = 1
            elif position == 'll':
                x_sign = -1
                y_sign = -1
            elif position == 'lr':
                x_sign = 1
                y_sign = -1

            marker_name = data[0]
            marker_spacing = data[1]
            layers = data[2]
            marker_rotation = data[3]

            if marker_rotation is None:
                marker_rotation = -self.global_rotation

            for layer in layers:

                self.lay.read(f"../../templates/{marker_name}.gds")
                cell = self.lay.top_cells()[1].cell_index()

                index = self.lay.layer(pya.LayerInfo(layer, 0))  # create or find new layer
                self.lay.top_cells()[1].swap(0, index)

                trans = pya.DCplxTrans.new(1, marker_rotation, False, x_sign*(self.chip_size[0]/2 - marker_spacing),
                                           y_sign*(self.chip_size[1]/2 - marker_spacing))
                self.top.insert(pya.DCellInstArray(cell, trans))
                self.top.flatten(1)

    def _write_logos(self):
        """
        Write the logos
        """
        print("Writing logos...")

        x_sign = -1
        y_sign = 1

        for position, data in self.logo_list.items():
            if position == 'ul':
                x_sign = -1
                y_sign = 1
            elif position == 'ur':
                x_sign = 1
                y_sign = 1
            elif position == 'll':
                x_sign = -1
                y_sign = -1
            elif position == 'lr':
                x_sign = 1
                y_sign = -1

            logo_name = data[0]
            size_multiplier = data[1]
            logo_spacing = data[2]

            self.lay.read(f"../../templates/{logo_name}.gds")
            cell = self.lay.top_cells()[1]
            bbox = cell.bbox()
            trans = pya.DCplxTrans.new(size_multiplier, 0, False,
                                       x_sign*(self.chip_size[0]/2 - logo_spacing - size_multiplier*bbox.width()/2000),
                                       y_sign*(self.chip_size[1]/2 - logo_spacing - size_multiplier*bbox.height()/2000))
            self.top.insert(pya.DCellInstArray(cell.cell_index(), trans))

            self.top.flatten(1)

    def _write_text(self):
        """
        Write the text at the bottom of the chip
        """
        print("Writing text...")

        frequencies = []
        for res in self.resonator_list:
            frequencies.append(Util.calc_f0(res.length*1000, self.eps_eff))

        f_text = ""

        for i in range(len(frequencies)):
            if len(frequencies) > 16 and i == np.floor(len(frequencies) / 2):
                f_text += "\n"
            f_text += "{:.2f}".format(frequencies[i])
            if i < len(frequencies) - 1:
                f_text += ", "

        self.text = self.text.replace("$FREQUENCIES$", f_text)

        lines = self.text.splitlines()

        y_shift = (-self.chip_size[1]/2 + len(lines)*150.) / self.dbu

        for line in lines:
            text = TextGen.write_text(self.lay, line)
            TextGen.place_cell_center(self.lay, self.top, text, 3, 0, y_shift*self.dbu)
            y_shift -= 150 / self.dbu

    def _perform_boolean_operations(self):
        """
        Subroutine for performing the boolean layer operations. This has to be done after adding all of the cells
        """

        print("performing boolean operations...")

        # define layers for convenience
        l0 = self.lay.layer(pya.LayerInfo(0, 0))  # logos and text
        l1 = self.lay.layer(pya.LayerInfo(1, 0))  # main structure
        l2 = self.lay.layer(pya.LayerInfo(2, 0))  # text mask
        l3 = self.lay.layer(pya.LayerInfo(3, 0))  # chip border for holes
        l10 = self.lay.layer(pya.LayerInfo(10, 0))  # spacing
        l11 = self.lay.layer(pya.LayerInfo(11, 0))  # high density hole mask
        l12 = self.lay.layer(pya.LayerInfo(12, 0))  # periodic holes
        l13 = self.lay.layer(pya.LayerInfo(13, 0))  # high density holes
        l14 = self.lay.layer(pya.LayerInfo(14, 0))  # logo background for removing periodic holes
        l15 = self.lay.layer(pya.LayerInfo(15, 0))  # airbridge contact pads
        l16 = self.lay.layer(pya.LayerInfo(16, 0))  # airbridge bridges (negative resist)

        # flatten, otherwise boolean operations won't work
        self.top.flatten(1)

        # prepare a shape processor
        processor = pya.ShapeProcessor()

        # make sure ground is also at high density holes
        processor.boolean(self.lay, self.top, l11, self.lay, self.top, l10, self.top.shapes(l11),
                          pya.EdgeProcessor.ModeANotB, True, True, True)

        # layer for chip boundaries
        self.top.shapes(l3).insert(pya.Box(-self.chip_size[0]/2/self.dbu, -self.chip_size[1]/2/self.dbu,
                                           self.chip_size[0]/2/self.dbu, self.chip_size[1]/2/self.dbu))

        # periodic holes in chip boundaries
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l3, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeAnd, True, True, True)


        # remove periodic holes from hd hole mask
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l11, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        # remove periodic holes from ground
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l10, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        # remove periodic holes from logo background
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l14, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        # remove periodic holes from text
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l2, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        # remove periodic holes from airbridge pads
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l15, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        processor.boolean(self.lay, self.top, l11, self.lay, self.top, l15, self.top.shapes(l11),
                          pya.EdgeProcessor.ModeANotB, True, True, True)

        # hd hole mask in chip boundaries
        processor.boolean(self.lay, self.top, l13, self.lay, self.top, l11, self.top.shapes(l13),
                          pya.EdgeProcessor.ModeAnd, True, True, True)

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


    def _rotate_design(self):
        """
        Rotate the whole design by the global rotation
        """
        if self.global_rotation != 0:
            print("Rotating design...")
            self.lay.transform(pya.DCplxTrans.new(1, self.global_rotation, False, 0, 0))

    def _save_chip(self, save_name: str, file_format: str):
        """
        Save the created chip design as a file
        @param save_name: name of the file
        @param file_format: file format, currently 'gds' and 'dxf' are supported
        """
        print("Saving file...")

        Path("../../chips/").mkdir(parents=True, exist_ok=True)

        if file_format.lower() == 'gds':
            self.lay.write("../../chips/" + save_name + ".gds")
        elif file_format.lower() == 'dxf':
            options = pya.SaveLayoutOptions()
            options.dxf_polygon_mode = 1
            options.dbu = 0.001
            options.scale_factor = 1
            options.format="DXF"
            self.lay.write("../../chips/" + save_name + ".dxf", options)
        else:
            raise ValueError(f"File format '{file_format}' is currently unsupported.")