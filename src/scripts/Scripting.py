import src.ChipBuilder as CB
import numpy as np
# from src.ChipBuilderNew import ChipBuilderNew
# import src.library.CellParamsNew as CP

# import src.legacy.ChipBuilderOld as CBO

"""
Tutorial for the Hanging Resonators Project
v3 06/2021
"""


cb = CB.ChipBuilder("template_B72_control")

for f, q in [(4, 5e5), (4.1, 3e5), (4.2, 7e5), (4.3, 1e5)]:
    cb.add_resonator(f, q_ext=q)
cb.set_text("B72-4 - low roughness test - ´f0´ from 4 - 5.2 GHz @ 100 MHz", False)
cb.set_logo('lr', "qr:NB - 16.09.2021\nSi in (100) orientation, > 10kOhm\nPiranha cleaned + BOE\nUD Nb 300mA @ RT @ 5e-3 mbar\nQc = 5e5", 1, 200)
cb.remove_hole_mask()
cb.build_chip("q_ext_test")


# cb = CB.ChipBuilder("template_B72_control")
#
# for f in np.linspace(4, 5.2, 13):
#     cb.add_resonator(f)
# cb.set_text("B72-4 - low roughness test - ´f0´ from 4 - 5.2 GHz @ 100 MHz", False)
# cb.set_logo('lr', "qr:NB - 16.09.2021\nSi in (100) orientation, > 10kOhm\nPiranha cleaned + BOE\nUD Nb 300mA @ RT @ 5e-3 mbar\nQc = 5e5", 1, 200)
# cb.build_chip("B72-4")

# cb = CB.ChipBuilder("template_B72_Al2O3")
#
# for f in np.linspace(4, 5.2, 13):
#     cb.add_resonator(f)
# cb.set_text("B72-3 - sapphire chips (´epsilon´=9.27) - ´f0´ from 4 - 5.2 GHz @ 100 MHz", False)
# cb.set_logo('lr', "qr:NB - 16.09.2021\nAl2O3 in (0001) orientation\nPiranha cleaned\nUD Nb 300mA @ RT @ 5e-3 mbar\nQc = 5e5", 1, 200)
# cb.build_chip("B72-3")

# cb = CB.ChipBuilder("template_B72_HF")
#
# for f in np.linspace(10, 18, 41):
#     print(f)
#     cb.add_resonator(f)
# cb.set_text("B72-1 - high frequency chips - ´f0´ from 10 - 18 GHz @ 200 MHz", False)
# cb.build_chip("B72-1")


# cb = CB.ChipBuilder("template_B72_AB")
#
# for f in np.linspace(4, 5.2, 13):
#     cb.add_resonator(f)
#
# for i in range(13):
#     # airbridge = CB.Airbridge(22, 22, 40, 18, 18, 18, 200 if i < 6 else 500)
#     airbridge = CB.AirbridgeRound(14, 40, 6, 12, 200 if i < 6 else 500)
#     if i % 2-1:
#         cb.add_decorator(i, airbridge)
#
# cb.set_text("B72-2 - Airbridge tests - ´f0´ from 4 - 5.2 GHz @ 100 MHz", False)
# cb.build_chip("B72-2")

# cb = CB.ChipBuilder("template_B64")
# for f in [4, 4.1, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5, 5.1]:
#     cb.add_resonator(f, q_ext=50_000, coupling_ground=10)
#
# for f in [4.2, 5.2]:
#     cb.add_resonator(f, q_ext=500_000)
#
# cb.set_text("Ta + 5nm TaN - ´f0´ from 4 to 5.2 GHz @ 100 MHz", False)
# cb.remove_marker('all')
# cb.remove_hole_mask()
# cb.set_global_rotation(0)
# cb.build_chip("Ta-3", file_format='dxf')


# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_text("P10-6 RCA2 + Piranha + HF - ´f0´ from 4 to 5.2 GHz @ 100 MHz", False)
# cb.remove_marker('all')
# cb.build_chip("P10-6")
#
# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_text("P10-1 Piranha + HF - ´f0´ from 4 to 5.2 GHz @ 100 MHz", False)
# cb.remove_marker('all')
# cb.build_chip("P10-1")
#
# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_text("P10-5 Huang + HF - ´f0´ from 4 to 5.2 GHz @ 100 MHz", False)
# cb.remove_marker('all')
# cb.build_chip("P10-5")
#
# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_text("P10-9 HF - ´f0´ from 4 to 5.2 GHz @ 100 MHz", False)
# cb.remove_marker('all')
# cb.build_chip("P10-9")

# cb = CB.ChipBuilder()
# cb.set_text("P10-3 Nb Q1", False)
# cb.remove_hole_mask()
# cb.build_chip("p10-3-text")

