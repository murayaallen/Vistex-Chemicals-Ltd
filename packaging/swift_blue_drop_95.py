#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swift Blue-Drop 4 x 50 g - production carton, 95 x 95 x 20 mm.

The client chose Concept F (Vortex). This is that design re-set for the real
pack: a 95 mm square front, a 20 mm deep carton, and a euro hang tab that
takes the back panel to 115 mm. Everything is drawn here, nothing is placed by
hand, so a dimension change is a one-line edit and a re-run.

What changed from the concept, and why
--------------------------------------
* "30 DAYS" is now "300 FLUSHES", set on a yellow disc in the same yellow as
  the 4 PACK flag, so the two claims read as one family.
* The side panels are 20 mm, not 48 mm, so their type runs vertically. On the
  concept the Swift mark and the Blue-Drop name were drawn over each other:
  the old guard only measured text against text, and the logo is an image.
  The guard here measures every element - text, logos, icons, the seal, the
  QR, the product itself and the die cut-outs - against every other one.
* Every string is held to a 1.2 mm x-height (EU 1169/2011 for packs whose
  largest face is over 80 cm2; this front is 90 cm2). That works out at
  6.4 pt for Plus Jakarta Sans and 7.2 pt for Outfit. The build fails any
  string under it.
* The carton is a straight tuck end (both tucks hinge off the front, because
  the hang tab is an unbroken extension of the back). The concept's tuck
  flaps were shorter than the carton depth and had no lip crease, so they
  could not actually close. Here the closure panel equals the depth and a
  creased 13 mm lip tucks in behind it.

Output (packaging/dist/95mm/)
-----------------------------
  Swift_Blue-Drop_95x95x20_FINAL_PRINT.pdf   p1 artwork + 3 mm bleed, p2 die only
  (the views / folding guide is built by swift_blue_drop_95_guide.py)

