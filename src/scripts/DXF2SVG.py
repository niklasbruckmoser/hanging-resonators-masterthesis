"""
Helper script that transforms DXF files to SVG, mainly for graphical output of designs and further use in image
processing programs. Only supports polyline entities.
Code mainly based on https://bitbucket.org/lukaszlaba/dxf2svg.
"""

import os
from math import sqrt, sin, cos, pi

import ezdxf
import svgwrite

LAYER = 'svgframe'
SVG_MAXSIZE = 300
SCALE = 1.0


def get_dxf_dwg_from_file(dxffilepath):
    return ezdxf.readfile(dxffilepath)


def get_clear_svg(minx=43.5, miny=-135.6, width=130.1, height=105.2):
    svg = svgwrite.Drawing(size = (SVG_MAXSIZE, SVG_MAXSIZE), viewBox="%s %s %s %s"%(minx, miny, width, height))
    return svg


def get_empty_svg(alerttext='Nothing to show!'):
    svg = svgwrite.Drawing(size = (SVG_MAXSIZE, SVG_MAXSIZE), viewBox="0 0 %s %s"%(SVG_MAXSIZE, SVG_MAXSIZE))
    svg.add(svgwrite.Drawing().text(alerttext, insert=[50, 50], font_size = 20))
    return svg


def trans_polyline(dxf_entity):
    points = [(x[0], x[1]) for x in dxf_entity.points()]
    if dxf_entity.CLOSED == 1:
        svg_entity = svgwrite.Drawing().polygon(points=points, stroke='black', fill='none', stroke_width=1.0/SCALE)
    else:
        svg_entity = svgwrite.Drawing().polyline(points=points, stroke='black', fill='none', stroke_width=1.0/SCALE)
    svg_entity.scale(SCALE, -SCALE)
    return svg_entity


def entity_filter(dxffilepath, frame_name=None):
    dxf = get_dxf_dwg_from_file(dxffilepath)

    frame_rect_entity = None
    name_text_entity = None

    if frame_name:
        for e in dxf.modelspace():
            if e.dxftype() == 'TEXT' and e.dxf.layer == LAYER:
                if e.dxf.text == frame_name:
                    name_text_entity = e
    if name_text_entity:
        text_point = name_text_entity.dxf.insert[:2]
        text_height = name_text_entity.dxf.height
        for e in dxf.modelspace():
            if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == LAYER:
                points = list(e.get_rstrip_points())
                for p in points:
                    dist = sqrt((p[0] - text_point[0])**2+(p[1] - text_point[1])**2)
                    if dist < 1.0 * text_height:
                        frame_rect_entity = e

    if frame_rect_entity and name_text_entity:
        frame_points = list(frame_rect_entity.get_rstrip_points())
        entitys_in_frame = []
        xmin = min([i[0] for i in frame_points])
        xmax = max([i[0] for i in frame_points])
        ymin = min([i[1] for i in frame_points])
        ymax = max([i[1] for i in frame_points])
        for e in dxf.modelspace():
            point = None
            if e.dxftype() == 'LINE': point = e.dxf.start[:2]
            if e.dxftype() == 'CIRCLE': point = e.dxf.center[:2]
            if e.dxftype() == 'TEXT': point = e.dxf.insert[:2]
            if e.dxftype() == 'ARC':
                center = e.dxf.center[:2]
                radius = e.dxf.radius
                start_angle = e.dxf.start_angle/ 360.0 * 2 * pi
                delta_x = radius * cos(start_angle)
                delta_y = radius * sin(start_angle)
                point = (center[0]+delta_x, center[1]+delta_y)
            if point:
                if (xmin <= point[0] <= xmax) and (ymin <= point[1] <= ymax):
                    if not e.dxf.layer == LAYER:
                        entitys_in_frame.append(e)
        return entitys_in_frame, [xmin, xmax, ymin, ymax]
    elif frame_name:
        return [], [300, 600, 300, 600]
    elif not frame_name:
        entitys = []
        xmin = 0
        xmax = 0
        ymin = 0
        ymax = 0
        for e in dxf.modelspace():
            if not e.dxf.layer == LAYER:
                entitys.append(e)
                if e.dxftype() == 'LINE':
                    xmin = min(xmin, e.dxf.start[0], e.dxf.end[0])
                    xmax = max(xmax, e.dxf.start[0], e.dxf.end[0])
                    ymin = min(ymin, e.dxf.start[1], e.dxf.end[1])
                    ymax = max(ymax,  e.dxf.start[1], e.dxf.end[1])
                if e.dxftype() == 'CIRCLE':
                    e.dxf.center[:2]
                    e.dxf.radius
                    xmin = min(xmin, e.dxf.center[0] - e.dxf.radius)
                    xmax = max(xmax, e.dxf.center[0] + e.dxf.radius)
                    ymin = min(ymin, e.dxf.center[1] - e.dxf.radius)
                    ymax = max(ymax,  e.dxf.center[1] + e.dxf.radius)
                if e.dxftype() == 'TEXT':
                    xmin = min(xmin, e.dxf.insert[0])
                    xmax = max(xmax, e.dxf.insert[0])
                    ymin = min(ymin, e.dxf.insert[1])
                    ymax = max(ymax,  e.dxf.insert[1])
                if e.dxftype() == 'ARC':
                    center = e.dxf.center[:2]
                    radius = e.dxf.radius
                if e.dxftype() == 'POLYLINE':
                    x = [p[0] for p in e.points()]
                    y = [p[1] for p in e.points()]
                    xmin = min(xmin, min(x))
                    xmax = max(xmax, max(x))
                    ymin = min(xmin, min(y))
                    ymax = max(xmax, max(y))
        xmargin = 0.05*abs(xmax - xmin)
        ymargin = 0.05*abs(ymax - ymin)
        return entitys, [xmin - xmargin, xmax + xmargin, ymin - ymargin, ymax + ymargin]