# cbn = ChipBuilderNew("template_P10")
# for i in range(13):
#     f = 4 + i*0.2
#     AB_params = CP.Airbridge(22, 22, 40, 18, 18, 18, 200 if i < 6 else 500)
#     AB_params = CP.AirbridgeRound(13, 40, 9, 18, 200 if i < 6 else 500)
#     pos = cbn.add_resonator(f)
#     if i%2 - 1:
#         cbn.add_decorator(pos, AB_params)
# cbn.remove_hole_mask()

# cbn.add_resonator(f0=4.1, width=30)

# cbn.build_chip("test-bridges")

# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_text("QR Test - ´f0´ from 4 to 5.2 GHz @ 100 MHz", False)
# cb.set_logo('lr', "qr:Air time: 3:30min, Plassys position: 9, MC BOE 7:1 for 30s, > 10kOhm Si 100 substrate, way more "
#                   "details: sputtered on 23.07.2021, written with program 7 at 100mJ, used resist AZ MiR 701, "
#                   "with 40um air bridges for better grounding, The code has been extended to investigate the behavior of"
#                   " $z$ for N > 4. The parameters $A=0.2$ and $beta=0.1$ are kept constant, while increasing $N$ from 10 "
#                   "up to 75. For each $N$ 20 iterations with different initial parameters are being calculated. "
#                   "By looking at $abs{z}$ we can detect chimera states if the coherence of one subsystem is equal to "
#                   "1, while the coherence of the other subsystem is smaller than 1.", 1, 300)
# cb.remove_hole_mask()
# cb.remove_marker('all')
# cb.build_chip("QR-Test")

# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_text("P9 RCA2 + Piranha + HF - ´f0´ from 4 to 5.2 GHz @ 100 MHz", False)
# cb.remove_marker('all')
# cb.build_chip("P9-RCA2-Piranha-HF")
#
# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_text("P9 Piranha + HF - ´f0´ from 4 to 5.2 GHz @ 100 MHz", False)
# cb.remove_marker('all')
# cb.build_chip("P9-Piranha-HF")
#
# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_text("P9 Huang + HF - ´f0´ from 4 to 5.2 GHz @ 100 MHz", False)
# cb.remove_marker('all')
# cb.build_chip("P9-Huang-HF")
#
# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_text("P9 HF - ´f0´ from 4 to 5.2 GHz @ 100 MHz", False)
# cb.remove_marker('all')
# cb.build_chip("P9-HF")

# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_airbridges(True)
# cb.set_airbridge_parameters(22, 22, 40, 18, 18, 18, 500)
# cb.set_text("AB Chip 10 - ´f0´: $FREQUENCIES$", False)
# cb.set_marker('all', "marker_AB_manual", 0)
# cb.build_chip("ab-chip-10")

# cb = CB.ChipBuilder("template_B64")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_logo('lr', f"qr:www.wmi.badw.de", 2, 300)
# cb.set_text("P8-1 - ´Qext´ = 5e5, ´f0´: $FREQUENCIES$", False)
# cb.remove_marker('all')
# cb.build_chip("P8-1")

# cb = CB.ChipBuilder("template_B60_1_wet_etching")
# cb.set_resonator_list(cb.get_resonator_list(4, 5.2, 13))
# cb.set_global_rotation(90)
# cb.set_logo('lr', f"qr:www.wmi.badw.de", 2, 300)
# cb.set_text("Ta-1 - ´Qext´ = 5e5, ´f0´: $FREQUENCIES$", False)
# cb.build_chip("Ta-1")


# cb = CB.ChipBuilder("template_W7_6x10")
# cb.set_logo('lr', "qr:W7-1, Piranha + HF, 150nm Nb", 2, 300).set_text("W7-1", True)
# cb.set_resonator_list(cb.get_resonator_list(4, 6, 21)).build_chip("W7-1")

# cbo = CBO.ChipBuilder()
# cbo.create_chip("test_fingers", cbo.res_fingers_params(4, 6, 6), hole_mask="hole_mask_small")





# cbl = CB.ChipBuilder()
# cbl.set_chip_size(8000, 4500)
# list_resonator_params = cbl.get_resonator_list(f0_start=4, f0_end=5.6, amount_resonators=9, q_ext=1e6, segment_length=650, coupling_ground=20, y_offset=300)
# cbl.set_resonator_list(list_resonator_params)
# cbl.set_logo('ll', "logo_wmi", 1.4, 100).set_logo('lr', "logo_mcqst", 1.2, 100)
# cbl.remove_hole_mask()
# cbl.set_text("OP-HF-18-1, Si(100), ´Qext´~1e6", write_frequencies=True)
# cbl.build_chip("OP-HF-18-1")