Run:  python packaging/swift_blue_drop_95.py
"""

import math
import os
from math import pi, sin, cos, sqrt

import numpy as np
from PIL import Image, ImageFilter
from reportlab.lib.colors import CMYKColor, CMYKColorSep
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as _canvas

import swift_blue_drop_dieline as B
import illustration as ILL
from swift_blue_drop_dieline import (MM, F, NAVY, NAVY_DK, NAVY_MID, BLUE_MID,
                                     BLUE_BR, CYAN, CYAN_LT, YELLOW, RED,
                                     WHITE, INK, P, sw, fit, rect, pill,
                                     circle, poly, line, clip_rect,
                                     register_fonts, EMAIL, WEBSITE, TEL)

HERE = B.HERE
ROOT = B.ROOT
ART = os.path.join(HERE, "art")
LOGOS = os.path.join(ROOT, "images", "logo")
OUT = os.path.join(B.DIST, "95mm")
STEM = "Swift_Blue-Drop_95x95x20_FINAL"

# ----------------------------------------------------------------------------
# 1. CARTON SPEC (mm). Finished outside dimensions as supplied by the client.
# ----------------------------------------------------------------------------
W_FACE = 95.0          # front / back width
H_BODY = 95.0          # front / back height
W_SIDE = 20.0          # carton depth = side panel width
W_GLUE = 13.0          # glue flap (glued inside the right side panel)
H_CLOSE = W_SIDE       # tuck closure panel = carton depth
H_LIP = 13.0           # tuck-in lip beyond the closure crease
H_TUCK = H_CLOSE + H_LIP
H_DUST = 15.0          # dust flaps
H_HANG = 20.0          # hang tab above the carton: back = 95 + 20 = 115 mm
TAB_W = 60.0
TAB_CH = 6.0           # tab shoulder chamfer
BLEED = 3.0
SAFE_FACE = 4.0        # live copy inside every fold / cut on front and back
SAFE_SIDE = 3.0        # on the 20 mm sides and the closures
GT = 3.0               # glue flap taper
DT = 3.0               # dust flap chamfer
LIP_R = 5.0            # lip corner radius
LIP_IN = 1.0           # lip shoulder, so it slides in past the dust flaps

# euro slot on the tab: 6 mm eye, 4 mm riser
SLOT_R = 3.0
SLOT_W = 4.0
SLOT_Y = 7.0           # eye centre above the carton top
SLOT_RISE = 3.5
TAB_HEADROOM = H_HANG - (SLOT_Y + SLOT_RISE + SLOT_W / 2.0)

# scent vents: three droplets near the top of each side
VENT_N = 3
VENT_H = 4.4
VENT_GAP = 4.8
VENT_DY = 8.0          # row centre below the top crease

# panel origins along x: glue | back | side L | front | side R
X_GLUE = 0.0
X_BACK = X_GLUE + W_GLUE
X_SIDL = X_BACK + W_FACE
X_FRNT = X_SIDL + W_SIDE
X_SIDR = X_FRNT + W_FACE
SHEET_W = X_SIDR + W_SIDE
Y_BODY = H_TUCK
Y_TOP = Y_BODY + H_BODY
SHEET_H = Y_TOP + H_TUCK
TAB_X0 = X_BACK + (W_FACE - TAB_W) / 2.0
TAB_X1 = TAB_X0 + TAB_W

PANELS = {   # label: (x, y, w, h, safe)
    "FRONT": (X_FRNT, Y_BODY, W_FACE, H_BODY, SAFE_FACE),
    "BACK": (X_BACK, Y_BODY, W_FACE, H_BODY, SAFE_FACE),
    "SIDE-L": (X_SIDL, Y_BODY, W_SIDE, H_BODY, SAFE_SIDE),
    "SIDE-R": (X_SIDR, Y_BODY, W_SIDE, H_BODY, SAFE_SIDE),
    "TOP": (X_FRNT, Y_TOP, W_FACE, H_CLOSE, SAFE_SIDE),
    "BOTTOM": (X_FRNT, Y_BODY - H_CLOSE, W_FACE, H_CLOSE, SAFE_SIDE),
    "TAB": (TAB_X0, Y_TOP, TAB_W, H_HANG, 2.0),
}

# ----------------------------------------------------------------------------
# 2. MEASURED TYPE. x-height and cap height per em, read from the TTFs.
# ----------------------------------------------------------------------------
XH = {"Jakarta-400": .536, "Jakarta-500": .539, "Jakarta-600": .541,
      "Jakarta-700": .544, "Jakarta-800": .546, "Outfit-400": .475,
      "Outfit-600": .483, "Outfit-700": .486, "Outfit-800": .489,
      "Outfit-900": .492}
CAP = {k: (.745 if k.startswith("Jakarta") else .71) for k in XH}
MIN_XH = 1.2           # mm
PT = 25.4 / 72.0       # mm per point


def cap_mm(font, size):
    return CAP[font] * size * PT


def xh_mm(font, size):
    return XH[font] * size * PT


# ----------------------------------------------------------------------------
# 3. ELEMENT REGISTRY - the layout guard.
# Every drawn thing that matters is registered with its box. Elements in the
# same group may touch (a label on its own pill); anything else must keep
# CLEAR mm apart and stay inside its panel's safe area.
# ----------------------------------------------------------------------------
CLEAR = 0.8
ELEMS = []
CUR = {"panel": None, "group": None}
_SEQ = [0]


def panel(label):
    CUR["panel"] = label
    x, y, w, h, _ = PANELS[label]
    B.panel(label, x, y, w, h)


def group(name):
    CUR["group"] = name


def _gid():
    if CUR["group"] is not None:
        return CUR["group"]
    _SEQ[0] += 1
    return "_%d" % _SEQ[0]


def REG(name, x0, y0, x1, y1, kind="art", gid=None, safe=True, **kw):
    e = dict(panel=CUR["panel"], name=name, kind=kind,
             group=gid if gid is not None else _gid(),
             box=(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)),
             safe=safe)
    e.update(kw)
    ELEMS.append(e)
    return e


_DESC = set("gjpqy,;()[]@Q")


def _vbox(s, font, size):
    asc = (CAP[font] + 0.03) * size * PT if s.upper() == s else \
        0.76 * size * PT
    dsc = 0.21 * size * PT if (set(s) & _DESC) else 0.02 * size * PT
    return asc, dsc


def T(c, x, y, s, font, size, colour, align="l", cs=0.0, name=None,
      gid=None):
    """Horizontal text, registered."""
    w = B.txt(c, x, y, s, font, size, colour, align, char_space=cs)
    x0 = x - (w / 2 if align == "c" else w if align == "r" else 0)
    asc, dsc = _vbox(s, font, size)
    REG(name or s, x0, y - dsc, x0 + w, y + asc, "text", gid=gid,
        font=font, size=size, text=s)
    return w


def VT(c, bx, y, s, font, size, colour, align="l", cs=0.0, name=None,
       gid=None):
    """Text rotated 90 deg anticlockwise, reading bottom to top.
    bx is the baseline; glyphs extend to the LEFT of it (towards -x)."""
    w = (sw(s, font, size) + cs * max(0, len(s) - 1)) / MM
    y0 = y - (w / 2 if align == "c" else w if align == "r" else 0)
    c.saveState()
    c.translate(P(bx), P(y0))
    c.rotate(90)
    c.setFillColor(colour)
    t = c.beginText(0, 0)
    t.setFont(font, size)
    if cs:
        t.setCharSpace(cs)
    t.textLine(s)
    if cs:
        t.setCharSpace(0)
    c.drawText(t)
    c.restoreState()
    asc, dsc = _vbox(s, font, size)
    REG(name or s, bx - asc, y0, bx + dsc, y0 + w, "text", gid=gid,
        font=font, size=size, text=s)
    return w


def check():
    """Returns (collisions, safe-area breaches, small type, containment)."""
    hits, safe, small, cont = [], [], [], []
    for i, a in enumerate(ELEMS):
        for b in ELEMS[i + 1:]:
            if a["panel"] != b["panel"] or a["group"] == b["group"]:
                continue
            ax0, ay0, ax1, ay1 = a["box"]
            bx0, by0, bx1, by1 = b["box"]
            gx = max(bx0 - ax1, ax0 - bx1)
            gy = max(by0 - ay1, ay0 - by1)
            if gx < CLEAR and gy < CLEAR:
                hits.append("%-7s %-28s x %-28s gap %.2f mm"
                            % (a["panel"], a["name"][:28], b["name"][:28],
                               max(gx, gy)))
    for e in ELEMS:
        x, y, w, h, s = PANELS[e["panel"]]
        x0, y0, x1, y1 = e["box"]
        if e["safe"]:
            d = max(x + s - x0, x0 * 0 + x1 - (x + w - s), y + s - y0,
                    y1 - (y + h - s))
            if d > 0.05:
                safe.append("%-7s %-34s %.2f mm past safe line"
                            % (e["panel"], e["name"][:34], d))
        if e["kind"] == "text":
            xh = xh_mm(e["font"], e["size"])
            if xh < MIN_XH - 1e-6:
                small.append("%-7s %-34s %.2f mm x-height (%s %.1f pt)"
                             % (e["panel"], e["name"][:34], xh, e["font"],
                                e["size"]))
        if "inside" in e:          # (cx, cy, r) circle or (x0,y0,x1,y1) box
            k = e["inside"]
            if len(k) == 3:
                cx, cy, r = k
                far = max(sqrt((px - cx) ** 2 + (py - cy) ** 2)
                          for px in (x0, x1) for py in (y0, y1))
                if far > r:
                    cont.append("%-7s %-30s leaves its disc by %.2f mm"
                                % (e["panel"], e["name"][:30], far - r))
            else:
                cx0, cy0, cx1, cy1 = k
                d = max(cx0 - x0, x1 - cx1, cy0 - y0, y1 - cy1)
                if d > 0.0:
                    cont.append("%-7s %-30s leaves its box by %.2f mm"
                                % (e["panel"], e["name"][:30], d))
    return hits, safe, small, cont


# ----------------------------------------------------------------------------
# 4. IMAGE GROUNDS
# The Vortex photograph was composed for a 107 x 157 mm face. On a 95 mm
# square its four blocks would fill the panel edge to edge, so the sharp photo
# is scaled down around the product and feathered into a heavily defocused,
# enlarged copy of itself. That copy also runs continuously across both side
# panels, so the water wraps the folds instead of stopping at them.
# ----------------------------------------------------------------------------
PXMM = 12.0                       # 305 dpi at finished size
SCENE_W = 107.0
BLOCK_C = (53.7, 74.5)            # block-group centre in the scene, mm
BLOCK_WH = (62.5, 53.0)           # block-group extent in the scene, mm
K_SHARP = 0.64                    # sharp photo scale on the front
PROD_C = (49.0, 35.5)             # where the blocks sit on the front, mm
K_BACK = 1.30                     # defocused backdrop scale
_IMG = {}


def _scene():
    if "scene" not in _IMG:
        _IMG["scene"] = Image.open(os.path.join(ART, "scene-vortex.png")
                                   ).convert("RGB")
    return _IMG["scene"]


def _place(src, k, centre, x0, y0, w, h):
    """Render src (mm-scaled by k, with BLOCK_C landing at centre) into a
    w x h mm window whose lower-left is (x0, y0) in front-panel mm."""
    spx = src.width / SCENE_W                    # src px per mm
    scale = k * PXMM / spx
    W, H = int(round(w * PXMM)), int(round(h * PXMM))
    # window origin in scene mm
    sx0 = BLOCK_C[0] + (x0 - centre[0]) / k
    sy_top = BLOCK_C[1] + (y0 + h - centre[1]) / k
    src_h_mm = src.height / spx
    left = sx0 * spx
    top = (src_h_mm - sy_top) * spx
    out = src.transform((W, H), Image.AFFINE,
                        (1 / scale, 0, left, 0, 1 / scale, top),
                        Image.BICUBIC, fillcolor=(10, 50, 130))
    return out


def ground_strip():
    """Side L + front + side R as one image, x from -20 to 115 (front mm)."""
    if "strip" in _IMG:
        return _IMG["strip"]
    x0, y0, w, h = -W_SIDE - 1.0, -1.0, W_FACE + 2 * W_SIDE + 2.0, H_BODY + 2.0
    back = _place(_scene(), K_BACK, PROD_C, x0, y0, w, h)
    back = back.filter(ImageFilter.GaussianBlur(5.0 * PXMM))
    sharp = _place(_scene(), K_SHARP, PROD_C, x0, y0, w, h)
    # feather: full strength over the product, gone by the panel edges
    yy, xx = np.mgrid[0:sharp.height, 0:sharp.width]
    mx = x0 + (xx + 0.5) / PXMM
    my = y0 + h - (yy + 0.5) / PXMM
    # The sharp photo is only ~68 mm wide at this scale, so the fade must be
    # complete before its edge or the edge prints as a visible box.
    half_w = min(BLOCK_C[0], SCENE_W - BLOCK_C[0]) * K_SHARP
    ex = np.abs(mx - PROD_C[0]) / (half_w / 1.36)
    ey = np.abs(my - PROD_C[1]) / 40.0
    d = np.sqrt(ex ** 2 + ey ** 2)
    a = np.clip((1.36 - d) / 0.5, 0, 1)
    a = a * a * (3 - 2 * a)
    m = Image.fromarray((a * 255).astype("uint8"), "L")
    img = Image.composite(sharp, back, m)
    _IMG["strip"] = (img, x0, y0, w, h)
    return _IMG["strip"]


def draw_strip(c, px, py, pw, ph):
    """Paint the part of the ground strip that falls on a panel."""
    img, x0, y0, w, h = ground_strip()
    c.saveState()
    clip_rect(c, px, py, pw, ph)
    c.drawImage(ImageReader(img), P(X_FRNT + x0), P(Y_BODY + y0),
                w * MM, h * MM)
    c.restoreState()


def logo_reader(name):
    key = "logo-" + name
    if key not in _IMG:
        _IMG[key] = ImageReader(os.path.join(LOGOS, name + ".png"))
    return _IMG[key]


def logo(c, cx, cy, w, name="swift-logo", rot=0, label="Swift logo"):
    img = logo_reader(name)
    iw, ih = img.getSize()
    h = w * ih / float(iw)
    c.saveState()
    c.translate(P(cx), P(cy))
    c.rotate(rot)
    c.drawImage(img, -w / 2 * MM, -h / 2 * MM, w * MM, h * MM, mask="auto")
    c.restoreState()
    bw, bh = (h, w) if rot % 180 else (w, h)
    REG(label, cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
    return h


def scrim(c, x, y, w, h, top=True, peak=0.88, bands=22, colour=NAVY_DK):
    for i in range(bands):
        t = i / float(bands - 1)
        a = peak * (1.0 - t) ** 1.9 / bands * 3.4
        bh = h * (1.0 - t)
        if bh > 0:
            rect(c, x, (y + h - bh) if top else y, w, bh, colour,
                 alpha=min(0.95, a))


# ----------------------------------------------------------------------------
# 5. FRONT - 95 x 95
# ----------------------------------------------------------------------------

def seal_300(c, cx, cy, r):
    """Yellow disc in the 4 PACK yellow: red numeral, navy words, exactly the
    flag's colour logic, so the two badges read as a pair."""
    group("seal")
    for k, a in ((1.12, 0.10), (1.06, 0.14), (1.0, 0.18)):
        circle(c, cx + 0.45, cy - 0.6, r * k, NAVY_DK, alpha=a)
    circle(c, cx, cy, r, YELLOW)
    c.saveState()
    c.setStrokeColor(NAVY, 0.55)
    c.setLineWidth(0.35 * MM)
    c.circle(P(cx), P(cy), (r - 1.1) * MM, fill=0, stroke=1)
    c.restoreState()
    REG("300 FLUSHES seal", cx - r, cy - r, cx + r, cy + r, gid="seal")
    inner = (cx, cy, r - 1.6)
    T(c, cx, cy + 3.95, "ONE BLOCK", F["subhead"], 7.3, NAVY, "c", cs=0.2,
      gid="seal")
    ELEMS[-1]["inside"] = inner
    T(c, cx, cy - 2.75, "300", F["display"], 21.0, RED, "c", gid="seal")
    ELEMS[-1]["inside"] = inner
    T(c, cx, cy - 6.85, "FLUSHES", F["head"], 7.6, NAVY, "c", cs=0.35,
      gid="seal")
    ELEMS[-1]["inside"] = inner
    group(None)


