
"""
Function definitions used in the Library CPW_pieces
v1 - (c) 20.11.2018 - Clemens Mueller, IBM Research Zurich
"""


## depending on if this is run in standalone python or kLayout python, module is called differently
import sys
if sys.version_info[0] == 2:  # v2 does not have importlib
    import pkgutil
    pyaLoad = pkgutil.find_loader('klayout')
else:
    import importlib
    pyaLoad = importlib.find_loader('klayout')
if pyaLoad is not None:
    import klayout.db as pya
else:
    import pya
## other required modules
import math
import numpy as np
import random as rd


## general functions, defining shapes through points
def arc(r1, r2=None, n=32):
    # array of points along 90 degree (double arc), inner radius r1, outer radius r2, n points per arcsegment
    pts = []
    # inner arc, full 90 degree
    da = math.pi / (n - 1) / 2
    for i in range(0, n):
        pts.append(pya.Point.from_dpoint(pya.DPoint(r1 * math.cos(i * da), r1 * math.sin(i * da))))
    if r2 is not None:
        pts.append(pya.Point.from_dpoint(pya.DPoint(0, r2)))
        # outer arc
        for i in range(n - 1, -1, -1):
            pts.append(pya.Point.from_dpoint(pya.DPoint(r2 * math.cos(i * da), r2 * math.sin(i * da))))
    return pts


def circle(r, n=64):
    # array of points along a circle, origin in middle
    pts = []
    # inner arc, full 90 degree
    da = 2 * math.pi / (n - 1)
    for i in range(0, n):
        pts.append(pya.DPoint(r * math.cos(i * da), r * math.sin(i * da)))
    return pts


def cross(size, width):
    # cross shape, arms with width and size, centered at zero
    al = size / 2  # length of arms, measured wrt centre
    aw = width / 2   # width of arms, measured wrt centre
    pts = [pya.DPoint(-al, -aw), pya.DPoint(-aw, -aw), pya.DPoint(-aw, -al), pya.DPoint(aw, -al),
        pya.DPoint(aw, -aw), pya.DPoint(al, -aw), pya.DPoint(al, aw), pya.DPoint(aw, aw),
        pya.DPoint(aw, al), pya.DPoint(-aw, al), pya.DPoint(-aw, aw), pya.DPoint(-al, aw)]
    return pts


##  functions that change something in a layout
def logo(obj, layer, size, initial_point=pya.DPoint(0, 0), orientation=0, mirror=0):

    if orientation == 0:
        trans = pya.ICplxTrans(1, 0, False, 0, 0)
    elif orientation == 1:
        trans = pya.ICplxTrans(1, 90, False, 0, 0)
    elif orientation == 2:
        trans = pya.ICplxTrans(1, 180, False, 0, 0)
    else:
        trans = pya.ICplxTrans(1, 270, False, 0, 0)

    if mirror:
        mirrorX = pya.ICplxTrans.M0
    else:
        mirrorX = pya.ICplxTrans.R0

    shift = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)

    allTrans =  mirrorX * shift * trans

    # letter thickness and other dimensions
    thick = size / 7;
    dist = size / 3
    rB = size / 4  # radius of arcs in B
    bSize = 2 * thick + rB
    nArc = 16  # number of points in arc
    mAngle = 35 / 180 * math.pi
    mSize = 2 * (size - thick) * math.tan(mAngle)

    # letter I
    obj.cell.shapes(layer).insert(pya.Box(0, 0, thick, size).transformed(allTrans))
    # letter B
    bStart = pya.DPoint(thick + dist, 0)
    def makeB(bStart, size, thick, rB, nArc):
        # outer contour
        bPts = [bStart, pya.DPoint(bStart.x + 2 * thick, 0)]
        dB = math.pi / (nArc - 1)  # 180 degree in nArc points
        for it in range(0, nArc):
            bPts.append(pya.DPoint(bStart.x + 2 * thick + rB * math.sin(it * dB), rB * (1 - math.cos(it * dB))))
        for it in range(0, nArc):
            bPts.append(pya.DPoint(bStart.x + 2 * thick + rB * math.sin(it * dB), rB * (3 - math.cos(it * dB))))
        bPts.append(pya.DPoint(bStart.x, size))
        # inner contour, upper
        bPts.append(pya.DPoint(bStart.x, size - thick))
        bPts.append(pya.DPoint(bStart.x + thick, size - thick))
        # bPts.append(pya.DPoint(bStart.x + 2 * thick, size - thick))
        for it in range(0, nArc):
            bPts.append(pya.DPoint(bStart.x + 2 * thick + (rB - thick) * math.sin(it * dB), size - rB + (rB - thick) * math.cos(it * dB)))
        # bPts.append(pya.DPoint(bStart.x + 2 * thick, size / 2 + thick ))
        bPts.append(pya.DPoint(bStart.x + thick, size / 2 + thick))
        bPts.append(pya.DPoint(bStart.x + thick, size - thick))
        bPts.append(pya.DPoint(bStart.x, size - thick))
        # inner contour, lower
        bPts.append(pya.DPoint(bStart.x, size - thick - 2 * rB))
        bPts.append(pya.DPoint(bStart.x + thick, size / 2 - thick))
        # bPts.append(pya.DPoint(bStart.x + 2 * thick, size / 2 - thick))
        for it in range(0, nArc):
            bPts.append(pya.DPoint(bStart.x + 2 * thick + (rB - thick) * math.sin(it * dB), thick + (rB - thick) * (1 + math.cos(it * dB))))
        bPts.append(pya.DPoint(bStart.x + thick, thick))
        bPts.append(pya.DPoint(bStart.x + thick, size / 2 - thick))
        bPts.append(pya.DPoint(bStart.x, size - thick - 2 * rB))

        return bPts
    # make the shape
    # obj.cell.shapes(obj.layer).insert(pya.Polygon(bPts).transformed(allTrans))
    obj.cell.shapes(layer).insert(pya.Polygon(makeB(bStart, size, thick, rB, nArc)).transformed(allTrans))
    # letter M
    mStart = pya.DPoint(thick + 2 * dist + bSize, 0)
    def makeM(mStart, size, thick, mAngle):
        # M with sharp corners
        # obj.cell.shapes(obj.layer).insert(pya.Polygon([
        #         mStart, pya.DPoint(mStart.x + thick, 0),
        #         pya.DPoint(mStart.x + thick, size - thick / math.sin(mAngle) - thick / math.tan(mAngle)), pya.DPoint(mStart.x + mSize / 2 - thick / 2, 0),
        #         pya.DPoint(mStart.x + mSize / 2 + thick / 2, 0), pya.DPoint(mStart.x + mSize - thick, size - thick / math.sin(mAngle) - thick / math.tan(mAngle)),
        #         pya.DPoint(mStart.x + mSize - thick, 0), pya.DPoint(mStart.x + mSize, 0),
        #         pya.DPoint(mStart.x + mSize, size),
        #         pya.DPoint(mStart.x + mSize / 2, thick),
        #         pya.DPoint(mStart.x, size)
        #     ]).transformed(allTrans))
        # M with step corners
        mPts = [
                mStart, pya.DPoint(mStart.x + thick, 0),
                pya.DPoint(mStart.x + thick, size - thick / math.sin(mAngle)), pya.DPoint(mStart.x + mSize / 2 - thick / 2, 0),
                pya.DPoint(mStart.x + mSize / 2 + thick / 2, 0), pya.DPoint(mStart.x + mSize - thick, size - thick / math.sin(mAngle)),
                pya.DPoint(mStart.x + mSize - thick, 0), pya.DPoint(mStart.x + mSize, 0),
                pya.DPoint(mStart.x + mSize, size), pya.DPoint(mStart.x + mSize - thick, size),
                pya.DPoint(mStart.x + mSize / 2, thick), pya.DPoint(mStart.x + thick, size),
                pya.DPoint(mStart.x, size)
            ]

        return mPts
    # make the shape
    obj.cell.shapes(layer).insert(pya.Polygon(makeM(mStart, size, thick, mAngle)).transformed(allTrans))


