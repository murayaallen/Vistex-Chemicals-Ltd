#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One presentation document per iteration.

Built in two passes, which is the whole trick:

  1. ReportLab lays out the pages - headings, labels, spec tables, swatches,
     and the 3D renders (those are rasters by nature).
  2. PyMuPDF stamps the actual artwork in with show_pdf_page, so every panel
     and every dieline arrives as VECTOR, clipped straight out of the print
     file.

Rasterising the panels at 400 dpi would have been one pass and half the code,
but then the client's document would be a picture of the design rather than
the design, and nobody could zoom into the type to check it.

Output: dist/documents/Swift_Blue-Drop_<X>_<Name>.pdf   (one per concept)
        dist/documents/Swift_Blue-Drop_Shipper_12ct.pdf

Run:  python packaging/make_document.py
"""

import os

import pymupdf
from reportlab.pdfgen import canvas as _cv

from swift_blue_drop_dieline import (MM, F, register_fonts, ROOT, DIST, BLEED,
                                     X_GLUE, X_BACK, X_SIDL, X_FRNT, X_SIDR,
                                     W_GLUE, W_FACE, W_SIDE, H_BODY, H_TUCK,
                                     H_HANG, Y_BODY, Y_TOP, TAB_X0, TAB_W,
                                     SHEET_W, SHEET_H, SAFE, VENT_N,
                                     NAVY, NAVY_DK, NAVY_MID, BLUE_MID,
                                     BLUE_BR, CYAN, CYAN_LT, WHITE, YELLOW,
                                     RED, GREY, INK)
import swift_shipper as SH

OUT = os.path.join(DIST, "documents")
INTEG = os.path.join(DIST, "integrated")
SHIPD = os.path.join(DIST, "shipper")
SPEC = os.path.join(DIST, "spec")
VIEWS = os.path.join(DIST, "views")
MOCK = os.path.join(DIST, "mockups")
FAM = os.path.join(DIST, "family")

PW, PH = 420.0, 297.0                 # A3 landscape, in mm
M = 16.0                              # page margin

CONCEPTS = (("D", "Immersion", "Deepest ground; water wrapping the product "
                               "from both sides."),
            ("E", "Cascade", "Water falling from the masthead; the lightest "
                             "and freshest of the three."),
            ("F", "Vortex", "Ring splash as a whirlpool; the strongest "
                            "product presence on shelf."))

PLACE = []        # (page_index, dest_mm, src_pdf, clip_mm) stamped in pass 2


# ---------------------------------------------------------------------------
# pass-1 helpers (ReportLab, millimetres, origin bottom-left)
# ---------------------------------------------------------------------------

def p(v):
    return v * MM


def rect(c, x, y, w, h, colour, alpha=1.0):
    c.saveState()
    c.setFillColor(colour, alpha)
    c.rect(p(x), p(y), p(w), p(h), fill=1, stroke=0)
    c.restoreState()


def frame(c, x, y, w, h, colour=GREY, lw=0.25, alpha=0.5):
    c.saveState()
    c.setStrokeColor(colour, alpha)
    c.setLineWidth(lw * MM)
    c.rect(p(x), p(y), p(w), p(h), fill=0, stroke=1)
    c.restoreState()


def sw(t, f, s):
    from reportlab.pdfbase import pdfmetrics
    return pdfmetrics.stringWidth(t, f, s)


def txt(c, x, y, t, font, size, colour, align="l", track=0.0):
    w = sw(t, font, size) + track * max(0, len(t) - 1)
    px = p(x) - (w / 2 if align == "c" else w if align == "r" else 0)
    c.setFillColor(colour)
    if track:
        to = c.beginText(px, p(y))
        to.setFont(font, size)
        to.setCharSpace(track)
        to.textLine(t)
        to.setCharSpace(0)
        c.drawText(to)
    else:
        c.setFont(font, size)
        c.drawString(px, p(y), t)
    return w / MM


def para(c, x, y, text, font, size, colour, width, lead):
    words, line, yy = text.split(), "", y
    for wd in words:
        t = (line + " " + wd).strip()
        if sw(t, font, size) / MM <= width or not line:
            line = t
        else:
            txt(c, x, yy, line, font, size, colour)
            yy -= lead
            line = wd
    if line:
        txt(c, x, yy, line, font, size, colour)
        yy -= lead
    return yy


def place(page, dest, src_pdf, clip):
    """Queue a vector stamp. dest and clip are (x, y, w, h) in mm; clip is in
    the source page's own artwork coordinates (incl. its origin offset)."""
    PLACE.append((page, dest, src_pdf, clip))


