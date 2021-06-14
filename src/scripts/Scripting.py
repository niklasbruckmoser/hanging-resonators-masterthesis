import src.ChipBuilder as CB

"""
Tutorial for the Hanging Resonators Project
v3 06/2021
"""

# # instatinate a ChipBuilder object with a template, e.g. 10x6_single
# cb = CB.ChipBuilder("10x6_wmi")
# # create a list of resonator params in a given frequency span
# list_resonator_params = cb.get_resonator_list(f0_start=4, f0_end=6, amount_resonators=21, q_ext=1e6, segment_length=400)
# cb.set_resonator_list(list_resonator_params)
# cb.set_text("Test resonators #2, ´Qext´=1m", write_frequencies=True)
# cb.build_chip("save_name2")



cbl = CB.ChipBuilder()
cbl.set_chip_size(14300, 14300)
list_resonator_params = cbl.get_resonator_list(f0_start=4.2, f0_end=11.2, amount_resonators=71, q_ext=1e6, segment_length=0.01, coupling_ground=15, y_offset=7000)
cbl.set_resonator_list(list_resonator_params)

cbl.set_logo('ur', "logo_wmi", 1.5, 200).set_logo('lr', "logo_mcqst", 1.2, 200)
cbl.remove_hole_mask()
cbl.set_text("Dense filling, ´Qext´=1 million\n´f0´ from 4.20 GHz to 11.20 GHz in 100 MHz steps", write_frequencies=False)
cbl.build_chip("large_chip")

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