def create_cpw_90(obj, ground, gap, width, n, hdHole, initial_point, orientation, mirror):
    # carrying over from legacy version - radius set fix to hdHole width
    radius = hdHole
    # 90 degree cpw arc - hardcoded layers for each part
    shiftorigin = pya.ICplxTrans(1, 0, False, -(radius + ground + gap + width / 2), 0)

    # mirroralongx = pya.ICplxTrans.R0
    # shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)
    if mirror:
        mirroralongx = pya.ICplxTrans.M0
    else:
        mirroralongx = pya.ICplxTrans.R0

    shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)

    # create the shape, initial direction pointing to the top; vector (x,y) = (0,1)
    if orientation == "tr":  # -> bottom to top right
        trans = pya.ICplxTrans(1, 180, True, 0, 0)
    elif orientation == "rb":  # -> left to bottom right
        trans = pya.ICplxTrans(1, 90, True, 0, 0)
    elif orientation == "br":  # -> top to bottom right
        trans = pya.ICplxTrans(1, 180, False, 0, 0)
    elif orientation == "rt":  # -> left to right top
        trans = pya.ICplxTrans(1, -90, False, 0, 0)
    elif orientation == "bl":  # -> bottom to top left
        trans = pya.ICplxTrans(1, 0, False, 0, 0)
    elif orientation == "lb":  # -> right to top left
        trans = pya.ICplxTrans(1, 270, True, 0, 0)
    elif orientation == "tl":  # -> right to bottom left
        trans = pya.ICplxTrans(1, 90, False, 0, 0)
    elif orientation == "lt":  # -> top to left left
        trans = pya.ICplxTrans(1, 0, True, 0, 0)
    else:  # fallback -> bottom to top left
        trans = pya.ICplxTrans(1, 0, False, 0, 0)

    allTrans = shifttopos * mirroralongx * trans * shiftorigin

    # inner ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Polygon(arc(radius, radius + ground, n)).transformed(allTrans))
    # centre conductor
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Polygon(arc(radius + ground + gap, radius + ground + gap + width, n)).transformed(allTrans))
    # outer ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Polygon(arc(radius + ground + 2 * gap + width, radius + 2 * ground + 2 * gap + width, n)).transformed(allTrans))

    # create boundary mask for ground plane cutout
    obj.cell.shapes(obj.layout.layer(10, 0)).insert(
        pya.Polygon(arc(radius, radius + 2 * ground + 2 * gap + width, n)).transformed(allTrans))

    # create additional boundary mask for burried structures
    obj.cell.shapes(obj.layout.layer(120, 0)).insert(
        pya.Polygon(arc(radius + ground / 2, radius + 3 * ground / 2 + 2 * gap + width, n)).transformed(allTrans))

    # create mask for dense hole pattern - inner segment
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Polygon(arc(0, radius, n)).transformed(allTrans))
    # outer segment
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Polygon(arc(radius + 2 * ground + 2 * gap + width, radius + 2 * ground + 2 * gap + width + hdHole, n)).transformed(allTrans))

    # final point = endpoint of arc
    final_point = arc(radius + ground + gap + width / 2, radius + 2 * ground + 2 * gap + width, n)[n - 1]

    # return final point
    return (shifttopos * trans * shiftorigin).trans(final_point)


def create_cpw_straight(obj, length, ground, width, gap, hdHole, initial_point, orientation, mirror):
    # straight cpw piece - hardcoded layers for each part
    if orientation == 0:  # horizontal to right
        trans = pya.ICplxTrans(1, 0, False, 0, 0)
    elif orientation == 1:  # vertical to top
        trans = pya.ICplxTrans(1, 90, False, 0, 0)
    elif orientation == 2:  # horizontal to left
        trans = pya.ICplxTrans(1, 180, False, 0, 0)
    else:  # vertical to bottom
        trans = pya.ICplxTrans(1, 270, False, 0, 0)

    if mirror:
        mirroralongx = pya.ICplxTrans.M0
    else:
        mirroralongx = pya.ICplxTrans.R0

    shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)

    allTrans = shifttopos * mirroralongx * trans

    # lower ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, -(2 * ground + 2 * gap + width) / 2, length, -(2 * gap + width) / 2).transformed(allTrans))
    # centre conductor
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, -width / 2 , length, width / 2).transformed(allTrans))
    # upper ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, gap + width / 2, length, gap + ground + width / 2).transformed(allTrans))

    # create boundary mask for ground plane cutout
    obj.cell.shapes(obj.layout.layer(10, 0)).insert(
        pya.Box(0, -(2 * ground + 2 * gap + width) / 2, length, (2 * ground + 2 * gap + width) / 2).transformed(allTrans))

    # create additional boundary mask for burried structures
    obj.cell.shapes(obj.layout.layer(120, 0)).insert(
        pya.Box(0, -(ground + 2 * gap + width) / 2, length, (ground + 2 * gap + width) / 2).transformed(allTrans))

    # create mask for dense dense hole pattern - lower
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Box(0, -(2 * ground + 2 * gap + width) / 2 - hdHole, length, -(2 * ground + 2 * gap + width) / 2).transformed(allTrans))
    # upper
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Box(0, (2 * ground + 2 * gap + width) / 2, length, (2 * ground + 2 * gap + width) / 2 + hdHole).transformed(allTrans))

    # return final point
    return (shifttopos * trans).trans(pya.DPoint(length, 0))

