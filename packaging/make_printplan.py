#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Print plan: the die and the content that prints on it, on one sheet.

The plan showed where the ink goes. The production drawing showed what the
die cuts. Neither on its own answers "what is printed on which panel, and at
what size" - the question a printer and a client both actually ask. This puts
the artwork at 1:1 under the dieline, dimensions it, and schedules every
panel against what it carries.

Composed in three passes, because PDF compositing only stacks forward:

  1. ReportLab  - sheet furniture: frame, schedule, inks, notes, title block,
                  with the artwork area left empty
  2. PyMuPDF    - the artwork stamped in as vector at 1:1
  3. ReportLab  - an unpainted overlay page of dielines, dimensions and
                  leaders, stamped on top

Drawing the overlay in pass 1 would have buried it under the artwork.

Output: dist/spec/Swift_Blue-Drop_<X>_<Name>_PRINTPLAN.pdf   (A1, 1:1)

Run:  python packaging/make_printplan.py
"""

import os

import pymupdf
from reportlab.pdfgen import canvas as _cv
from reportlab.lib.colors import CMYKColor

import swift_blue_drop_dieline as B
import make_spec as MS
from swift_blue_drop_dieline import (MM, F, register_fonts, ROOT, DIST,
                                     W_GLUE, W_FACE, W_SIDE, H_BODY, H_TUCK,
                                     H_DUST, H_HANG, TAB_W, SLOT_R, SLOT_W,
                                     SLOT_RISE, TAB_HEADROOM, VENT_N, VENT_H,
                                     VENT_GAP, VENT_Y, SHEET_W, SHEET_H,
                                     BLEED, SAFE, X_GLUE, X_BACK, X_SIDL,
                                     X_FRNT, X_SIDR, Y_BODY, Y_TOP, TAB_X0,
                                     NAVY, BLUE_BR, YELLOW, RED, CYAN)

OUT = os.path.join(DIST, "spec")
INTEG = os.path.join(DIST, "integrated")

PAGE = (841.0, 594.0)                  # A1 landscape
INK = CMYKColor(0, 0, 0, 1)
THIN = CMYKColor(0, 0, 0, 0.62)
DIMC = CMYKColor(0.85, 0.45, 0, 0.10)
CUTC = CMYKColor(0, 1, 0, 0)
CREASEC = CMYKColor(1, 0, 0, 0)
PAPER = CMYKColor(0, 0, 0, 0.02)

# artwork placement, 1:1
S = 1.0
OX, OY = 58.0, 254.0                   # page position of the source origin
SRC_W, SRC_H = SHEET_W + 2 * BLEED, SHEET_H + 2 * BLEED

CONCEPTS = (("D", "Immersion"), ("E", "Cascade"), ("F", "Vortex"))


def X(v):
    return OX + (v + BLEED) * S


def Y(v):
    return OY + (v + BLEED) * S


# ---------------------------------------------------------------------------
# what each panel carries - the whole point of the sheet
# ---------------------------------------------------------------------------

SCHEDULE = (
    ("GLUE TAB", "%g x %g" % (W_GLUE, H_BODY),
     "Unprinted. Varnish-free - ink under the glue line is the usual cause "
     "of cartons popping open."),
    ("BACK", "%g x %g" % (W_FACE, H_BODY),
     "Water ground veiled to a watermark. Header; HOW TO USE, three "
     "illustrated steps; CAUTION; WHY IT WORKS; COMPOSITION and STORAGE; "
     "Vistex foot block with white recycle mark."),
    ("SIDE, left", "%g x %g" % (W_SIDE, H_BODY),
     "Swift mark; Blue-Drop; benefit stack of four with icons; product "
     "block; 4 x 50 g foot band. Five scent vents (cut)."),
    ("FRONT", "%g x %g" % (W_FACE, H_BODY),
     "Composed photographic scene. Swift mark; Blue-Drop wordmark with "
     "gloss droplet; descriptor; four product blocks; 30 DAYS seal; "
     "CLEANS / FRESHENS / PROTECTS; weights; navy foot band."),
    ("SIDE, right", "%g x %g" % (W_SIDE, H_BODY),
     "Swift mark; Blue-Drop; IDEAL FOR list; ONE BLOCK 30 DAYS; recycle "
     "mark; 4 x 50 g foot band. Five scent vents (cut)."),
    ("TOP TUCK, front", "%g x %g" % (W_FACE, H_TUCK),
     "Swift mark and product descriptor line."),
    ("BOTTOM TUCK, front", "%g x %g" % (W_FACE, H_TUCK),
     "Swift mark and manufacturer line."),
    ("DUST FLAPS, x4", "%g x %g" % (W_SIDE, H_DUST),
     "Swift mark, reduced."),
    ("HANG TAB, back", "%g x %g" % (TAB_W, H_HANG),
     "SWIFT BLUE-DROP line. Euro slot is a cut feature, knocked out of the "
     "artwork so proofs read as a hole."),
)

INKS = ((NAVY, "Ground", "C100 M85 Y10 K15"),
        (BLUE_BR, "Water / accent", "C85 M40 Y0 K0"),
        (CYAN, "Highlight", "C65 M10 Y0 K0"),
        (YELLOW, "Flag", "C0 M12 Y100 K0"),
        (RED, "Signal", "C0 M95 Y90 K0"))


# ---------------------------------------------------------------------------
# pass 1 - sheet furniture
# ---------------------------------------------------------------------------

def base_page(path, letter, name):
    MS.PAGE = PAGE
    c = _cv.Canvas(path, pagesize=(MS.p(PAGE[0]), MS.p(PAGE[1])))
    c.setTitle("Swift Blue-Drop %s %s - print plan" % (letter, name))
    c.setAuthor("Vistex Chemicals Ltd")
    c.setCreator("packaging/make_printplan.py")
    MS.rect(c, 0, 0, PAGE[0], PAGE[1], PAPER, None)
    MS.sheet_frame(c, "VISTEX CHEMICALS LTD   -   PRINT PLAN   -   "
                      "ARTWORK, DIE AND CONTENT")

    # ---- content schedule -------------------------------------------------
    sx, sy, swid = 404.0, 254.0, 420.0
    MS.txt(c, sx, sy + 248, "CONTENT SCHEDULE", F["bodysemi"], 8.0, INK,
           track=0.6)
    MS.line(c, sx, sy + 244, sx + swid, sy + 244, INK, 0.3)
    hy = sy + 238
    for lab, xo in (("PANEL", 0), ("SIZE mm", 86), ("PRINTED CONTENT", 134)):
        MS.txt(c, sx + xo, hy, lab, F["bodysemi"], 5.6, THIN, track=0.4)
    MS.line(c, sx, hy - 2.6, sx + swid, hy - 2.6, THIN, 0.2)

    yy = hy - 9.0
    for lab, size, body in SCHEDULE:
        MS.txt(c, sx, yy, lab, F["bodysemi"], 6.2, INK)
        MS.txt(c, sx + 86, yy, size, F["body"], 6.2, INK)
        words, line_, ly = body.split(), "", yy
        for wd in words:
            t = (line_ + " " + wd).strip()
            if MS.sw(t, F["body"], 6.0) / MM <= swid - 138 or not line_:
                line_ = t
            else:
                MS.txt(c, sx + 134, ly, line_, F["body"], 6.0, INK)
                ly -= 3.6
                line_ = wd
        if line_:
            MS.txt(c, sx + 134, ly, line_, F["body"], 6.0, INK)
            ly -= 3.6
        yy = min(ly, yy - 3.6) - 2.6
        MS.line(c, sx, yy + 2.2, sx + swid, yy + 2.2, THIN, 0.15, alpha=0.5)

    # ---- inks -------------------------------------------------------------
    ix, iy = 404.0, 128.0
    MS.txt(c, ix, iy + 100, "PROCESS INKS", F["bodysemi"], 8.0, INK,
           track=0.6)
    MS.line(c, ix, iy + 96, ix + 200, iy + 96, INK, 0.3)
    for i, (col, nm, spec) in enumerate(INKS):
        ry = iy + 86 - i * 13
        MS.rect(c, ix, ry - 3, 11, 9, col, THIN, 0.2)
        MS.txt(c, ix + 15, ry, nm, F["bodysemi"], 6.2, INK)
        MS.txt(c, ix + 78, ry, spec, F["body"], 6.2, INK)
    MS.txt(c, ix, iy + 10,
           "CMYK process throughout, no spot colours. Mixes are hand-specified, "
           "not machine-converted from RGB.", F["body"], 5.8, INK)
    MS.txt(c, ix, iy + 4,
           "Total ink under 300%. Soft-proof against the press profile before "
           "plates.", F["body"], 5.8, INK)

    # ---- finish -----------------------------------------------------------
    fx = 630.0
    MS.txt(c, fx, iy + 100, "FINISH", F["bodysemi"], 8.0, INK, track=0.6)
    MS.line(c, fx, iy + 96, fx + 194, iy + 96, INK, 0.3)
    for i, (k, v) in enumerate((("Board", "to converter's recommendation"),
                                ("Grain", "parallel to carton height"),
                                ("Varnish", "overall, excluding glue tab"),
                                ("Type", "live text, embedded subsets"),
                                ("Images", "300 dpi at final size"),
                                ("Proof", "wet proof before plates"))):
        ry = iy + 86 - i * 13
        MS.txt(c, fx, ry, k, F["bodysemi"], 6.2, THIN)
        MS.txt(c, fx + 42, ry, v, F["body"], 6.2, INK)

    # ---- notes ------------------------------------------------------------
    nx, ny = 26.0, 206.0
    MS.txt(c, nx, ny, "NOTES", F["bodysemi"], 8.0, INK, track=0.6)
    MS.line(c, nx, ny - 4, nx + 330, ny - 4, INK, 0.3)
    for i, t in enumerate((
            "1.  Artwork shown at 1:1. All dimensions in millimetres. Do not "
            "scale from drawing.",
            "2.  Bleed %g mm beyond cut on every outer edge." % BLEED,
            "3.  Live copy kept %g mm inside every cut and crease; enforced "
            "in the build, not drawn." % SAFE,
            "4.  Euro slot and scent vents are CUT features. They are "
            "knocked out white in the artwork",
            "     so that proofs read as holes; the die removes them in any "
            "case.",
            "5.  Glue tab carries no print and no varnish.",
            "6.  Hang tab has no crease at its base - it is continuous with "
            "the back panel.",
            "7.  Carton dimensions are design intent, not a measured die. "
            "Confirm before tooling.")):
        MS.txt(c, nx, ny - 11 - i * 6.2, t, F["body"], 6.0, INK)

    MS.title_block(c, PAGE[0] - 10 - 250, 16, 250, 72,
                   (("PRODUCT", "Swift Blue-Drop"),
                    ("PACK", "4 x 50 g, net 200 g"),
                    ("CONCEPT", "%s - %s" % (letter, name)),
                    ("STYLE", "Straight tuck end"),
                    ("CARTON", "%g x %g x %g mm" % (W_FACE, W_SIDE, H_BODY)),
                    ("BLANK", "%g x %g mm + %g bleed"
                     % (SHEET_W, SHEET_H, BLEED)),
                    ("SCALE", "1:1 at A1"),
                    ("SHEET", "A1 landscape, 841 x 594")),
                   "PRINT PLAN - ARTWORK, DIE AND CONTENT",
                   "Vistex Chemicals Ltd")
    c.showPage()
    c.save()
    return path


# ---------------------------------------------------------------------------
# pass 3 - the overlay: dielines, dimensions, leaders. No background painted,
# so the artwork underneath shows through.
# ---------------------------------------------------------------------------

def overlay_page(path):
    MS.PAGE = PAGE
    c = _cv.Canvas(path, pagesize=(MS.p(PAGE[0]), MS.p(PAGE[1])))

    def geom(cc):
        MS.stroke_pts(cc, B.blank_outline(), CUTC, 0.45)
        for fx in (X_BACK, X_SIDL, X_FRNT, X_SIDR):
            MS.stroke_pts(cc, [(fx, Y_BODY), (fx, Y_TOP)], CREASEC, 0.35,
                          False, [3, 2])
        MS.stroke_pts(cc, [(X_GLUE, Y_BODY + B.GT), (X_GLUE, Y_TOP - B.GT)],
                      CREASEC, 0.35, False, [3, 2])
        MS.stroke_pts(cc, [(X_SIDL, Y_TOP), (X_SIDR + W_SIDE, Y_TOP)],
                      CREASEC, 0.35, False, [3, 2])
        MS.stroke_pts(cc, [(X_BACK, Y_BODY), (X_SIDR + W_SIDE, Y_BODY)],
                      CREASEC, 0.35, False, [3, 2])
        cc.saveState()
        cc.setStrokeColor(CUTC)
        cc.setLineWidth(0.45 * MM)
        cc.drawPath(B.euro_slot_path(cc, TAB_X0 + TAB_W / 2.0, Y_TOP),
                    fill=0, stroke=1)
        for px, pw in ((X_SIDL, W_SIDE), (X_SIDR, W_SIDE)):
            for vx, vy in B.vent_positions(px, pw):
                cc.drawPath(B.vent_path(cc, vx, vy, VENT_H), fill=0, stroke=1)
        cc.restoreState()

    MS.in_space(c, OX + BLEED * S, OY + BLEED * S, S, geom)

    # dimension chains
    yc = Y(Y_BODY - H_TUCK) - 20
    for x0, wd in ((X_GLUE, W_GLUE), (X_BACK, W_FACE), (X_SIDL, W_SIDE),
                   (X_FRNT, W_FACE), (X_SIDR, W_SIDE)):
        MS.dim_h(c, X(x0), X(x0 + wd), yc, "%g" % wd,
                 ext_from=Y(Y_BODY - H_TUCK))
    MS.dim_h(c, X(0), X(SHEET_W), yc - 12, "%g OVERALL" % SHEET_W)

    xc = X(0) - 14
    MS.dim_v(c, Y(Y_BODY - H_TUCK), Y(Y_BODY), xc, "%g" % H_TUCK,
             ext_from=X(0))
    MS.dim_v(c, Y(Y_BODY), Y(Y_TOP), xc, "%g" % H_BODY, ext_from=X(0))
    MS.dim_v(c, Y(Y_TOP), Y(Y_TOP + H_TUCK), xc, "%g" % H_TUCK, ext_from=X(0))
    MS.dim_v(c, Y(Y_BODY - H_TUCK), Y(Y_TOP + H_TUCK), xc - 12,
             "%g OVERALL" % SHEET_H)
    MS.dim_h(c, X(TAB_X0), X(TAB_X0 + TAB_W), Y(Y_TOP + H_HANG) + 11,
             "%g" % TAB_W, ext_from=Y(Y_TOP + H_HANG))
    MS.dim_v(c, Y(Y_TOP), Y(Y_TOP + H_HANG), X(TAB_X0) - 8, "%g" % H_HANG)

    # Panel keys, below the blank rather than on it. Dropped inside the
    # panels they landed on the back-panel heading and the front wordmark.
    for px, pw, key in ((X_GLUE, W_GLUE, "1"), (X_BACK, W_FACE, "2"),
                        (X_SIDL, W_SIDE, "3"), (X_FRNT, W_FACE, "4"),
                        (X_SIDR, W_SIDE, "5")):
        kx, ky = X(px + pw / 2), Y(Y_BODY - H_TUCK) - 6.5
        c.saveState()
        c.setFillColor(DIMC)
        c.circle(MS.p(kx), MS.p(ky), MS.p(3.4), fill=1, stroke=0)
        c.restoreState()
        MS.txt(c, kx, ky - 1.4, key, F["bodyblk"], 7.0,
               CMYKColor(0, 0, 0, 0), "c")
    MS.txt(c, X(TAB_X0 + TAB_W / 2), Y(Y_TOP + H_HANG) + 4.0,
           "9  HANG TAB", F["bodysemi"], 6.0, DIMC, "c")
    MS.txt(c, X(X_FRNT + W_FACE / 2), Y(Y_TOP + H_TUCK) + 4.0,
           "6  TOP TUCK", F["bodysemi"], 6.0, DIMC, "c")
    MS.txt(c, X(X_FRNT + W_FACE / 2) + 34, Y(Y_BODY - H_TUCK) + 4.0,
           "7  BOTTOM TUCK", F["bodysemi"], 6.0, DIMC, "c")
    MS.txt(c, X(X_SIDL + W_SIDE / 2), Y(Y_TOP + H_DUST) + 4.0,
           "8", F["bodysemi"], 6.0, DIMC, "c")
    MS.txt(c, X(X_SIDR + W_SIDE / 2), Y(Y_TOP + H_DUST) + 4.0,
           "8", F["bodysemi"], 6.0, DIMC, "c")

    MS.leader(c, X(X_SIDR + W_SIDE / 2), Y(VENT_Y), X(SHEET_W) + 10,
              Y(VENT_Y) - 20,
              "SCENT VENTS  %d off, droplet %.1f high, %.1f pitch"
              % (VENT_N, VENT_H, VENT_GAP))
    MS.leader(c, X(TAB_X0 + TAB_W / 2 + SLOT_W), Y(Y_TOP + 8.5),
              X(TAB_X0 + TAB_W) + 14, Y(Y_TOP + H_HANG) + 20,
              "EURO SLOT  dia %.1f, riser %.1f, headroom %.1f"
              % (SLOT_R * 2, SLOT_W, TAB_HEADROOM))
    MS.leader(c, X(W_GLUE / 2), Y(Y_TOP - 18), X(W_GLUE / 2) + 5,
              Y(Y_TOP + H_TUCK) + 10, "GLUE TAB  no print, no varnish")

    c.showPage()
    c.save()
    return path


# ---------------------------------------------------------------------------

def build(letter, name):
    art = os.path.join(INTEG, "Concept_%s_%s.pdf" % (letter, name))
    if not os.path.exists(art):
        return None
    out = os.path.join(OUT, "Swift_Blue-Drop_%s_%s_PRINTPLAN.pdf"
                       % (letter, name))
    tmp_base = out + ".base"
    tmp_over = out + ".over"
    base_page(tmp_base, letter, name)
    overlay_page(tmp_over)

    doc = pymupdf.open(tmp_base)
    page = doc[0]
    src = pymupdf.open(art)
    page.show_pdf_page(
        pymupdf.Rect(OX * MM, (PAGE[1] - OY - SRC_H * S) * MM,
                     (OX + SRC_W * S) * MM, (PAGE[1] - OY) * MM),
        src, 0)
    src.close()
    ov = pymupdf.open(tmp_over)
    page.show_pdf_page(pymupdf.Rect(0, 0, PAGE[0] * MM, PAGE[1] * MM), ov, 0)
    ov.close()
    doc.save(out)
    doc.close()
    os.remove(tmp_base)
    os.remove(tmp_over)
    return out


def main():
    register_fonts()
    os.makedirs(OUT, exist_ok=True)
    for letter, name in CONCEPTS:
        f = build(letter, name)
        if not f:
            print("skip %s" % letter)
            continue
        print("%-54s %6.1f KB" % (os.path.basename(f),
                                  os.path.getsize(f) / 1024.0))
        B.preview(f, f[:-4] + ".png", dpi=110)
    print("")
    print("print plans 1:1 at A1 (841 x 594), artwork + die + content")


if __name__ == "__main__":
    main()