def place_scaled(page, x, y, src, clip, scale):
    """Place at a true scale. Writing dest width and height by hand is how
    the vent crop ended up squashed - derive them from the clip instead."""
    dw, dh = clip[2] * scale, clip[3] * scale
    place(page, (x, y, dw, dh), src, clip)
    return dw, dh


def caption(c, x, y, w, label, sub=None):
    txt(c, x, y, label, F["subhead"], 8.4, NAVY, track=0.4)
    if sub:
        txt(c, x + w, y, sub, F["body"], 7.4, GREY, "r")


def page_header(c, title, kicker, pageno, total):
    rect(c, 0, PH - 22, PW, 22, NAVY)
    txt(c, M, PH - 13.5, title, F["head"], 13, WHITE)
    txt(c, M, PH - 19.0, kicker, F["body"], 7.6, CYAN_LT)
    txt(c, PW - M, PH - 13.5, "%d / %d" % (pageno, total), F["bodyblk"], 11,
        WHITE, "r")
    rect(c, 0, PH - 22.6, PW, 0.6, CYAN, alpha=0.6)


def page_footer(c, note):
    rect(c, 0, 0, PW, 10, NAVY_DK)
    txt(c, M, 3.6, "Swift Blue-Drop  -  Vistex Chemicals Ltd", F["bodysemi"],
        7.0, WHITE)
    txt(c, PW - M, 3.6, note, F["body"], 7.0, CYAN_LT, "r")


def swatch_row(c, x, y, items, sz=13.0, gap=4.0):
    for i, (col, name, spec) in enumerate(items):
        cx = x + i * (sz + gap + 26.0)
        rect(c, cx, y, sz, sz, col)
        frame(c, cx, y, sz, sz, GREY, 0.2, 0.4)
        txt(c, cx + sz + 2.5, y + sz - 4.0, name, F["bodysemi"], 7.0, NAVY)
        txt(c, cx + sz + 2.5, y + sz - 9.0, spec, F["body"], 6.2, GREY)


# ---------------------------------------------------------------------------
# the pages
# ---------------------------------------------------------------------------