def create_cpw_straight_fingers(obj, length, ground, width, gap, hdHole, initial_point, orientation, mirror, fingers, fingerLength, fingerEndGap, hookWidth, hookLength, hookUnit, holeLength):
    if fingers <= 0:
        return create_cpw_straight(obj, length, ground, width, gap, hdHole, initial_point, orientation, mirror)
    else:
        # straight cpw piece with fingers - hardcoded layers for each part
        if orientation == 0:  # horizontal to right
            trans = pya.ICplxTrans(1, 0, False, 0, 0)
        elif orientation == 1:  # vertical to top
            trans = pya.ICplxTrans(1, 90, False, 0, 0)
        elif orientation == 2:  # horizontal to left
            trans = pya.ICplxTrans(1, 180, False, 0, 0)
        else:  # vertical to bottom
            trans = pya.ICplxTrans(1, 270, False, 0, 0)
    
        if mirror:
            mirroralongx = pya.ICplxTrans.M0
        else:
            mirroralongx = pya.ICplxTrans.R0
    
        shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)
    
        allTrans = shifttopos * mirroralongx * trans
    
        # lower ground plane
        obj.cell.shapes(obj.layout.layer(1, 0)).insert(
            pya.Box(0, -(ground + fingerEndGap + fingerLength + width/2), length, -(fingerEndGap + fingerLength + width/2)).transformed(allTrans))
        # centre conductor
        obj.cell.shapes(obj.layout.layer(1, 0)).insert(
            pya.Box(0, -width/2 , length, width/2).transformed(allTrans))
        # upper ground plane
        obj.cell.shapes(obj.layout.layer(1, 0)).insert(
            pya.Box(0, fingerEndGap + fingerLength + width/2, length, ground + fingerEndGap + fingerLength + width/2).transformed(allTrans))
    
        # create boundary mask for ground plane cutout
        obj.cell.shapes(obj.layout.layer(10, 0)).insert(
            pya.Box(0, -(ground + fingerEndGap + fingerLength + width/2), length, ground + fingerEndGap + fingerLength + width/2).transformed(allTrans))
    
        # create additional boundary mask for burried structures
        obj.cell.shapes(obj.layout.layer(120, 0)).insert(
            pya.Box(0, -(ground/2 + fingerEndGap + fingerLength + width/2), length, ground/2 + fingerEndGap + fingerLength + width/2).transformed(allTrans))
    
        # create mask for dense dense hole pattern - lower
        obj.cell.shapes(obj.layout.layer(11, 0)).insert(
            pya.Box(0, -(ground + fingerEndGap + fingerLength + width/2) - hdHole, length, -(ground + fingerEndGap + fingerLength + width/2)).transformed(allTrans))
        # upper
        obj.cell.shapes(obj.layout.layer(11, 0)).insert(
            pya.Box(0, ground + fingerEndGap + fingerLength + width/2, length, ground + fingerEndGap + fingerLength + width/2 + hdHole).transformed(allTrans))
        
        # calc possible number of fingers
        spacing = 2*width
        possibleFingers = 2*int((length - spacing)/(spacing + width + 2*gap))
        if possibleFingers < fingers:
            fingers = possibleFingers
        # calc finger sites
        fingerSites = int(fingers/2) + fingers%2
        # calc spacing
        spacing = (length - fingerSites*(width + 2*gap))/(fingerSites + 1)
        # create first upper and lower ground block
        obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(0, gap + width/2, spacing, fingerEndGap + fingerLength + width/2).transformed(allTrans))
        obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(0, -(fingerEndGap + fingerLength + width/2), spacing, -(gap + width/2)).transformed(allTrans))
        # create fingers
        for i in range(fingerSites):
            # calc coordinates for basewire hooks
            x_hook = spacing + gap + width/2 + i*(width + 2*gap + spacing)
            y_hook = fingerLength + width/2
            # upper finger
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(spacing + gap + i*(width + 2*gap + spacing), width/2, spacing + gap + width + i*(width + 2*gap + spacing), fingerLength + width/2).transformed(allTrans))
            # basewire hook
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook - hookWidth/2, y_hook, x_hook + hookWidth/2, y_hook + hookLength - holeLength - hookUnit).transformed(allTrans))
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook - hookWidth/2, y_hook, x_hook - hookWidth/2 + hookUnit, y_hook + hookLength).transformed(allTrans))
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook + hookWidth/2 - hookUnit, y_hook, x_hook + hookWidth/2, y_hook + hookLength).transformed(allTrans))
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook - hookWidth/2, y_hook + hookLength - hookUnit, x_hook - hookUnit/2, y_hook + hookLength).transformed(allTrans))
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook + hookUnit/2, y_hook + hookLength - hookUnit, x_hook + hookWidth/2, y_hook + hookLength).transformed(allTrans))
            # electrodes
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook - hookWidth/2 - 4*hookUnit, y_hook + hookLength + hookUnit, x_hook - hookWidth/2 - 2*hookUnit, y_hook + hookLength + 2*hookUnit).transformed(allTrans))
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook - hookWidth/2 - 3*hookUnit, y_hook + hookLength + hookUnit, x_hook - hookWidth/2 - 2*hookUnit, y_hook + fingerEndGap).transformed(allTrans))
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook + hookWidth/2 + 2*hookUnit, y_hook + hookLength + hookUnit, x_hook + hookWidth/2 + 4*hookUnit, y_hook + hookLength + 2*hookUnit).transformed(allTrans))
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook + hookWidth/2 + 2*hookUnit, y_hook + hookLength + hookUnit, x_hook + hookWidth/2 + 3*hookUnit, y_hook + fingerEndGap).transformed(allTrans))
            # Al
            obj.cell.shapes(obj.layout.layer(98, 0)).insert(pya.Box(x_hook - hookWidth/2 - hookUnit/2, y_hook - hookUnit/2, x_hook + hookWidth/2 + hookUnit/2, y_hook + hookLength + hookUnit/2).transformed(allTrans))
            obj.cell.shapes(obj.layout.layer(98, 0)).insert(pya.Box(x_hook - hookWidth/2 - 9*hookUnit/2, y_hook + hookLength + hookUnit/2, x_hook - hookWidth/2 - 3*hookUnit/2, y_hook + hookLength + 7*hookUnit/2).transformed(allTrans))
            obj.cell.shapes(obj.layout.layer(98, 0)).insert(pya.Box(x_hook + hookWidth/2 + 9*hookUnit/2, y_hook + hookLength + hookUnit/2, x_hook + hookWidth/2 + 3*hookUnit/2, y_hook + hookLength + 7*hookUnit/2).transformed(allTrans))
            # following ground block
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(spacing + 2*gap + width + i*(width + 2*gap + spacing), width/2 + gap, 2*spacing + 2*gap + width + i*(width + 2*gap + spacing), fingerEndGap + fingerLength + width/2).transformed(allTrans))
            # lower finger
            if 2*(i+1) - fingers == 1:
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(spacing + i*(width + 2*gap + spacing), -(fingerEndGap + fingerLength + width/2), spacing + 2*gap + width + i*(width + 2*gap + spacing), -(gap + width/2)).transformed(allTrans))
            else:
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(spacing + gap + i*(width + 2*gap + spacing), -(fingerLength + width/2), spacing + gap + width + i*(width + 2*gap + spacing), -width/2).transformed(allTrans))
                # basewire hook
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook - hookWidth/2, -(y_hook + hookLength - holeLength - hookUnit), x_hook + hookWidth/2, -y_hook).transformed(allTrans))
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook - hookWidth/2, -(y_hook + hookLength), x_hook - hookWidth/2 + hookUnit, -y_hook).transformed(allTrans))
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook + hookWidth/2 - hookUnit, -(y_hook + hookLength), x_hook + hookWidth/2, -y_hook).transformed(allTrans))
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook - hookWidth/2, -(y_hook + hookLength), x_hook - hookUnit/2, -(y_hook + hookLength - hookUnit)).transformed(allTrans))
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook + hookUnit/2, -(y_hook + hookLength), x_hook + hookWidth/2, -(y_hook + hookLength - hookUnit)).transformed(allTrans))
                # electrodes
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook - hookWidth/2 - 4*hookUnit, -(y_hook + hookLength + 2*hookUnit), x_hook - hookWidth/2 - 2*hookUnit, -(y_hook + hookLength + hookUnit)).transformed(allTrans))
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook - hookWidth/2 - 3*hookUnit, -(y_hook + fingerEndGap), x_hook - hookWidth/2 - 2*hookUnit, -(y_hook + hookLength + hookUnit)).transformed(allTrans))
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook + hookWidth/2 + 2*hookUnit, -(y_hook + hookLength + 2*hookUnit), x_hook + hookWidth/2 + 4*hookUnit, -(y_hook + hookLength + hookUnit)).transformed(allTrans))
                obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(x_hook + hookWidth/2 + 2*hookUnit, -(y_hook + fingerEndGap), x_hook + hookWidth/2 + 3*hookUnit, -(y_hook + hookLength + hookUnit)).transformed(allTrans))
                # Al
                obj.cell.shapes(obj.layout.layer(98, 0)).insert(pya.Box(x_hook - hookWidth/2 - hookUnit/2, -(y_hook + hookLength + hookUnit/2), x_hook + hookWidth/2 + hookUnit/2, -(y_hook - hookUnit/2)).transformed(allTrans))
                obj.cell.shapes(obj.layout.layer(98, 0)).insert(pya.Box(x_hook - hookWidth/2 - 9*hookUnit/2, -(y_hook + hookLength + 7*hookUnit/2), x_hook - hookWidth/2 - 3*hookUnit/2, -(y_hook + hookLength + hookUnit/2)).transformed(allTrans))
                obj.cell.shapes(obj.layout.layer(98, 0)).insert(pya.Box(x_hook + hookWidth/2 + 9*hookUnit/2, -(y_hook + hookLength + 7*hookUnit/2), x_hook + hookWidth/2 + 3*hookUnit/2, -(y_hook + hookLength + hookUnit/2)).transformed(allTrans))
            # following ground block
            obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Box(spacing + 2*gap + width + i*(width + 2*gap + spacing), -(fingerEndGap + fingerLength + width/2), 2*spacing + 2*gap + width + i*(width + 2*gap + spacing), -(gap + width/2)).transformed(allTrans))
        
        # return final point
        return (shifttopos * trans).trans(pya.DPoint(length, 0))


def create_cpw_end(obj, length, ground, width, gap, endGap, hdHole, initial_point, orientation, mirror):
    # straight cpw piece plus end capacitor - hardcoded layers for each part
    if orientation == 0:  # horizontal to right
        trans = pya.ICplxTrans(1, 0, False, 0, 0)
    elif orientation == 1:  # vertical to top
        trans = pya.ICplxTrans(1, 90, False, 0, 0)
    elif orientation == 2:  # horizontal to left
        trans = pya.ICplxTrans(1, 180, False, 0, 0)
    else:  # vertical to bottom
        trans = pya.ICplxTrans(1, 270, False, 0, 0)

    if mirror:
        mirroralongx = pya.ICplxTrans.M0
    else:
        mirroralongx = pya.ICplxTrans.R0

    shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)

    allTrans = shifttopos * mirroralongx * trans

    # ground plane as a single Polygon
    pPoints = []
    pPoints.append(pya.DPoint(0, -(2 * ground + 2 * gap + width) / 2))
    pPoints.append(pya.DPoint(length + endGap + ground, -(2 * ground + 2 * gap + width) / 2))
    pPoints.append(pya.DPoint(length + endGap + ground, gap + ground + width / 2))
    pPoints.append(pya.DPoint(0, gap + ground + width / 2))
    pPoints.append(pya.DPoint(0, gap + width / 2))
    pPoints.append(pya.DPoint(length + endGap, gap + width / 2))
    pPoints.append(pya.DPoint(length + endGap, -(gap + width / 2)))
    pPoints.append(pya.DPoint(0, -(gap + width / 2)))
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Polygon(pPoints).transformed(allTrans))

    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, -width / 2 , length, width / 2).transformed(allTrans))

    # create boundary mask for ground plane cutout
    obj.cell.shapes(obj.layout.layer(10, 0)).insert(
        pya.Box(0, -(2 * ground + 2 * gap + width) / 2, length + endGap + ground, (2 * ground + 2 * gap + width) / 2).transformed(allTrans))

    # create additional boundary mask for burried structures
    obj.cell.shapes(obj.layout.layer(120, 0)).insert(
        pya.Box(0, -(ground + 2 * gap + width) / 2, length + endGap + ground / 2, (ground + 2 * gap + width) / 2).transformed(allTrans))

    # create mask for dense dense hole pattern - lower
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Box(0, -(2 * ground + 2 * gap + width) / 2 - hdHole, length + endGap + ground, -(2 * ground + 2 * gap + width) / 2).transformed(allTrans))
    # upper
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Box(0, (2 * ground + 2 * gap + width) / 2, length + endGap + ground, (2 * ground + 2 * gap + width) / 2 + hdHole).transformed(allTrans))

    # return final point of cpw part
    return (shifttopos * trans).trans(pya.DPoint(length, 0))


