#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swift Blue-Drop - 12-count shipper (outer case).

A regular slotted container (RSC): the universal shipping box. One blank,
four panels, eight flaps, all flaps half the case depth so the top pair meet
down the middle and tape seals one seam.

Sized from the retail carton rather than guessed. 3 across x 4 deep gives the
squarest footprint for a 105 x 48 mm carton; 4 x 3 or 2 x 6 both produce long
thin cases that pallet badly and crush at the middle.

Print is deliberately plainer than the retail pack: a shipper is read from
three metres away in a stockroom, so it carries identity, count and handling
marks and nothing else. Full-bleed photography on an outer is money spent
where no shopper ever looks.

Output
------
  dist/shipper/Swift_Blue-Drop_12ct_Shipper_PRINT.pdf
  dist/shipper/Swift_Blue-Drop_12ct_Shipper_PLAN.pdf

Run:  python packaging/swift_shipper.py
"""

import os

from reportlab.pdfgen import canvas as _cv
from reportlab.lib.utils import ImageReader
from PIL import Image

from swift_blue_drop_dieline import (MM, F, register_fonts, HERE, ROOT, DIST,
                                     NAVY, NAVY_DK, NAVY_MID, BLUE_MID,
                                     BLUE_BR, CYAN, CYAN_LT, WHITE, YELLOW,
                                     RED, GREY, CUT, CREASE,
                                     W_FACE as R_W, W_SIDE as R_D,
                                     H_BODY as R_H)
import swift_blue_drop_dieline as B

ART = os.path.join(HERE, "art")
SCENE_W, SCENE_H = 107.0, 157.0      # must match make_scene.py
BRAND = os.path.join(ROOT, "images", "logo")
_CACHE = {}

# ---------------------------------------------------------------------------
# 1. CASE SPEC - derived from the retail carton, not invented
# ---------------------------------------------------------------------------
ACROSS, DEEP, HIGH = 3, 4, 1          # retail cartons per case
CLEAR = 4.0                           # total slack per axis, for fit

CASE_L = ACROSS * R_W + CLEAR         # 319 front/back panel width
CASE_W = DEEP * R_D + CLEAR           # 196 side panel width
CASE_H = HIGH * R_H + 5.0             # 160 internal height
COUNT = ACROSS * DEEP * HIGH          # 12
NET_KG = COUNT * 0.200                # 2.4 kg of product

GLUE = 40.0                           # manufacturer joint
FLAP = CASE_W / 2.0                   # RSC: flaps meet down the middle
BLEED = 3.0
SAFE = 12.0                           # shippers get knocked about; keep clear

# panel origins, left to right: front | side | back | side | glue
X_FRONT = 0.0
X_SIDE1 = X_FRONT + CASE_L
X_BACK = X_SIDE1 + CASE_W
X_SIDE2 = X_BACK + CASE_L
X_GLUE = X_SIDE2 + CASE_W
SHEET_W = X_GLUE + GLUE
SHEET_H = CASE_H + 2 * FLAP
Y_BODY = FLAP
Y_TOP = Y_BODY + CASE_H

ORIGIN = [BLEED]


def P(v):
    return (v + ORIGIN[0]) * MM


# ---------------------------------------------------------------------------
# 2. HELPERS (local P, so the retail module's helpers cannot be reused)
# ---------------------------------------------------------------------------

def _img(name, tint=None):
    key = (name, tint)
    if key not in _CACHE:
        path = os.path.join(ART, name + ".png")
        if not os.path.exists(path):
            path = os.path.join(BRAND, name + ".png")
        im = Image.open(path).convert("RGBA")
        if tint:
            flat = Image.new("RGBA", im.size, tint + (255,))
            flat.putalpha(im.getchannel("A"))
            im = flat
        _CACHE[key] = ImageReader(im)
    return _CACHE[key]


def clip_rect(c, x, y, w, h):
    pth = c.beginPath()
    pth.rect(P(x), P(y), w * MM, h * MM)
    c.clipPath(pth, stroke=0, fill=0)


def scene_fill(c, x, y, w, h, key="vortex", veil=0.30):
    """The retail photograph, stretched across a case panel and veiled back.

    A shipper is read from three metres in a stockroom, so the picture is
    atmosphere only: at full strength it swallows the count, which is the
    one thing a storeman is actually looking for.
    """
    path = os.path.join(ART, "scene-%s.png" % key)
    if not os.path.exists(path):
        rect(c, x, y, w, h, NAVY)
        return
    c.saveState()
    clip_rect(c, x, y, w, h)
    img = _img("scene-" + key)
    iw, ih = img.getSize()
    # cover the panel, anchored low so the product sits in the lower half
    sc = max(w / SCENE_W, h / SCENE_H)
    dw, dh = SCENE_W * sc, SCENE_H * sc
    c.drawImage(img, P(x + (w - dw) / 2), P(y + (h - dh) * 0.62),
                dw * MM, dh * MM, mask="auto")
    c.setFillColor(NAVY, veil)
    c.rect(P(x), P(y), w * MM, h * MM, fill=1, stroke=0)
    c.restoreState()


def seal(c, cx, cy, r=17.0):
    """The retail 30 DAYS seal, scaled up for the case."""
    k = r / 13.6
    for kk, a in ((1.12, 0.07), (1.05, 0.09), (1.0, 0.11)):
        c.saveState()
        c.setFillColor(NAVY_DK, a)
        c.circle(P(cx + 0.6), P(cy - 0.8), r * kk * MM, fill=1, stroke=0)
        c.restoreState()
    c.saveState()
    c.setFillColor(WHITE, 0.97)
    c.circle(P(cx), P(cy), r * MM, fill=1, stroke=0)
    c.setStrokeColor(CYAN, 0.9)
    c.setLineWidth(0.9 * MM)
    c.circle(P(cx), P(cy), (r - 1.9) * MM, fill=0, stroke=1)
    c.setStrokeColor(BLUE_MID, 0.35)
    c.setLineWidth(0.3 * MM)
    c.circle(P(cx), P(cy), (r - 3.6) * MM, fill=0, stroke=1)
    c.restoreState()
    txt(c, cx, cy + 5.8 * k, "ONE BLOCK", F["subhead"], 6.4 * k, BLUE_MID,
        "c", char_space=0.6 * k)
    c.saveState()
    c.setStrokeColor(CYAN, 0.65)
    c.setLineWidth(0.4 * MM)
    c.line(P(cx - 6.6 * k), P(cy + 4.0 * k), P(cx + 6.6 * k), P(cy + 4.0 * k))
    c.restoreState()
    txt(c, cx, cy - 4.2 * k, "30", F["display"], 26 * k, NAVY, "c")
    txt(c, cx, cy - 10.2 * k, "DAYS", F["head"], 9.4 * k, BLUE_MID, "c",
        char_space=1.0 * k)


def droplet(c, cx, cy, h):
    """Brand droplet, flat - a case does not need the glass treatment."""
    r = h * 0.335
    by = cy - h * 0.5 + r
    c.saveState()
    c.setFillColor(CYAN_LT, 0.95)
    pth = c.beginPath()
    pth.moveTo(P(cx), P(cy + h * 0.5))
    pth.curveTo(P(cx + r * 0.30), P(cy + h * 0.20),
                P(cx + r * 0.95), P(by + r * 0.80), P(cx + r), P(by))
    pth.curveTo(P(cx + r), P(by - r * 1.336), P(cx - r), P(by - r * 1.336),
                P(cx - r), P(by))
    pth.curveTo(P(cx - r * 0.95), P(by + r * 0.80),
                P(cx - r * 0.30), P(cy + h * 0.20), P(cx), P(cy + h * 0.5))
    pth.close()
    c.drawPath(pth, fill=1, stroke=0)
    c.restoreState()


def rect(c, x, y, w, h, colour, alpha=1.0):
    c.saveState()
    c.setFillColor(colour, alpha)
    c.rect(P(x), P(y), w * MM, h * MM, fill=1, stroke=0)
    c.restoreState()


def pill(c, x, y, w, h, colour, r=None, alpha=1.0):
    c.saveState()
    c.setFillColor(colour, alpha)
    c.roundRect(P(x), P(y), w * MM, h * MM,
                (r if r is not None else h / 2) * MM, fill=1, stroke=0)
    c.restoreState()


def line(c, x1, y1, x2, y2, colour, lw, alpha=1.0, dash=None):
    c.saveState()
    c.setStrokeColor(colour, alpha)
    c.setLineWidth(lw * MM)
    c.setLineCap(1)
    if dash:
        c.setDash([d * MM for d in dash], 0)
    c.line(P(x1), P(y1), P(x2), P(y2))
    c.restoreState()


def poly(c, pts, colour, alpha=1.0):
    c.saveState()
    c.setFillColor(colour, alpha)
    p = c.beginPath()
    p.moveTo(P(pts[0][0]), P(pts[0][1]))
    for px, py in pts[1:]:
        p.lineTo(P(px), P(py))
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def sw(t, f, s):
    from reportlab.pdfbase import pdfmetrics
    return pdfmetrics.stringWidth(t, f, s)


def txt(c, x, y, t, font, size, colour, align="l", char_space=0.0):
    w = sw(t, font, size) + char_space * max(0, len(t) - 1)
    px = P(x) - (w / 2 if align == "c" else w if align == "r" else 0)
    c.setFillColor(colour)
    if char_space:
        to = c.beginText(px, P(y))
        to.setFont(font, size)
        to.setCharSpace(char_space)
        to.textLine(t)
        to.setCharSpace(0)
        c.drawText(to)
    else:
        c.setFont(font, size)
        c.drawString(px, P(y), t)
    return w / MM


def logo(c, name, cx, cy, w, tint=None):
    img = _img(name, tint)
    iw, ih = img.getSize()
    h = w * ih / iw
    c.drawImage(img, P(cx - w / 2), P(cy - h / 2), w * MM, h * MM,
                mask="auto")
    return h


# ---------------------------------------------------------------------------
# 3. HANDLING MARKS - drawn, because ISO 780 symbols are not a typeface
# ---------------------------------------------------------------------------

def mark_this_way_up(c, cx, cy, s, colour=WHITE):
    c.saveState()
    c.setStrokeColor(colour, 0.95)
    c.setLineWidth(s * 0.05 * MM)
    c.setLineCap(0)
    c.rect(P(cx - s * 0.30), P(cy - s * 0.42), s * 0.60 * MM, s * 0.84 * MM,
           fill=0, stroke=1)
    c.restoreState()
    for sx in (-1, 1):
        ax = cx + sx * s * 0.16
        line(c, ax, cy - s * 0.22, ax, cy + s * 0.18, colour, s * 0.045)
        poly(c, [(ax, cy + s * 0.32), (ax - s * 0.10, cy + s * 0.16),
                 (ax + s * 0.10, cy + s * 0.16)], colour)


def mark_keep_dry(c, cx, cy, s, colour=WHITE):
    c.saveState()
    c.setStrokeColor(colour, 0.95)
    c.setLineWidth(s * 0.05 * MM)
    c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(P(cx - s * 0.34), P(cy + s * 0.02))
    p.curveTo(P(cx - s * 0.30), P(cy + s * 0.34),
              P(cx + s * 0.30), P(cy + s * 0.34),
              P(cx + s * 0.34), P(cy + s * 0.02))
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()
    for k in (-0.18, 0.0, 0.18):
        line(c, cx + k * s, cy - s * 0.06, cx + k * s, cy - s * 0.30,
             colour, s * 0.045)


def mark_stack(c, cx, cy, s, n=4, colour=WHITE):
    c.saveState()
    c.setStrokeColor(colour, 0.95)
    c.setLineWidth(s * 0.05 * MM)
    c.rect(P(cx - s * 0.30), P(cy - s * 0.40), s * 0.60 * MM, s * 0.80 * MM,
           fill=0, stroke=1)
    c.restoreState()
    txt(c, cx, cy - s * 0.10, str(n), F["bodyblk"], s * 1.5, colour, "c")


# ---------------------------------------------------------------------------
# 4. PANELS
# ---------------------------------------------------------------------------

def panel_front(c, x):
    """The retail face, case-scaled.

    Zoned rather than placed by eye: the first pass dropped the Vistex logo,
    the handling marks and their caption into the same bottom-left corner
    and all three overlapped.

        y 100..155   masthead - Swift mark, Blue-Drop, descriptor
        y  30..120   count block and the 30 DAYS seal, right
        y   0..32    Vistex mark left, handling marks right
    """
    w, h = CASE_L, CASE_H
    y = Y_BODY
    scene_fill(c, x, y, w, h, veil=0.34)
    rect(c, x, y + h - 3.0, w, 3.0, CYAN, alpha=0.5)
    for i in range(14):
        t = i / 13.0
        rect(c, x, y + h - 58.0 * (1 - t), w, 58.0 * (1 - t), NAVY_DK,
             alpha=0.055)
    for i in range(12):
        t = i / 11.0
        rect(c, x, y, w, 42.0 * (1 - t), NAVY_DK, alpha=0.06)

    # ---- masthead ---------------------------------------------------------
    logo(c, "swift-logo", x + 56, y + 130, 84)
    txt(c, x + 16, y + 92, "Blue-Drop", F["display"], 54, WHITE)
    droplet(c, x + 182, y + 99, 28)
    txt(c, x + 18, y + 77, "AUTOMATIC TOILET BOWL CLEANER", F["label"], 13,
        CYAN_LT, char_space=1.2)

    # ---- seal and count ---------------------------------------------------
    seal(c, x + 268, y + 100, 23.0)
    bx, bw = x + 182, 116.0
    pill(c, bx, y + 32, bw, 38.0, WHITE, r=3.0)
    txt(c, bx + bw / 2, y + 32 + 22.5, str(COUNT) + " CARTONS", F["head"],
        22, NAVY, "c")
    txt(c, bx + bw / 2, y + 32 + 13.0, "4 x 50 g each", F["bodysemi"], 12,
        BLUE_MID, "c")
    txt(c, bx + bw / 2, y + 32 + 3.8, "NET " + ("%.1f" % NET_KG) + " kg",
        F["bodyblk"], 13.5, NAVY, "c")

    # ---- foot: maker left, handling right ---------------------------------
    logo(c, "vistex-logo-white", x + 54, y + 17, 78)
    for i, fn in enumerate((mark_this_way_up, mark_keep_dry, mark_stack)):
        fn(c, x + 164 + i * 38, y + 17, 21)
    txt(c, x + w - 16, y + 6, "THIS WAY UP   KEEP DRY   MAX 4 HIGH",
        F["bodysemi"], 8.0, CYAN_LT, "r")


def panel_back(c, x):
    w, h = CASE_L, CASE_H
    y = Y_BODY
    scene_fill(c, x, y, w, h, veil=0.52)
    rect(c, x, y + h - 2.5, w, 2.5, CYAN, alpha=0.5)
    logo(c, "swift-logo", x + w / 2, y + h * 0.72, 74)
    txt(c, x + w / 2, y + h * 0.48, "Blue-Drop", F["display"], 46, WHITE, "c")
    txt(c, x + w / 2, y + h * 0.38, "FLUSH-ACTIVATED WC CLEANER - 4 x 50 g",
        F["label"], 11, CYAN_LT, "c", char_space=1.0)

    # despatch fields, overprinted at pack-out
    fy = y + h * 0.30
    fw = (w - 60) / 3.0
    for i, lab in enumerate(("BATCH No.", "PACKED", "BEST BEFORE")):
        fx = x + 30 + i * fw
        txt(c, fx, fy, lab, F["bodysemi"], 9, CYAN_LT)
        line(c, fx, fy - 3.5, fx + fw - 14, fy - 3.5, WHITE, 0.4, alpha=0.5)
    txt(c, x + 30, y + 22, "Store upright in a cool, dry place.",
        F["body"], 9, WHITE)
    rc = _img("recycle-outline", (255, 255, 255))
    iw, ih = rc.getSize()
    c.drawImage(rc, P(x + w - 56), P(y + 14), 26 * MM, 26 * ih / iw * MM,
                mask="auto")


def panel_side(c, x):
    w, h = CASE_W, CASE_H
    y = Y_BODY
    scene_fill(c, x, y, w, h, veil=0.42)
    for i in range(12):
        t = i / 11.0
        rect(c, x, y + h - 48.0 * (1 - t), w, 48.0 * (1 - t), NAVY_DK,
             alpha=0.06)
        rect(c, x, y, w, 34.0 * (1 - t), NAVY_DK, alpha=0.06)
    logo(c, "swift-logo", x + w / 2, y + h * 0.76, 74)
    txt(c, x + w / 2, y + h * 0.54, "Blue-Drop", F["display"], 38, WHITE, "c")
    txt(c, x + w / 2, y + h * 0.46, "AUTOMATIC TOILET BOWL CLEANER",
        F["label"], 8.0, CYAN_LT, "c", char_space=0.9)
    pill(c, x + w / 2 - 40, y + h * 0.26, 80, 23, WHITE, r=2.5)
    txt(c, x + w / 2, y + h * 0.26 + 13.0, str(COUNT) + " CARTONS",
        F["head"], 13, NAVY, "c")
    txt(c, x + w / 2, y + h * 0.26 + 5.0, "4 x 50 g each", F["bodysemi"],
        9, BLUE_MID, "c")
    txt(c, x + w / 2, y + 26, "NET " + ("%.1f" % NET_KG) + " kg",
        F["bodyblk"], 12, WHITE, "c")
    mark_this_way_up(c, x + w / 2, y + h * 0.085, 19)


def flaps(c):
    for x, wd in ((X_FRONT, CASE_L), (X_SIDE1, CASE_W),
                  (X_BACK, CASE_L), (X_SIDE2, CASE_W)):
        rect(c, x, Y_TOP, wd, FLAP, NAVY_DK)
        rect(c, x, Y_BODY - FLAP, wd, FLAP, NAVY_DK)
        if wd == CASE_L:
            logo(c, "swift-logo", x + wd / 2, Y_TOP + FLAP * 0.55, 60)
            txt(c, x + wd / 2, Y_TOP + FLAP * 0.22,
                "SWIFT BLUE-DROP   -   " + str(COUNT) + " x 4 x 50 g",
                F["bodysemi"], 9, CYAN_LT, "c", char_space=0.8)
            logo(c, "swift-logo", x + wd / 2, Y_BODY - FLAP * 0.45, 60)
    rect(c, X_GLUE, Y_BODY, GLUE, CASE_H, WHITE)


# ---------------------------------------------------------------------------
# 5. PLAN
# ---------------------------------------------------------------------------

def outline():
    return [(X_FRONT, Y_BODY - FLAP), (SHEET_W, Y_BODY - FLAP),
            (SHEET_W, Y_TOP + FLAP), (X_FRONT, Y_TOP + FLAP)]


def draw_plan(c):
    c.saveState()
    c.setStrokeColor(CUT)
    c.setLineWidth(1.0)
    pts = outline()
    p = c.beginPath()
    p.moveTo(P(pts[0][0]), P(pts[0][1]))
    for px, py in pts[1:]:
        p.lineTo(P(px), P(py))
    p.close()
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()

    # slots between the flaps - what makes it "slotted"
    c.saveState()
    c.setStrokeColor(CUT)
    c.setLineWidth(1.0)
    for fx in (X_SIDE1, X_BACK, X_SIDE2, X_GLUE):
        c.line(P(fx), P(Y_TOP), P(fx), P(Y_TOP + FLAP))
        c.line(P(fx), P(Y_BODY), P(fx), P(Y_BODY - FLAP))
    c.restoreState()

    # creases
    c.saveState()
    c.setStrokeColor(CREASE)
    c.setLineWidth(0.8)
    c.setDash([6, 4], 0)
    for fx in (X_SIDE1, X_BACK, X_SIDE2, X_GLUE):
        c.line(P(fx), P(Y_BODY - FLAP), P(fx), P(Y_TOP + FLAP))
    c.line(P(X_FRONT), P(Y_TOP), P(SHEET_W), P(Y_TOP))
    c.line(P(X_FRONT), P(Y_BODY), P(SHEET_W), P(Y_BODY))
    c.restoreState()

    for lx, lab in ((X_FRONT + CASE_L / 2, "FRONT"),
                    (X_SIDE1 + CASE_W / 2, "SIDE"),
                    (X_BACK + CASE_L / 2, "BACK"),
                    (X_SIDE2 + CASE_W / 2, "SIDE"),
                    (X_GLUE + GLUE / 2, "JOINT")):
        txt(c, lx, Y_TOP + FLAP + 7.0, lab, F["bodyblk"], 11, CUT, "c")
    for lx, lab in ((X_FRONT + CASE_L / 2, "%g mm" % CASE_L),
                    (X_SIDE1 + CASE_W / 2, "%g mm" % CASE_W),
                    (X_BACK + CASE_L / 2, "%g mm" % CASE_L),
                    (X_SIDE2 + CASE_W / 2, "%g mm" % CASE_W)):
        txt(c, lx, Y_BODY - FLAP - 14.0, lab, F["bodysemi"], 10, CUT, "c")

    lx, ly = -ORIGIN[0] + 8.0, SHEET_H + 33.0
    txt(c, lx, ly, "SWIFT BLUE-DROP  -  %d-COUNT SHIPPER  -  DIELINE" % COUNT,
        F["head"], 15, CUT)
    spec = ("Style: regular slotted container (RSC)",
            "Case: %g L x %g W x %g H mm internal" % (CASE_L, CASE_W, CASE_H),
            "Holds: %d retail cartons, %d across x %d deep"
            % (COUNT, ACROSS, DEEP),
            "Retail carton: %g x %g x %g mm" % (R_W, R_D, R_H),
            "Flat blank: %g x %g mm + %g mm bleed"
            % (SHEET_W, SHEET_H, BLEED),
            "Flaps: %g mm, meeting at the centre" % FLAP,
            "Net product: %.1f kg per case" % NET_KG,
            "Board: B or BC flute recommended; confirm with converter")
    # two columns: nine lines at 5.4 mm leading is 48 mm, and the top margin
    # is only 40 mm, so a single column ran down into the artwork
    half = (len(spec) + 1) // 2
    for col, group in enumerate((spec[:half], spec[half:])):
        sy = ly - 8.0
        for t in group:
            txt(c, lx + col * 150.0, sy, t, F["bodymed"], 9.5, CUT)
            sy -= 5.2
    ky = -ORIGIN[0] + 24.0
    for col, lab, dash in ((CUT, "CUT / SLOT", None),
                           (CREASE, "CREASE / FOLD", [6, 4])):
        c.saveState()
        c.setStrokeColor(col)
        c.setLineWidth(1.4)
        if dash:
            c.setDash(dash, 0)
        c.line(P(lx), P(ky + 1.2), P(lx + 22), P(ky + 1.2))
        c.restoreState()
        txt(c, lx + 26, ky, lab, F["bodysemi"], 10, col)
        ky -= 8.0


# ---------------------------------------------------------------------------

def paint(c):
    rect(c, -BLEED, -BLEED, SHEET_W + 2 * BLEED, SHEET_H + 2 * BLEED, NAVY)
    flaps(c)
    panel_front(c, X_FRONT)
    panel_side(c, X_SIDE1)
    panel_back(c, X_BACK)
    panel_side(c, X_SIDE2)
    rect(c, X_GLUE, Y_BODY, GLUE, CASE_H, WHITE)


def build(path, plan=False):
    ORIGIN[0] = 40.0 if plan else BLEED
    page = ((SHEET_W + 2 * ORIGIN[0]) * MM, (SHEET_H + 2 * ORIGIN[0]) * MM)
    c = _cv.Canvas(path, pagesize=page)
    c.setTitle("Swift Blue-Drop %d-count shipper%s"
               % (COUNT, " - PLAN" if plan else ""))
    c.setAuthor("Vistex Chemicals Ltd")
    c.setCreator("packaging/swift_shipper.py")
    if plan:
        from reportlab.lib.colors import CMYKColor
        c.setFillColor(CMYKColor(0, 0, 0, 0.04))
        c.rect(0, 0, page[0], page[1], fill=1, stroke=0)
    paint(c)
    if plan:
        draw_plan(c)
    c.showPage()
    c.save()
    ORIGIN[0] = BLEED
    return path


def main():
    register_fonts()
    out = os.path.join(DIST, "shipper")
    os.makedirs(out, exist_ok=True)
    stem = "Swift_Blue-Drop_%dct_Shipper" % COUNT
    a = build(os.path.join(out, stem + "_PRINT.pdf"))
    b = build(os.path.join(out, stem + "_PLAN.pdf"), plan=True)
    for p in (a, b):
        print("%-46s %7.1f KB" % (os.path.basename(p),
                                  os.path.getsize(p) / 1024.0))
        B.preview(p, p[:-4] + ".png", dpi=110)
    print("")
    print("case    %g L x %g W x %g H mm, holds %d cartons (%dx%d)"
          % (CASE_L, CASE_W, CASE_H, COUNT, ACROSS, DEEP))
    print("blank   %g x %g mm + %g mm bleed" % (SHEET_W, SHEET_H, BLEED))
    print("net     %.1f kg product per case" % NET_KG)


if __name__ == "__main__":
    main()
