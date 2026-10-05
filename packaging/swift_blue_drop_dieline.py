#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swift Blue-Drop - Flush-Activated WC Cleaner, 50 g x 4
Print-ready folding-carton dieline (reverse tuck end).

Why this file exists
--------------------
The previous pack ("Swift_Toilet_Blocks_4PCS_Printable_Dieline.pdf") was a single
flat raster dropped into a PDF: no live text, no vector cut paths, the wrong Swift
mark, and a green/yellow palette that read as laundry powder. A printer cannot
produce from that, and nobody could revise it because the generator was never
kept. This script IS the artwork, so every future revision is a one-line change
and a re-run.

Art direction follows the iteration the client approved over WhatsApp: deep navy
ground, the real blue-oval Swift mark, one yellow accent, red reserved for signal.

Output
------
  dist/Swift_Blue-Drop_4x50g_Carton_PRINT.pdf   artwork only, for the converter
  dist/Swift_Blue-Drop_4x50g_Carton_GUIDES.pdf  same + cut/crease/bleed/safe layer

Run:  python packaging/swift_blue_drop_dieline.py
"""

import os
from math import pi, sin, cos

from reportlab.pdfgen import canvas
from reportlab.lib.colors import CMYKColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(HERE, "dist")
FONTDIR = os.path.join(HERE, "fonts")
LOGO = os.path.join(ROOT, "images", "logo", "swift-logo.png")

# ----------------------------------------------------------------------------
# 1. CARTON SPEC - every dimension in millimetres, all in one place.
#    Set these to the converter's actual die spec and the whole pack re-flows.
# ----------------------------------------------------------------------------
MM = 72.0 / 25.4            # points per millimetre

W_FACE = 105.0              # front / back panel width
W_SIDE = 48.0               # side panel width (carton depth)
H_BODY = 155.0              # panel height
W_GLUE = 15.0               # glue tab
H_TUCK = 45.0               # tuck flap depth  (~ W_SIDE - 3)
H_DUST = 43.0               # dust flap depth  (~ W_SIDE - 5)
BLEED = 3.0                 # bleed on every outer edge
SAFE = 5.0                  # keep live copy this far inside every fold/cut

# Panel origins along x, left to right: glue | back | sideL | front | sideR
X_GLUE = 0.0
X_BACK = X_GLUE + W_GLUE
X_SIDL = X_BACK + W_FACE
X_FRNT = X_SIDL + W_SIDE
X_SIDR = X_FRNT + W_FACE
SHEET_W = X_SIDR + W_SIDE
SHEET_H = H_TUCK + H_BODY + H_TUCK
Y_BODY = H_TUCK                         # bottom of the body band
Y_TOP = Y_BODY + H_BODY                 # top of the body band

# Distance from the page edge to artwork x=0. Normally the bleed; the guides
# build widens it so the legend and panel callouts have somewhere to live.
ORIGIN = BLEED

# ---- Euro hang tab ---------------------------------------------------------
# A peg hole needs unbroken material to pull against, so the tab is a straight
# extension of the BACK panel with no crease at its base - creasing it there is
# what makes hang tabs tear off. That pushes BOTH tuck ends onto the front
# panel, which makes this a straight tuck end rather than a reverse tuck.
H_HANG = 26.0               # how far the tab stands above the closed carton
TAB_W = 62.0                # tab width (panel is 105)
TAB_CH = 7.0                # shoulder chamfer
SLOT_R = 3.2                # euro hole radius
SLOT_W = 5.0                # riser width
SLOT_RISE = 7.2             # riser height above the hole centre
SLOT_Y = 8.5                # hole centre, above the top crease
# material left above the slot; under ~6 mm a peg hole tears out
TAB_HEADROOM = H_HANG - (SLOT_Y + SLOT_RISE + SLOT_W / 2)

# ---- Scent vents -----------------------------------------------------------
# The product is bought on fragrance; a sealed carton releases none of it.
# Five droplet cut-outs per side panel, sized so scent escapes but a 48 mm
# block cannot. Droplets rather than round holes so the die feature doubles
# as a brand mark.
# A vertical column down the middle of a 48 mm panel runs straight through
# the copy, so the vents sit in a horizontal row in a band kept clear for
# them on both side panels.
VENT_N = 5
VENT_H = 5.6                # droplet height
VENT_GAP = 7.6              # pitch across the panel
VENT_Y = 100.0              # row centre, absolute

TUCK_TOP_X = X_FRNT
TUCK_BOT_X = X_FRNT
TAB_X0 = X_BACK + (W_FACE - TAB_W) / 2.0
TAB_X1 = TAB_X0 + TAB_W

# ----------------------------------------------------------------------------
# 2. PALETTE - CMYK, hand-specified rather than machine-converted from RGB.
#    A naive RGB->CMYK of the navy prints muddy; these are mixes a press can hit.
#    Total ink stays under 300% everywhere.
# ----------------------------------------------------------------------------
NAVY      = CMYKColor(1.00, 0.85, 0.10, 0.15)   # #01236B  client-ref ground
NAVY_DK   = CMYKColor(1.00, 0.90, 0.15, 0.40)   # burst outer edge
NAVY_MID  = CMYKColor(1.00, 0.78, 0.05, 0.05)
BLUE_MID  = CMYKColor(1.00, 0.70, 0.00, 0.05)   # #00459A  Swift oval, dark stop
BLUE_BR   = CMYKColor(0.85, 0.40, 0.00, 0.00)   # #0079C4  Swift oval, light stop
CYAN      = CMYKColor(0.65, 0.10, 0.00, 0.00)   # #33BFF3  water
CYAN_LT   = CMYKColor(0.35, 0.02, 0.00, 0.00)   # #99DFF9  water highlight
YELLOW    = CMYKColor(0.00, 0.12, 1.00, 0.00)   # #FEDA00  single accent
RED       = CMYKColor(0.00, 0.95, 0.90, 0.00)   # #ED1E26  signal only
GREEN     = CMYKColor(0.75, 0.05, 0.95, 0.00)   # recycling marks
WHITE     = CMYKColor(0.00, 0.00, 0.00, 0.00)
INK       = CMYKColor(0.00, 0.00, 0.00, 0.85)   # body text on white
GREY      = CMYKColor(0.00, 0.00, 0.00, 0.45)

# Dieline guide colours (guides build only - never printed)
CUT    = CMYKColor(0.00, 1.00, 0.00, 0.00)      # magenta
CREASE = CMYKColor(1.00, 0.00, 0.00, 0.00)      # cyan, dashed
BLEEDC = CMYKColor(0.00, 0.40, 1.00, 0.00)      # orange
SAFEC  = CMYKColor(0.80, 0.00, 1.00, 0.00)      # green, dashed

# ----------------------------------------------------------------------------
# 3. FONTS - Outfit + Plus Jakarta Sans, both SIL Open Font License, so they may
#    be embedded in a commercial package without a foundry licence. (Arial and
#    Segoe UI are Microsoft-licensed; cleaner to avoid them on client artwork.)
# ----------------------------------------------------------------------------
FONTS = {
    "display":  "Outfit-900",
    "head":     "Outfit-800",
    "subhead":  "Outfit-700",
    "label":    "Outfit-600",
    "body":     "Jakarta-400",
    "bodymed":  "Jakarta-500",
    "bodysemi": "Jakarta-600",
    "bodybold": "Jakarta-700",
    "bodyblk":  "Jakarta-800",
}
F = FONTS


def register_fonts():
    for name in sorted(set(FONTS.values())):
        path = os.path.join(FONTDIR, name + ".ttf")
        if not os.path.exists(path):
            raise SystemExit("missing font: " + path)
        pdfmetrics.registerFont(TTFont(name, path))


# ----------------------------------------------------------------------------
# 4. GEOMETRY + TEXT HELPERS
#    Everything downstream speaks millimetres on the flat sheet; P() is the only
#    place that knows about points and the bleed offset.
# ----------------------------------------------------------------------------

def P(v):
    return (v + ORIGIN) * MM


def sw(text, font, size):
    return pdfmetrics.stringWidth(text, font, size)


def fit(text, font, target_mm, cap=400.0):
    """Largest point size at which text fits target_mm wide."""
    w = sw(text, font, 100.0)
    if w <= 0:
        return cap
    return min(cap, target_mm * MM / w * 100.0)


# Live layout guard. Dense panels are easy to overrun by a millimetre and the
# damage is invisible until it is on press, so every string is measured against
# the panel it was drawn into and anything that escapes is reported by name.
PANEL = None          # (label, x, y, w, h) of the panel currently being painted
OVERFLOW = []
BOXES = []            # every text bbox drawn, for the collision pass


def panel(label, x, y, w, h):
    global PANEL
    PANEL = (label, x, y, w, h)


def panel_end():
    global PANEL
    PANEL = None


def _check(s, x0, x1, y0):
    if PANEL is None:
        return
    label, px, py, pw, ph = PANEL
    over = []
    if x0 < px + 1.0:
        over.append("left by %.1f" % (px + 1.0 - x0))
    if x1 > px + pw - 1.0:
        over.append("right by %.1f" % (x1 - (px + pw - 1.0)))
    if y0 < py + 1.0:
        over.append("bottom by %.1f" % (py + 1.0 - y0))
    if y0 > py + ph - 1.0:
        over.append("top by %.1f" % (y0 - (py + ph - 1.0)))
    if over:
        OVERFLOW.append("%-10s %-44s %s mm" %
                        (label, (s[:41] + "..") if len(s) > 43 else s,
                         ", ".join(over)))


def _record(s, x0, x1, y0, size_pt):
    """Remember where each string landed so collisions can be found later.
    Escaping the panel is one failure mode; two blocks landing on top of each
    other inside it is the other, and only measurement catches either."""
    if PANEL is None or not s.strip():
        return
    asc, desc = size_pt / MM * 0.76, size_pt / MM * 0.22
    BOXES.append((PANEL[0], s, x0, x1, y0 - desc, y0 + asc))


def collisions(min_overlap=0.7):
    """Pairwise overlap test, panel by panel."""
    hits = []
    for i in range(len(BOXES)):
        pi, si, ax0, ax1, ay0, ay1 = BOXES[i]
        for j in range(i + 1, len(BOXES)):
            pj, sj, bx0, bx1, by0, by1 = BOXES[j]
            if pi != pj:
                continue
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > min_overlap and oy > min_overlap:
                hits.append("%-10s %-30s X %-30s  %.1f x %.1f mm" %
                            (pi, si[:28], sj[:28], ox, oy))
    return hits


def txt(c, x, y, s, font, size, colour, align="l", char_space=0.0):
    """Letter-spacing lives on the text object, not the canvas, so tracked
    strings go through beginText and plain ones take the cheaper path."""
    w = sw(s, font, size) + char_space * max(0, len(s) - 1)
    px = P(x) - (w / 2 if align == "c" else w if align == "r" else 0)
    _x0 = px / MM - ORIGIN
    _check(s, _x0, _x0 + w / MM, y)
    _record(s, _x0, _x0 + w / MM, y, size)
    c.setFillColor(colour)
    if char_space:
        t = c.beginText(px, P(y))
        t.setFont(font, size)
        t.setCharSpace(char_space)
        t.textLine(s)
        # Tc is graphics state, not text-object state: without resetting it
        # here the tracking leaks into every later string, which renders them
        # wider than stringWidth predicts and silently breaks every wrap.
        t.setCharSpace(0)
        c.drawText(t)
    else:
        c.setFont(font, size)
        c.drawString(px, P(y), s)
    return w / MM


def wrap(text, font, size, width_mm):
    limit = width_mm * MM
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if sw(trial, font, size) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(c, x, y, text, font, size, colour, width_mm, leading_mm, align="l"):
    """Draw wrapped copy downward from y. Returns the y below the last line."""
    for ln in wrap(text, font, size, width_mm):
        txt(c, x, y, ln, font, size, colour, align)
        y -= leading_mm
    return y


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


def clip_rect(c, x, y, w, h):
    p = c.beginPath()
    p.rect(P(x), P(y), w * MM, h * MM)
    c.clipPath(p, stroke=0, fill=0)


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


def circle(c, cx, cy, r, colour, alpha=1.0, stroke=None, lw=0.0):
    c.saveState()
    c.setFillColor(colour, alpha)
    if stroke is not None:
        c.setStrokeColor(stroke, alpha)
        c.setLineWidth(lw * MM)
    c.circle(P(cx), P(cy), r * MM, fill=1, stroke=1 if stroke is not None else 0)
    c.restoreState()


def line(c, x1, y1, x2, y2, colour, lw, alpha=1.0, dash=None, cap=1):
    c.saveState()
    c.setStrokeColor(colour, alpha)
    c.setLineWidth(lw * MM)
    c.setLineCap(cap)
    if dash:
        c.setDash([d * MM for d in dash], 0)
    c.line(P(x1), P(y1), P(x2), P(y2))
    c.restoreState()


# ----------------------------------------------------------------------------
# 5. VECTOR ART PRIMITIVES
#    Everything on this pack is drawn, not photographed, so it stays crisp at
#    any size and carries no resampling or generative artefacts. Functions that
#    need rotation or squash work in raw point space inside their own
#    save/restore, which is why they do not call P() on inner coordinates.
# ----------------------------------------------------------------------------

def burst(c, x, y, w, h, cx, cy, inner=BLUE_BR, mid=BLUE_MID, outer=NAVY_DK,
          rays=40, ray_alpha=0.07):
    """Radial ground with soft spokes - the client reference signature look."""
    c.saveState()
    clip_rect(c, x, y, w, h)
    radius = max(w, h) * 1.15 * MM
    c.radialGradient(P(cx), P(cy), radius,
                     [inner, mid, outer], [0.0, 0.42, 1.0], extend=True)
    R = max(w, h) * 1.6
    for i in range(rays):
        a0 = i * 2 * pi / rays
        a1 = a0 + (2 * pi / rays) * 0.42
        poly(c, [(cx, cy),
                 (cx + R * cos(a0), cy + R * sin(a0)),
                 (cx + R * cos(a1), cy + R * sin(a1))],
             WHITE, alpha=ray_alpha)
    c.restoreState()


def annulus(c, cx, cy, r_in, r_out, a0, a1, colour, alpha=1.0, squash=1.0,
            steps=48):
    """Filled annular sector - the building block for every water form."""
    c.saveState()
    c.setFillColor(colour, alpha)
    c.translate(P(cx), P(cy))
    c.scale(1.0, squash)
    p = c.beginPath()
    first = True
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        px, py = r_out * cos(a) * MM, r_out * sin(a) * MM
        if first:
            p.moveTo(px, py)
            first = False
        else:
            p.lineTo(px, py)
    for i in range(steps, -1, -1):
        a = a0 + (a1 - a0) * i / steps
        p.lineTo(r_in * cos(a) * MM, r_in * sin(a) * MM)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def _drop_path(c, cx, cy, h, bulge=1.00):
    """The silhouette on its own, so fill, clip and stroke all share one curve.

    The shoulder control points sit at 0.30h rather than hard against the apex,
    which is what gives a real droplet its slightly concave neck instead of the
    plain cone the first version drew.
    """
    r = h * 0.335 * bulge
    top = cy + h * 0.5
    by = cy - h * 0.5 + r
    p = c.beginPath()
    p.moveTo(P(cx), P(top))
    p.curveTo(P(cx + r * 0.30), P(top - h * 0.30),
              P(cx + r * 0.95), P(by + r * 0.80),
              P(cx + r), P(by))
    p.curveTo(P(cx + r), P(by - r * 1.336),
              P(cx - r), P(by - r * 1.336),
              P(cx - r), P(by))
    p.curveTo(P(cx - r * 0.95), P(by + r * 0.80),
              P(cx - r * 0.30), P(top - h * 0.30),
              P(cx), P(top))
    p.close()
    return p, r, by


def droplet(c, cx, cy, h, colour, alpha=1.0, highlight=True):
    """Flat droplet. Correct for icon use, where a solid silhouette has to
    read at 4 mm; see droplet_gloss for the hero mark."""
    c.saveState()
    c.setFillColor(colour, alpha)
    p, r, by = _drop_path(c, cx, cy, h)
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()
    if highlight:
        circle(c, cx - r * 0.34, by + r * 0.10, r * 0.26, WHITE,
               alpha=0.55 * alpha)


def droplet_gloss(c, cx, cy, h, light=True, alpha=1.0, shadow=True):
    """The hero droplet: refracting water, not a flat teardrop.

    Built the way a real drop reads - a graded body, a dark rim where the
    surface turns away, a bright caustic pooled at the bottom where light
    exits, one soft specular and one tight glint. Everything is clipped to a
    single shared path so no element can drift off the silhouette.

    light=True  : glass drop for dark grounds (white-to-cyan)
    light=False : solid brand-blue drop for light grounds
    """
    r = h * 0.335
    by = cy - h * 0.5 + r

    if shadow:
        for k, a in ((1.12, 0.07), (1.0, 0.10), (0.88, 0.13)):
            c.saveState()
            c.setFillColor(NAVY_DK, a * alpha)
            c.translate(P(cx + h * 0.035), P(by - r * 0.52))
            c.scale(1.0, 0.34)
            c.circle(0, 0, r * k * MM, fill=1, stroke=0)
            c.restoreState()

    stops = ([WHITE, CYAN_LT, BLUE_BR, BLUE_MID] if light
             else [CYAN_LT, BLUE_BR, BLUE_MID, NAVY])

    # body
    c.saveState()
    p, _, _ = _drop_path(c, cx, cy, h)
    c.clipPath(p, stroke=0, fill=0)
    c.radialGradient(P(cx - r * 0.34), P(by + r * 0.46), h * 0.92 * MM,
                     stops, [0.0, 0.34, 0.72, 1.0], extend=True)

    # caustic: light that has passed through the drop pools at the base
    for i in range(7):
        k = 0.80 - i * 0.085
        c.saveState()
        c.setFillColor(WHITE, 0.14 * alpha)
        c.translate(P(cx), P(by - r * 0.30))
        c.scale(1.0, 0.52)
        c.circle(0, 0, r * k * MM, fill=1, stroke=0)
        c.restoreState()

    # rim darkening where the surface turns away from the viewer
    c.setStrokeColor(BLUE_MID if light else NAVY, 0.45 * alpha)
    c.setLineWidth(h * 0.030 * MM)
    p2, _, _ = _drop_path(c, cx, cy, h)
    c.drawPath(p2, fill=0, stroke=1)
    c.restoreState()

    # soft specular, upper left, following the neck
    c.saveState()
    c.setFillColor(WHITE, 0.82 * alpha)
    c.translate(P(cx - r * 0.40), P(by + r * 0.72))
    c.rotate(-18)
    c.scale(0.46, 1.0)
    c.circle(0, 0, r * 0.62 * MM, fill=1, stroke=0)
    c.restoreState()
    # tight glint
    circle(c, cx - r * 0.16, by + r * 0.04, r * 0.15, WHITE, alpha=0.95 * alpha)
    # rim light on the lower right, where the ground bounces back up
    c.saveState()
    c.setStrokeColor(WHITE, 0.55 * alpha)
    c.setLineWidth(h * 0.022 * MM)
    c.setLineCap(1)
    c.translate(P(cx), P(by))
    pa = c.beginPath()
    for i in range(25):
        a = -0.95 + (1.75 * i / 24.0)
        px, py = r * 0.90 * cos(a) * MM, r * 0.90 * sin(a) * MM
        (pa.moveTo if i == 0 else pa.lineTo)(px, py)
    c.drawPath(pa, fill=0, stroke=1)
    c.restoreState()


def bubble(c, cx, cy, r, colour=WHITE, alpha=0.30):
    circle(c, cx, cy, r, colour, alpha=alpha * 0.55)
    c.saveState()
    c.setStrokeColor(WHITE, alpha)
    c.setLineWidth(max(0.12, r * 0.14) * MM)
    c.circle(P(cx), P(cy), r * MM, fill=0, stroke=1)
    c.restoreState()
    circle(c, cx - r * 0.34, cy + r * 0.34, r * 0.24, WHITE,
           alpha=min(1.0, alpha * 2.2))


def sparkle(c, cx, cy, r, colour=WHITE, alpha=1.0):
    """Four-point star - the clean signal used across the benefit row."""
    k = r * 0.17
    poly(c, [(cx, cy + r), (cx + k, cy + k), (cx + r, cy),
             (cx + k, cy - k), (cx, cy - r), (cx - k, cy - k),
             (cx - r, cy), (cx - k, cy + k)], colour, alpha=alpha)


def _disc(c, cx, cy, r, squash, colour, alpha=1.0):
    c.saveState()
    c.setFillColor(colour, alpha)
    c.translate(P(cx), P(cy))
    c.scale(1.0, squash)
    c.circle(0, 0, r * MM, fill=1, stroke=0)
    c.restoreState()


def tablet(c, cx, cy, r, squash=0.50, ribs=30, rot=0.0, shadow=True):
    """The product itself: a ribbed blue cistern block.

    Drawn as a short cylinder rather than a flat disc - a bottom ellipse, a
    straight wall band of the same width, then the ribbed top face. The wall is
    what makes it read as a solid object on shelf; the first pass drew only the
    top face and the blocks looked like printed circles.
    """
    thick = r * 0.30

    if shadow:                      # stacked ellipses fake a soft contact shadow
        for k, a in ((1.14, 0.05), (1.08, 0.07), (1.02, 0.10)):
            _disc(c, cx, cy - thick - r * 0.06, r * k, squash, NAVY_DK, a)

    # --- side wall ----------------------------------------------------------
    _disc(c, cx, cy - thick, r, squash, NAVY_DK)
    c.saveState()
    c.setFillColor(NAVY_DK)
    c.rect(P(cx - r), P(cy - thick), 2 * r * MM, thick * MM, fill=1, stroke=0)
    c.restoreState()
    # vertical flutes down the wall, so the ribbing wraps the whole block
    for i in range(ribs):
        a = rot + i * 2 * pi / ribs
        wx = cx + r * cos(a)
        if sin(a) > 0.1:
            continue
        c.saveState()
        c.setFillColor(BLUE_MID, 0.55)
        c.rect(P(wx - r * 0.022), P(cy - thick), r * 0.044 * MM,
               thick * MM, fill=1, stroke=0)
        c.restoreState()
    # the wall catches light along its upper edge
    c.saveState()
    c.setFillColor(BLUE_MID, 0.45)
    c.rect(P(cx - r), P(cy - thick * 0.30), 2 * r * MM, thick * 0.30 * MM,
           fill=1, stroke=0)
    c.restoreState()

    # --- top face -----------------------------------------------------------
    _disc(c, cx, cy, r, squash, BLUE_MID)
    annulus(c, cx, cy, r * 0.93, r, 0, 2 * pi, BLUE_BR, squash=squash)
    annulus(c, cx, cy, r * 0.89, r * 0.94, 0, 2 * pi, CYAN_LT, alpha=0.70,
            squash=squash)

    # ribbing: a light face and a dark groove per rib, which holds its shape
    # far better on press than a single alternating wedge did
    for i in range(ribs):
        a0 = rot + i * 2 * pi / ribs
        step = 2 * pi / ribs
        annulus(c, cx, cy, r * 0.34, r * 0.89, a0, a0 + step * 0.50,
                CYAN_LT, alpha=0.30, squash=squash, steps=3)
        annulus(c, cx, cy, r * 0.34, r * 0.89, a0 + step * 0.50, a0 + step,
                NAVY_MID, alpha=0.20, squash=squash, steps=3)

    # hub
    _disc(c, cx, cy, r * 0.34, squash, NAVY_MID, 0.75)
    _disc(c, cx, cy, r * 0.27, squash, BLUE_BR)
    _disc(c, cx, cy, r * 0.13, squash, CYAN_LT, 0.80)

    # specular sweep across the upper left, plus a tight glint
    annulus(c, cx, cy, r * 0.38, r * 0.92, pi * 0.60, pi * 1.04, WHITE,
            alpha=0.26, squash=squash)
    annulus(c, cx, cy, r * 0.94, r * 0.99, pi * 0.52, pi * 0.92, WHITE,
            alpha=0.55, squash=squash)


def water_swirl(c, cx, cy, r, alpha=1.0):
    """Stylised vortex - reads as flushing water without a photograph."""
    bands = [(0.90, 1.00, CYAN_LT, 0.40, 0.25, 1.70),
             (0.70, 0.84, WHITE,   0.30, 0.70, 2.05),
             (0.50, 0.64, CYAN_LT, 0.45, 1.15, 1.80),
             (0.30, 0.44, WHITE,   0.34, 1.65, 1.50)]
    for r0, r1, col, a, a_start, span in bands:
        annulus(c, cx, cy, r * r0, r * r1, a_start, a_start + span, col,
                alpha=a * alpha, squash=0.46)


def bowl(c, cx, cy, w, alpha=1.0):
    """Flat-art WC bowl. Deliberately simple: a supporting cue, not the hero,
    so it must not compete with the tablets."""
    h = w * 1.05
    c.saveState()
    c.setFillColor(WHITE, alpha)
    c.roundRect(P(cx - w * 0.40), P(cy + h * 0.10), w * 0.80 * MM,
                h * 0.42 * MM, w * 0.07 * MM, fill=1, stroke=0)
    c.setFillColor(CYAN_LT, 0.45 * alpha)
    c.roundRect(P(cx - w * 0.34), P(cy + h * 0.16), w * 0.68 * MM,
                h * 0.30 * MM, w * 0.05 * MM, fill=1, stroke=0)
    c.restoreState()
    poly(c, [(cx - w * 0.26, cy + h * 0.10), (cx + w * 0.26, cy + h * 0.10),
             (cx + w * 0.17, cy - h * 0.36), (cx - w * 0.17, cy - h * 0.36)],
         WHITE, alpha=alpha)
    c.saveState()
    c.setFillColor(WHITE, alpha)
    c.translate(P(cx), P(cy + h * 0.06))
    c.scale(1.0, 0.44)
    c.circle(0, 0, w * 0.46 * MM, fill=1, stroke=0)
    c.setFillColor(BLUE_BR)
    c.circle(0, 0, w * 0.35 * MM, fill=1, stroke=0)
    c.restoreState()
    water_swirl(c, cx, cy + h * 0.06, w * 0.30, alpha=alpha)


def cistern_diagram(c, x, y, w, colour=INK, lw=0.30):
    """Line drawing for the back panel: where the tablet goes in the tank."""
    h = w * 0.74
    c.saveState()
    c.setStrokeColor(colour)
    c.setFillColor(colour)
    c.setLineWidth(lw * MM)
    c.setLineJoin(1)
    c.rect(P(x), P(y), w * MM, h * MM, fill=0, stroke=1)
    c.saveState()
    c.setDash([1.1 * MM, 1.1 * MM], 0)
    c.setStrokeAlpha(0.55)
    c.line(P(x + 1.5), P(y + h * 0.66), P(x + w - 1.5), P(y + h * 0.66))
    c.restoreState()
    c.circle(P(x + w * 0.74), P(y + h * 0.62), w * 0.09 * MM, fill=0, stroke=1)
    c.line(P(x + w * 0.40), P(y + h * 0.62), P(x + w * 0.65), P(y + h * 0.62))
    c.line(P(x + w * 0.40), P(y + h * 0.14), P(x + w * 0.40), P(y + h * 0.86))
    c.rect(P(x + w * 0.30), P(y + h * 0.08), w * 0.20 * MM, h * 0.10 * MM,
           fill=0, stroke=1)
    c.line(P(x + w * 0.40), P(y), P(x + w * 0.40), P(y - h * 0.16))
    c.restoreState()
    tablet(c, x + w * 0.20, y + h * 0.40, w * 0.115, squash=0.52, ribs=16)
    line(c, x + w * 0.20, y + h * 0.86, x + w * 0.20, y + h * 0.58, colour,
         lw * 1.4)
    poly(c, [(x + w * 0.20, y + h * 0.50),
             (x + w * 0.20 - w * 0.045, y + h * 0.61),
             (x + w * 0.20 + w * 0.045, y + h * 0.61)], colour)


# The address the carton QR resolves to. The site declares this as its
# canonical host, and datasheet.html?id=<product> is a real page in the repo -
# a QR that lands on a 404 is worse than no QR at all.
QR_BASE = "https://www.vistexchemicals.co.ke/datasheet.html?id="


def qr_code(c, x, y, size, data, dark=NAVY, plate=WHITE, quiet=1.6):
    """QR on its own white plate. Printing modules straight onto the navy
    band would halve the contrast a phone camera has to work with, and a
    code that needs three attempts in a store room may as well not be there.
    """
    from reportlab.graphics.barcode import qr as _qr
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics import renderPDF
    if plate is not None:
        rect(c, x - quiet, y - quiet, size + 2 * quiet, size + 2 * quiet,
             plate)
    w = _qr.QrCodeWidget(data, barLevel="M")
    bb = w.getBounds()
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    w.barFillColor = dark
    d = Drawing(size * MM, size * MM, transform=[
        size * MM / bw, 0, 0, size * MM / bh,
        -bb[0] * size * MM / bw, -bb[1] * size * MM / bh])
    d.add(w)
    renderPDF.draw(d, c, P(x), P(y))
    return size + 2 * quiet


_RECYCLE = {}


def _recycle_reader():
    """White-tinted recycle mark. The supplied art is blue, which disappears
    on a navy panel."""
    if "w" not in _RECYCLE:
        from PIL import Image as _I
        path = os.path.join(HERE, "art", "recycle-outline.png")
        if not os.path.exists(path):
            _RECYCLE["w"] = None
        else:
            im = _I.open(path).convert("RGBA")
            flat = _I.new("RGBA", im.size, (255, 255, 255, 255))
            flat.putalpha(im.getchannel("A"))
            _RECYCLE["w"] = ImageReader(flat)
    return _RECYCLE["w"]


def swift_logo(c, cx, cy, width, shadow=True):
    """The authentic mark: blue oval, droplet over the i, Usafi Halisi inside.
    Placed from the brand asset rather than redrawn, so it cannot drift."""
    img = ImageReader(LOGO)
    iw, ih = img.getSize()
    h = width * ih / iw
    if shadow:
        c.saveState()
        c.setFillColor(NAVY_DK, 0.20)
        c.translate(P(cx), P(cy - h * 0.06))
        c.scale(1.0, 0.52)
        c.circle(0, 0, width * 0.44 * MM, fill=1, stroke=0)
        c.restoreState()
    c.drawImage(img, P(cx - width / 2), P(cy - h / 2),
                width * MM, h * MM, mask="auto")
    return h


def shield(c, cx, cy, r, colour, alpha=1.0):
    """Protection mark - a crest, not a circle, so it reads apart from the
    sparkle and droplet at thumbnail size."""
    c.saveState()
    c.setFillColor(colour, alpha)
    p = c.beginPath()
    p.moveTo(P(cx), P(cy + r))
    p.lineTo(P(cx + r * 0.82), P(cy + r * 0.52))
    p.curveTo(P(cx + r * 0.82), P(cy - r * 0.52),
              P(cx + r * 0.38), P(cy - r * 0.88),
              P(cx), P(cy - r))
    p.curveTo(P(cx - r * 0.38), P(cy - r * 0.88),
              P(cx - r * 0.82), P(cy - r * 0.52),
              P(cx - r * 0.82), P(cy + r * 0.52))
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def tick(c, cx, cy, r, colour, lw_scale=0.26):
    c.saveState()
    c.setStrokeColor(colour)
    c.setLineWidth(r * lw_scale * MM)
    c.setLineCap(1)
    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(P(cx - r * 0.52), P(cy + r * 0.04))
    p.lineTo(P(cx - r * 0.14), P(cy - r * 0.42))
    p.lineTo(P(cx + r * 0.56), P(cy + r * 0.46))
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()


def txt_outlined(c, x, y, s, font, size, fill, outline, lw,
                 align="l", shadow=None, shadow_off=(0.6, -0.6)):
    """Display type with a stroke and an optional cast shadow.

    Render mode 2 (fill-then-stroke) keeps this as one glyph run, so it stays
    live, selectable text on press rather than outlines or a raster.
    """
    w = sw(s, font, size)
    px = P(x) - (w / 2 if align == "c" else w if align == "r" else 0)
    if shadow is not None:
        c.saveState()
        c.setFillColor(shadow)
        c.setFont(font, size)
        c.drawString(px + shadow_off[0] * MM, P(y) + shadow_off[1] * MM, s)
        c.restoreState()
    c.saveState()
    t = c.beginText(px, P(y))
    t.setFont(font, size)
    c.setFillColor(fill)
    if lw > 0:
        # Render mode 2 strokes every contour in the glyph, including the
        # internal edges where a heavy weight self-overlaps, which drew bars
        # and notches through the counters. Only stroke when asked for.
        t.setTextRenderMode(2)
        c.setStrokeColor(outline)
        c.setLineWidth(lw * MM)
        c.setLineJoin(1)
    t.textLine(s)
    c.drawText(t)
    c.restoreState()
    return w / MM


def section_pill(c, x, y, w, label, bg=NAVY, fg=WHITE, h=6.2, size=7.2):
    pill(c, x, y, w, h, bg)
    txt(c, x + w / 2, y + h * 0.31, label, F["subhead"], size, fg, "c")
    return y - 2.6


def bullets(c, x, y, items, width_mm, size=5.9, leading=3.0, gap=1.3,
            colour=INK, dot=BLUE_MID, dot_r=0.55):
    for it in items:
        lines = wrap(it, F["body"], size, width_mm - 3.2)
        circle(c, x + 0.9, y + 0.72, dot_r, dot)
        for i, ln in enumerate(lines):
            txt(c, x + 3.2, y - i * leading, ln, F["body"], size, colour)
        y -= leading * len(lines) + gap
    return y


# ----------------------------------------------------------------------------
# 6. PANEL COMPOSITIONS
# ----------------------------------------------------------------------------

EMAIL = "info@vistexchemicals.co.ke"
WEBSITE = "www.vistexchemicals.co.ke"
TEL = "0739 446 655"
ADDRESS = "P.O. Box 218 - 00606, Industrial Area, Nairobi, Kenya"


def panel_front(c):
    x, y, w, h = X_FRNT, Y_BODY, W_FACE, H_BODY
    panel("FRONT", x, y, w, h)
    top = y + h
    cx = x + w / 2

    burst(c, x, y, w, h, cx, y + h * 0.62)
    # The burst is lightest exactly where the blocks sit, so they were washing
    # out against it. Stacked low-alpha bands sink the lower third instead.
    for i in range(11):
        rect(c, x, y, w, 70.0 - i * 6.0, NAVY_DK, alpha=0.035)

    # --- hero, painted before the type so the copy always sits on top -------
    # Three depths: the bowl is a faint watermark that names the category, the
    # vortex sits behind the product, the four blocks are the only thing in
    # full contrast. An earlier pass drew the bowl at full strength beside the
    # blocks and it fought them for attention and sat on the weight statement.
    hx, hy = cx, y + 50.0
    # A faint bowl was tried here as a category cue and read as a rectangular
    # tray behind the blocks, so the backdrop is just light on water now.
    for rr, aa in ((48.0, 0.045), (42.0, 0.05), (35.0, 0.055), (27.0, 0.06)):
        _disc(c, hx, hy - 2.0, rr, 0.52, CYAN_LT, aa)
    water_swirl(c, hx, hy - 1.0, 34)
    # back row first, then the front row overlapping it
    for dx, dy, rot in ((-15.0, 10.0, 0.00), (15.0, 10.0, 0.22),
                        (-15.0, -10.0, 0.11), (15.0, -10.0, 0.33)):
        tablet(c, hx + dx, hy + dy, 14.0, squash=0.50, ribs=30, rot=rot)
    for bx, by, br, ba in ((x + 10, y + 70, 2.3, 0.34), (x + 17, y + 59, 1.3, 0.28),
                           (x + 94, y + 72, 2.0, 0.30), (x + 87, y + 83, 1.2, 0.24),
                           (x + 8, y + 36, 1.6, 0.22), (x + 97, y + 40, 1.5, 0.20)):
        bubble(c, bx, by, br, alpha=ba)

    # --- masthead ------------------------------------------------------------
    swift_logo(c, x + 28.5, top - 12.0, 43)

    # 4 PACK flag, skewed so it reads as a sticker rather than a box.
    # The 4 and PACK share a baseline; staggering them looked like an error.
    fx0, fy0, fw, fh = x + 62.5, top - 20.0, 37, 13.6
    poly(c, [(fx0 + 2.2, fy0), (fx0 + fw, fy0), (fx0 + fw - 2.2, fy0 + fh),
             (fx0, fy0 + fh)], YELLOW)
    txt(c, fx0 + 10.5, fy0 + 4.3, "4", F["display"], 21, RED, "c")
    txt(c, fx0 + 24.5, fy0 + 7.3, "PACK", F["head"], 10.0, NAVY, "c")
    txt(c, fx0 + 24.5, fy0 + 3.0, "50 g each", F["bodysemi"], 5.2, NAVY, "c")

    # --- product name --------------------------------------------------------
    name = "Blue-Drop"
    size = fit(name, F["display"], 74.0)
    txt_outlined(c, cx - 6.0, top - 42.0, name, F["display"], size,
                 WHITE, NAVY_DK, 0.0, "c", shadow=NAVY_DK,
                 shadow_off=(0.7, -0.75))
    droplet(c, cx + 39.0, top - 36.5, 12.0, CYAN_LT, alpha=0.98)

    txt(c, cx, top - 50.0, "AUTOMATIC TOILET BOWL CLEANER",
        F["label"], 8.4, WHITE, "c", char_space=0.7)

    # red strapline - the only red on the face, so it carries real weight
    sz = 7.6
    sw_ = sw("Fights Hard Water Stains", F["head"], sz) / MM
    pill(c, cx - (sw_ + 11) / 2, top - 61.0, sw_ + 11, 7.4, RED)
    txt(c, cx, top - 58.8, "Fights Hard Water Stains", F["head"], sz, WHITE, "c")

    # --- benefit row ---------------------------------------------------------
    labels = (("CLEANS", "sparkle"), ("FRESHENS", "drop"), ("PROTECTS", "shield"))
    step = 30.0
    bx0 = cx - step
    for i, (lab, kind) in enumerate(labels):
        bx = bx0 + i * step
        by = top - 70.0
        circle(c, bx, by, 4.6, WHITE, alpha=0.17)
        circle(c, bx, by, 4.6, WHITE, alpha=0.0, stroke=WHITE, lw=0.3)
        if kind == "sparkle":
            sparkle(c, bx, by, 3.3, WHITE)
        elif kind == "drop":
            droplet(c, bx, by, 6.4, WHITE, highlight=False)
        else:
            shield(c, bx, by, 3.5, WHITE)
            tick(c, bx, by + 0.2, 2.0, NAVY, lw_scale=0.34)
        txt(c, bx, by - 9.6, lab, F["subhead"], 6.4, WHITE, "c", char_space=0.3)

    # --- long lasting freshness ribbon --------------------------------------
    rx, ry, rw, rh = x + 4.5, y + 12.0, 46, 11.5
    poly(c, [(rx, ry), (rx + rw, ry), (rx + rw - 4.2, ry + rh), (rx, ry + rh)],
         YELLOW)
    txt(c, rx + 3.4, ry + 6.4, "LONG LASTING", F["head"], 7.2, NAVY)
    txt(c, rx + 3.4, ry + 1.9, "FRESHNESS", F["head"], 7.2, NAVY)

    # --- net weight ----------------------------------------------------------
    txt(c, x + w - 6.5, y + 19.6, "NET WT. 50 g per block", F["bodysemi"],
        6.4, CYAN_LT, "r")
    txt(c, x + w - 6.5, y + 13.8, "TOTAL NET WT. 200 g", F["bodyblk"],
        9.0, WHITE, "r")

    # --- footer bar ----------------------------------------------------------
    rect(c, x, y, w, 9.5, NAVY_DK)
    rect(c, x, y + 9.5, w, 0.5, CYAN, alpha=0.55)
    txt(c, x + 5.5, y + 3.4, EMAIL, F["bodymed"], 5.6, WHITE)
    txt(c, x + w - 5.5, y + 3.4, "VISTEX CHEMICALS LTD", F["bodyblk"], 5.9,
        WHITE, "r")


def panel_back(c):
    x, y, w, h = X_BACK, Y_BODY, W_FACE, H_BODY
    panel("BACK", x, y, w, h)
    top = y + h
    m = 6.0                       # inner margin
    cw = w - 2 * m                # content width
    col = (cw - 7.0) / 2          # two-column width, 7 mm gutter
    cl, cr = x + m, x + m + col + 7.0

    rect(c, x, y, w, h, WHITE)
    rect(c, x, top - 2.2, w, 2.2, NAVY)      # tiny crown tying it to the face

    # --- heading -------------------------------------------------------------
    txt(c, x + m, top - 11.5, "Swift Blue-Drop", F["head"],
        fit("Swift Blue-Drop", F["head"], 62.0), NAVY)
    txt(c, x + m, top - 17.4, "Flush-Activated WC Cleaner", F["subhead"], 8.6,
        BLUE_BR)
    droplet_gloss(c, x + w - m - 5.0, top - 11.0, 16.0, light=False)

    line(c, x + m, top - 20.6, x + w - m, top - 20.6, NAVY, 0.35, alpha=0.35)

    yy = para(c, x + m, top - 25.4,
              "One tablet in the cistern releases cleaner with every flush - "
              "fighting hard-water stains, lifting limescale and leaving a "
              "lasting fresh scent for up to 30 days.",
              F["body"], 6.0, INK, cw, 3.1)

    # --- left column ---------------------------------------------------------
    ly = yy - 3.0
    ly = section_pill(c, cl, ly - 6.2, col, "HOW TO USE")
    steps = ("Lift the cistern lid and take the tablet from its wrapper.",
             "Drop one tablet into the tank, clear of the inlet and float.",
             "Replace the lid. The tablet dissolves gradually with each flush.")
    sy = ly - 1.0
    for i, s in enumerate(steps, 1):
        circle(c, cl + 1.9, sy + 0.6, 1.9, BLUE_MID)
        txt(c, cl + 1.9, sy - 0.65, str(i), F["bodyblk"], 5.2, WHITE, "c")
        lines = wrap(s, F["body"], 5.9, col - 5.6)
        for j, ln in enumerate(lines):
            txt(c, cl + 5.4, sy - j * 3.0, ln, F["body"], 5.9, INK)
        sy -= 3.0 * len(lines) + 1.8

    sy = section_pill(c, cl, sy - 6.4, col, "IDEAL FOR")
    txt(c, cl, sy - 2.4,
        "Homes - Hotels - Restaurants", F["body"], 5.9, INK)
    txt(c, cl, sy - 5.4,
        "Schools - Hospitals - Offices", F["body"], 5.9, INK)
    txt(c, cl, sy - 8.4,
        "Public and staff washrooms", F["body"], 5.9, INK)
    sy -= 11.4

    # --- right column --------------------------------------------------------
    ry_ = yy - 3.0
    ry_ = section_pill(c, cr, ry_ - 6.2, col, "KEY BENEFITS")
    for i, b in enumerate(("Cleans with every flush",
                           "Fights germs and odour",
                           "Prevents limescale and stains",
                           "Up to 30 days per tablet",
                           "Long-lasting fresh scent")):
        tick(c, cr + 1.8, ry_ - 0.8 - i * 4.0, 1.7, GREEN)
        txt(c, cr + 4.8, ry_ - 1.9 - i * 4.0, b, F["body"], 5.9, INK)
    ry_ -= 5 * 4.0 + 1.0

    ry_ = section_pill(c, cr, ry_ - 6.2, col, "CAUTION", bg=RED)
    pill(c, cr, ry_ - 25.0, col, 25.0, RED, r=1.6, alpha=0.07)
    bullets(c, cr + 1.0, ry_ - 3.2,
            ("Keep out of reach of children.",
             "Do not ingest. Not a toilet freshener for handling.",
             "Avoid contact with skin and eyes. Wash hands after use.",
             "Store in a cool, dry place away from direct sunlight."),
            col - 2.0, size=5.6, leading=2.9, gap=0.9, dot=RED, dot_r=0.5)
    ry_ -= 26.5

    # --- cistern diagram, bridging the two columns ---------------------------
    # The diagram gets whatever vertical room is left between the columns and
    # the composition strip, and is sized to fit rather than assumed to fit.
    band_top = min(sy, ry_) - 1.0
    band_bot = y + 39.0
    avail = band_top - band_bot
    if avail >= 15.0:
        dw = min(29.0, (avail - 3.0) / 0.90)
        cistern_diagram(c, cl + 1.0, band_bot + 2.0, dw)
        txt(c, cl + dw + 7.0, band_top - 4.5, "Where it goes", F["subhead"],
            6.4, NAVY)
        para(c, cl + dw + 7.0, band_top - 8.5,
             "Keep the tablet clear of the inlet and the float ball so it "
             "cannot block either.", F["body"], 5.6, GREY,
             cw - dw - 8.0, 2.9)

    # --- composition / storage strip -----------------------------------------
    cyy = y + 30.0
    line(c, x + m, cyy + 7.0, x + w - m, cyy + 7.0, NAVY, 0.3, alpha=0.3)
    txt(c, x + m, cyy + 3.2, "COMPOSITION", F["subhead"], 5.6, NAVY,
        char_space=0.4)
    para(c, x + m, cyy - 0.4,
         "Anionic surfactants, dissolution modifiers, anti-redeposition "
         "agents, colourant, perfume.", F["body"], 5.4, GREY, col - 1.0, 2.7)
    txt(c, cr, cyy + 3.2, "STORAGE", F["subhead"], 5.6, NAVY, char_space=0.4)
    para(c, cr, cyy - 0.4,
         "Store upright in a cool, dry place. Keep the wrapper sealed until "
         "use.", F["body"], 5.4, GREY, col - 1.0, 2.7)

    # --- contact block -------------------------------------------------------
    bh = 22.0
    rect(c, x, y, w, bh, NAVY)
    rect(c, x, y + bh, w, 0.5, CYAN, alpha=0.5)
    txt(c, x + m, y + bh - 6.4, "A product of VISTEX CHEMICALS LTD",
        F["bodyblk"], 6.8, WHITE)
    txt(c, x + m, y + bh - 10.6, ADDRESS, F["body"], 5.8, WHITE)
    txt(c, x + m, y + bh - 14.4, "Tel " + TEL + "   -   " + EMAIL,
        F["body"], 5.8, WHITE)
    txt(c, x + m, y + bh - 18.2, WEBSITE, F["bodysemi"], 5.8, CYAN_LT)


def panel_side(c, x, variant):
    """The two 48 mm flanks. Left carries the benefit stack, right carries the
    regulatory copy, so neither panel is a wasted face on shelf."""
    y, w, h = Y_BODY, W_SIDE, H_BODY
    top = y + h
    cx = x + w / 2
    panel("SIDE-" + variant[:4].upper(), x, y, w, h)

    burst(c, x, y, w, h, cx, y + h * 0.70, rays=26, ray_alpha=0.055)

    swift_logo(c, cx, top - 11.0, 36)
    txt(c, cx, top - 23.5, "Blue-Drop", F["display"],
        fit("Blue-Drop", F["display"], 38.0), WHITE, "c")
    txt(c, cx, top - 28.6, "WC CLEANER", F["label"], 6.2, CYAN_LT, "c",
        char_space=0.6)
    line(c, x + 7, top - 32.0, x + w - 7, top - 32.0, WHITE, 0.3, alpha=0.35)

    if variant == "benefits":
        items = (("sparkle", "Cleans with", "every flush"),
                 ("drop", "Fights hard", "water stains"),
                 ("shield", "Prevents", "limescale"),
                 ("sparkle", "Long lasting", "freshness"))
        yy = top - 42.0
        for kind, l1, l2 in items:
            circle(c, x + 9.5, yy, 4.0, WHITE, alpha=0.16)
            if kind == "sparkle":
                sparkle(c, x + 9.5, yy, 2.9, WHITE)
            elif kind == "drop":
                droplet(c, x + 9.5, yy, 5.6, WHITE, highlight=False)
            else:
                shield(c, x + 9.5, yy, 3.0, WHITE)
            txt(c, x + 16.0, yy + 1.0, l1, F["bodysemi"], 6.6, WHITE)
            txt(c, x + 16.0, yy - 2.9, l2, F["bodysemi"], 6.6, WHITE)
            yy -= 13.5
        tablet(c, cx, y + 32.0, 11.0, squash=0.52, ribs=26)
    else:
        # Composition, storage and caution now live on the back panel, where
        # there is room to set them properly. Repeating them here wasted the
        # face; it carries the retail copy instead.
        yy = top - 40.0
        txt(c, x + 6, yy, "IDEAL FOR", F["subhead"], 6.4, CYAN_LT,
            char_space=0.4)
        yy -= 4.6
        for ln in ("Homes & offices", "Hotels & lodges", "Restaurants",
                   "Schools & hospitals", "Public washrooms"):
            circle(c, x + 7.2, yy + 0.7, 0.6, CYAN_LT)
            txt(c, x + 10.0, yy, ln, F["body"], 6.2, WHITE)
            yy -= 4.3
        yy -= 3.0
        line(c, x + 6, yy + 1.6, x + w - 6, yy + 1.6, WHITE, 0.3, alpha=0.35)
        yy -= 3.0
        txt(c, x + 6, yy, "ONE BLOCK", F["subhead"], 6.4, CYAN_LT,
            char_space=0.4)
        txt(c, x + 6, yy - 5.4, "30 days", F["head"], 12.0, WHITE)
        txt(c, x + 6, yy - 10.2, "of continuous clean", F["body"], 6.2, WHITE)

        # recycling, below the vent band
        my = y + 34.0
        rc = _recycle_reader()
        if rc is not None:
            rw = 12.0
            iw, ih = rc.getSize()
            c.drawImage(rc, P(cx - rw / 2), P(my - rw * ih / iw / 2),
                        rw * MM, rw * ih / iw * MM, mask="auto")
        txt(c, cx, my - 10.2, "RECYCLE", F["bodysemi"], 5.6, WHITE, "c")
        txt(c, cx, my - 14.2, "CARTON", F["bodysemi"], 5.6, WHITE, "c")

    # foot
    rect(c, x, y, w, 9.5, NAVY_DK)
    rect(c, x, y + 9.5, w, 0.5, CYAN, alpha=0.55)
    txt(c, cx, y + 5.8, "4 x 50 g", F["bodyblk"], 7.8, WHITE, "c")
    txt(c, cx, y + 1.8, "NET 200 g", F["bodysemi"], 6.0, WHITE, "c")


def euro_slot_path(c, cx, y_base):
    """The hang hole: a round eye with a narrower riser above it."""
    cy = y_base + SLOT_Y
    hw = SLOT_W / 2.0
    top = cy + SLOT_RISE
    p = c.beginPath()
    p.moveTo(P(cx - SLOT_R), P(cy))
    # eye, drawn as two arcs
    for i in range(25):
        a = pi + (pi * i / 24.0)
        p.lineTo(P(cx + SLOT_R * cos(a)), P(cy + SLOT_R * sin(a)))
    p.lineTo(P(cx + hw), P(cy))
    p.lineTo(P(cx + hw), P(top))
    for i in range(17):
        a = -(pi / 2) * (1 - i / 16.0) * 0 + (0 + pi * i / 16.0)
        p.lineTo(P(cx + hw * cos(a)), P(top + hw * sin(a)))
    p.lineTo(P(cx - hw), P(cy))
    p.close()
    return p


def hang_tab(c):
    """The tab itself. Printed like the rest of the pack; the eye is knocked
    out so previews read as a hole, which the die removes in any case."""
    rect(c, TAB_X0, Y_TOP, TAB_W, H_HANG, NAVY)
    rect(c, TAB_X0, Y_TOP + H_HANG - 0.6, TAB_W, 0.6, CYAN, alpha=0.5)
    cx = TAB_X0 + TAB_W / 2.0
    txt(c, cx, Y_TOP + 2.4, "SWIFT BLUE-DROP", F["subhead"], 6.4, WHITE, "c",
        char_space=0.8)
    c.saveState()
    c.setFillColor(WHITE)
    c.drawPath(euro_slot_path(c, cx, Y_TOP), fill=1, stroke=0)
    c.restoreState()


def vent_path(c, cx, cy, h):
    """One droplet-shaped vent as a closed path."""
    p, _, _ = _drop_path(c, cx, cy, h)
    return p


def vent_positions(panel_x, panel_w):
    cx = panel_x + panel_w / 2.0
    x0 = cx - (VENT_N - 1) * VENT_GAP / 2.0
    return [(x0 + i * VENT_GAP, VENT_Y) for i in range(VENT_N)]


def vents_art(c):
    """Knocked out white so previews read as holes; the die removes them."""
    for px, pw in ((X_SIDL, W_SIDE), (X_SIDR, W_SIDE)):
        for cx, cy in vent_positions(px, pw):
            c.saveState()
            c.setFillColor(WHITE)
            c.drawPath(vent_path(c, cx, cy, VENT_H), fill=1, stroke=0)
            c.restoreState()
            # a thin ring so the cut edge reads as deliberate on shelf
            c.saveState()
            c.setStrokeColor(CYAN_LT, 0.55)
            c.setLineWidth(0.3 * MM)
            c.drawPath(vent_path(c, cx, cy, VENT_H * 1.55), fill=0, stroke=1)
            c.restoreState()


def flap_art(c):
    """Tuck and dust flaps, all branded.

    A tuck flap is the first face anyone sees opening a case, and the dust
    flaps are what show when the carton is half open on a shelf. Leaving them
    plain navy wasted four printed surfaces, so each now carries the mark.
    """
    # top tuck, on the FRONT panel (the back carries the hang tab)
    cxf = TUCK_TOP_X + W_FACE / 2
    rect(c, TUCK_TOP_X, Y_TOP, W_FACE, H_TUCK, NAVY)
    swift_logo(c, cxf, Y_TOP + H_TUCK * 0.58, 40, shadow=False)
    txt(c, cxf, Y_TOP + H_TUCK * 0.18,
        "FLUSH-ACTIVATED WC CLEANER - 4 x 50 g", F["bodysemi"], 6.2,
        CYAN_LT, "c")

    # bottom tuck
    cxb = TUCK_BOT_X + W_FACE / 2
    rect(c, TUCK_BOT_X, Y_BODY - H_TUCK, W_FACE, H_TUCK, NAVY)
    swift_logo(c, cxb, Y_BODY - H_TUCK * 0.42, 40, shadow=False)
    txt(c, cxb, Y_BODY - H_TUCK * 0.82,
        "VISTEX CHEMICALS LTD - NAIROBI, KENYA", F["bodysemi"], 6.2,
        CYAN_LT, "c")

    # dust flaps
    for sx in (X_SIDL, X_SIDR):
        rect(c, sx, Y_TOP, W_SIDE, H_DUST, NAVY_MID)
        rect(c, sx, Y_BODY - H_DUST, W_SIDE, H_DUST, NAVY_MID)
        swift_logo(c, sx + W_SIDE / 2, Y_TOP + H_DUST * 0.55, 26,
                   shadow=False)
        swift_logo(c, sx + W_SIDE / 2, Y_BODY - H_DUST * 0.45, 26,
                   shadow=False)

    hang_tab(c)


def glue_tab(c):
    """Left unprinted. Ink under the glue line is the usual cause of cartons
    popping open, so the tab stays bare and varnish-free."""
    rect(c, X_GLUE - BLEED, Y_BODY, W_GLUE + BLEED, H_BODY, WHITE)


# ----------------------------------------------------------------------------
# 7. DIELINE / GUIDES LAYER
# ----------------------------------------------------------------------------

GT = 3.0    # glue tab taper
TT = 4.0    # tuck flap taper
DT = 3.0    # dust flap chamfer


def blank_outline():
    """The cut path of the whole blank, clockwise from the glue tab."""
    bw, bh = X_BACK + W_FACE, None
    return [
        (X_GLUE, Y_BODY + GT), (X_GLUE, Y_TOP - GT), (X_BACK, Y_TOP),
        # back panel: free edge, then the hang tab rises, then free edge again
        (TAB_X0, Y_TOP), (TAB_X0 + TAB_CH, Y_TOP + H_HANG),
        (TAB_X1 - TAB_CH, Y_TOP + H_HANG), (TAB_X1, Y_TOP),
        (X_SIDL, Y_TOP),
        # left side top dust flap
        (X_SIDL, Y_TOP + H_DUST - DT), (X_SIDL + DT, Y_TOP + H_DUST),
        (X_SIDL + W_SIDE - DT, Y_TOP + H_DUST),
        (X_SIDL + W_SIDE, Y_TOP + H_DUST - DT), (X_FRNT, Y_TOP),
        # front panel top tuck
        (X_FRNT + TT, Y_TOP + H_TUCK), (X_SIDR - TT, Y_TOP + H_TUCK),
        (X_SIDR, Y_TOP),
        # right side top dust flap
        (X_SIDR, Y_TOP + H_DUST - DT), (X_SIDR + DT, Y_TOP + H_DUST),
        (X_SIDR + W_SIDE - DT, Y_TOP + H_DUST),
        (X_SIDR + W_SIDE, Y_TOP + H_DUST - DT), (X_SIDR + W_SIDE, Y_TOP),
        # right edge
        (X_SIDR + W_SIDE, Y_BODY),
        # right side bottom dust flap
        (X_SIDR + W_SIDE, Y_BODY - H_DUST + DT),
        (X_SIDR + W_SIDE - DT, Y_BODY - H_DUST), (X_SIDR + DT, Y_BODY - H_DUST),
        (X_SIDR, Y_BODY - H_DUST + DT), (X_SIDR, Y_BODY),
        # front panel bottom tuck
        (X_FRNT + W_FACE - TT, Y_BODY - H_TUCK), (X_FRNT + TT, Y_BODY - H_TUCK),
        (X_FRNT, Y_BODY),
        # left side bottom dust flap
        (X_SIDL + W_SIDE, Y_BODY - H_DUST + DT),
        (X_SIDL + W_SIDE - DT, Y_BODY - H_DUST), (X_SIDL + DT, Y_BODY - H_DUST),
        (X_SIDL, Y_BODY - H_DUST + DT), (X_SIDL, Y_BODY),
        # back panel bottom is flat
        (X_BACK, Y_BODY),
    ]


def stroke_path(c, pts, colour, lw, dash=None, close=True):
    c.saveState()
    c.setStrokeColor(colour)
    c.setLineWidth(lw)
    c.setLineJoin(1)
    if dash:
        c.setDash(dash, 0)
    p = c.beginPath()
    p.moveTo(P(pts[0][0]), P(pts[0][1]))
    for px, py in pts[1:]:
        p.lineTo(P(px), P(py))
    if close:
        p.close()
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()


def draw_guides(c):
    """Plan layers. The bleed boundary and safe-area rectangles were dropped
    on request: the only lines now are the die profile and the folds. The cut
    stays because without it there is no die to check."""
    # cut
    stroke_path(c, blank_outline(), CUT, 0.9)
    # the hang hole is a cut too
    c.saveState()
    c.setStrokeColor(CUT)
    c.setLineWidth(0.9)
    c.drawPath(euro_slot_path(c, TAB_X0 + TAB_W / 2.0, Y_TOP), fill=0, stroke=1)
    c.restoreState()
    txt(c, TAB_X0 + TAB_W / 2.0, Y_TOP + H_HANG + 3.0, "EURO HANG TAB",
        F["bodyblk"], 6.5, CUT, "c")
    # scent vents
    c.saveState()
    c.setStrokeColor(CUT)
    c.setLineWidth(0.7)
    for px, pw in ((X_SIDL, W_SIDE), (X_SIDR, W_SIDE)):
        for vx, vy in vent_positions(px, pw):
            c.drawPath(vent_path(c, vx, vy, VENT_H), fill=0, stroke=1)
    c.restoreState()
    txt(c, X_SIDL + W_SIDE / 2, VENT_Y + VENT_H, "SCENT VENTS",
        F["bodyblk"], 5.6, CUT, "c")

    # creases
    for fx in (X_BACK, X_SIDL, X_FRNT, X_SIDR):
        line_pts = [(fx, Y_BODY), (fx, Y_TOP)]
        stroke_path(c, line_pts, CREASE, 0.7, dash=[5, 3], close=False)
    stroke_path(c, [(X_GLUE, Y_BODY + GT), (X_GLUE, Y_TOP - GT)], CREASE, 0.7,
                dash=[5, 3], close=False)
    # horizontal creases along the body band
    # no crease across the tab: it is continuous with the back panel
    stroke_path(c, [(X_SIDL, Y_TOP), (X_SIDR + W_SIDE, Y_TOP)], CREASE, 0.7,
                dash=[5, 3], close=False)
    stroke_path(c, [(X_BACK, Y_BODY), (X_SIDR + W_SIDE, Y_BODY)], CREASE, 0.7,
                dash=[5, 3], close=False)

    # panel labels, dropped into the margin the guides build adds
    labels = ((X_GLUE + W_GLUE / 2, "GLUE TAB"),
              (X_BACK + W_FACE / 2, "BACK"),
              (X_SIDL + W_SIDE / 2, "SIDE"),
              (X_FRNT + W_FACE / 2, "FRONT"),
              (X_SIDR + W_SIDE / 2, "SIDE"))
    for lx, lab in labels:
        txt(c, lx, Y_TOP + H_TUCK + 5.0, lab, F["bodyblk"], 7.5, CUT, "c")
    for lx, lab in ((X_BACK + W_FACE / 2, str(int(W_FACE)) + " mm"),
                    (X_SIDL + W_SIDE / 2, str(int(W_SIDE)) + " mm"),
                    (X_FRNT + W_FACE / 2, str(int(W_FACE)) + " mm"),
                    (X_SIDR + W_SIDE / 2, str(int(W_SIDE)) + " mm")):
        txt(c, lx, Y_BODY - H_TUCK - 8.0, lab, F["bodysemi"], 6.5, CUT, "c")

    # legend + spec, in the left margin
    lx, ly = -ORIGIN + 5.0, SHEET_H + 29.0
    txt(c, lx, ly, "SWIFT BLUE-DROP  -  4 x 50 g CARTON  -  DIELINE",
        F["head"], 9.0, CUT)
    spec = ("Style: straight tuck end, euro hang tab",
            "Carton: " + str(int(W_FACE)) + " W x " + str(int(W_SIDE)) +
            " D x " + str(int(H_BODY)) + " H mm",
            "Flat blank: " + str(int(SHEET_W)) + " x " + str(int(SHEET_H)) +
            " mm  +  " + str(int(BLEED)) + " mm bleed",
            "Colours: CMYK process, no spots",
            "Safe area: " + str(int(SAFE)) + " mm (enforced in build, not drawn)",
            "Hang tab: " + str(int(TAB_W)) + " x " + str(int(H_HANG)) +
            " mm, euro slot, " + ("%.1f" % TAB_HEADROOM) + " mm headroom",
            "Scent vents: " + str(VENT_N) + " droplet cut-outs per side panel")
    sy = ly - 4.6
    for s in spec:
        txt(c, lx, sy, s, F["bodymed"], 6.2, CUT)
        sy -= 3.2
    key = ((CUT, "solid", "CUT"), (CREASE, "dash", "CREASE / FOLD"))
    ky = -14.0
    for col, kind, lab in key:
        c.saveState()
        c.setStrokeColor(col)
        c.setLineWidth(1.0)
        if kind == "dash":
            c.setDash([4, 3], 0)
        c.line(P(lx), P(ky + 0.8), P(lx + 12), P(ky + 0.8))
        c.restoreState()
        txt(c, lx + 14, ky, lab, F["bodysemi"], 6.2, col)
        ky -= 4.5


# ----------------------------------------------------------------------------
# 8. BUILD
# ----------------------------------------------------------------------------

def paint_artwork(c):
    # Full-bleed ground first. Painting the whole sheet guarantees bleed on
    # every flap and chamfer without hand-building an offset outline.
    rect(c, -BLEED, -BLEED, SHEET_W + 2 * BLEED, SHEET_H + 2 * BLEED, NAVY)
    flap_art(c)
    for paint in (panel_back,
                  lambda cc: panel_side(cc, X_SIDL, "benefits"),
                  panel_front,
                  lambda cc: panel_side(cc, X_SIDR, "legal")):
        paint(c)
        panel_end()
    vents_art(c)          # after the panels, or they paint over the holes
    glue_tab(c)


def build(path, guides=False):
    global ORIGIN
    ORIGIN = 34.0 if guides else BLEED
    page = ((SHEET_W + 2 * ORIGIN) * MM, (SHEET_H + 2 * ORIGIN) * MM)

    c = canvas.Canvas(path, pagesize=page)
    c.setTitle("Swift Blue-Drop - Flush-Activated WC Cleaner - 4 x 50 g carton")
    c.setAuthor("Vistex Chemicals Ltd")
    c.setSubject("Folding carton dieline, reverse tuck end, CMYK")
    c.setCreator("packaging/swift_blue_drop_dieline.py")

    if guides:
        # a plain ground in the margin so the guide legend stays readable
        c.setFillColor(CMYKColor(0, 0, 0, 0.04))
        c.rect(0, 0, page[0], page[1], fill=1, stroke=0)

    paint_artwork(c)
    if guides:
        draw_guides(c)

    c.showPage()
    c.save()
    ORIGIN = BLEED
    return path


def preview(pdf_path, png_path, dpi=120):
    """Optional PNG proof. Skipped silently if PyMuPDF is not installed."""
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            return None
    doc = pymupdf.open(pdf_path)
    doc[0].get_pixmap(dpi=dpi).save(png_path)
    doc.close()
    return png_path


def main():
    register_fonts()
    os.makedirs(DIST, exist_ok=True)
    stem = "Swift_Blue-Drop_4x50g_Carton"

    out_print = os.path.join(DIST, stem + "_PRINT.pdf")
    out_guides = os.path.join(DIST, stem + "_GUIDES.pdf")

    build(out_print, guides=False)
    measured = list(BOXES), list(OVERFLOW)
    build(out_guides, guides=True)
    BOXES[:], OVERFLOW[:] = measured

    for p in (out_print, out_guides):
        print("wrote", os.path.relpath(p, ROOT),
              "(%.1f KB)" % (os.path.getsize(p) / 1024.0))
        preview(p, p[:-4] + ".png")

    hits = collisions()
    if hits:
        print("")
        print("TEXT COLLISIONS (%d):" % len(hits))
        for hhh in sorted(set(hits)):
            print("  " + hhh)
    if OVERFLOW:
        print("")
        print("LAYOUT OVERFLOW (%d):" % len(OVERFLOW))
        for o in sorted(set(OVERFLOW)):
            print("  " + o)
    else:
        print("")
        print("layout clean - every string inside its panel")
    print("carton  %g W x %g D x %g H mm" % (W_FACE, W_SIDE, H_BODY))
    print("blank   %g x %g mm + %g mm bleed" % (SHEET_W, SHEET_H, BLEED))


if __name__ == "__main__":
    main()