def create_cpw_parallel(obj, length, ground, width, gap, midGround, hdHole, initial_point, orientation, mirror):
    # two parallel straight cpw elements  - hardcoded layers for each part
    if orientation == 0:  # horizontal to right
        trans = pya.ICplxTrans(1, 0, False, 0, 0)
    elif orientation == 1:  # vertical to top
        trans = pya.ICplxTrans(1, 90, False, 0, 0)
    elif orientation == 2:  # horizontal to left
        trans = pya.ICplxTrans(1, 180, False, 0, 0)
    else:  # vertical to bottom
        trans = pya.ICplxTrans(1, 270, False, 0, 0)

    if mirror:
        mirroralongx = pya.ICplxTrans.M0
        shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)
    else:
        mirroralongx = pya.ICplxTrans.R0
        shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)

    allTrans = shifttopos * mirroralongx * trans

    # lower ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, -(2 * ground + 4 * gap + 2 * width + midGround) / 2, length, -(2 * ground + 4 * gap + 2 * width + midGround) / 2 + ground).transformed(allTrans))
    # centre conductor lower cpw
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, -(gap + width + midGround / 2), length, -(gap + width + midGround / 2) + width).transformed(allTrans))
    # middle ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, -midGround / 2, length, midGround / 2).transformed(allTrans))
    # centre conductor, upper cpw
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, (gap + midGround / 2), length, (gap + width + midGround / 2)).transformed(allTrans))
    # upper ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, 2 * gap + width + midGround / 2, length, 2 * gap + width + ground + midGround / 2).transformed(allTrans))

    # create boundary mask for ground plane cutout
    obj.cell.shapes(obj.layout.layer(10, 0)).insert(
        pya.Box(0, -(2 * ground + 4 * gap + 2 * width + midGround) / 2, length, (2 * ground + 4 * gap + 2 * width + midGround) / 2).transformed(allTrans))

    # create additional boundary mask for burried structures
    obj.cell.shapes(obj.layout.layer(120, 0)).insert(
        pya.Box(0, -(ground + 4 * gap + 2 * width + midGround) / 2, length, (ground + 4 * gap + 2 * width + midGround) / 2).transformed(allTrans))

    # create mask for dense dense hole pattern
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Box(0, -(2 * ground + 4 * gap + 2 * width + midGround) / 2 - hdHole, length, -(2 * ground + 4 * gap + 2 * width + midGround) / 2).transformed(allTrans))
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Box(0, (2 * ground + 4 * gap + 2 * width + midGround) / 2, length, (2 * ground + 4 * gap + 2 * width + midGround) / 2 + hdHole).transformed(allTrans))

    # return final point of upper cpw - lower cpw shifted by (2 * gap + width + midGround) below
    return (shifttopos * trans).trans(pya.DPoint(length, (2 * gap + midGround + width) / 2))