def doc_concept(letter, name, blurb, path):
    art = os.path.join(INTEG, "Concept_%s_%s.pdf" % (letter, name))
    plan = os.path.join(INTEG, "Concept_%s_%s_PLAN.pdf" % (letter, name))
    mock = os.path.join(MOCK, "Concept_%s_%s_3D.png" % (letter, name))
    O = BLEED
    PLACE[:] = []
    total = 8
    c = _cv.Canvas(path, pagesize=(p(PW), p(PH)))
    c.setTitle("Swift Blue-Drop - concept %s, %s" % (letter, name))
    c.setAuthor("Vistex Chemicals Ltd")
    c.setCreator("packaging/make_document.py")
    full = "Concept %s  -  %s" % (letter, name)

    # ---- 1. cover ---------------------------------------------------------
    rect(c, 0, 0, PW, PH, NAVY)
    rect(c, 0, 0, PW * 0.46, PH, NAVY_DK)
    txt(c, M, PH - 46, "SWIFT BLUE-DROP", F["head"], 26, WHITE, track=1.4)
    txt(c, M, PH - 58, "Flush-Activated WC Cleaner  -  4 x 50 g", F["subhead"],
        11, CYAN_LT)
    rect(c, M, PH - 68, 56, 1.0, CYAN)
    txt(c, M, PH - 86, "Concept " + letter, F["display"], 44, WHITE)
    txt(c, M, PH - 102, name, F["head"], 22, CYAN_LT)
    para(c, M, PH - 120, blurb, F["body"], 10, WHITE, PW * 0.40, 5.6)
    yy = 96
    for lab, val in (("Carton", "105 x 48 x 155 mm, straight tuck end"),
                     ("Hanging", "euro hang tab, 62 x 26 mm"),
                     ("Venting", "%d droplet cut-outs per side" % VENT_N),
                     ("Colour", "CMYK process, no spot colours"),
                     ("Type", "live text, embedded subsets"),
                     ("Outer", "12-count RSC, 319 x 196 x 160 mm")):
        txt(c, M, yy, lab.upper(), F["bodysemi"], 7.0, CYAN, track=0.5)
        txt(c, M + 34, yy, val, F["body"], 8.4, WHITE)
        yy -= 9.0
    if os.path.exists(mock):
        c.drawImage(mock, p(PW * 0.455), p(14), p(PW * 0.53), p(PH - 30),
                    mask="auto", preserveAspectRatio=True, anchor="c")
    txt(c, PW - M, 8, "Vistex Chemicals Ltd  -  Nairobi", F["body"], 8,
        CYAN_LT, "r")
    c.showPage()

    # ---- 2. views ---------------------------------------------------------
    # A pack gets approved once, so the faces nobody has been shown - the
    # back, the far flank, the top - go in front of the client here rather
    # than being discovered on press.
    rect(c, 0, 0, PW, PH, WHITE)
    page_header(c, full + "  -  Views", "Six angles from one camera rig",
                2, total)
    page_footer(c, "renders, not photography")
    vsheet = os.path.join(VIEWS, "Carton_ALL_VIEWS.png")
    if os.path.exists(vsheet):
        c.drawImage(vsheet, p(M), p(16), p(PW - 2 * M), p(PH - 52),
                    mask="auto", preserveAspectRatio=True, anchor="c")
    c.showPage()

    # ---- 3. panels --------------------------------------------------------
    rect(c, 0, 0, PW, PH, WHITE)
    page_header(c, full + "  -  Panels", "Every printed face, at a common "
                "scale", 3, total)
    page_footer(c, "vector artwork, clipped from the print file")
    ph_ = 196.0
    scale = ph_ / H_BODY
    gap = 7.0
    widths = [(W_FACE, "FRONT"), (W_SIDE, "SIDE  -  benefits"),
              (W_FACE, "BACK"), (W_SIDE, "SIDE  -  retail")]
    xs = [X_FRNT, X_SIDL, X_BACK, X_SIDR]
    total_w = sum(w * scale for w, _ in widths) + gap * 3
    cx0 = (PW - total_w) / 2
    ytop = PH - 44
    for (pw_, lab), sx in zip(widths, xs):
        dw = pw_ * scale
        place(2, (cx0, ytop - ph_, dw, ph_), art,
              (sx + O, Y_BODY + O, pw_, H_BODY))
        frame(c, cx0, ytop - ph_, dw, ph_)
        caption(c, cx0, ytop + 3.0, dw, lab, "%g mm" % pw_)
        cx0 += dw + gap
    txt(c, M, 20, "Panels are shown at one scale so proportions can be "
        "compared directly. Fold lines fall on the frame edges.",
        F["body"], 8, GREY)
    c.showPage()

    # ---- 3. flaps and features -------------------------------------------
    rect(c, 0, 0, PW, PH, WHITE)
    page_header(c, full + "  -  Flaps & features", "Hang tab, tuck flap and "
                "the scent vents", 4, total)
    page_footer(c, "all die features shown at true proportion")

    TOP = PH - 40.0               # everything hangs off one line, clear of
                                  # the header band at PH-22

    # hang tab
    dw, dh = place_scaled(2, M, TOP - 52.0, art,
                          (TAB_X0 + O, Y_TOP + O, TAB_W, H_HANG), 2.0)
    frame(c, M, TOP - 52.0, dw, dh)
    caption(c, M, TOP - 52.0 + dh + 3.5, dw, "EURO HANG TAB",
            "%g x %g mm" % (TAB_W, H_HANG))
    ty = para(c, M, TOP - 59.0,
              "A straight extension of the back panel with no crease at its "
              "base. Creasing it there is what makes hang tabs tear off. "
              "That choice pushes both tuck ends onto the front panel, which "
              "is why this is a straight tuck end rather than a reverse "
              "tuck. The euro slot leaves 7.8 mm of headroom; under about "
              "6 mm a peg hole tears out of the board.",
              F["body"], 8, INK, dw + 14, 4.6)

    # top tuck flap
    tx = M + 160.0
    dw2, dh2 = place_scaled(2, tx, TOP - 54.0, art,
                            (X_FRNT + O, Y_TOP + O, W_FACE, H_TUCK), 1.2)
    frame(c, tx, TOP - 54.0, dw2, dh2)
    caption(c, tx, TOP - 54.0 + dh2 + 3.5, dw2, "TOP TUCK FLAP",
            "%g x %g mm" % (W_FACE, H_TUCK))
    para(c, tx, TOP - 61.0,
         "Every flap carries the mark. A tuck is the first face anyone sees "
         "opening a case and the dust flaps show when a carton sits half "
         "open on shelf, so leaving them plain wasted four printed "
         "surfaces.", F["body"], 8, INK, dw2 + 20, 4.6)

    # scent vents
    vy = 44.0
    dw3, dh3 = place_scaled(2, M, vy, art,
                            (X_SIDR + O, 86 + O, W_SIDE, 28), 2.6)
    frame(c, M, vy, dw3, dh3)
    caption(c, M, vy + dh3 + 3.5, dw3, "SCENT VENTS",
            "%d per side panel" % VENT_N)
    para(c, M + dw3 + 14, vy + dh3 - 4.0,
         "The product is bought on smell and a sealed carton releases none "
         "of it. Five droplet cut-outs per side panel let the scent out - "
         "droplets rather than drilled holes, so the die feature doubles as "
         "a brand mark. They sit in a band kept clear of copy: a vertical "
         "column down a 48 mm panel runs straight through the text. Knocked "
         "out white in the artwork so proofs read as holes; the die removes "
         "them in any case.",
         F["body"], 8, INK, PW - M * 2 - dw3 - 14, 4.6)
    c.showPage()

    # ---- 4. flat blank ----------------------------------------------------
    rect(c, 0, 0, PW, PH, WHITE)
    page_header(c, full + "  -  Flat blank", "Printed artwork, as it reaches "
                "the converter", 5, total)
    page_footer(c, "artwork only; no guide layers print")
    # fit BOTH axes: scaling to width alone made the blank 298 mm tall on a
    # 297 mm page, so it covered its own header
    sheet_w, sheet_h = SHEET_W + 2 * BLEED, SHEET_H + 2 * BLEED
    bs = min((PW - 2 * M) / sheet_w, (PH - 52) / sheet_h)
    bw, bh = sheet_w * bs, sheet_h * bs
    by = (PH - 32 - bh) / 2 + 6
    bx = (PW - bw) / 2
    place(4, (bx, by, bw, bh), art, (0, 0, sheet_w, sheet_h))
    frame(c, bx, by, bw, bh)
    txt(c, bx, by + bh + 4.0, "Flat blank %g x %g mm plus %g mm bleed"
        % (SHEET_W, SHEET_H, BLEED), F["bodysemi"], 8.4, NAVY)
    c.showPage()

    # ---- 5. dieline plan --------------------------------------------------
    rect(c, 0, 0, PW, PH, WHITE)
    page_header(c, full + "  -  Dieline", "Cut and fold only; for approval "
                "and die check", 6, total)
    page_footer(c, "NOT for printing - guide layers are live objects")
    src = pymupdf.open(plan)
    sp = src[0].rect
    src.close()
    pw_mm, ph_mm = sp.width / MM, sp.height / MM
    ds = min((PW - 2 * M) / pw_mm, (PH - 46) / ph_mm)
    dw, dh = pw_mm * ds, ph_mm * ds
    place(5, ((PW - dw) / 2, (PH - 32 - dh) / 2 + 6, dw, dh), plan,
          (0, 0, pw_mm, ph_mm))
    c.showPage()

    # ---- 6. specification -------------------------------------------------
    rect(c, 0, 0, PW, PH, WHITE)
    page_header(c, full + "  -  Specification", "Everything a converter and a "
                "printer need", 7, total)
    page_footer(c, "confirm die and substrate before plates")
    col1, col2 = M, PW / 2 + 6
    yy = PH - 42
    txt(c, col1, yy, "STRUCTURE", F["subhead"], 9, NAVY, track=0.5)
    yy -= 7
    for lab, val in (("Style", "Straight tuck end (STE) with euro hang tab"),
                     ("Carton", "105 W x 48 D x 155 H mm"),
                     ("Flat blank", "%g x %g mm" % (SHEET_W, SHEET_H)),
                     ("Bleed", "%g mm all round" % BLEED),
                     ("Safe area", "%g mm inside every cut and crease" % SAFE),
                     ("Glue tab", "%g mm, unprinted and varnish-free" % W_GLUE),
                     ("Hang tab", "%g x %g mm, euro slot, 7.8 mm headroom"
                      % (TAB_W, H_HANG)),
                     ("Vents", "%d droplet cut-outs per side panel" % VENT_N),
                     ("Outer", "12-count RSC, 319 x 196 x 160 mm")):
        txt(c, col1, yy, lab, F["bodysemi"], 7.6, BLUE_MID)
        txt(c, col1 + 34, yy, val, F["body"], 8, INK)
        yy -= 6.4

    yy -= 6
    txt(c, col1, yy, "COLOUR", F["subhead"], 9, NAVY, track=0.5)
    yy -= 20
    swatch_row(c, col1, yy, ((NAVY, "Ground", "C100 M85 Y10 K15"),
                            (BLUE_BR, "Water", "C85 M40 Y0 K0"),
                            (YELLOW, "Accent", "C0 M12 Y100 K0"),
                            (RED, "Signal", "C0 M95 Y90 K0")))
    yy -= 12
    para(c, col1, yy, "Mixes are hand-specified, not machine-converted from "
         "RGB: a naive conversion of the navy prints muddy. Total ink stays "
         "under 300%. Soft-proof against the press profile before plates.",
         F["body"], 7.6, GREY, PW / 2 - M - 10, 4.4)

    yy2 = PH - 42
    txt(c, col2, yy2, "TYPOGRAPHY", F["subhead"], 9, NAVY, track=0.5)
    yy2 -= 8
    for nm, fnt, sz in (("Display", F["display"], 17),
                        ("Headings", F["head"], 13),
                        ("Body", F["body"], 10)):
        txt(c, col2, yy2, "Swift Blue-Drop", fnt, sz, NAVY)
        txt(c, col2 + 92, yy2, nm, F["bodysemi"], 7.4, GREY)
        yy2 -= sz * 0.62
    yy2 -= 6
    para(c, col2, yy2, "Outfit and Plus Jakarta Sans, both SIL Open Font "
         "License 1.1, so they may be embedded in commercial packaging "
         "without a foundry licence. Arial and Segoe UI were avoided: "
         "Microsoft-licensed and murkier on client artwork.",
         F["body"], 7.6, GREY, PW / 2 - M - 10, 4.4)

    yy2 -= 16
    txt(c, col2, yy2, "ARTWORK", F["subhead"], 9, NAVY, track=0.5)
    yy2 -= 7
    for lab, val in (("Type", "Live text, embedded subsets - not outlined"),
                     ("Scene", "One composed photograph, 300 dpi"),
                     ("Product", "Photographic, from the client card"),
                     ("Illustration", "Flat vector, one stroke weight"),
                     ("Logos", "Swift and Vistex, placed from brand assets")):
        txt(c, col2, yy2, lab, F["bodysemi"], 7.6, BLUE_MID)
        txt(c, col2 + 34, yy2, val, F["body"], 8, INK)
        yy2 -= 6.4

    yy2 -= 8
    rect(c, col2, yy2 - 48, PW / 2 - M - 6, 52, RED, alpha=0.06)
    txt(c, col2 + 4, yy2 - 4, "BEFORE PLATES", F["subhead"], 8.4, RED,
        track=0.5)
    ry = yy2 - 12
    for t in ("Replace the product shot: the blocks are ~160 dpi at pack "
              "size, lifted from the client card.",
              "Barcode: removed on request. Most retailers require an "
              "EAN-13; confirm before launch.",
              "Regulatory copy is drafted, not legally reviewed.",
              "Carton and case dimensions are sensible retail sizes, not "
              "measured dies. Confirm with the converter."):
        c.setFillColor(RED)
        c.circle(p(col2 + 6), p(ry + 0.9), p(0.6), fill=1, stroke=0)
        ry = para(c, col2 + 9, ry, t, F["body"], 7.4, INK,
                  PW / 2 - M - 22, 4.2) - 1.0
    c.showPage()

    # ---- 7. dimensioned production drawing -------------------------------
    spec = os.path.join(SPEC, "Swift_Blue-Drop_Carton_SPEC.pdf")
    if os.path.exists(spec):
        rect(c, 0, 0, PW, PH, WHITE)
        page_header(c, full + "  -  Production drawing",
                    "Dimensioned die specification, 1:1 at A2", 8, total)
        page_footer(c, "the sheet a toolmaker works from")
        src = pymupdf.open(spec)
        sp = src[0].rect
        src.close()
        pw_mm, ph_mm = sp.width / MM, sp.height / MM
        ds = min((PW - 2 * M) / pw_mm, (PH - 48) / ph_mm)
        place(7, ((PW - pw_mm * ds) / 2, (PH - 32 - ph_mm * ds) / 2 + 6,
                  pw_mm * ds, ph_mm * ds), spec, (0, 0, pw_mm, ph_mm))
        txt(c, M, 15, "Reproduced here at reduced size. The 1:1 sheet is "
            "dist/spec/Swift_Blue-Drop_Carton_SPEC.pdf", F["body"], 7.4, GREY)
        c.showPage()

    c.save()
    return path