def get_svg_from_dxf(dxffilepath, frame_name=None):
    global SCALE

    entites_filter = entity_filter(dxffilepath, frame_name)
    entites = entites_filter[0]
    frame_coord = entites_filter[1]

    if not entites:
        return get_empty_svg()

    minx= frame_coord[0]
    miny= -frame_coord[3]
    width= abs(frame_coord[0] - frame_coord[1])
    height=abs(frame_coord[2] - frame_coord[3])
    SCALE = 1.0*SVG_MAXSIZE/max(width, height)

    svg = get_clear_svg(minx*SCALE, miny*SCALE, width*SCALE, height*SCALE)
    for e in entites:
        if e.dxftype() == 'POLYLINE':
            svg.add(trans_polyline(e))
        else:
            print(f"unsupported dxf type {e.dxftype()}!")
    return svg


def save_svg_from_dxf(dxffilepath, svgfilepath=None, frame_name=None, size = 300):
    global SVG_MAXSIZE
    _oldsize = SVG_MAXSIZE
    SVG_MAXSIZE = size
    # if frame_name:
    #     print('>>making %s svgframe for %s ...'%(frame_name, os.path.basename(dxffilepath)))
    # else:
    #     print('Creating svg from %s...'%(os.path.basename(dxffilepath)))
    print(f"Creating SVG from {os.path.basename(dxffilepath)}...")
    svg = get_svg_from_dxf(dxffilepath, frame_name)
    print("...saving SVG...")
    if frame_name: postfix = '_%s'%frame_name
    else: postfix = ''
    if not svgfilepath:
        svgfilepath = dxffilepath.replace('.dxf', '%s.svg'%postfix)
    svg.saveas(svgfilepath)
    print(f"...saved as {os.path.basename(svgfilepath)}")
    # print ('...saved as %s'%os.path.basename(svgfilepath))

    SVG_MAXSIZE = _oldsize


def extract_all(dxffilepath, size = 300):
    dxf = get_dxf_dwg_from_file(dxffilepath)

    frame_list = []
    for e in dxf.modelspace():
        if e.dxftype() == 'TEXT' and e.dxf.layer == LAYER:
            frame_list.append(e.dxf.text)

    if frame_list:
        for frame in frame_list:
            try:
                save_svg_from_dxf(dxffilepath, frame_name = frame, size = size)
            except:
                pass
    else:
        try:
            save_svg_from_dxf(dxffilepath, size = size)
        except:
            pass


if __name__ == "__main__":
    extract_all("/Users/niklas/PycharmProjects/wafers/qr_wafer.dxf")