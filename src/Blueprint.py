import pickle
import os
from pathlib import Path

import numpy as np
import src.coplanar_coupler
import src.library.CPW_pieces
from src.Params import *


class Blueprint:

    def __init__(self, gap=6, width=10, ground=50, hd_holes=40, chip_w=10000, chip_h=6000, silver_glue_port=True,
                 port_spacing=0, p_hole_dist=50, p_hole_sigma=5, p_hole_size=5, hd_hole_dist=10, hd_hole_sigma=2.5,
                 hd_hole_size=5, res_segment_w=800, res_coupling_ground=5, res_length=8000, res_lambda_4=1,
                 res_mirror=0, res_shift_y=300, res_fingers=0, res_finger_length=26, res_finger_endgap=8,
                 res_hook_width=5, res_hook_length=3, res_hook_unit=1, res_hole_length=1):
        """
        Creates a blueprint with the given parameters. Can be used for generating .gds chips.
        :@param gap: Size of the CPW gap to ground
        :@param width: Size of the CPW width
        :@param ground: Extra spacing without holes (flux traps)
        :@param hd_holes: High density hole width
        :@param chip_w: Width of the chip
        :@param chip_h: Height of the chip
        :@param silver_glue_port: True, if the ports are being used for silver gluing
        :@param p_hole_dist: Distance between two periodic holes
        :@param p_hole_sigma: Random position offset of periodic holes
        :@param p_hole_size: Size of periodic holes
        :@param hd_hole_dist: Distance between two high density holes
        :@param hd_hole_sigma: Random position offset of high density holes
        :@param hd_hole_size: Size of high density holes
        :@param res_segment_w: Segment width of the resonator (i.e. the length it uses in the TL)
        :@param res_length: Length of the meandering resonator, determines f0
        :@param res_lambda_4: True, if using lambda/4 resonator design
        :@param res_mirror: True, if the design should be mirrored
        :@param res_shift_y: Y-shift of the resonator away from the TL
        :@param res_fingers: Amount of fingers in the resonator y shift
        :@param res_finger_length: Length of each finger
        :@param res_finger_endgap: @Leo?
        :@param res_hook_width: @Leo?
        :@param res_hook_length: @Leo?
        :@param res_hook_unit: @Leo?
        :@param res_hole_length: @Leo?
        """

        self.chip_params = ChipParams(chip_w, chip_h, gap, width, ground, hd_holes)
        self.port_params = PortParams(self.chip_params, silver_glue_port, port_spacing)
        self.straight_params = StraightParams(self.chip_params)
        self.p_hole_params = HoleParams(self.chip_params, p_hole_dist, p_hole_sigma, p_hole_size, False)
        self.hd_hole_params = HoleParams(self.chip_params, hd_hole_dist, hd_hole_sigma, hd_hole_size, True)
        self.res_params = ResonatorParams(self.chip_params, res_segment_w, res_coupling_ground, res_length, res_mirror,
                                          res_lambda_4, res_shift_y, res_fingers, res_finger_length, res_finger_endgap,
                                          res_hook_width, res_hook_length, res_hook_unit, res_hole_length)

        # self.port_x = self.port_params.port_x()

        self.frequencies = []

        # calculating kappa takes some time. Better search for an existing value of kappa instead of recalculating
        key = (self.chip_params.width, self.chip_params.gap, self.chip_params.width, self.chip_params.gap,
               self.res_params.coupling_ground, 6.45)

        kappa_dict = _load_kappa_dict()

        if key in kappa_dict:
            self.kappa = kappa_dict[key]
        else:
            print("No value for kappa detected. Calculating new value for determining Q_ext...")
            cpw_c = src.coplanar_coupler.coplanar_coupler()
            cpw_c.w1 = self.chip_params.width
            cpw_c.s1 = self.chip_params.gap
            cpw_c.w2 = self.chip_params.width
            cpw_c.s2 = self.chip_params.gap
            cpw_c.w3 = self.res_params.coupling_ground
            cpw_c.epsilon_eff = 6.45
            Cl, Ll, Zl = cpw_c.coupling_matrices(mode='notch')
            self.kappa = Zl[0, 1] / (np.sqrt(Zl[0, 0] * Zl[1, 1]))

            kappa_dict[key] = self.kappa
            _save_kappa_dict(kappa_dict)

        self.lay = None
        self.top = None
        self.dbu = None

    def create_chip(self, file_out, f_start, f_end, amount_resonators=0, printed_text=None, print_frequencies=True,
                    markers=False):
        """
        Creates a chip from the blueprint in the given frequency range and saves it automatically as a .gds file.
        :@param file_out: Name of the gds file
        :@param f_start: Start frequency
        :@param f_end: End frequency
        :@param amount_resonators: Amount of resonators on the chip. Set to 0 for a dense filling
        :@param printed_text: Can be used for displaying custom text on the chip
        :@param print_frequencies: In addition to the text, print the frequencies of the resonators
        :@param markers: Add nb5 markers (6x10) to the chip layout
        """

        self.lay = pya.Layout()
        self.top = self.lay.create_cell("TOP")
        self.dbu = self.lay.dbu

        self._write_structures(f_start, f_end, amount_resonators)
        self._write_logos()
        if markers:
            self._write_markers()
        self._write_text(printed_text, print_frequencies)
        self._perform_boolean_operations()
        self._write_file(file_out)

        self.frequencies = []

    def _write_structures(self, f_start, f_end, amount_resonators=0):
        """
        Subroutine for writing the main structures.
        :@param f_start: Start frequency
        :@param f_end: End frequency
        :@param amount_resonators: Amount of resonators on the chip. Set to 0 for a dense filling
        """

        print("Writing structures...")

        # dummy coordinate for writing progress
        progress_x = -self.port_params.port_x()

        # add hole patterns

        # periodic holes
        p_holes = self.lay.create_cell("Hole_Pattern", "cQED", self.p_hole_params.list())
        trans = pya.DCplxTrans.new(1, 0, False, -self.chip_params.w / 2 + self.p_hole_params.dist / 2,
                                   -self.chip_params.h / 2 + self.p_hole_params.dist / 2)
        self.top.insert(pya.DCellInstArray(p_holes.cell_index(), trans))

        # high density holes
        hd_holes = self.lay.create_cell("Hole_Pattern", "cQED", self.hd_hole_params.list())
        trans = pya.DCplxTrans.new(1, 0, False, -self.chip_params.w / 2, -self.chip_params.h / 2)
        self.top.insert(pya.DCellInstArray(hd_holes.cell_index(), trans))

        # add ports to layout
        port = self.lay.create_cell("CPW_Port", "cQED", self.port_params.list())
        trans = pya.DCplxTrans.new(1, 0, False, -self.port_params.port_x(), 0)
        self.top.insert(pya.DCellInstArray(port.cell_index(), trans))
        trans = pya.DCplxTrans.new(1, 180, False, self.port_params.port_x(), 0)
        self.top.insert(pya.DCellInstArray(port.cell_index(), trans))

        padding = 0
        if self.res_params.shift_x > 800:  # or even smaller?
            padding = self.res_params.shift_x - 800

        # see how many resonators fit inside
        possible_amount = int(np.floor(2 * (self.port_params.port_x() - padding) / self.res_params.segment_w))
        if amount_resonators == 0 or possible_amount < amount_resonators:
            amount_resonators = possible_amount

        residual = 2 * (self.port_params.port_x() - padding) - amount_resonators * self.res_params.segment_w

        self.straight_params.length = int(residual / 2)
        tl = self.lay.create_cell("CPW_Straight", "cQED", self.straight_params.list())
        trans = pya.DCplxTrans.new(1, 0, False, progress_x, 0)
        self.top.insert(pya.DCellInstArray(tl.cell_index(), trans))
        progress_x += self.straight_params.length

        # add resonators (main part)
        if self.calc_resonator_height(calc_length(f_start)) > self.chip_params.h / 2 - 700:
            print("WARNING: resonator height exceeds critical height of ~" + str(self.chip_params.h / 2 - 700) +
                  "µm! Increase coupling_w for broader resonators.")

        interval = (f_end - f_start) / (amount_resonators - 1)
        for i in range(amount_resonators):
            f = f_end - i * interval
            self.res_params.length = calc_length(f)
            self.res_params.coupling_w = self.calc_coupling_length(self.res_params.length, 1e5)

            # print("res " + str(i) + ": " + str(self.res_params.length) + ", " + str(self.res_params.coupling_w))
            # print("y height: " + str(_calc_res_y(res_params.length)))
            # print("expected: " + str(res_params.length) + ", actual: " + str(_calc_actual_length(res_params.length)))

            old_shift_y = self.res_params.shift_y

            if self.res_params.coupling_w + 0.25 * 2 * np.pi * 101 + self.res_params.shift_y < self.res_params.length <\
                    self.res_params.coupling_w + 2 * np.pi * 101 + self.res_params.shift_y:
                self.res_params.shift_y = 3000  # exact value doesn't matter, because we check the length

            self.frequencies.append(calc_f0(self.calc_actual_length(self.res_params.length)))

            self.res_params.mirror = (self.res_params.mirror + 1) % 2
            res = self.lay.create_cell("CPW_Res", "cQED", self.res_params.list())
            trans = pya.DCplxTrans.new(1, 0 if i % 2 == 0 else 180, False,
                                       progress_x if i % 2 == 0 else progress_x + self.res_params.segment_w, 0)
            self.top.insert(pya.DCellInstArray(res.cell_index(), trans))

            self.res_params.shift_y = old_shift_y

            progress_x += self.res_params.segment_w

        # add ending TL to connect to the port
        self.straight_params.length = self.port_params.port_x() - progress_x
        tl = self.lay.create_cell("CPW_Straight", "cQED", self.straight_params.list())
        trans = pya.DCplxTrans.new(1, 0, False, progress_x, 0)
        self.top.insert(pya.DCellInstArray(tl.cell_index(), trans))

    def _write_logos(self):
        """
        Subroutine for writing the logos on the chip.
        """

        print("Writing logos...")

        # spacing from edges
        logo_spacing = 150
        size_multiplier = 0.7

        # logo files
        self.lay.read("../templates/logo_mcqst.gds")
        self.lay.read("../templates/logo_wmi.gds")

        cell_mcqst = self.lay.cell_by_name("MCQST")
        trans = pya.DCplxTrans.new(size_multiplier, 0, False, self.chip_params.w / 2 - logo_spacing - 550,
                                   self.chip_params.h / 2 - logo_spacing - 325)
        self.top.insert(pya.DCellInstArray(cell_mcqst, trans))

        cell_wmi = self.lay.cell_by_name("WMI")
        trans = pya.DCplxTrans.new(size_multiplier, 0, False, -(self.chip_params.w / 2 - logo_spacing - 550),
                                   self.chip_params.h / 2 - logo_spacing - 325)
        self.top.insert(pya.DCellInstArray(cell_wmi, trans))

    def _write_markers(self):
        """
        Subroutine for writing nanobeam markers on the chip
        """
        print("Writing markers...")

        self.lay.read("../templates/nb5marker.gds")
        cell_marker = self.lay.cell_by_name("nb5marker")
        trans = pya.DCplxTrans.new(1, 0, False, 0, 0)
        self.top.insert(pya.DCellInstArray(cell_marker, trans))

    def _write_text(self, text=None, frequencies=True):
        """
        Subroutine for writing text on the chip.
        :@param text: Text that will be printed on the chip. Set to None for printing the resonance frequencies
        """
        print("Writing text...")

        # spacing for removing holes
        text_spacing = 40. / self.dbu

        if text is None:
            text = ""
        else:
            text += "\n"

        if frequencies is True:
            text += "f0 (GHz): "
            for i in range(len(self.frequencies)):
                if len(self.frequencies) > 12 and i == np.floor(len(self.frequencies) / 2):
                    text += "\n"
                text += "{:.2f}".format(self.frequencies[i])
                if i < len(self.frequencies) - 1:
                    text += ", "

        lines = text.splitlines()

        if len(lines) > 1:
            y_shift = (-(self.chip_params.h / 2 - 150) + (len(lines) - 1) * 150.) / self.dbu
        else:
            y_shift = -(self.chip_params.h / 2 - 150) / self.dbu

        for line in lines:
            region = pya.TextGenerator.default_generator().text(line, 0.001, 150)
            width = region.bbox().width()
            height = region.bbox().height()
            region.move(-width / 2, y_shift)
            region.insert_into(self.lay, self.top.cell_index(), self.lay.layer(pya.LayerInfo(0, 0)))

            self.top.shapes(self.lay.layer(pya.LayerInfo(14, 0))).insert(
                pya.Box(-width / 2 - text_spacing, y_shift - text_spacing, width / 2 + text_spacing,
                        y_shift + height + text_spacing))
            y_shift -= 150. / self.dbu

    def _perform_boolean_operations(self):
        """
        Subroutine for performing the boolean layer operations. This has to be the last step before saving the gds file.
        """

        print("performing boolean operations...")

        # define layers for convenience
        l0 = self.lay.layer(pya.LayerInfo(0, 0))  # logos and text
        l1 = self.lay.layer(pya.LayerInfo(1, 0))  # main structure
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

        # hole boolean operations
        processor.boolean(self.lay, self.top, l13, self.lay, self.top, l11, self.top.shapes(l13),
                          pya.EdgeProcessor.ModeAnd, True, True, True)
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l11, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l10, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        processor.boolean(self.lay, self.top, l12, self.lay, self.top, l14, self.top.shapes(l12),
                          pya.EdgeProcessor.ModeANotB, True, True, True)

        # imo, the mask is negative -> boolean operations to invert the structure
        processor.boolean(self.lay, self.top, l10, self.lay, self.top, l11, self.top.shapes(l10),
                          pya.EdgeProcessor.ModeANotB, True, True, True)
        processor.boolean(self.lay, self.top, l1, self.lay, self.top, l10, self.top.shapes(l1),
                          pya.EdgeProcessor.ModeXor, True, True, True)

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

        self.lay.clear_layer(l0)
        self.lay.clear_layer(l12)
        self.lay.clear_layer(l13)

    def _write_file(self, file_out):
        """
        Subroutine for saving the file.
        :@param file_out: Name of the .gds file
        """

        print("Saving file...")
        Path("../chips/").mkdir(parents=True, exist_ok=True)
        self.lay.write("../chips/" + file_out + ".gds")

    ##################################
    # HELPER METHODS
    ##################################

    def calc_resonator_height(self, length):
        """
        Calculates the height of a resonator, measured from the center (y=0) to the mid of the width of the resonator
        (excluding the gap + ground + hd_holes)
        :@param length: Length of the resonator
        :@return: Height of the resonator
        """

        y = self.chip_params.width / 2 + self.chip_params.gap + self.res_params.coupling_ground \
            + self.chip_params.gap + self.chip_params.width / 2

        if length < self.res_params.coupling_w + 0.25 * 2 * np.pi * 101 + self.res_params.shift_y:
            return y + 101 + length - (self.res_params.coupling_w + 0.25 * 2 * np.pi)

        remaining_length = length - self.res_params.coupling_w - 2 * np.pi * 101 \
                                  - self.res_params.shift_y - max(self.res_params.shift_x - 202, 0)
        y += self.res_params.shift_y + 4 * 101

        while remaining_length > 0:
            remaining_length -= self.res_params.w - 2 * (101 + self.chip_params.ground + self.chip_params.hd_holes
                                                         + self.chip_params.gap + self.chip_params.width / 2)
            if remaining_length < 101 + self.chip_params.ground:
                break  # if < 101+ground, the resonator will be finished with a straight
            # always running a full pi rotation (because IBM was lazy?)
            remaining_length -= 0.5 * 2 * np.pi * 101
            y += 202

        return y

    def calc_actual_length(self, length):
        """
        As the meandering structure will always be written with full half circles, the true length may actually vary.
        This method returns the true length, assuming shift_x > 0.
        :@param length: Theoretical length of the resonator
        :@return: The true length of the written resonator
        """

        if length < self.res_params.coupling_w + 0.25 * 2 * np.pi * 101 + self.res_params.shift_y:
            return length

        real = self.res_params.coupling_w + 2 * np.pi * 101 + self.res_params.shift_y + max(
            self.res_params.shift_x - 202, 0)
        remaining_length = length - real

        len_straight = self.res_params.w - 2 * (101 + self.chip_params.ground + self.chip_params.hd_holes
                                                + self.chip_params.gap + self.chip_params.width / 2)

        while remaining_length > 0:
            if remaining_length < len_straight:
                real += remaining_length
                break
            elif remaining_length < len_straight + 101 + self.chip_params.ground:
                real += remaining_length
                break
            remaining_length -= len_straight + 0.5 * 2 * np.pi * 101
            real += len_straight + 0.5 * 2 * np.pi * 101

        return real

    def calc_coupling_length(self, l_res, intended_q=1e5):
        """
        Calculates the needed coupling length for achieving a given Q factor. Assuming all units in microns
         and epsilon_eff = 6.45.
        For reference, see https://doi.org/10.1140/epjqt/s40507-018-0066-3
        :@param l_res: length of the resonator
        :@param intended_q: external Q one wishes to achieve
        :@return: The calculated coupling length
        """
        return int((_v_ph() / (2 * np.pi * calc_f0(l_res) * 1e9) * np.arcsin(
            np.sqrt(np.pi / (2 * self.kappa ** 2 * intended_q)))) * 1e6)


