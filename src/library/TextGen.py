import klayout.db as pya


def write_text(layout, text):

    # auxilliary layout for font loading
    aux = pya.Layout()
    dbu = aux.dbu

    lines = text.splitlines()
    aux.read("../templates/circular_font.gds")
    text = aux.create_cell("text")

    letter_spacing = 5
    height = aux.cell("0").bbox().height()*dbu

    x, y = 0, height*(len(lines)-1)

    for line in lines:

        text.shapes(aux.layer(2, 0)).insert(pya.Box(-3*letter_spacing/dbu, y/dbu, 0, y/dbu+height/dbu))

        buffer = None

        for letter in line:
            if buffer is None and letter == "´":
                buffer = ""
                continue

            if buffer is not None:
                if letter == "´":
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