def doc_shipper(path):
    PLACE[:] = []
    art = os.path.join(SHIPD, "Swift_Blue-Drop_12ct_Shipper_PRINT.pdf")
    plan = os.path.join(SHIPD, "Swift_Blue-Drop_12ct_Shipper_PLAN.pdf")
    fam = os.path.join(FAM, "Swift_Blue-Drop_Family.png")
    spec = os.path.join(SPEC, "Swift_Blue-Drop_Shipper_SPEC.pdf")
    sviews = os.path.join(VIEWS, "Shipper_ALL_VIEWS.png")
    total = 3 + (1 if os.path.exists(spec) else 0) \
              + (1 if os.path.exists(sviews) else 0)
    c = _cv.Canvas(path, pagesize=(p(PW), p(PH)))
    c.setTitle("Swift Blue-Drop - 12-count shipper")
    c.setAuthor("Vistex Chemicals Ltd")
    c.setCreator("packaging/make_document.py")

    rect(c, 0, 0, PW, PH, NAVY)
    txt(c, M, PH - 42, "SWIFT BLUE-DROP", F["head"], 24, WHITE, track=1.3)
    txt(c, M, PH - 54, "12-count shipper  -  outer case", F["subhead"], 13,
        CYAN_LT)
    rect(c, M, PH - 62, 56, 1.0, CYAN)
    if os.path.exists(fam):
        c.drawImage(fam, p(M), p(70), p(PW - 2 * M), p(PH - 150),
                    mask="auto", preserveAspectRatio=True, anchor="c")
    xx = M
    for lab, val in (("Case", "319 x 196 x 160 mm internal"),
                     ("Holds", "12 retail cartons (3 across x 4 deep)"),
                     ("Net", "2.4 kg of product"),
                     ("Blank", "1070 x 356 mm"),
                     ("Board", "B or BC flute recommended")):
        txt(c, xx, 46, lab.upper(), F["bodysemi"], 7.0, CYAN, track=0.5)
        txt(c, xx, 38, val, F["body"], 8.2, WHITE)
        xx += 78
    para(c, M, 26, "Sized from the retail carton, not guessed: 3 across x 4 "
         "deep gives the squarest footprint for a 105 x 48 mm carton. 4 x 3 "
         "and 2 x 6 both produce long thin cases that pallet badly and crush "
         "in the middle.", F["body"], 8, CYAN_LT, PW - 2 * M, 4.6)
    c.showPage()

    if os.path.exists(sviews):
        rect(c, 0, 0, PW, PH, WHITE)
        page_header(c, "12-count shipper  -  Views",
                    "Six angles from one camera rig", 2, total)
        page_footer(c, "renders, not photography")
        c.drawImage(sviews, p(M), p(16), p(PW - 2 * M), p(PH - 52),
                    mask="auto", preserveAspectRatio=True, anchor="c")
        c.showPage()

    rect(c, 0, 0, PW, PH, WHITE)
    page_header(c, "12-count shipper  -  Flat blank", "Printed artwork", 3,
                total)
    page_footer(c, "regular slotted container")
    src = pymupdf.open(art)
    sp = src[0].rect
    src.close()
    pw_mm, ph_mm = sp.width / MM, sp.height / MM
    ds = min((PW - 2 * M) / pw_mm, (PH - 50) / ph_mm)
    place(2, ((PW - pw_mm * ds) / 2, (PH - 32 - ph_mm * ds) / 2 + 6,
              pw_mm * ds, ph_mm * ds), art, (0, 0, pw_mm, ph_mm))
    c.showPage()

    rect(c, 0, 0, PW, PH, WHITE)
    page_header(c, "12-count shipper  -  Dieline", "Cut, slot and fold", 3,
                total)
    page_footer(c, "NOT for printing")
    src = pymupdf.open(plan)
    sp = src[0].rect
    src.close()
    pw_mm, ph_mm = sp.width / MM, sp.height / MM
    ds = min((PW - 2 * M) / pw_mm, (PH - 50) / ph_mm)
    place(3, ((PW - pw_mm * ds) / 2, (PH - 32 - ph_mm * ds) / 2 + 6,
              pw_mm * ds, ph_mm * ds), plan, (0, 0, pw_mm, ph_mm))
    c.showPage()

    if os.path.exists(spec):
        rect(c, 0, 0, PW, PH, WHITE)
        page_header(c, "12-count shipper  -  Production drawing",
                    "Dimensioned die specification, 1:2 at A2", 5, total)
        page_footer(c, "the sheet a toolmaker works from")
        src = pymupdf.open(spec)
        sp = src[0].rect
        src.close()
        pw_mm, ph_mm = sp.width / MM, sp.height / MM
        ds = min((PW - 2 * M) / pw_mm, (PH - 48) / ph_mm)
        place(4, ((PW - pw_mm * ds) / 2, (PH - 32 - ph_mm * ds) / 2 + 6,
                  pw_mm * ds, ph_mm * ds), spec, (0, 0, pw_mm, ph_mm))
        c.showPage()

    c.save()
    return path