def calc_f0(length):
    """
    Calculate a rough estimate for f0. Assuming Si-Air boundary and a lambda/4 resonator.
    :@param length: The length of the resonator in microns
    :@return: The resonance frequency in GHz
    """

    return _v_ph() / (4 * length * 1e-6) * 1e-9


def calc_length(f0):
    """
    Calculate a rough estimate for the length. Assuming Si-Air boundary and a lambda/4 resonator.
    :@param f0: The resonance frequency in GHz
    :@return: The length of the resonator in microns
    """

    return _v_ph() / (4 * f0 * 1e9) * 1e6


def _v_ph():
    """
    Get the phase velocity for Si-Air
    @return: Approximate phase velocity of light
    """
    return 3e8 / np.sqrt(6.45)


def _load_kappa_dict():
    """
    Load the kappa dictionary for fast calculation of the Quality factor
    @return: Dictionary containing the parameters and associated kappa value
    """
    if not os.path.exists('../kappaValues.txt'):
        _save_kappa_dict({(10, 6, 10, 6, 3, 6.45): 0.11358238085799895})
    with open('../kappaValues.txt', 'rb') as handle:
        return pickle.loads(handle.read())


def _save_kappa_dict(kappa_dict):
    """
    Save the kappa dictionary into a binary (non-readable) file
    @param kappa_dict: Dictionary to save
    """
    with open('../kappaValues.txt', 'wb') as handle:
        pickle.dump(kappa_dict, handle)