# def name():
#     return w_name + "-" + str(res_id)
#
#
# def next_name():
#     global res_id
#     res_id += 1
#     return name()
#
#
# w_name = "W7"
# res_id = 0
#
# cb = CB.ChipBuilder("template_W7_6x10")
#
# cb.set_logo('lr', f"qr:www.wmi.badw.de", 2, 300).set_text(name(), True)
# cb.set_resonator_list(cb.get_resonator_list(4, 6, 21)).build_chip(name())





# 7x4.3, 14.3x14.3











# # DESIGN 1
#
# # instatinate a ChipBuilder object with a template, e.g. 10x6_single
# cb = CB.ChipBuilder("10x6_wmi")
# # create a list of resonator params in a given frequency span
# list_resonator_params = cb.get_resonator_list(f0_start=4, f0_end=6, amount_resonators=21, q_ext=1e6, segment_length=400)
# # set the list as resonators
# cb.set_resonator_list(list_resonator_params)
# # define the text on the chip
# cb.set_text("Test resonators #1, ´Qext´=1m", write_frequencies=True)
# # generate the design with a given name
# cb.build_chip("Batch1-1")
#
# # DESIGN 2
#
# # instatinate the ChipBuilder
# cb = CB.ChipBuilder("10x6_wmi")
# # change the dielectric constant
# cb.set_eps_eff((1+11.45)/2)
# # set default resonator parameters
# cb.set_default_resonator_parameters(segment_length=500, q_ext=5e5)
# # add resonators one by one, with the set default parameters
# cb.add_resonator(cb.get_resonator(5))
# cb.add_resonator(cb.get_resonator(6))
# cb.add_resonator(cb.get_resonator(7))
# # add markers
# cb.set_marker('all', "marker_nb5", 500)
# # set the text
# cb.set_text("Test resonators #2, ´Qext´=500k\nFrequencies at 5, 6 and 7 GHz", write_frequencies=False)
# # generate the design
# cb.build_chip("Batch1-2")






# cbl = CB.ChipBuilder()
# cbl.set_chip_size(14300, 14300)
# list_resonator_params = cbl.get_resonator_list(f0_start=4.2, f0_end=11.2, amount_resonators=71, q_ext=1e6, segment_length=0.01, coupling_ground=15, y_offset=7000)
# cbl.set_resonator_list(list_resonator_params)
#
# cbl.set_logo('ur', "logo_wmi", 1.5, 200).set_logo('lr', "logo_mcqst", 1.2, 200)
# cbl.remove_hole_mask()
# cbl.set_text("Dense filling, ´Qext´=1 million\n´f0´ from 4.20 GHz to 11.20 GHz in 100 MHz steps", write_frequencies=False)
# cbl.build_chip("large_chip")



# # instantinate a chipbuilder that creates 10x6mm chips and has a transmission line width of 10µm and a gap of 6µm
# # distance from the gap to the high density holes (ground) = 50µm, high density hole width (hole) = 40µm
# cb = ChipBuilder(chip_width=10000, chip_height=6000, width=10, gap=6, ground=50, hole=40)
#
# # ---
#
# # create a list of resonator parameters: 11 equally frequency-spaced resonators from 4 to 6 GHz with an external
# # coupling of roughly 1e6
# resonator_params = cb.res_params(f_start=4, f_end=6, amount_resonators=11, q_ext=1e6)
#
# # create a chip with the given resonator parameters and save it in wd/chips/
# cb.create_chip(file_out="Batch1-1", res_params=resonator_params, text="Text on the chip\nResonators from 4 to 6 GHz",
#                markers=True, hole_mask="hole_mask_small")
# # ---
#
# # we can also re-use the chip builder and use different (or no) resonator params
# cb.create_chip(file_out="Batch1-2", res_params=[], text="Transmission Line only", hole_mask=False)
#
# # ---
#
# # instead of creating the resonator params with the cb.res_params method (see line 16), we can also create our own
# params_resonator_1 = HangingResonatorParams(950, 7000, 950, 300, 1e6, 10, 100, 1, 10, 6, 10, 6, 50, 40)
# params_resonator_2 = HangingResonatorParams(950, 6500, 950, 300, 1e6, 10, 100, 1, 10, 6, 20, 12, 50, 40)
#
# # create a chip with our two resonators we have defined above with the given params
# cb.create_chip(file_out="Batch1-3", res_params=[params_resonator_1, params_resonator_2], text="Two Resonators")
#
# # ---
#
# # We can now put our chips onto a wafer
# wafer = WaferBuilder(spacing_x=10000, spacing_y=6000)
#
# # load all chips from a given folder with a given prefix, include every design 5 times
# chip_list = wafer.load_prefixed_chips("../chips", "Batch1", amount=5)
#
# # sorting the chips by number (relevant if one wants to have a defined order on the wafer)
# chip_list = sorted(chip_list, key=lambda x: int(x[0].split("-")[1]))
#
# # create the wafer and save it in wd/wafers/
# wafer.create_wafer("WaferLayout", chip_list)