def flag_4pack(c, x, y, w, h):
    group("flag")
    poly(c, [(x + 2.2, y), (x + w, y), (x + w - 2.2, y + h), (x, y + h)],
         YELLOW)
    REG("4 PACK flag", x, y, x + w, y + h, gid="flag")
    box = (x + 2.2, y + 0.6, x + w - 2.2, y + h - 0.6)
    T(c, x + 9.6, y + 3.35, "4", F["display"], 22.0, RED, "c", gid="flag")
    ELEMS[-1]["inside"] = box
    T(c, x + 23.6, y + 6.9, "PACK", F["head"], 11.2, NAVY, "c", gid="flag")
    ELEMS[-1]["inside"] = box
    T(c, x + 23.6, y + 2.75, "50 g each", F["bodybold"], 7.0, NAVY, "c",
      gid="flag")
    ELEMS[-1]["inside"] = box
    group(None)


def flanked_rule(c, x0, x1, y, colour, alpha=0.75):
    line(c, x0, y, x1, y, colour, 0.3, alpha=alpha)
    for ex in (x0, x1):
        poly(c, [(ex - 0.9, y), (ex, y + 0.7), (ex + 0.9, y), (ex, y - 0.7)],
             colour, alpha=alpha)


def front(c):
    x, y, w, h = PANELS["FRONT"][:4]
    top, cx = y + h, x + w / 2
    panel("FRONT")
    draw_strip(c, x, y, w, h)
    scrim(c, x, top - 44.0, w, 44.0, top=True, peak=0.92)
    scrim(c, x, y, w, 26.0, top=False, peak=0.9)

    # the product is part of the photograph; register it so nothing is
    # allowed to land on the blocks
    bw, bh = BLOCK_WH[0] * K_SHARP, BLOCK_WH[1] * K_SHARP
    REG("product (4 blocks)", x + PROD_C[0] - bw / 2, y + PROD_C[1] - bh / 2,
        x + PROD_C[0] + bw / 2, y + PROD_C[1] + bh / 2, safe=False)

    # masthead
    lw_ = 30.0
    lh = lw_ * 425.0 / 760.0
    l_top = top - SAFE_FACE
    lcy = l_top - lh / 2
    logo(c, x + SAFE_FACE + lw_ / 2, lcy, lw_)
    fw, fh = 35.0, 13.0
    flag_4pack(c, x + w - SAFE_FACE - fw, lcy - fh / 2, fw, fh)

    # wordmark + droplet, centred as one unit
    name = "Blue-Drop"
    size = fit(name, F["display"], 56.0)
    nw = sw(name, F["display"], size) / MM
    dh = 10.0
    dw = dh * 0.67
    unit = nw + 2.0 + dw
    ux0 = cx - unit / 2
    base = (l_top - lh) - 2.6 - cap_mm(F["display"], size)
    group("wordmark")
    T(c, ux0, base, name, F["display"], size, WHITE, gid="wordmark")
    B.droplet_gloss(c, ux0 + nw + 2.0 + dw / 2,
                    base + cap_mm(F["display"], size) * 0.48, dh,
                    light=True, shadow=False)
    REG("droplet", ux0 + nw + 2.0, base + cap_mm(F["display"], size) * 0.48
        - dh / 2, ux0 + unit, base + cap_mm(F["display"], size) * 0.48
        + dh / 2, gid="wordmark")
    group(None)

    deck = "AUTOMATIC TOILET BOWL CLEANER"
    dsz = 7.6
    dbase = base - 0.21 * size * PT - 1.7 - cap_mm(F["label"], dsz)
    group("deck")
    dwid = T(c, cx, dbase, deck, F["label"], dsz, WHITE, "c", cs=0.45,
             gid="deck")
    ry = dbase + cap_mm(F["label"], dsz) / 2
    gap = dwid / 2 + 2.6
    if (w / 2 - SAFE_FACE - 0.9) - gap > 3.0:
        flanked_rule(c, x + SAFE_FACE + 0.9, cx - gap, ry, CYAN_LT)
        flanked_rule(c, cx + gap, x + w - SAFE_FACE - 0.9, ry, CYAN_LT)
    group(None)

    # 300 FLUSHES seal, left of the blocks
    r = 11.4
    seal_300(c, x + SAFE_FACE + 0.4 + r, y + 31.0, r)

    # net quantity, right of the blocks (EU e-mark minimum is 3 mm for
    # 50-200 g; the figures here are 4.2 mm)
    rx = x + w - SAFE_FACE
    group("net")
    T(c, rx, y + 36.6, "NET WT.", F["subhead"], 7.4, CYAN_LT, "r", cs=0.3,
      gid="net")
    T(c, rx, y + 29.4, "200 g", F["display"], 17.0, WHITE, "r", gid="net")
    T(c, rx, y + 24.4, "4 × 50 g", F["bodybold"], 7.6, WHITE, "r",
      gid="net")
    group(None)

    # benefit band
    band = 11.5
    rect(c, x, y, w, band, NAVY_DK, alpha=0.9)
    rect(c, x, y + band, w, 0.5, CYAN, alpha=0.6)
    items = (("CLEANS", "sparkle"), ("FRESHENS", "drop"),
             ("PROTECTS", "shield"))
    lsz = 7.8
    widths = [sw(t, F["subhead"], lsz) / MM + 0.3 * (len(t) - 1) / MM
              for t, _ in items]
    unit_w = [5.4 + 1.8 + wd for wd in widths]
    space = (w - 2 * SAFE_FACE - sum(unit_w)) / 2.0
    bx = x + SAFE_FACE
    by = y + 5.4
    for (lab, kind), uw in zip(items, unit_w):
        g = "ben-" + lab
        group(g)
        ix, iy = bx + 2.7, by + cap_mm(F["subhead"], lsz) / 2
        if kind == "sparkle":
            B.sparkle(c, ix, iy, 2.4, CYAN_LT)
        elif kind == "drop":
            B.droplet(c, ix, iy, 4.7, CYAN_LT, highlight=False)
        else:
            B.shield(c, ix, iy, 2.3, CYAN_LT)
        REG(lab + " icon", ix - 2.4, iy - 2.35, ix + 2.4, iy + 2.35, gid=g)
        T(c, bx + 5.4 + 1.8, by, lab, F["subhead"], lsz, WHITE, cs=0.3,
          gid=g)
        group(None)
        bx += uw + space


