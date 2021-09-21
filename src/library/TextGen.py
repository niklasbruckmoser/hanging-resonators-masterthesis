import klayout.db as pya

"""
Quick and dirty text generator using the custom font
"""


def write_text(layout, text, font="circular_font", buffer_trigger="´") -> pya.Cell:
    """
    Write a text with a given font file. Special characters (i.e. cells with names longer than one char) can be written
    by enclosing the cell name with the buffer trigger, e.g. ´Qext´ or ´epsilon´.
    @param layout: layout to be used for the cell
    @param text: text to write
    @param font: font to be used, currently only "circular_font" exists
    @param buffer_trigger: trigger for the buffer, should be a character without any practical use
    @return: a cell object
    """
    # auxilliary layout for font loading
    aux = pya.Layout()
    dbu = aux.dbu

    lines = text.splitlines()
    aux.read(f"../../templates/{font}.gds")
    text = aux.create_cell("text")

    letter_spacing = 5
    height = aux.cell("0").bbox().height()*dbu

    x, y = 0, height*(len(lines)-1)

    for line in lines:

        text.shapes(aux.layer(2, 0)).insert(pya.Box(-3*letter_spacing/dbu, y/dbu, 0, y/dbu+height/dbu))

        buffer = None

        for letter in line:
            if buffer is None and letter == buffer_trigger:
                buffer = ""
                continue

            if buffer is not None:
                if letter == buffer_trigger:
                    letter = buffer
                    buffer = None
                else:
                    buffer += letter
                    continue

            if letter == " ":
                letter = "space"
            letter_cell = aux.cell_by_name(letter)
            trans = pya.DCplxTrans.new(1, 0, False, x, y)
            text.insert(pya.DCellInstArray(letter_cell, trans))

            x += aux.cell(letter_cell).bbox().width()*dbu

            text.shapes(aux.layer(2, 0)).insert(pya.Box(x/dbu, y/dbu, x/dbu+letter_spacing/dbu, y/dbu+height/dbu))

            x += letter_spacing

        text.shapes(aux.layer(2, 0)).insert(pya.Box(x/dbu, y/dbu, x/dbu+2*letter_spacing/dbu, y/dbu+height/dbu))

        y -= height
        x = 0

    text.flatten(1)

    cell = layout.create_cell("rtext")
    cell.copy_shapes(text)

    return cell


def place_cell_center(layout, cell, text, mag, x, y):

    bbox = text.bbox()
    x = x-bbox.width()*mag*layout.dbu/2
    y = y-bbox.height()*mag*layout.dbu/2

    trans = pya.DCplxTrans.new(mag, 0, False, x, y)
    cell.insert(pya.DCellInstArray(text.cell_index(), trans))

def place_cell(layout, cell, text, mag, x, y):

    trans = pya.DCplxTrans.new(mag, 0, False, x, y)
    cell.insert(pya.DCellInstArray(text.cell_index(), trans))