def create_cpw_rescoupler(obj, length, ground, width, gap, endGap, midGround, n, hdHole, initial_point, orientation, mirror):
    # two parallel straight cpw elements plus arc segment for lower cpw  - hardcoded layers for each part
    # additional endcap on lower cpw
    if orientation == 0:  # horizontal to right
        trans = pya.ICplxTrans(1, 0, False, 0, 0)
    elif orientation == 1:  # vertical to top
        trans = pya.ICplxTrans(1, 90, False, 0, 0)
    elif orientation == 2:  # horizontal to left
        trans = pya.ICplxTrans(1, 180, False, 0, 0)
    else:  # vertical to bottom
        trans = pya.ICplxTrans(1, 270, False, 0, 0)

    # additional shift in y-direction to have upper cpw at (0,0)
    #shiftOrigin = pya.ICplxTrans(1,0, False, 0, -(midGround / 2 + widht / 2 + gap))

    if mirror:
        mirroralongx = pya.ICplxTrans.M0
        shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y -(midGround / 2 + width / 2 + gap))
    else:
        mirroralongx = pya.ICplxTrans.R0
        shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y -(midGround / 2 + width / 2 + gap))

    allTrans = shifttopos * mirroralongx * trans

    # length of endcap piece
    lengthEnd = ground + endGap
    # shift with respect to endcap
    shiftEnd = pya.ICplxTrans(1, 0, False, lengthEnd, 0)
    # length of arc in x-plane
    lengthArc = 2 * ground + 2 * gap + width + 2 * hdHole
    # shift in initial point for arc segments
    shiftArc = pya.ICplxTrans(1, 0, False, length + lengthEnd, -(2 * ground + 4 * gap + 2 * width + midGround) / 2 - hdHole)

    # lower ground plane as polygon
    def lGround(length, gap, width, ground, lengthArc, midGround, hdHole, n):
        height = midGround / 2 + 2 * gap + width + ground + hdHole
        pts=[]
        pts.append(pya.DPoint(0, -(2 * ground + 4 * gap + 2 * width + midGround) / 2))
        pts.append(pya.DPoint(length, -(2 * ground + 4 * gap + 2 * width + midGround) / 2))
        da = math.pi / (n - 1) / 2
        # lower arc, starting from top
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(hdHole * math.cos(i * da) + length, hdHole * math.sin(i * da) - height))
        pts.append(pya.DPoint(hdHole + ground + length,  -height))
        # upper arc, starting from bottom
        for i in range(0, n):
            pts.append(pya.DPoint((hdHole + ground) * math.cos(i * da) + length, (hdHole + ground) * math.sin(i * da) - height))
        pts.append(pya.DPoint(0, -(4 * gap + 2 * width + midGround) / 2))

        return pts
    # centre conductor lower cpw as Polygon
    def lcentre(length, gap, width, ground, lengthArc, midGround, hdHole, n):
        height = midGround / 2 + 2 * gap + width + ground + hdHole
        r1 = hdHole + ground + gap
        r2 = hdHole + ground + gap + width
        pts = []
        pts.append(pya.DPoint(0, -(gap + width + midGround / 2)))
        pts.append(pya.DPoint(length, -(gap + width + midGround / 2)))
        da = math.pi / (n - 1) / 2
        # lower arc, starting from top
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(r1 * math.cos(i * da) + length, r1 * math.sin(i * da) - height))
        pts.append(pya.DPoint(r2 + length, -height))
        # upper arc, starting from bottom
        for i in range(0, n):
            pts.append(pya.DPoint(r2 * math.cos(i * da) + length, r2 * math.sin(i * da) - height))
        # pts.extend(arc(hdHole + ground + gap, hdHole + ground + gap + width, n))
        pts.append(pya.DPoint(0, -(gap + width + midGround / 2) + width))

        return pts
    # middle ground plane as polygon
    def midPoly(length, gap, width, ground, lengthArc, midGround, hdHole, n):
        # Polygon defining the middle groundplane
        pts = []
        pts.append(pya.DPoint(0, -midGround / 2))
        pts.append(pya.DPoint(length, -midGround / 2))
        da = math.pi / (n - 1) / 2
        height = midGround / 2 + 2 * gap + width + ground + hdHole
        r1 = hdHole + ground + 2 * gap + width
        r2 = hdHole + 2 * ground + 2 * gap + width
        # inner arc segment
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(r1 * math.cos(i * da) + length, r1 * math.sin(i * da) - height))
        # outer arc segment, starting from lowest point
        pts.append(pya.DPoint(r2 + length, - height))
        # maximum angle, given size of middle ground plane
        da = np.arcsin((hdHole + 2 * gap + width + midGround) / r2) / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(r2 * math.cos(i * da) + length, r2 * math.sin(i * da) - height))
        pts.append(pya.DPoint(length + lengthArc, midGround / 2 - ground))
        pts.append(pya.DPoint(length + lengthArc, midGround / 2))
        pts.append(pya.DPoint(0, midGround / 2))

        return pts
    # middle and lower ground plane as polygon, including endcap
    def midLowPoly(length, gap, width, ground, lengthArc, midGround, hdHole, n):
        height = midGround / 2 + 2 * gap + width + ground + hdHole
        pts = []
        pts.append(pya.DPoint(0, -(2 * ground + 4 * gap + 2 * width + midGround) / 2))
        pts.append(pya.DPoint(length, -(2 * ground + 4 * gap + 2 * width + midGround) / 2))
        da = math.pi / (n - 1) / 2
        # lower arc, starting from top
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(hdHole * math.cos(i * da) + length, hdHole * math.sin(i * da) - height))
        pts.append(pya.DPoint(hdHole + ground + length,  -height))
        # upper arc, starting from bottom
        for i in range(0, n):
            pts.append(pya.DPoint((hdHole + ground) * math.cos(i * da) + length, (hdHole + ground) * math.sin(i * da) - height))
        pts.append(pya.DPoint(ground, -(4 * gap + 2 * width + midGround) / 2))
        # end cap
        pts.append(pya.DPoint(ground, -midGround / 2))
        pts.append(pya.DPoint(length, -midGround / 2))
        da = math.pi / (n - 1) / 2
        height = midGround / 2 + 2 * gap + width + ground + hdHole
        r1 = hdHole + ground + 2 * gap + width
        r2 = hdHole + 2 * ground + 2 * gap + width
        # inner arc segment
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(r1 * math.cos(i * da) + length, r1 * math.sin(i * da) - height))
        # outer arc segment, starting from lowest point
        pts.append(pya.DPoint(r2 + length, - height))
        # maximum angle, given size of middle ground plane
        da = np.arcsin((hdHole + 2 * gap + width + midGround) / r2) / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(r2 * math.cos(i * da) + length, r2 * math.sin(i * da) - height))
        pts.append(pya.DPoint(length + lengthArc, midGround / 2 - ground))
        pts.append(pya.DPoint(length + lengthArc, midGround / 2))
        pts.append(pya.DPoint(0, midGround / 2))

        return pts
    # boundary mask for ground cutout as polygon
    def bound(length, gap, width, ground, lengthArc, midGround, hdHole, n):
        height = 2 * gap + width + ground + hdHole + midGround / 2
        pts = []
        pts.append(pya.DPoint(0, -(ground + 2 * gap + width + midGround / 2)))
        pts.append(pya.DPoint(length, -(ground + 2 * gap + width + midGround / 2)))
        # arc 1, starting from top, full 90 degree
        da = math.pi / (n - 1) / 2
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(hdHole * math.cos(i * da) + length, hdHole * math.sin(i * da) - height))
        pts.append(pya.DPoint(length + hdHole + ground, -height))
        pts.append(pya.DPoint(length + hdHole + 2 * ground + 2 * gap + width, -height))
        # arc 2, stating at bottom, up to groundplane
        r = hdHole + 2 * ground + 2 * gap + width
        da = np.arcsin((hdHole + 2 * gap + width + midGround) / r) / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(r * math.cos(i * da) + length, r * math.sin(i * da) - height))
        pts.append(pya.DPoint(length + lengthArc, - height + (hdHole + 2 * gap + width + midGround)))
        pts.append(pya.DPoint(length + lengthArc, 2 * gap + ground + width + midGround / 2))
        pts.append(pya.DPoint(0, 2 * gap + ground + width + midGround / 2))

        return pts
    # boundary mask for additional boundary mask as polygon
    def bound2(length, gap, width, ground, lengthArc, midGround, hdHole, n):
        height = 2 * gap + width + ground + hdHole + midGround / 2
        pts = []
        pts.append(pya.DPoint(0, - height + (hdHole + 2 * gap + width + midGround + ground / 2)))
        pts.append(pya.DPoint(ground / 2, - height + (hdHole + 2 * gap + width + midGround + ground / 2)))
        pts.append(pya.DPoint(ground / 2, -(ground / 2 + 2 * gap + width + midGround / 2)))
        pts.append(pya.DPoint(length, -(ground / 2 + 2 * gap + width + midGround / 2)))
        # arc 1, starting from top, full 90 degree
        da = math.pi / (n - 1) / 2
        r = (hdHole + ground / 2)
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(r * math.cos(i * da) + length, r * math.sin(i * da) - height))
        pts.append(pya.DPoint(length + hdHole + ground, -height))
        pts.append(pya.DPoint(length + hdHole + ground + 2 * gap + width, -height))
        # arc 2, stating at bottom, up to groundplane
        r = hdHole + 3 * ground / 2 + 2 * gap + width
        da = np.arcsin((hdHole + 2 * gap + width + midGround + ground / 2) / r) / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(r * math.cos(i * da) + length, r * math.sin(i * da) - height))
        pts.append(pya.DPoint(length + lengthArc, - height + (hdHole + 2 * gap + width + midGround + ground / 2)))
        pts.append(pya.DPoint(length + lengthArc, 2 * gap + ground / 2 + width + midGround / 2))
        pts.append(pya.DPoint(0, 2 * gap + ground / 2 + width + midGround / 2))

        return pts
    # create mask for dense hole pattern - lower bit as polygon
    def lHole(length, gap, width, ground, midGround, hdHole, n):
        height = 2 * gap + width + ground + hdHole + midGround / 2
        pts = []
        pts.append(pya.DPoint(0, -height))
        pts.append(pya.DPoint(length + hdHole, -height))
        da = math.pi / (n - 1) / 2
        # arc, starting from bottom
        for i in range(0, n):
            pts.append(pya.DPoint(hdHole * math.cos(i * da) + length, hdHole * math.sin(i * da) - height))
        pts.append(pya.DPoint(0, -height + hdHole))

        return pts
    # final hdHole pattern as Polygon
    def hdPoly(length, gap, width, ground, lengthArc, midGround, hdHole, n):
        # Polygon defining the middle groundplane
        height = midGround / 2 + 2 * gap + width + ground + hdHole
        r2 = hdHole + 2 * ground + 2 * gap + width
        pts = []
        pts.append(pya.DPoint(length + lengthArc - hdHole, - height))
        pts.append(pya.DPoint(length + lengthArc, - height))
        pts.append(pya.DPoint(length + lengthArc, - height + (hdHole + 2 * gap + width + midGround)))
        # maximum angle, given size of middle ground plane
        da = np.arcsin((hdHole + 2 * gap + width + midGround) / r2) / (n - 1)
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(r2 * math.cos(i * da) + length, r2 * math.sin(i * da) - height))

        return pts

    # lower centre conductor
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Polygon(lcentre(length, gap, width, ground, lengthArc, midGround, hdHole, n)).transformed(allTrans * shiftEnd))
    # middle and lower ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Polygon(midLowPoly(length + lengthEnd, gap, width, ground, lengthArc, midGround, hdHole, n)).transformed(allTrans))
    # centre conductor, upper cpw
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, (gap + midGround / 2), length + lengthArc + lengthEnd, (gap + width + midGround / 2)).transformed(allTrans))
    # upper ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, 2 * gap + width + midGround / 2, length + lengthArc + lengthEnd, 2 * gap + width + ground + midGround / 2).transformed(allTrans))

    # boundary of groundplane cutout
    obj.cell.shapes(obj.layout.layer(10, 0)).insert(
        pya.Polygon(bound(length + lengthEnd, gap, width, ground, lengthArc, midGround, hdHole, n)).transformed(allTrans))

    # additional boundary mask for burried structures
    obj.cell.shapes(obj.layout.layer(120, 0)).insert(
        pya.Polygon(bound2(length + lengthEnd, gap, width, ground, lengthArc, midGround, hdHole, n)).transformed(allTrans))

    # lower hd hole
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Polygon(lHole(length + lengthEnd, gap, width, ground, midGround, hdHole, n)).transformed(allTrans))
    # upper
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Box(0, (2 * ground + 4 * gap + 2 * width + midGround) / 2, length + lengthArc + lengthEnd, (2 * ground + 4 * gap + 2 * width + midGround) / 2 + hdHole).transformed(allTrans))
    # final hd Hole piece
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Polygon(hdPoly(length + lengthEnd, gap, width, ground, lengthArc, midGround, hdHole, n)).transformed(allTrans))

    # return final point of upper cpw - and final point of lower cpw
    p1 = (shifttopos * trans).trans(pya.DPoint(length + lengthEnd + lengthArc, (2 * gap + midGround + width) / 2))
    p2 = (shifttopos * trans).trans(pya.DPoint(length + lengthEnd + lengthArc -(hdHole + ground + gap + width / 2),
                                                # (2 * gap + midGround + width) / 2 - (hdHole + ground + midGround + 3 * gap + 2 * width)))
                                                -(2 * gap + midGround / 2 + hdHole + ground + width)))
    resPoints = {'cpw': p1, 'res': p2}
    # dx = -(hdHole + ground + gap + width / 2), dy = -(hdHole + ground + midGround + 3 * gap + 3/2 * width)
    return resPoints


