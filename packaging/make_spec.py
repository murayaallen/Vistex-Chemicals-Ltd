#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dimensioned production drawings - the sheet a toolmaker actually works from.

This is not the artwork plan. The plan shows where the ink goes; this shows
what the die has to cut, dimensioned, at a stated scale, with a title block.
A converter quoting a tool needs the second, and it has to be a drawing
rather than a picture of one.

  Retail carton   A2 landscape, 1:1
  Shipper         A2 landscape, 1:2 (the blank is 1070 mm wide)

Geometry is taken from the build scripts, never retyped - a drawing that
disagrees with the artwork is worse than no drawing. Setting the source
module's ORIGIN to zero makes its own path helpers emit raw millimetres,
which a canvas transform then places and scales.

Run:  python packaging/make_spec.py
"""

import os
from math import pi, cos, sin, atan2

from reportlab.pdfgen import canvas as _cv
from reportlab.lib.colors import CMYKColor

import swift_blue_drop_dieline as B
import swift_shipper as SH
from swift_blue_drop_dieline import (MM, F, register_fonts, ROOT, DIST,
                                     W_GLUE, W_FACE, W_SIDE, H_BODY, H_TUCK,
                                     H_DUST, H_HANG, TAB_W, TAB_CH, SLOT_R,
                                     SLOT_W, SLOT_RISE, SLOT_Y, TAB_HEADROOM,
                                     VENT_N, VENT_H, VENT_GAP, VENT_Y,
                                     SHEET_W, SHEET_H, BLEED, SAFE,
                                     X_GLUE, X_BACK, X_SIDL, X_FRNT, X_SIDR,
                                     Y_BODY, Y_TOP, TAB_X0)

OUT = os.path.join(DIST, "spec")

INK = CMYKColor(0, 0, 0, 1)
THIN = CMYKColor(0, 0, 0, 0.62)
DIMC = CMYKColor(0.85, 0.45, 0, 0.10)       # dimension lines, a cool blue
CUTC = CMYKColor(0, 1, 0, 0)                # cut
CREASEC = CMYKColor(1, 0, 0, 0)             # crease
PAPER = CMYKColor(0, 0, 0, 0.02)

PAGE = (594.0, 420.0)                        # A2 landscape, mm


# ---------------------------------------------------------------------------
# page-space drawing (mm, origin bottom-left of the sheet)
# ---------------------------------------------------------------------------

def p(v):
    return v * MM


def line(c, x1, y1, x2, y2, colour=INK, lw=0.25, dash=None, alpha=1.0):
    c.saveState()
    c.setStrokeColor(colour, alpha)
    c.setLineWidth(lw * MM)
    c.setLineCap(0)
    if dash:
        c.setDash([d * MM for d in dash], 0)
    c.line(p(x1), p(y1), p(x2), p(y2))
    c.restoreState()


def rect(c, x, y, w, h, colour=None, stroke=INK, lw=0.25, alpha=1.0):
    c.saveState()
    if colour is not None:
        c.setFillColor(colour, alpha)
    if stroke is not None:
        c.setStrokeColor(stroke, alpha)
        c.setLineWidth(lw * MM)
    c.rect(p(x), p(y), p(w), p(h), fill=colour is not None,
           stroke=stroke is not None)
    c.restoreState()


def sw(t, f, s):
    from reportlab.pdfbase import pdfmetrics
    return pdfmetrics.stringWidth(t, f, s)


def txt(c, x, y, t, font, size, colour=INK, align="l", track=0.0, rot=0.0):
    w = sw(t, font, size) + track * max(0, len(t) - 1)
    c.saveState()
    c.translate(p(x), p(y))
    if rot:
        c.rotate(rot)
    c.setFillColor(colour)
    off = -(w / 2 if align == "c" else w if align == "r" else 0)
    if track:
        to = c.beginText(off, 0)
        to.setFont(font, size)
        to.setCharSpace(track)
        to.textLine(t)
        to.setCharSpace(0)
        c.drawText(to)
    else:
        c.setFont(font, size)
        c.drawString(off, 0, t)
    c.restoreState()
    return w / MM


def arrow(c, x, y, ang, size=2.2, colour=DIMC):
    c.saveState()
    c.setFillColor(colour)
    pth = c.beginPath()
    pth.moveTo(p(x), p(y))
    pth.lineTo(p(x + size * cos(ang + 0.26)), p(y + size * sin(ang + 0.26)))
    pth.lineTo(p(x + size * cos(ang - 0.26)), p(y + size * sin(ang - 0.26)))
    pth.close()
    c.drawPath(pth, fill=1, stroke=0)
    c.restoreState()


def dim_h(c, x1, x2, y, label=None, ext_from=None, size=5.4, flip=False):
    """Horizontal dimension with extension lines and inward arrows."""
    if ext_from is not None:
        for xx in (x1, x2):
            line(c, xx, ext_from, xx, y + (1.6 if y > ext_from else -1.6),
                 DIMC, 0.18, alpha=0.75)
    line(c, x1, y, x2, y, DIMC, 0.22)
    arrow(c, x1, y, 0.0)
    arrow(c, x2, y, pi)
    t = label if label is not None else ("%g" % round(x2 - x1, 1))
    tw = sw(t, F["bodysemi"], size) / MM
    cx = (x1 + x2) / 2
    c.saveState()
    c.setFillColor(PAPER)
    c.rect(p(cx - tw / 2 - 0.8), p(y - 1.1), p(tw + 1.6), p(size / MM * 0.9),
           fill=1, stroke=0)
    c.restoreState()
    txt(c, cx, y - 0.6, t, F["bodysemi"], size, DIMC, "c")


def dim_v(c, y1, y2, x, label=None, ext_from=None, size=5.4):
    if ext_from is not None:
        for yy in (y1, y2):
            line(c, ext_from, yy, x + (1.6 if x > ext_from else -1.6), yy,
                 DIMC, 0.18, alpha=0.75)
    line(c, x, y1, x, y2, DIMC, 0.22)
    arrow(c, x, y1, pi / 2)
    arrow(c, x, y2, -pi / 2)
    t = label if label is not None else ("%g" % round(y2 - y1, 1))
    tw = sw(t, F["bodysemi"], size) / MM
    cy = (y1 + y2) / 2
    c.saveState()
    c.setFillColor(PAPER)
    c.rect(p(x - size / MM * 0.55), p(cy - tw / 2 - 0.8),
           p(size / MM * 0.95), p(tw + 1.6), fill=1, stroke=0)
    c.restoreState()
    txt(c, x - 0.6, cy, t, F["bodysemi"], size, DIMC, "c", rot=90)


def leader(c, x1, y1, x2, y2, text, size=5.2, align="l"):
    """Leader with a shoulder. The arrow points back along the line at the
    thing being called out - the first version computed its angle from an
    expression that always evaluated to zero, so every arrowhead faced left."""
    tail = 7.0 if align == "l" else -7.0
    line(c, x1, y1, x2, y2, DIMC, 0.2)
    line(c, x2, y2, x2 + tail, y2, DIMC, 0.2)
    arrow(c, x1, y1, atan2(y2 - y1, x2 - x1) + pi, size=2.0)
    txt(c, x2 + tail + (1.0 if align == "l" else -1.0), y2 - 0.9, text,
        F["body"], size, INK, "l" if align == "l" else "r")


# ---------------------------------------------------------------------------
# title block - what makes it a drawing rather than a picture
# ---------------------------------------------------------------------------

def title_block(c, x, y, w, h, rows, title, sub):
    rect(c, x, y, w, h, None, INK, 0.35)
    line(c, x, y + h - 11, x + w, y + h - 11, INK, 0.35)
    txt(c, x + 3, y + h - 7.6, title, F["head"], 9.5)
    txt(c, x + w - 3, y + h - 7.6, sub, F["bodysemi"], 7, THIN, "r")
    colw = w / 2
    rh = (h - 11) / ((len(rows) + 1) // 2)
    for i, (k, v) in enumerate(rows):
        cx = x + (i % 2) * colw
        cy = y + h - 11 - (i // 2 + 1) * rh
        line(c, cx, cy, cx + colw, cy, INK, 0.18, alpha=0.5)
        txt(c, cx + 3, cy + rh * 0.34, k, F["bodysemi"], 5.4, THIN)
        txt(c, cx + 26, cy + rh * 0.34, v, F["body"], 6.0)
    line(c, x + colw, y, x + colw, y + h - 11, INK, 0.18, alpha=0.5)


def sheet_frame(c, label):
    rect(c, 8, 8, PAGE[0] - 16, PAGE[1] - 16, None, INK, 0.4)
    for i in range(1, 8):
        xx = 8 + (PAGE[0] - 16) * i / 8.0
        line(c, xx, 8, xx, 12, THIN, 0.2)
        line(c, xx, PAGE[1] - 12, xx, PAGE[1] - 8, THIN, 0.2)
    for i in range(1, 6):
        yy = 8 + (PAGE[1] - 16) * i / 6.0
        line(c, 8, yy, 12, yy, THIN, 0.2)
        line(c, PAGE[0] - 12, yy, PAGE[0] - 8, yy, THIN, 0.2)
    txt(c, 12, PAGE[1] - 16, label, F["bodysemi"], 6.4, THIN)


# ---------------------------------------------------------------------------
# geometry, drawn through a transform so source millimetres land on the sheet
# ---------------------------------------------------------------------------

def in_space(c, ox, oy, scale, fn):
    """Run fn(c) with the source module emitting raw mm, placed and scaled."""
    old = B.ORIGIN
    B.ORIGIN = 0.0
    c.saveState()
    c.translate(p(ox), p(oy))
    c.scale(scale, scale)
    try:
        fn(c)
    finally:
        c.restoreState()
        B.ORIGIN = old


def stroke_pts(c, pts, colour, lw, close=True, dash=None):
    c.saveState()
    c.setStrokeColor(colour)
    c.setLineWidth(lw * MM)
    c.setLineJoin(0)
    if dash:
        c.setDash([d * MM for d in dash], 0)
    pth = c.beginPath()
    pth.moveTo(pts[0][0] * MM, pts[0][1] * MM)
    for px, py in pts[1:]:
        pth.lineTo(px * MM, py * MM)
    if close:
        pth.close()
    c.drawPath(pth, fill=0, stroke=1)
    c.restoreState()


def carton_geometry(c):
    stroke_pts(c, B.blank_outline(), CUTC, 0.5)
    for fx in (X_BACK, X_SIDL, X_FRNT, X_SIDR):
        stroke_pts(c, [(fx, Y_BODY), (fx, Y_TOP)], CREASEC, 0.4, False,
                   [3, 2])
    stroke_pts(c, [(X_GLUE, Y_BODY + B.GT), (X_GLUE, Y_TOP - B.GT)],
               CREASEC, 0.4, False, [3, 2])
    stroke_pts(c, [(X_SIDL, Y_TOP), (X_SIDR + W_SIDE, Y_TOP)], CREASEC, 0.4,
               False, [3, 2])
    stroke_pts(c, [(X_BACK, Y_BODY), (X_SIDR + W_SIDE, Y_BODY)], CREASEC,
               0.4, False, [3, 2])
    c.saveState()
    c.setStrokeColor(CUTC)
    c.setLineWidth(0.5 * MM)
    c.drawPath(B.euro_slot_path(c, TAB_X0 + TAB_W / 2.0, Y_TOP), fill=0,
               stroke=1)
    for px, pw in ((X_SIDL, W_SIDE), (X_SIDR, W_SIDE)):
        for vx, vy in B.vent_positions(px, pw):
            c.drawPath(B.vent_path(c, vx, vy, VENT_H), fill=0, stroke=1)
    c.restoreState()


# ---------------------------------------------------------------------------

def draw_carton(path):
    c = _cv.Canvas(path, pagesize=(p(PAGE[0]), p(PAGE[1])))
    c.setTitle("Swift Blue-Drop 4 x 50 g carton - production drawing")
    c.setAuthor("Vistex Chemicals Ltd")
    c.setCreator("packaging/make_spec.py")
    rect(c, 0, 0, PAGE[0], PAGE[1], PAPER, None)
    sheet_frame(c, "VISTEX CHEMICALS LTD   -   PRODUCTION DRAWING")

    # Sheet plan. The first pass centred the blank and then dropped the
    # notes and detail views wherever they fitted, which put the notes
    # inside the carton outline and the details through the dimension
    # chain. Zones first, content second.
    #
    #   left column  x 18..176   detail views, notes
    #   drawing      x 200..521  the blank, with its chains at 175/186
    #   title block  bottom right
    S = 1.0
    ox, oy = 200.0, 150.0
    in_space(c, ox, oy, S, carton_geometry)

    def X(v):
        return ox + v * S

    def Y(v):
        return oy + v * S

    # horizontal chain: panel widths, then the overall
    yc = Y(Y_BODY - H_TUCK) - 16
    runs = ((X_GLUE, W_GLUE), (X_BACK, W_FACE), (X_SIDL, W_SIDE),
            (X_FRNT, W_FACE), (X_SIDR, W_SIDE))
    for x0, wd in runs:
        dim_h(c, X(x0), X(x0 + wd), yc, "%g" % wd, ext_from=Y(Y_BODY - H_TUCK))
    dim_h(c, X(0), X(SHEET_W), yc - 12, "%g OVERALL" % SHEET_W)

    # vertical chain
    xc = X(0) - 14
    dim_v(c, Y(Y_BODY - H_TUCK), Y(Y_BODY), xc, "%g" % H_TUCK, ext_from=X(0))
    dim_v(c, Y(Y_BODY), Y(Y_TOP), xc, "%g" % H_BODY, ext_from=X(0))
    dim_v(c, Y(Y_TOP), Y(Y_TOP + H_TUCK), xc, "%g" % H_TUCK, ext_from=X(0))
    dim_v(c, Y(Y_BODY - H_TUCK), Y(Y_TOP + H_TUCK), xc - 11,
          "%g OVERALL" % SHEET_H)

    # hang tab and dust flap
    dim_h(c, X(TAB_X0), X(TAB_X0 + TAB_W), Y(Y_TOP + H_HANG) + 11,
          "%g" % TAB_W, ext_from=Y(Y_TOP + H_HANG))
    dim_v(c, Y(Y_TOP), Y(Y_TOP + H_HANG), X(TAB_X0) - 8, "%g" % H_HANG)
    dim_v(c, Y(Y_TOP), Y(Y_TOP + H_DUST), X(X_SIDR + W_SIDE) + 10,
          "%g" % H_DUST)

    # callouts, kept short and to the nearest clear edge
    leader(c, X(TAB_X0 + TAB_W / 2 + SLOT_W), Y(Y_TOP + SLOT_Y),
           X(TAB_X0 + TAB_W) + 20, Y(Y_TOP + H_HANG) + 14,
           "EURO SLOT - detail A")
    leader(c, X(X_SIDR + W_SIDE / 2), Y(VENT_Y),
           X(SHEET_W) + 12, Y(VENT_Y) - 16, "SCENT VENTS - detail B")
    leader(c, X(W_GLUE / 2), Y(Y_TOP - 18), X(W_GLUE / 2) + 5,
           Y(Y_TOP + H_TUCK) + 12, "GLUE TAB - unprinted")

    # ---- left column: detail views ---------------------------------------
    das = 4.0

    dax, day, dbw, dbh = 18.0, 300.0, 74.0, 86.0
    rect(c, dax, day, dbw, dbh, None, THIN, 0.3)
    txt(c, dax + 3, day + dbh - 7, "DETAIL A   EURO SLOT   4:1",
        F["bodysemi"], 6.2, INK)

    def slot(cc):
        # -SLOT_Y so the eye lands on the origin: the helper measures from
        # the tab base, and at 4:1 that offset threw the shape out of frame
        cc.saveState()
        cc.setStrokeColor(CUTC)
        cc.setLineWidth(0.13 * MM)
        cc.drawPath(B.euro_slot_path(cc, 0, -SLOT_Y), fill=0, stroke=1)
        cc.restoreState()
    slot_h = SLOT_R + SLOT_RISE + SLOT_W / 2
    in_space(c, dax + dbw * 0.56, day + 30, das, slot)
    dim_v(c, day + 30 - SLOT_R * das, day + 30 + (slot_h - SLOT_R) * das,
          dax + dbw * 0.28, "%.1f" % slot_h, size=5.0)
    dim_h(c, dax + dbw * 0.56 - SLOT_R * das, dax + dbw * 0.56 + SLOT_R * das,
          day + 20, "%.1f" % (SLOT_R * 2), size=5.0)
    txt(c, dax + 3, day + 5.5, "Riser %.1f wide   %.1f headroom above"
        % (SLOT_W, TAB_HEADROOM), F["body"], 5.0, INK)

    dbx, dby = 18.0, 196.0
    rect(c, dbx, dby, dbw, dbh, None, THIN, 0.3)
    txt(c, dbx + 3, dby + dbh - 7, "DETAIL B   SCENT VENT   4:1",
        F["bodysemi"], 6.2, INK)

    def vent(cc):
        cc.saveState()
        cc.setStrokeColor(CUTC)
        cc.setLineWidth(0.13 * MM)
        for i in range(2):
            cc.drawPath(B.vent_path(cc, i * VENT_GAP, 0, VENT_H), fill=0,
                        stroke=1)
        cc.restoreState()
    in_space(c, dbx + 18, dby + 46, das, vent)
    dim_h(c, dbx + 18, dbx + 18 + VENT_GAP * das, dby + 24,
          "%.1f" % VENT_GAP, size=5.0)
    dim_v(c, dby + 46 - VENT_H / 2 * das, dby + 46 + VENT_H / 2 * das,
          dbx + 9, "%.1f" % VENT_H, size=5.0)
    _vw = VENT_H * 0.335 * 2
    dim_h(c, dbx + 18 - _vw / 2 * das, dbx + 18 + _vw / 2 * das, dby + 64,
          "%.2f" % _vw, size=5.0)
    txt(c, dbx + 3, dby + 5.5, "%d per side panel   row centre %g from foot"
        % (VENT_N, VENT_Y), F["body"], 5.0, INK)

    # ---- notes, below the details ----------------------------------------
    nx, ny = 18.0, 176.0
    txt(c, nx, ny, "NOTES", F["bodysemi"], 6.4, INK, track=0.5)
    for i, t in enumerate((
            "1.  All dimensions in millimetres.",
            "2.  Do not scale from drawing.",
            "3.  Bleed %g mm beyond cut, all outer edges." % BLEED,
            "4.  Live copy %g mm inside every cut and crease." % SAFE,
            "5.  Glue tab unprinted and varnish-free.",
            "6.  Slot and vents are cut features, not print.",
            "7.  Board and grain to converter's recommendation.",
            "8.  Design intent, not a measured die.",
            "     Confirm before tooling.")):
        txt(c, nx, ny - 6.4 - i * 5.0, t, F["body"], 5.4, INK)

    title_block(c, PAGE[0] - 8 - 232, 14, 232, 62,
                (("PRODUCT", "Swift Blue-Drop"),
                 ("PACK", "4 x 50 g, net 200 g"),
                 ("STYLE", "Straight tuck end"),
                 ("FEATURE", "Euro hang tab + scent vents"),
                 ("CARTON", "%g x %g x %g mm" % (W_FACE, W_SIDE, H_BODY)),
                 ("BLANK", "%g x %g mm" % (SHEET_W, SHEET_H)),
                 ("SCALE", "1:1 at A2"),
                 ("SHEET", "A2 landscape, 594 x 420")),
                "RETAIL CARTON - DIE SPECIFICATION",
                "Vistex Chemicals Ltd")
    c.showPage()
    c.save()
    return path


def shipper_geometry(c):
    pts = SH.outline()
    stroke_pts(c, pts, CUTC, 1.0)
    for fx in (SH.X_SIDE1, SH.X_BACK, SH.X_SIDE2, SH.X_GLUE):
        stroke_pts(c, [(fx, SH.Y_TOP), (fx, SH.Y_TOP + SH.FLAP)], CUTC, 1.0,
                   False)
        stroke_pts(c, [(fx, SH.Y_BODY), (fx, SH.Y_BODY - SH.FLAP)], CUTC,
                   1.0, False)
        stroke_pts(c, [(fx, SH.Y_BODY - SH.FLAP), (fx, SH.Y_TOP + SH.FLAP)],
                   CREASEC, 0.8, False, [6, 4])
    stroke_pts(c, [(0, SH.Y_TOP), (SH.SHEET_W, SH.Y_TOP)], CREASEC, 0.8,
               False, [6, 4])
    stroke_pts(c, [(0, SH.Y_BODY), (SH.SHEET_W, SH.Y_BODY)], CREASEC, 0.8,
               False, [6, 4])


def draw_shipper(path):
    c = _cv.Canvas(path, pagesize=(p(PAGE[0]), p(PAGE[1])))
    c.setTitle("Swift Blue-Drop 12-count shipper - production drawing")
    c.setAuthor("Vistex Chemicals Ltd")
    c.setCreator("packaging/make_spec.py")
    rect(c, 0, 0, PAGE[0], PAGE[1], PAPER, None)
    sheet_frame(c, "VISTEX CHEMICALS LTD   -   PRODUCTION DRAWING")

    S = 0.5                       # 1070 mm will not fit A2 at 1:1
    ox = (PAGE[0] - SH.SHEET_W * S) / 2
    oy = 190.0
    in_space(c, ox, oy, S, shipper_geometry)

    def X(v):
        return ox + v * S

    def Y(v):
        return oy + v * S

    yc = Y(SH.Y_BODY - SH.FLAP) - 14
    for x0, wd, _ in ((SH.X_FRONT, SH.CASE_L, "F"), (SH.X_SIDE1, SH.CASE_W, "S"),
                      (SH.X_BACK, SH.CASE_L, "B"), (SH.X_SIDE2, SH.CASE_W, "S"),
                      (SH.X_GLUE, SH.GLUE, "J")):
        dim_h(c, X(x0), X(x0 + wd), yc, "%g" % wd,
              ext_from=Y(SH.Y_BODY - SH.FLAP))
    dim_h(c, X(0), X(SH.SHEET_W), yc - 11, "%g OVERALL" % SH.SHEET_W)

    xc = X(0) - 14
    dim_v(c, Y(SH.Y_BODY - SH.FLAP), Y(SH.Y_BODY), xc, "%g" % SH.FLAP,
          ext_from=X(0))
    dim_v(c, Y(SH.Y_BODY), Y(SH.Y_TOP), xc, "%g" % SH.CASE_H, ext_from=X(0))
    dim_v(c, Y(SH.Y_TOP), Y(SH.Y_TOP + SH.FLAP), xc, "%g" % SH.FLAP,
          ext_from=X(0))
    dim_v(c, Y(SH.Y_BODY - SH.FLAP), Y(SH.Y_TOP + SH.FLAP), xc - 11,
          "%g OVERALL" % SH.SHEET_H)

    leader(c, X(SH.X_GLUE + SH.GLUE / 2), Y(SH.Y_BODY + SH.CASE_H / 2),
           X(SH.SHEET_W) + 14, Y(SH.Y_TOP + SH.FLAP) + 12,
           "MANUFACTURER JOINT")
    leader(c, X(SH.X_SIDE1), Y(SH.Y_TOP + SH.FLAP * 0.5),
           X(SH.X_SIDE1) - 26, Y(SH.Y_TOP + SH.FLAP) + 22,
           "SLOT, full flap depth", align="r")

    nx, ny = 26.0, 150.0
    txt(c, nx, ny, "NOTES", F["bodysemi"], 6.4, INK, track=0.5)
    for i, t in enumerate((
            "1.  All dimensions in millimetres. Do not scale from drawing.",
            "2.  Regular slotted container. All flaps %g mm, meeting at the "
            "centre." % SH.FLAP,
            "3.  Holds %d retail cartons, %d across x %d deep, one layer."
            % (SH.COUNT, SH.ACROSS, SH.DEEP),
            "4.  Internal %g x %g x %g mm; %g mm total slack per axis."
            % (SH.CASE_L, SH.CASE_W, SH.CASE_H, SH.CLEAR),
            "5.  Net product %.1f kg per case." % SH.NET_KG,
            "6.  B or BC flute recommended; confirm with converter.",
            "7.  Dimensions are a design intent, not a measured die.")):
        txt(c, nx, ny - 6.0 - i * 5.0, t, F["body"], 5.6, INK)

    title_block(c, PAGE[0] - 8 - 232, 14, 232, 62,
                (("PRODUCT", "Swift Blue-Drop"),
                 ("CONTENTS", "%d x 4 x 50 g" % SH.COUNT),
                 ("STYLE", "Regular slotted container"),
                 ("NET", "%.1f kg per case" % SH.NET_KG),
                 ("CASE", "%g x %g x %g mm int."
                  % (SH.CASE_L, SH.CASE_W, SH.CASE_H)),
                 ("BLANK", "%g x %g mm" % (SH.SHEET_W, SH.SHEET_H)),
                 ("SCALE", "1:2 at A2"),
                 ("SHEET", "A2 landscape, 594 x 420")),
                "SHIPPER - DIE SPECIFICATION",
                "Vistex Chemicals Ltd")
    c.showPage()
    c.save()
    return path


def main():
    register_fonts()
    os.makedirs(OUT, exist_ok=True)
    a = draw_carton(os.path.join(OUT, "Swift_Blue-Drop_Carton_SPEC.pdf"))
    b = draw_shipper(os.path.join(OUT, "Swift_Blue-Drop_Shipper_SPEC.pdf"))
    for f in (a, b):
        print("%-46s %6.1f KB" % (os.path.basename(f),
                                  os.path.getsize(f) / 1024.0))
        B.preview(f, f[:-4] + ".png", dpi=130)
    print("")
    print("carton drawing  1:1 at A2   blank %g x %g mm"
          % (SHEET_W, SHEET_H))
    print("shipper drawing 1:2 at A2   blank %g x %g mm"
          % (SH.SHEET_W, SH.SHEET_H))


if __name__ == "__main__":
    main()