# ----------------------------------------------------------------------------
# 6. BACK - 95 x 95 (+ 20 mm tab above)
# ----------------------------------------------------------------------------
STEPS = ((ILL.step_unwrap, "Unwrap", "Take one block out of its wrapper."),
         (ILL.step_tank, "Drop in", "Drop it into the tank, clear of the "
                                    "float."),
         (ILL.step_flush, "Flush", "Each block lasts up to 300 flushes."))


def badge(c, cx, cy, n, r, gid):
    circle(c, cx, cy, r, NAVY)
    T(c, cx, cy - cap_mm(F["bodyblk"], 7.6) / 2, str(n), F["bodyblk"], 7.6,
      WHITE, "c", gid=gid)
    ELEMS[-1]["inside"] = (cx, cy, r)
    REG("badge %d" % n, cx - r, cy - r, cx + r, cy + r, gid=gid)


def back(c):
    x, y, w, h = PANELS["BACK"][:4]
    top, cx = y + h, x + w / 2
    m = SAFE_FACE
    cw = w - 2 * m
    panel("BACK")

    # ground: white, the photograph veiled to a watermark, a faint flower
    rect(c, x, y, w, h, WHITE)
    c.saveState()
    clip_rect(c, x, y, w, h)
    sc = _scene()
    c.drawImage(ImageReader(sc), P(x - (SCENE_W - w) / 2),
                P(y - (157.0 - h) / 2 - 18.0), SCENE_W * MM, 157.0 * MM)
    c.setFillColor(WHITE, 0.84)
    c.rect(P(x), P(y), w * MM, h * MM, fill=1, stroke=0)
    fl = ImageReader(os.path.join(ART, "flower-22.png"))
    fiw, fih = fl.getSize()
    fw = 44.0
    c.drawImage(fl, P(x + w - fw * 0.60), P(top - fw * fih / fiw * 0.66),
                fw * MM, fw * fih / fiw * MM, mask="auto")
    c.restoreState()
    rect(c, x, top - 2.0, w, 2.0, NAVY)

    # header
    tsz = fit("Swift Blue-Drop", F["head"], 56.0)
    tb = top - m - 1.0 - cap_mm(F["head"], tsz)
    T(c, x + m, tb, "Swift Blue-Drop", F["head"], tsz, NAVY)
    T(c, x + m, tb - 5.4, "Flush-Activated WC Cleaner", F["subhead"], 8.4,
      BLUE_BR)
    dh = 12.0
    B.droplet_gloss(c, x + w - m - 4.5, tb - 0.4, dh, light=False,
                    shadow=False)
    REG("droplet", x + w - m - 4.5 - dh * 0.34, tb - 0.4 - dh / 2,
        x + w - m - 4.5 + dh * 0.34, tb - 0.4 + dh / 2)
    rule_y = tb - 8.0
    line(c, x + m, rule_y, x + w - m, rule_y, NAVY, 0.35, alpha=0.35)

    # HOW TO USE
    ph = 5.6
    py_ = rule_y - 1.6 - ph
    group("howto-pill")
    pill(c, x + m, py_, cw, ph, NAVY)
    REG("HOW TO USE pill", x + m, py_, x + m + cw, py_ + ph, gid="howto-pill")
    T(c, cx, py_ + (ph - cap_mm(F["subhead"], 7.8)) / 2, "HOW TO USE",
      F["subhead"], 7.8, WHITE, "c", cs=0.5, gid="howto-pill")
    ELEMS[-1]["inside"] = (x + m, py_, x + m + cw, py_ + ph)
    group(None)

    gap = 3.0
    col = (cw - 2 * gap) / 3.0
    bsz = 6.6
    lead = 3.0
    title_y = py_ - 1.4 - 2.9           # badge centre line
    art_w = 16.0
    art_h = art_w * 0.86
    art_y = title_y - 2.9 - 1.0 - art_h
    body_y = art_y - 1.2 - cap_mm(F["body"], bsz)
    for i, (fn, title, body) in enumerate(STEPS):
        g = "step%d" % (i + 1)
        group(g)
        cx0 = x + m + i * (col + gap)
        badge(c, cx0 + 2.9, title_y, i + 1, 2.9, g)
        T(c, cx0 + 7.2, title_y - cap_mm(F["subhead"], 8.0) / 2, title,
          F["subhead"], 8.0, NAVY, gid=g)
        ax = cx0 + (col - art_w) / 2
        fn(c, ax, art_y, art_w)
        REG("step %d art" % (i + 1), ax - 0.6, art_y, ax + art_w + 0.4,
            art_y + art_h, gid=g + "-art")
        lines = B.wrap(body, F["body"], bsz, col)
        if len(lines) > 2:
            raise SystemExit("step %d copy runs to %d lines" % (i + 1,
                                                               len(lines)))
        for j, ln in enumerate(lines):
            T(c, cx0, body_y - j * lead, ln, F["body"], bsz, INK, gid=g)
        group(None)
    steps_bottom = body_y - lead - 0.21 * bsz * PT

    # CAUTION
    foot_h = 26.0
    cau = ("Keep out of reach of children. Do not ingest. Avoid contact with "
           "skin and eyes; wash hands after use.")
    ctop = steps_bottom - 2.0
    lab_w = 19.0
    lines = B.wrap(cau, F["body"], bsz, cw - lab_w - 4.0)
    box_h = 3.0 + lead * len(lines)
    cy0 = ctop - box_h
    group("caution")
    pill(c, x + m, cy0, cw, box_h, RED, r=1.4, alpha=0.08)
    REG("caution box", x + m, cy0, x + m + cw, ctop, gid="caution")
    pill(c, x + m + 1.2, cy0 + (box_h - 5.2) / 2, lab_w, 5.2, RED, r=2.6)
    T(c, x + m + 1.2 + lab_w / 2,
      cy0 + (box_h - cap_mm(F["head"], 7.4)) / 2, "CAUTION", F["head"], 7.4,
      WHITE, "c", cs=0.3, gid="caution")
    ly = ctop - 1.5 - cap_mm(F["body"], bsz)
    for ln in lines:
        T(c, x + m + lab_w + 3.4, ly, ln, F["body"], bsz, INK, gid="caution")
        ELEMS[-1]["inside"] = (x + m, cy0, x + m + cw, ctop)
        ly -= lead
    group(None)
    if cy0 < y + foot_h + 2.0:
        raise SystemExit("back panel over-full: caution ends %.1f mm into "
                         "the foot band" % (y + foot_h + 2.0 - cy0))

    # foot: maker, address, data-sheet QR, recycling
    rect(c, x, y, w, foot_h, NAVY)
    rect(c, x, y + foot_h, w, 0.6, CYAN, alpha=0.55)
    vw = 20.0
    vh = vw * 279.0 / 806.0
    vtop = y + foot_h - 2.2
    logo(c, x + m + vw / 2, vtop - vh / 2, vw, "vistex-logo-white",
         label="Vistex logo")
    fsz = 6.6
    lines = ("P.O. Box 218 – 00606, Industrial Area,",
             "Nairobi, Kenya   ·   Tel " + TEL,
             EMAIL)
    fy = vtop - vh - 2.0 - cap_mm(F["body"], fsz)
    group("address")
    for ln in lines:
        T(c, x + m, fy, ln, F["body"], fsz, WHITE, gid="address")
        fy -= 2.9
    T(c, x + m, fy, WEBSITE, F["bodybold"], fsz, CYAN_LT, gid="address")
    group(None)

    qs = 13.5
    q = 1.3
    qx = x + w - m - q - qs
    qy = y + m + q
    group("qr")
    B.qr_code(c, qx, qy, qs, B.qr_url("blue-drop-wc"), quiet=q)
    REG("QR", qx - q, qy - q, qx + qs + q, qy + qs + q, gid="qr")
    group(None)
    group("qr-cap")
    T(c, qx - q - 2.0, qy + qs - 2.6, "SCAN FOR", F["bodybold"], 6.6,
      CYAN_LT, "r", gid="qr-cap")
    T(c, qx - q - 2.0, qy + qs - 6.0, "DATA SHEET", F["bodybold"], 6.6,
      CYAN_LT, "r", gid="qr-cap")
    group(None)
    rc = ImageReader(_white_recycle())
    rw_ = 7.5
    rx_ = qx - q - 2.0 - rw_
    ry_ = qy - q
    c.drawImage(rc, P(rx_), P(ry_), rw_ * MM, rw_ * MM, mask="auto")
    REG("recycle mark", rx_, ry_, rx_ + rw_, ry_ + rw_)