def create_cpw_indcoupler(obj, length, ground, width, gap, n, hdHole, initial_point, orientation, mirror):
    # inductive coupling element for two cpws  - hardcoded layers for each part
    if orientation == 0:  # horizontal to right
        trans = pya.ICplxTrans(1, 0, False, 0, 0)
    elif orientation == 1:  # vertical to top
        trans = pya.ICplxTrans(1, 90, False, 0, 0)
    elif orientation == 2:  # horizontal to left
        trans = pya.ICplxTrans(1, 180, False, 0, 0)
    else:  # vertical to bottom
        trans = pya.ICplxTrans(1, 270, False, 0, 0)

    if mirror:
        mirroralongx = pya.ICplxTrans.M0
    else:
        mirroralongx = pya.ICplxTrans.R0

    shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)

    allTrans = shifttopos * mirroralongx * trans

    # length of arc in x/y-plane
    lengthArc = 2 * ground + 2 * gap + width + 2 * hdHole
    # shift in initial point for arc segments
    # shiftArc = pya.ICplxTrans(1, 0, False, length + lengthEnd, -(2 * ground + 4 * gap + 2 * width + midGround) / 2 - hdHole)

    # centre conductor as Polygon
    def centre(length, gap, width, ground, lengthArc, hdHole, n):
        pts = [pya.DPoint(0, width / 2), pya.DPoint(length + 2 * lengthArc, width / 2), pya.DPoint(length + 2 * lengthArc, -width / 2)]
        # right arc, upper line
        r1 = hdHole + ground + gap + width
        da1 = np.arcsin((r1 - width) / r1) / (n - 1)
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc + length + r1 * math.cos(i * da1), width / 2 - r1 + r1 * math.sin(i * da1)))
        # right arc, lower line
        r = hdHole + ground + gap
        da = math.pi / 2 / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        # left arc, lower line
        for i in range(n-1, -1, -1):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        # left arc, upper line
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc - r1 * math.cos(i * da1), width / 2 - r1 + r1 * math.sin(i * da1)))
        pts.append(pya.DPoint(0, -width / 2))

        return pts
    # left lower ground as Polygon
    def lground(length, gap, width, ground, lengthArc, hdHole, n):
        pts = [pya.DPoint(0, -width / 2 - gap)]
        r1 = hdHole + ground + gap + width
        # lower arc
        r = hdHole + ground + 2 * gap + width
        da = np.arcsin((r - width - 2 * gap) / r) / (n - 1)
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        # upper arc
        r = hdHole + 2 * ground + 2 * gap + width
        da = np.arcsin((r - width - 2 * gap - 2 * ground) / r) / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        pts.append(pya.DPoint(0, -width / 2 - gap - ground))

        return pts
    # right lower ground as Polygon
    def rground(length, gap, width, ground, lengthArc, hdHole, n):
        pts = [pya.DPoint(length + 2 * lengthArc, -width / 2 - gap)]
        r1 = hdHole + ground + gap + width
        # inner arc
        r = hdHole + ground + 2 * gap + width
        da = np.arcsin((r - width - 2 * gap) / r) / (n - 1)
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        # outer arc
        r = hdHole + 2 * ground + 2 * gap + width
        da = np.arcsin((r - width - 2 * gap - 2 * ground) / r) / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        pts.append(pya.DPoint(length + 2 * lengthArc, -width / 2 - gap - ground))

        return pts
    # mid lower ground as Polygon
    def mground(length, gap, width, ground, lengthArc, hdHole, n):
        pts = []
        r1 = hdHole + ground + gap + width
        # left arc
        r = hdHole + ground
        da = math.pi / 2 / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        # upper arc
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        # lower arcs
        r = hdHole
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))

        return pts
    # ground cutout as Polygon
    def cutout(length, gap, width, ground, lengthArc, hdHole, n):
        pts = [pya.DPoint(0, -(width / 2 + gap + ground)), pya.DPoint(0, width / 2 + gap + ground),
                pya.DPoint(length + 2 * lengthArc, width / 2 + gap + ground), pya.DPoint(length + 2 * lengthArc, -(width / 2 + gap + ground))]
        r1 = hdHole + ground + gap + width
        # left lower, outer arc
        r = hdHole + 2 * ground + 2 * gap + width
        da = np.arcsin((r - width - 2 * gap - 2 * ground) / r) / (n - 1)
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        # lower, inner arcs
        r = hdHole
        da = math.pi / 2 / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        # right lower, counter arc
        r = hdHole + 2 * ground + 2 * gap + width
        da = np.arcsin((r - width - 2 * gap - 2 * ground) / r) / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))

        return pts
    # second ground cutout as Polygon - for buried structures
    def cutout2(length, gap, width, ground, lengthArc, hdHole, n):
        pts = [pya.DPoint(0, -(width / 2 + gap + ground / 2)), pya.DPoint(0, width / 2 + gap + ground / 2),
                pya.DPoint(length + 2 * lengthArc, width / 2 + gap + ground / 2), pya.DPoint(length + 2 * lengthArc, -(width / 2 + gap + ground / 2))]
        r1 = hdHole + ground + gap + width
        # left lower, outer arc
        r = hdHole + 3 * ground / 2 + 2 * gap + width
        da = np.arcsin((r - width - 2 * gap - ground) / r) / (n - 1)
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        # lower, inner arcs
        r = hdHole + ground / 2
        da = math.pi / 2 / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        # right lower, counter arc
        r = hdHole + 3 * ground / 2 + 2 * gap + width
        da = np.arcsin((r - width - 2 * gap - ground) / r) / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))

        return pts
    # mid hd Hole as Polygon
    def mHD(length, gap, width, ground, lengthArc, hdHole, n):
        pts = []
        r1 = hdHole + ground + gap + width
        # upper arc
        r = hdHole
        da = math.pi / 2 / (n - 1)
        for i in range(0, n):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))

        return pts
    # right hd Hole as Polygon
    def rHD(length, gap, width, ground, lengthArc, hdHole, n):
        pts = [pya.DPoint(length + 2 * lengthArc, -width / 2 - gap - ground)]
        r1 = hdHole + ground + gap + width
        # arc
        r = hdHole + 2 * ground + 2 * gap + width
        da = np.arcsin((r - width - 2 * gap - 2 * ground) / r) / (n - 1)
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc + length + r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        pts.append(pya.DPoint(length + 2 * lengthArc, -width / 2 - gap - ground - hdHole))

        return pts
    # left hd Hole as Polygon
    def lHD(length, gap, width, ground, lengthArc, hdHole, n):
        pts = [pya.DPoint(0, -width / 2 - gap - ground)]
        r1 = hdHole + ground + gap + width
        # upper arc
        r = hdHole + 2 * ground + 2 * gap + width
        da = np.arcsin((r - width - 2 * gap - 2 * ground) / r) / (n - 1)
        for i in range(n - 1, -1, -1):
            pts.append(pya.DPoint(lengthArc - r * math.cos(i * da), width / 2 - r1 + r * math.sin(i * da)))
        pts.append(pya.DPoint(0, -width / 2 - gap - ground - hdHole))

        return pts

    # upper ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Box(0, width / 2 + gap, length + 2 * lengthArc, width / 2 + gap + ground).transformed(allTrans))
    # centre conductor
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Polygon(centre(length, gap, width, ground, lengthArc, hdHole, n)).transformed(allTrans))
    # lower ground plane - left bit
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Polygon(lground(length, gap, width, ground, lengthArc, hdHole, n)).transformed(allTrans))
    # lower ground plane - right bit - same as left but transformed
    # lrTrans = pya.ICplxTrans.M90 * pya.ICplxTrans(1, 0, False, length + 2 * lengthArc, 0)
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Polygon(rground(length, gap, width, ground, lengthArc, hdHole, n)).transformed(allTrans))
    # middle ground plane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(
        pya.Polygon(mground(length, gap, width, ground, lengthArc, hdHole, n)).transformed(allTrans))
    # ground cutout
    obj.cell.shapes(obj.layout.layer(10, 0)).insert(
        pya.Polygon(cutout(length, gap, width, ground, lengthArc, hdHole, n)).transformed(allTrans))

    # additional boundary mask for burried structures
    obj.cell.shapes(obj.layout.layer(120, 0)).insert(
        pya.Polygon(cutout2(length, gap, width, ground, lengthArc, hdHole, n)).transformed(allTrans))

    # upper hd hole plane
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Box(0, width / 2 + gap + ground, length + 2 * lengthArc, width / 2 + gap + ground + hdHole).transformed(allTrans))
    # lower, middle hd hole plane
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Polygon(mHD(length, gap, width, ground, lengthArc, hdHole, n)).transformed(allTrans))
    # lower, right hd hole plane
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Polygon(rHD(length, gap, width, ground, lengthArc, hdHole, n)).transformed(allTrans))
    # lower, left hd hole plane
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(
        pya.Polygon(lHD(length, gap, width, ground, lengthArc, hdHole, n)).transformed(allTrans))

    # return final point of upper cpw - plus both endpoints of lower cpw
    p1 = allTrans.trans(pya.DPoint(length + 2 * lengthArc, 0))
    p2 = allTrans.trans(pya.DPoint(hdHole + ground + gap + width /2, -(hdHole + ground + gap + width / 2)))
    p3 = allTrans.trans(pya.DPoint(length + lengthArc + hdHole + ground + gap + width /2, -(hdHole + ground + gap + width / 2)))
    endPoints = {'cpw': p1, 'res0': p2, 'res1': p3}
    # # dx = -(hdHole + ground + gap + width / 2), dy = -(hdHole + ground + midGround + 3 * gap + 3/2 * width)
    return endPoints


