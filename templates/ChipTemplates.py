from src.ChipBuilder import ChipBuilder


"""
Chip templates for fast initialization.
Initialize the ChipBuilder object with the method name as a String argument.
"""


def template_test_template(obj: ChipBuilder):
    """
    Template for a 10x6 wmi chip. Initialize with "10x6_wmi"
    """
    obj.set_chip_size(14300, 14400).set_TL_width(10).set_TL_gap(6)
    obj.set_TL_ground(10).set_TL_hole(40).set_hole_mask("hole_mask_small")
    obj.set_port_parameters(160, 200, 300, 100)
    obj.set_default_resonator_parameters(950, 300, 4e5, 20, 100, 1, 10, 6, 10, 40)
    obj.set_logo('ur', "logo_mcqst", 0.4, 300).set_logo('ul', "logo_wmi", 0.5, 300)
    obj.set_eps_eff(6.45)
    obj.set_text("´f0´ (GHz): $FREQUENCIES$", False)

def template_10x6_wmi(obj: ChipBuilder):
    """
    Template for a 10x6 wmi chip. Initialize with "10x6_wmi"
    """
    obj.set_chip_size(10000, 6000).set_TL_width(10).set_TL_gap(6)
    obj.set_TL_ground(10).set_TL_hole(40).set_hole_mask("hole_mask_small")
    obj.set_port_parameters(160, 200, 300, 100)
    obj.set_default_resonator_parameters(950, 300, 4e5, 20, 100, 1, 10, 6, 10, 40)
    obj.set_logo('ur', "logo_mcqst", 0.4, 300).set_logo('ul', "logo_wmi", 0.5, 300)
    obj.set_eps_eff(6.45)
    obj.set_text("´f0´ (GHz): $FREQUENCIES$", False)

def template_10x6_single(obj: ChipBuilder):
    """
    Template for a 10x6 wmi chip. Initialize with "10x6_single"
    """
    obj.set_chip_size(8000, 4000).set_TL_width(10).set_TL_gap(6)
    obj.set_TL_ground(10).set_TL_hole(40).set_hole_mask("hole_mask_small")
    obj.set_port_parameters(160, 200, 300, 100)
    obj.set_default_resonator_parameters(950, 300, 4e5, 20, 100, 1, 10, 6, 10, 40)
    obj.set_logo('ur', "logo_mcqst", 0.4, 200).set_logo('ul', "logo_wmi", 0.5, 200)
    obj.set_eps_eff(6.45)
    obj.set_text("´f0´ (GHz): $FREQUENCIES$", False)

def template_10x6_single_LW(obj: ChipBuilder):
    """
    Template for a 10x6 wmi chip. Initialize with "10x6_single"
    """
    obj.set_chip_size(8000, 4000).set_TL_width(10).set_TL_gap(6)
    obj.set_TL_ground(10).set_TL_hole(40).set_hole_mask("hole_mask_small")
    obj.set_port_parameters(160, 200, 300, 100)
    obj.set_default_resonator_parameters(950, 300, 4e5, 20, 100, 1, 10, 6, 10, 40)
    obj.set_logo('ur', "logo_mcqst", 0.4, 200).set_logo('ul', "logo_wmi", 0.5, 200)
    obj.set_marker('ll', "marker_LW", 0, 90).set_marker('ur', "marker_LW", 0, 90)
    obj.set_global_rotation(-90)
    obj.set_eps_eff(6.45)
    obj.set_text("´f0´ (GHz): $FREQUENCIES$", False)

def template_10x6_single_nb5(obj: ChipBuilder):
    """
    Template for a 10x6 wmi chip. Initialize with "10x6_single"
    """
    obj.set_chip_size(9000, 5000).set_TL_width(10).set_TL_gap(6)
    obj.set_TL_ground(10).set_TL_hole(40).set_hole_mask("hole_mask_small")
    obj.set_port_parameters(160, 200, 300, 100)
    obj.set_default_resonator_parameters(950, 300, 4e5, 20, 100, 1, 10, 6, 10, 40)
    obj.set_logo('ur', "logo_mcqst", 0.4, 200).set_logo('ul', "logo_wmi", 0.5, 200)
    obj.set_marker('ll', "marker_nb5", 0, 90).set_marker('ur', "marker_nb5", 0, 90)
    obj.set_global_rotation(-90)
    obj.set_eps_eff(6.45)
    obj.set_text("´f0´ (GHz): $FREQUENCIES$", False)

def template_10x6_single_ab(obj: ChipBuilder):
    """
    Template for a single 10x6 airbridge chip (not wafer scale). Initialize with "10x6_wmi_ab"
    """
    obj.set_chip_size(8500, 4500).set_TL_width(10).set_TL_gap(6)
    obj.set_TL_ground(10).set_TL_hole(40).set_hole_mask("hole_mask_small")
    obj.set_port_parameters(160, 200, 300, 100)
    obj.set_default_resonator_parameters(950, 300, 4e5, 20, 100, 1, 10, 6, 10, 40)
    obj.set_marker('ll', "marker_LW", 0, 90).set_marker('ur', "marker_LW", 0, 90)
    obj.set_logo('ur', "logo_mcqst", 0.4, 300).set_logo('ul', "logo_wmi", 0.5, 300)
    obj.set_eps_eff(6.45)
    obj.set_text("´f0´ (GHz): $FREQUENCIES$", False)
    obj.set_airbridges(True)



def template_7x4p3_wmi(obj: ChipBuilder):
    """
    Template for a 7x4.3 chip. Initialize with "7x4p3_wmi"
    """
    obj.set_chip_size(7000, 4300).set_TL_width(10).set_TL_gap(6)
    obj.set_TL_ground(10).set_TL_hole(40).set_hole_mask("hole_mask_small")
    obj.set_port_parameters(160, 200, 300, 100)
    obj.set_logo('ul', "logo_mcqst", 0.4, 300).set_logo('ur', "logo_wmi", 0.5, 300)
    obj.set_eps_eff(6.45)
    obj.set_text("´f0´ (GHz): $FREQUENCIES$", False)


def template_W7_6x10(obj: ChipBuilder):
    """
    Template for the W7 chip.
    """
    obj.set_chip_size(10000, 6000).set_TL_width(10).set_TL_gap(6)
    obj.set_TL_ground(40).set_TL_hole(40).set_hole_mask("hole_mask_small")
    obj.set_port_parameters(160, 200, 300, 100)
    obj.set_default_resonator_parameters(400, 300, 5e5, 20, 100, 1, 10, 6, 10, 40)
    obj.set_logo('ul', "logo_wmi", 0.5, 300).set_logo('ur', "logo_mcqst", 0.4, 300)
    obj.set_eps_eff(6.45)
    obj.set_text("´f0´ (GHz): $FREQUENCIES$", False)