def _white_recycle():
    if "rc" not in _IMG:
        im = Image.open(os.path.join(ART, "recycle-outline.png")).convert(
            "RGBA")
        bb = im.getchannel("A").getbbox()
        im = im.crop(bb)
        s = max(im.size)
        sq = Image.new("RGBA", (s, s), (255, 255, 255, 0))
        sq.paste(im, ((s - im.width) // 2, (s - im.height) // 2))
        flat = Image.new("RGBA", sq.size, (255, 255, 255, 255))
        # the supplied mark is a soft outline; lift it to full strength or
        # it prints as a grey smudge on the navy
        flat.putalpha(sq.getchannel("A").point(lambda v: min(255, v * 3)))
        _IMG["rc"] = flat
    return _IMG["rc"]


# ----------------------------------------------------------------------------
# 7. SIDES - 20 x 95, type running bottom to top
# ----------------------------------------------------------------------------

def vent_positions(px):
    cx = px + W_SIDE / 2.0
    x0 = cx - (VENT_N - 1) * VENT_GAP / 2.0
    return [(x0 + i * VENT_GAP, Y_TOP - VENT_DY) for i in range(VENT_N)]


def side(c, label, variant):
    x, y, w, h = PANELS[label][:4]
    cx = x + w / 2
    panel(label)
    draw_strip(c, x, y, w, h)
    rect(c, x, y, w, h, NAVY, alpha=0.42)

    s = SAFE_SIDE
    # Swift mark, turned to read bottom to top with the type
    lw_ = 24.0
    logo(c, cx, y + s + 1.0 + lw_ / 2, lw_, rot=90)
    ystart = y + s + 1.0 + lw_ + 5.0
    yend = Y_TOP - VENT_DY - VENT_H / 2 - 4.0      # stop short of the vents

    if variant == "brand":
        name = "Blue-Drop"
        size = min(fit(name, F["display"], yend - ystart), 30.0)
        asc, dsc = _vbox(name, F["display"], size)
        sub = "WC CLEANER"
        ssz = 7.4
        sasc, _ = _vbox(sub, F["label"], ssz)
        stack = asc + dsc + 1.6 + sasc
        # glyph tops face -x, so the first line sits on the left
        b1 = cx - stack / 2 + asc
        VT(c, b1, ystart, name, F["display"], size, WHITE)
        b2 = b1 + dsc + 1.6 + sasc
        nw = sw(name, F["display"], size) / MM
        VT(c, b2, ystart + nw / 2, sub, F["label"], ssz, CYAN_LT, "c",
           cs=0.6)
    else:
        l1, s1 = "300 FLUSHES", None
        s1 = min(fit(l1, F["display"], yend - ystart - 0.5), 16.0)
        a1, d1 = _vbox(l1, F["display"], s1)
        l2 = "4 × 50 g  ·  NET 200 g"
        s2 = 7.4
        a2, d2 = _vbox(l2, F["bodybold"], s2)
        stack = a1 + d1 + 1.8 + a2 + d2
        b1 = cx - stack / 2 + a1
        VT(c, b1, ystart, l1, F["display"], s1, YELLOW)
        w1 = sw(l1, F["display"], s1) / MM
        b2 = b1 + d1 + 1.8 + a2
        VT(c, b2, ystart + w1 / 2, l2, F["bodybold"], s2, WHITE, "c")

    # vents are knocked out white so the proof reads as holes
    for vx, vy in vent_positions(x):
        c.saveState()
        c.setStrokeColor(CYAN_LT, 0.55)
        c.setLineWidth(0.3 * MM)
        c.drawPath(B._drop_path(c, vx, vy, VENT_H * 1.45)[0], fill=0,
                   stroke=1)
        c.restoreState()
        c.saveState()
        c.setFillColor(WHITE)
        c.drawPath(B._drop_path(c, vx, vy, VENT_H)[0], fill=1, stroke=0)
        c.restoreState()
    v = vent_positions(x)
    REG("scent vents", v[0][0] - VENT_H * 0.49, v[0][1] - VENT_H * 0.73,
        v[-1][0] + VENT_H * 0.49, v[0][1] + VENT_H * 0.73)


# ----------------------------------------------------------------------------
# 8. CLOSURES, TAB, FLAPS
# ----------------------------------------------------------------------------

def closures(c):
    # top closure panel (outside face is the top of the carton)
    x, y, w, h = PANELS["TOP"][:4]
    panel("TOP")
    rect(c, x, y, w, h, NAVY)
    lw_ = 24.0
    lh = lw_ * 425.0 / 760.0
    logo(c, x + SAFE_SIDE + 4.0 + lw_ / 2, y + h / 2, lw_)
    tx = x + SAFE_SIDE + 4.0 + lw_ + 6.0
    nsz = 15.0
    T(c, tx, y + h / 2 + 0.6, "Blue-Drop", F["display"], nsz, WHITE)
    T(c, tx, y + h / 2 - 4.8, "4 × 50 g  ·  UP TO 300 FLUSHES PER BLOCK",
      F["bodybold"], 6.6, CYAN_LT)

    # bottom closure panel: composition and storage
    x, y, w, h = PANELS["BOTTOM"][:4]
    panel("BOTTOM")
    rect(c, x, y, w, h, NAVY)
    s = SAFE_SIDE + 1.0
    bsz = 6.6
    colw = 52.0
    group("comp")
    T(c, x + s, y + h - s - cap_mm(F["subhead"], 7.4), "COMPOSITION",
      F["subhead"], 7.4, CYAN_LT, cs=0.4, gid="comp")
    yy = y + h - s - cap_mm(F["subhead"], 7.4) - 3.6
    for ln in B.wrap("Anionic surfactants, dissolution modifiers, "
                     "anti-redeposition agents, colourant, perfume.",
                     F["body"], bsz, colw):
        T(c, x + s, yy, ln, F["body"], bsz, WHITE, gid="comp")
        yy -= 3.0
    group("store")
    sx = x + s + colw + 5.0
    T(c, sx, y + h - s - cap_mm(F["subhead"], 7.4), "STORAGE", F["subhead"],
      7.4, CYAN_LT, cs=0.4, gid="store")
    yy = y + h - s - cap_mm(F["subhead"], 7.4) - 3.6
    for ln in B.wrap("Store upright, cool and dry. Keep sealed until use.",
                     F["body"], bsz, x + w - s - sx):
        T(c, sx, yy, ln, F["body"], bsz, WHITE, gid="store")
        yy -= 3.0
    group(None)

    # lips and dust flaps are hidden once closed: flat ink only
    rect(c, X_FRNT, Y_TOP + H_CLOSE, W_FACE, H_LIP, NAVY)
    rect(c, X_FRNT, Y_BODY - H_TUCK, W_FACE, H_LIP, NAVY)
    for sx in (X_SIDL, X_SIDR):
        rect(c, sx, Y_TOP, W_SIDE, H_DUST, NAVY_MID)
        rect(c, sx, Y_BODY - H_DUST, W_SIDE, H_DUST, NAVY_MID)


def euro_slot_path(c, cx, y_base):
    cy = y_base + SLOT_Y
    hw = SLOT_W / 2.0
    top = cy + SLOT_RISE
    p = c.beginPath()
    # eye: lower semicircle and the shoulders up to the riser
    p.moveTo(P(cx - SLOT_R), P(cy))
    for i in range(1, 37):
        a = pi + pi * i / 36.0
        p.lineTo(P(cx + SLOT_R * cos(a)), P(cy + SLOT_R * sin(a)))
    # upper right of the eye, from 0 up to where it meets the riser
    ang = math.acos(hw / SLOT_R)
    for i in range(1, 13):
        a = ang * i / 12.0
        p.lineTo(P(cx + SLOT_R * cos(a)), P(cy + SLOT_R * sin(a)))
    p.lineTo(P(cx + hw), P(top))
    for i in range(1, 19):
        a = pi * i / 18.0
        p.lineTo(P(cx + hw * cos(a)), P(top + hw * sin(a)))
    p.lineTo(P(cx - hw), P(cy + SLOT_R * sin(ang)))
    for i in range(1, 13):
        a = pi - ang + ang * i / 12.0
        p.lineTo(P(cx + SLOT_R * cos(a)), P(cy + SLOT_R * sin(a)))
    p.close()
    return p


def hang_tab(c):
    panel("TAB")
    x, y, w, h = PANELS["TAB"][:4]
    cx = x + w / 2
    poly(c, [(x, y - 0.5), (x, y), (x + TAB_CH, y + h), (x + w - TAB_CH, y + h),
             (x + w, y), (x + w, y - 0.5)], NAVY)
    line(c, x + TAB_CH + 0.2, y + h - 0.3, x + w - TAB_CH - 0.2, y + h - 0.3,
         CYAN, 0.6, alpha=0.5, cap=0)
    sz = 7.4
    by = y + SLOT_Y - cap_mm(F["subhead"], sz) / 2
    T(c, cx - SLOT_R - 3.0, by, "SWIFT", F["subhead"], sz, WHITE, "r",
      cs=0.8)
    T(c, cx + SLOT_R + 3.0, by, "BLUE-DROP", F["subhead"], sz, WHITE,
      cs=0.8)
    c.saveState()
    c.setFillColor(WHITE)
    c.drawPath(euro_slot_path(c, cx, y), fill=1, stroke=0)
    c.restoreState()
    REG("euro slot", cx - SLOT_R, y + SLOT_Y - SLOT_R, cx + SLOT_R,
        y + SLOT_Y + SLOT_RISE + SLOT_W / 2)


def glue_tab(c):
    """Unprinted: ink under the glue line is what pops cartons open."""
    rect(c, X_GLUE - BLEED, Y_BODY, W_GLUE + BLEED, H_BODY, WHITE)


# ----------------------------------------------------------------------------
# 9. DIE
# ----------------------------------------------------------------------------

def _lip(x0, x1, y_hinge, depth, up=True):
    """Tuck lip outline from the left shoulder to the right, rounded corners."""
    s = 1 if up else -1
    pts = [(x0, y_hinge), (x0 + LIP_IN, y_hinge + s * 1.0)]
    yb = y_hinge + s * depth
    r = LIP_R
    xa, xb = x0 + LIP_IN, x1 - LIP_IN
    pts.append((xa, yb - s * r))
    for i in range(1, 10):
        a = pi * i / 18.0          # 0..90 deg
        pts.append((xa + r - r * cos(a), yb - s * r + s * r * sin(a)))
    for i in range(0, 10):
        a = pi / 2 - pi * i / 18.0
        pts.append((xb - r + r * cos(a), yb - s * r + s * r * sin(a)))
    pts.append((xb, yb - s * r))
    pts.append((xb, y_hinge + s * 1.0))
    pts.append((x1, y_hinge))
    return pts


def blank_outline():
    """Cut path of the whole blank, clockwise from the glue flap."""
    yt, yb = Y_TOP, Y_BODY
    pts = [(X_GLUE, yb + GT), (X_GLUE, yt - GT), (X_BACK, yt),
           (TAB_X0, yt), (TAB_X0 + TAB_CH, yt + H_HANG),
           (TAB_X1 - TAB_CH, yt + H_HANG), (TAB_X1, yt),
           (X_SIDL, yt),
           (X_SIDL, yt + H_DUST - DT), (X_SIDL + DT, yt + H_DUST),
           (X_FRNT - DT, yt + H_DUST), (X_FRNT, yt + H_DUST - DT),
           (X_FRNT, yt + H_CLOSE)]
    lip = _lip(X_FRNT, X_SIDR, yt + H_CLOSE, H_LIP, up=True)
    pts += lip[1:-1]
    pts += [(X_SIDR, yt + H_CLOSE), (X_SIDR, yt + H_DUST - DT),
            (X_SIDR + DT, yt + H_DUST), (SHEET_W - DT, yt + H_DUST),
            (SHEET_W, yt + H_DUST - DT), (SHEET_W, yb - H_DUST + DT),
            (SHEET_W - DT, yb - H_DUST), (X_SIDR + DT, yb - H_DUST),
            (X_SIDR, yb - H_DUST + DT), (X_SIDR, yb - H_CLOSE)]
    lip = _lip(X_FRNT, X_SIDR, yb - H_CLOSE, H_LIP, up=False)
    pts += list(reversed(lip))[1:-1]
    pts += [(X_FRNT, yb - H_CLOSE), (X_FRNT, yb - H_DUST + DT),
            (X_FRNT - DT, yb - H_DUST), (X_SIDL + DT, yb - H_DUST),
            (X_SIDL, yb - H_DUST + DT), (X_SIDL, yb), (X_BACK, yb)]
    return pts


def internal_cuts():
    """Cuts inside the outline: the closure panels' free side edges are
    shared with the dust flaps, and the two lips' side edges."""
    yt, yb = Y_TOP, Y_BODY
    return [[(X_FRNT, yt), (X_FRNT, yt + H_DUST - DT)],
            [(X_SIDR, yt), (X_SIDR, yt + H_DUST - DT)],
            [(X_FRNT, yb), (X_FRNT, yb - H_DUST + DT)],
            [(X_SIDR, yb), (X_SIDR, yb - H_DUST + DT)]]


def creases():
    yt, yb = Y_TOP, Y_BODY
    out = [[(fx, yb), (fx, yt)] for fx in (X_BACK, X_SIDL, X_FRNT, X_SIDR)]
    # body top: across side L, front, side R (the back runs on into the tab)
    out.append([(X_SIDL, yt), (SHEET_W, yt)])
    out.append([(X_SIDL, yb), (SHEET_W, yb)])   # the back's foot is a cut
    # lip creases
    out.append([(X_FRNT, yt + H_CLOSE), (X_SIDR, yt + H_CLOSE)])
    out.append([(X_FRNT, yb - H_CLOSE), (X_SIDR, yb - H_CLOSE)])
    return out


CUT_SEP = CMYKColorSep(0, 1, 0, 0, spotName="CutContour", density=1)
CREASE_SEP = CMYKColorSep(1, 0, 0, 0, spotName="Crease", density=1)


def _poly_path(c, pts, close=True):
    p = c.beginPath()
    p.moveTo(P(pts[0][0]), P(pts[0][1]))
    for px, py in pts[1:]:
        p.lineTo(P(px), P(py))
    if close:
        p.close()
    return p


def draw_die(c, cut=CUT_SEP, crease=CREASE_SEP, lw=0.5, dash=(4, 2.5)):
    c.saveState()
    c.setLineJoin(1)
    c.setStrokeColor(cut)
    c.setLineWidth(lw)
    c.drawPath(_poly_path(c, blank_outline()), fill=0, stroke=1)
    for seg in internal_cuts():
        c.drawPath(_poly_path(c, seg, False), fill=0, stroke=1)
    c.drawPath(euro_slot_path(c, TAB_X0 + TAB_W / 2, Y_TOP), fill=0,
               stroke=1)
    for px in (X_SIDL, X_SIDR):
        for vx, vy in vent_positions(px):
            c.drawPath(B._drop_path(c, vx, vy, VENT_H)[0], fill=0, stroke=1)
    c.setStrokeColor(crease)
    c.setDash([d * MM for d in dash], 0)
    for seg in creases():
        c.drawPath(_poly_path(c, seg, False), fill=0, stroke=1)
    c.restoreState()


# ----------------------------------------------------------------------------
# 10. BUILD
# ----------------------------------------------------------------------------

def paint(c):
    rect(c, -BLEED, -BLEED, SHEET_W + 2 * BLEED, SHEET_H + 2 * BLEED, NAVY)
    closures(c)
    hang_tab(c)
    back(c)
    side(c, "SIDE-L", "brand")
    front(c)
    side(c, "SIDE-R", "claim")
    glue_tab(c)
    B.panel_end()
    CUR["panel"] = None


def build_print(path):
    B.ORIGIN = BLEED
    page = ((SHEET_W + 2 * BLEED) * MM, (SHEET_H + 2 * BLEED) * MM)
    # ReportLab opens every page with a Helvetica preamble; pointing it at an
    # embedded face keeps an unembedded base-14 font out of the print file
    c = _canvas.Canvas(path, pagesize=page, initialFontName=F["body"],
                       initialFontSize=8)
    # the QR is drawn through reportlab.graphics, whose state defaults to
    # Times-Roman (unembedded) even though no text is set in it
    from reportlab.graphics import shapes as _shapes
    _shapes.STATE_DEFAULTS["fontName"] = F["body"]
    c.setTitle("Swift Blue-Drop 4 x 50 g - carton 95 x 95 x 20 mm - PRINT")
    c.setAuthor("Vistex Chemicals Ltd")
    c.setSubject("Folding carton artwork, straight tuck end with euro hang "
                 "tab. Page 1 artwork with 3 mm bleed; page 2 die line "
                 "(spot CutContour / Crease) in register.")
    c.setCreator("packaging/swift_blue_drop_95.py")
    trim = (BLEED * MM, BLEED * MM, (SHEET_W + BLEED) * MM,
            (SHEET_H + BLEED) * MM)
    for draw in (paint, draw_die):
        # trim box = the flat blank, so a RIP knows the finished extent
        if hasattr(c, "setTrimBox"):
            c.setTrimBox(trim)
            c.setBleedBox((0, 0) + page)
        draw(c)
        c.showPage()
    c.save()
    return path


def report():
    hits, safe, small, cont = check()
    over = sorted(set(B.OVERFLOW))
    ok = not (hits or safe or small or cont or over)
    print("elements checked : %d (%d text)" % (
        len(ELEMS), sum(1 for e in ELEMS if e["kind"] == "text")))
    for title, rows in (("OVERLAPS", hits), ("SAFE AREA", safe),
                        ("TYPE UNDER 1.2 mm x-height", small),
                        ("CONTAINMENT", cont), ("PANEL OVERFLOW", over)):
        print("%-28s %s" % (title, "none" if not rows else len(rows)))
        for r in rows:
            print("    " + r)
    smallest = min((xh_mm(e["font"], e["size"]), e["name"])
                   for e in ELEMS if e["kind"] == "text")
    print("smallest x-height: %.2f mm (%s)" % smallest)
    print("tab headroom above slot: %.1f mm" % TAB_HEADROOM)
    print("flat blank %.0f x %.0f mm, page %.0f x %.0f mm with bleed"
          % (SHEET_W, SHEET_H, SHEET_W + 2 * BLEED, SHEET_H + 2 * BLEED))
    return ok


def main():
    register_fonts()
    os.makedirs(OUT, exist_ok=True)
    ELEMS[:] = []
    B.BOXES[:] = []
    B.OVERFLOW[:] = []
    p = build_print(os.path.join(OUT, STEM + "_PRINT.pdf"))
    ok = report()
    print("wrote", os.path.relpath(p, ROOT),
          "(%.0f KB)" % (os.path.getsize(p) / 1024.0))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