def create_cpw_S(obj, ground, width, gap, hdHole, ioff, vStart, initial_point, dx, dy):
    # determine shape
    if dx > 0 and dy > 0:  # going right and up
        straights = [0, 1]
        bends = ['rt', 'tr']
    elif dx > 0 and dy < 0:  # going right and down
        straights = [0, 3]
        bends = ['rb', 'br']
    elif dx < 0 and dy > 0:  # going left and up
        straights = [2, 1]
        bends = ['lb', 'bl']
    elif dx < 0 and dy < 0:  # going left and down
        straights = [2, 3]
        bends = ['tl', 'lt']

    # vertical start: switch orientation order (first up / down then right / left)
    if vStart:
        straights = [straights[1], straights[0]]
        bends = [bends[1], bends[0]]

    # define intermediate variables for calculation
    radius = hdHole + ground + gap + width / 2  # radius of arc
    bendLength = math.pi * radius / 2  # cpw length in single arc
    arcSize = 2 * (hdHole + gap + ground) + width  # size of arc (x,y)
    # check that total width is sufficient for bends, if not force
    if math.fabs(dy) < 2 * arcSize:
        # end_point.y = initial_point.y + 2 * arcSize
        dy = np.sign(dy) * 2 * arcSize
    if math.fabs(dx) < 2 * arcSize:
        # end_point.x = initial_point.x + 2 * arcSize
        dx = np.sign(dx) * 2 * arcSize
    # check that offset is not too large
    if ioff > math.fabs(dx) - arcSize:
        ioff = math.fabs(dx) - arcSize
    endLength = math.fabs(dx) - arcSize - ioff

    # create the sequence of shapes
    segs = []
    obj.length = 0
    # initial straight bit, going right
    segs.append({'type': "cpw_straight", 'ln': ioff, 'orientation': straights[0]})
    obj.length += ioff
    segs.append({'type': "cpw_90", 'orientation': bends[0]})
    obj.length += bendLength
    segs.append({'type': "cpw_straight", 'ln': math.fabs(dy) - arcSize, 'orientation': straights[1]})
    obj.length += dy - arcSize
    segs.append({'type': "cpw_90", 'orientation': bends[1]})
    obj.length += bendLength
    if endLength > 0:
        segs.append({'type': "cpw_straight", 'ln': endLength, 'orientation': straights[0]})
        obj.length += endLength

    # create the shape
    curr_point = pya.DPoint(initial_point.x, initial_point.y)
    for elem in segs:
        if elem['type'] == "cpw_90":
            curr_point = create_cpw_90(obj, ground, gap, width, obj.n, hdHole, curr_point, elem['orientation'], False)
        elif elem['type'] == "cpw_straight":
            curr_point = create_cpw_straight(obj, elem['ln'], ground, width, gap, hdHole, curr_point, elem['orientation'], False)

    return curr_point


def create_cpw_meander(obj, ground, width, gap, hdHole, widthTot, lengthTot, initStraight, initDown, endGap, initial_point=pya.DPoint(0, 0), orientation=0, mirror=False, fingers=0, fingerLength=26, fingerEndGap=8, hookWidth=5, hookLength=3, hookUnit=1, holeLength=1):
    # create simple meander resonator, given total length and width of meander structure

    # coordinate transformation of initial points
    shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)

    if orientation == 0:  # horizontal to right, first meander going down
        straights = [0, 3, 1]
        bends = [['rb', 'br'], ['rt', 'tr']]
        # trans = pya.ICplxTrans(1, 0, False, 0, 0)
    elif orientation == 1:  # vertical to top, first meander going right
        straights = [1, 2, 0]
        bends = [['tr', 'rt'], ['bl', 'lb']]
        # trans = pya.ICplxTrans(1, 90, False, 0, 0)
    elif orientation == 2:  # horizontal to left, first meander going up
        straights = [2, 3, 1]
        bends = [['lb', 'bl'], ['tl', 'lt']]
        # trans = pya.ICplxTrans(1, 180, False, 0, 0)
    else:  # vertical to bottom, first meander going left
        straights = [3, 2, 0]
        bends = [['lt', 'tl'], ['br', 'rb']]
        # trans = pya.ICplxTrans(1, 270, False, 0, 0)

    # mirroring changes order of elements
    if mirror:
        straights = [straights[0], straights[2], straights[1]]
        bends = [bends[1], bends[0]]

    # define intermediate variables for calculation
    radius = hdHole + ground + gap + width / 2  # radius of arc
    bendLength = math.pi * radius / 2  # cpw length in single arc
    arcSize = 2 * (hdHole + gap + ground) + width  # size of arc (x,y)
    # some sanity checks for geometry
    if initDown > 0:  # initial counter bend defined
        # check that total width is sufficient for bends, if not force
        if widthTot < 3 * arcSize:
            widthTot = 3 * arcSize
        if arcSize > initDown:  # check that initial counter bend has minimal possible size permitted by arcsize
            initDown = arcSize
        downStraight = initDown - arcSize  # straight length of initial counter bend
        downLength = downStraight + 2 * bendLength  # total cpw length of intial counter bend
    else:  # no counter bend
        # check that total width is sufficient for bends, if not force
        if widthTot < 2 * arcSize:
            widthTot = 2 * arcSize
        downStraight = 0
        downLength = 0
    # calculate number of meanders
    meanderStraight = widthTot - 2 * arcSize  # straight length of single meander
    meanderLength = 2 * bendLength + meanderStraight  # total cpw length of single meander
    obj.numMeander = int(math.floor((lengthTot - initStraight - downLength) / meanderLength))  # number of full meanders
    lengthEnd = lengthTot - initStraight - downLength - (obj.numMeander * meanderLength)  # length of end piece
    numEven = (obj.numMeander % 2 == 0)  # even number of meanders?
    # create the sequence of shapes
    segs = []
    # obj.calclen_dbu = 0
    obj.calclen = 0
    # initial straight bit, going right
    if initStraight > lengthTot:  # initial offset longer than total length - add straight bit, end cap, nothing else
        segs.append({'type': "cpw_straight_fingers", 'ln': lengthTot, 'orientation': straights[0]})
        obj.calclen += lengthTot
        segs.append({'type': 'cpw_end', 'orientation': straights[0]})
    else:  # full straight bit plus meanders
        segs.append({'type': "cpw_straight_fingers", 'ln': initStraight, 'orientation': straights[0]})
        obj.calclen += initStraight
        if initDown > 0:  # first partial meander going down instead of up
            segs.append({'type': 'cpw_90', 'orientation': bends[1][0]})
            segs.append({'type': "cpw_straight", 'ln': downStraight, 'orientation': straights[2]})
            segs.append({'type': 'cpw_90', 'orientation': bends[1][1]})
            obj.calclen += downLength
        # iterate over all meanders
        for it in range(0, obj.numMeander):
            if it % 2 == 0 or it == 0:  # even iterators - meander going up
                segs.append({'type': 'cpw_90', 'orientation': bends[0][0]})
                segs.append({'type': "cpw_straight", 'ln': meanderStraight, 'orientation': straights[1]})
                segs.append({'type': 'cpw_90', 'orientation': bends[0][1]})
                obj.calclen += meanderLength
            else:  # odd iterators - meander going down
                segs.append({'type': 'cpw_90', 'orientation': bends[1][0]})
                segs.append({'type': "cpw_straight", 'ln': meanderStraight, 'orientation': straights[2]})
                segs.append({'type': 'cpw_90', 'orientation': bends[1][1]})
                obj.calclen += meanderLength

        if lengthEnd >= bendLength:  # one more bend plus a straight bit
            lengthRest = lengthEnd - bendLength
            if numEven:  # even number of meanders - last bit goes up
                segs.append({'type': 'cpw_90', 'orientation': bends[0][0]})
                segs.append({'type': "cpw_straight", 'ln': lengthRest, 'orientation': straights[1]})
                obj.calclen += lengthRest + bendLength
            else:  # odd number of meanders - last bit goes down
                segs.append({'type': 'cpw_90', 'orientation': bends[1][0]})
                segs.append({'type': "cpw_straight", 'ln': lengthRest, 'orientation': straights[2]})
                obj.calclen += lengthRest + bendLength
        elif lengthEnd > 0:  # only bend - total length might be bit too long
            if numEven:  # even number of meanders - last bit goes up
                segs.append({'type': 'cpw_90', 'orientation': bends[0][0]})
                obj.calclen += bendLength
            else:  # odd number of meanders - last bit goes down
                segs.append({'type': 'cpw_90', 'orientation': bends[1][0]})
                obj.calclen += bendLength
        if numEven:  # add end capacitor, going up
            segs.append({'type': 'cpw_end', 'orientation': straights[1]})
        else:  # going down
            segs.append({'type': 'cpw_end', 'orientation': straights[2]})

    # create the shape
    curr_point = shifttopos.trans(pya.DPoint(0, 0))
    for elem in segs:
        if elem['type'] == "cpw_90":
            curr_point = create_cpw_90(obj, ground, gap, width, obj.n, hdHole, curr_point, elem['orientation'], False)
        elif elem['type'] == "cpw_straight":
            curr_point = create_cpw_straight(obj, elem['ln'], ground, width, gap, hdHole, curr_point, elem['orientation'], False)
        elif elem['type'] == "cpw_straight_fingers":
            curr_point = create_cpw_straight_fingers(obj, elem['ln'], ground, width, gap, hdHole, curr_point, elem['orientation'], False, fingers, fingerLength, fingerEndGap, hookWidth, hookLength, hookUnit, holeLength)
        elif elem['type']== "cpw_end":
            curr_point = create_cpw_end(obj, 0, ground, width, gap, endGap, hdHole, curr_point, elem['orientation'], False)

    # return end point of resonator cpw
    return curr_point