# ---------------------------------------------------------------------------
# pass 2 - stamp the vector artwork in
# ---------------------------------------------------------------------------

def stamp(path, placements):
    doc = pymupdf.open(path)
    opened = {}
    for pno, dest, src_pdf, clip in placements:
        if src_pdf not in opened:
            opened[src_pdf] = pymupdf.open(src_pdf)
        src = opened[src_pdf]
        page = doc[pno]
        dx, dy, dw, dh = dest
        # ReportLab y is from the bottom; fitz y is from the top
        r = pymupdf.Rect(dx * MM, (PH - dy - dh) * MM,
                         (dx + dw) * MM, (PH - dy) * MM)
        sh = src[0].rect.height
        cx, cy, cw, ch = clip
        cr = pymupdf.Rect(cx * MM, sh - (cy + ch) * MM,
                          (cx + cw) * MM, sh - cy * MM)
        page.show_pdf_page(r, src, 0, clip=cr)
    doc.saveIncr()
    doc.close()
    for d in opened.values():
        d.close()


def main():
    register_fonts()
    os.makedirs(OUT, exist_ok=True)
    made = []
    for letter, name, blurb in CONCEPTS:
        src = os.path.join(INTEG, "Concept_%s_%s.pdf" % (letter, name))
        if not os.path.exists(src):
            print("skip %s (no artwork)" % letter)
            continue
        out = os.path.join(OUT, "Swift_Blue-Drop_%s_%s.pdf" % (letter, name))
        doc_concept(letter, name, blurb, out)
        stamp(out, list(PLACE))
        made.append(out)
    out = os.path.join(OUT, "Swift_Blue-Drop_Shipper_12ct.pdf")
    doc_shipper(out)
    stamp(out, list(PLACE))
    made.append(out)
    for m in made:
        d = pymupdf.open(m)
        print("%-44s %2d pp  %6.1f KB" %
              (os.path.basename(m), d.page_count,
               os.path.getsize(m) / 1024.0))
        d.close()
    print("")
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