def create_cpw_port(obj, widthPort, groundPort, gapPort, widthCPW, groundCPW, gapCPW, taperLength, padSize, hole, initial_point, orientation, mirror):

    # global transformations
    if orientation == 0:  # horizontal to left
        trans = pya.ICplxTrans(1, 0, False, 0, 0)
    elif orientation == 1:  # vertical to top
        trans = pya.ICplxTrans(1, 90, False, 0, 0)
    elif orientation == 2:  # horizontal to right
        trans = pya.ICplxTrans(1, 180, False, 0, 0)
    else:  # vertical to bottom
        trans = pya.ICplxTrans(1, 270, False, 0, 0)

    shifttopos = pya.ICplxTrans(1, 0, False, initial_point.x, initial_point.y)

    if mirror:
        mirroralongx = pya.ICplxTrans.M0
    else:
        mirroralongx = pya.ICplxTrans.R0

    allTrans = shifttopos * mirroralongx * trans

    # create shape
    # centre conductor
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Polygon([
            pya.DPoint(0, widthCPW / 2),
            pya.DPoint(-taperLength, widthPort / 2),
            pya.DPoint(-(taperLength + padSize), widthPort / 2),
            pya.DPoint(-(taperLength + padSize), -widthPort / 2),
            pya.DPoint(-taperLength, -widthPort / 2),
            pya.DPoint(0, -widthCPW / 2),]).transformed(allTrans))

    # groundplane
    obj.cell.shapes(obj.layout.layer(1, 0)).insert(pya.Polygon([
        pya.DPoint(0, gapCPW + widthCPW / 2), pya.DPoint(-taperLength, gapPort + widthPort / 2),
        pya.DPoint(-(taperLength + padSize + gapPort), gapPort + widthPort / 2), pya.DPoint(-(taperLength + padSize + gapPort), -(gapPort + widthPort / 2)),
        pya.DPoint(-taperLength, -(gapPort + widthPort / 2)), pya.DPoint(0, -(gapCPW + widthCPW / 2)),
        pya.DPoint(0, -(groundCPW + gapCPW + widthCPW / 2)), pya.DPoint(-taperLength, -(groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-(taperLength + padSize + gapPort + groundPort), -(groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-(taperLength + padSize + gapPort + groundPort), (groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-taperLength, (groundPort + gapPort + widthPort / 2)),
        pya.DPoint(0, (groundCPW + gapCPW + widthCPW / 2))]).transformed(allTrans))

    # cutout mask
    obj.cell.shapes(obj.layout.layer(10, 0)).insert(pya.Polygon([
        pya.DPoint(0, -(groundCPW + gapCPW + widthCPW / 2)), pya.DPoint(-taperLength, -(groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-(taperLength + padSize + gapPort + groundPort), -(groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-(taperLength + padSize + gapPort + groundPort), (groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-taperLength, (groundPort + gapPort + widthPort / 2)),
        pya.DPoint(0, (groundCPW + gapCPW + widthCPW / 2))]).transformed(allTrans))

    # additional cutout mask for buried structures
    obj.cell.shapes(obj.layout.layer(120, 0)).insert(pya.Polygon([
        pya.DPoint(0, -(groundCPW / 2 + gapCPW + widthCPW / 2)), pya.DPoint(-taperLength, -(groundPort / 2 + gapPort + widthPort / 2)),
        pya.DPoint(-(taperLength + padSize + gapPort + groundPort / 2), -(groundPort / 2 + gapPort + widthPort / 2)),
        pya.DPoint(-(taperLength + padSize + gapPort + groundPort / 2 ), (groundPort / 2 + gapPort + widthPort / 2)),
        pya.DPoint(-taperLength, (groundPort / 2 + gapPort + widthPort / 2)),
        pya.DPoint(0, (groundCPW / 2 + gapCPW + widthCPW / 2))]).transformed(allTrans))

    # hd Hole pattern
    obj.cell.shapes(obj.layout.layer(11, 0)).insert(pya.Polygon([
        pya.DPoint(0, -(groundCPW + gapCPW + widthCPW / 2)), pya.DPoint(-taperLength, -(groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-(taperLength + padSize + gapPort + groundPort), -(groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-(taperLength + padSize + gapPort + groundPort), (groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-taperLength, (groundPort + gapPort + widthPort / 2)),
        pya.DPoint(0, (groundCPW + gapCPW + widthCPW / 2)),
        pya.DPoint(0, (hole + groundCPW + gapCPW + widthCPW / 2)), pya.DPoint(-taperLength, (hole + groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-(hole + taperLength + padSize + gapPort + groundPort), (hole + groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-(hole + taperLength + padSize + gapPort + groundPort), -(hole + groundPort + gapPort + widthPort / 2)),
        pya.DPoint(-taperLength, -(hole + groundPort + gapPort + widthPort / 2)),
        pya.DPoint(0, -(hole + groundCPW + gapCPW + widthCPW / 2))]).transformed(allTrans))

    # return end point of resonator cpw
    return allTrans.trans(pya.DPoint(0, 0))
