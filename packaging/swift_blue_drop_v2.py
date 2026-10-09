#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swift Blue-Drop 4 x 50 g - integrated-photography fronts.

The cut-out approach is gone. Each face is ONE composed photograph built by
make_scene.py (water, depth field, botanical and product blended together),
with only the brand furniture set over it as live vector type.

Legibility over a photograph is handled with tonal scrims - a navy gradient
fading into the image at the top and foot - rather than with white panels.
A scrim is part of the picture; a white box sits on top of it.

  immersion   water wrapping the product from both sides, deepest ground
  cascade     water falling from the masthead, lightest and freshest
  vortex      ring splash as a whirlpool, strongest product presence

Run:  python packaging/make_cutouts.py
      python packaging/make_scene.py
      python packaging/swift_blue_drop_v2.py
"""

import os

from PIL import Image
from reportlab.lib.utils import ImageReader

from swift_blue_drop_dieline import *            # noqa: F401,F403
import swift_blue_drop_dieline as B
import illustration as ILL

ART = os.path.join(HERE, "art")
_CACHE = {}

SCENE_W, SCENE_H = 107.0, 157.0      # must match make_scene.py


BRAND = os.path.join(ROOT, "images", "logo")


def _img(name, alpha=1.0):
    """Art assets live in packaging/art; brand marks in images/logo."""
    key = (name, round(alpha, 3))
    if key not in _CACHE:
        path = os.path.join(ART, name + ".png")
        if not os.path.exists(path):
            path = os.path.join(BRAND, name + ".png")
        im = Image.open(path).convert("RGBA")
        if alpha < 1.0:
            im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
        _CACHE[key] = ImageReader(im)
    return _CACHE[key]


def _tinted(name, rgb):
    """Recolour an asset to a flat tint, keeping its alpha. The supplied
    recycle marks are blue, which is invisible on the navy foot band."""
    key = (name, "tint", rgb)
    if key not in _CACHE:
        path = os.path.join(ART, name + ".png")
        if not os.path.exists(path):
            path = os.path.join(BRAND, name + ".png")
        im = Image.open(path).convert("RGBA")
        flat = Image.new("RGBA", im.size, rgb + (255,))
        flat.putalpha(im.getchannel("A"))
        _CACHE[key] = ImageReader(flat)
    return _CACHE[key]


def scene(c, key, x, y, w, h):
    """Lay the composed photograph over the panel, bleeding 1 mm each side."""
    c.saveState()
    clip_rect(c, x, y, w, h)
    ox, oy = (SCENE_W - w) / 2.0, (SCENE_H - h) / 2.0
    c.drawImage(_img("scene-" + key), P(x - ox), P(y - oy),
                SCENE_W * MM, SCENE_H * MM, mask="auto")
    c.restoreState()


def scrim(c, x, y, w, h, colour=NAVY_DK, top=True, peak=0.88, bands=22):
    """A tonal gradient fading into the photograph. Banded rather than a true
    gradient because a PDF gradient cannot carry an alpha ramp in CMYK."""
    for i in range(bands):
        t = i / float(bands - 1)
        a = peak * (1.0 - t) ** 1.9 / bands * 3.4
        bh = h * (1.0 - t)
        if bh <= 0:
            continue
        yy = (y + h - bh) if top else y
        rect(c, x, yy, w, bh, colour, alpha=min(0.95, a))


def side_ground(c, x, y, w, h, cx=None, cy=None, **kw):
    """Sides take the same photograph, cropped, so the pack reads as one."""
    c.saveState()
    clip_rect(c, x, y, w, h)
    c.drawImage(_img("scene-" + CURRENT[0]), P(x - (SCENE_W - w) / 2.0),
                P(y - (SCENE_H - h) / 2.0), SCENE_W * MM, SCENE_H * MM,
                mask="auto")
    c.setFillColor(NAVY, 0.45)
    c.rect(P(x), P(y), w * MM, h * MM, fill=1, stroke=0)
    c.restoreState()


CURRENT = ["immersion"]
B.burst = side_ground


# ----------------------------------------------------------------------------
# KEEP-OUT GUARD
# Originally this tested copy against the drawn border. The border is gone,
# but the need is not: copy still has to stay inside the die safe area, so the
# same test now runs against that.
# ----------------------------------------------------------------------------

FRAME = {}


def set_frame(label, x, y, w, h, inset, clear=1.2, foot=None, cut=8.0):
    """foot: y below which copy belongs to the foot band and is not expected
    to sit inside the frame.
    cut: the mitre, so the test matches the octagon actually drawn."""
    FRAME[label] = (x + inset + clear, y + inset + clear,
                    x + w - inset - clear, y + h - inset - clear,
                    foot if foot is not None else -1e9, cut + clear)


def frame_breaches(min_over=0.3):
    out = []
    for label, (fx0, fy0, fx1, fy1, foot, cut) in FRAME.items():
        for pi, t, bx0, bx1, by0, by1 in B.BOXES:
            if pi != label or not t.strip() or by1 <= foot:
                continue
            d = max(fx0 - bx0, bx1 - fx1, fy0 - by0, by1 - fy1)
            # The frame is an octagon, not a rectangle. Testing only the
            # bounding box let copy sit straight on a mitre and pass.
            for px, py in ((bx0, by0), (bx1, by0), (bx0, by1), (bx1, by1)):
                for u, v in (((px - fx0), (py - fy0)),
                             ((fx1 - px), (py - fy0)),
                             ((px - fx0), (fy1 - py)),
                             ((fx1 - px), (fy1 - py))):
                    if u < cut and v < cut:
                        d = max(d, cut - (u + v))
            if d > min_over:
                out.append("%-10s %-32s outside safe area by %.1f mm"
                           % (label, t[:30], d))
    return out


# ----------------------------------------------------------------------------
# GRAPHIC FURNITURE - curves, waves and rules
# The keyline frame, corner mitres and edge ticks were removed on request;
# the only lines left on the pack are the folds, which are die features and
# are not printed at all.
# Drawn as vector over the photograph so none of it softens on press, and all
# of it stays editable.
# ----------------------------------------------------------------------------

def hard_rule(c, x, y, w, colour, lw=0.4, alpha=0.7, caps=True):
    """A straight rule with square tick ends. Butt caps and a vertical stop
    at each end, so it reads as drawn to a measure rather than trailing off."""
    c.saveState()
    c.setStrokeColor(colour, alpha)
    c.setLineWidth(lw * MM)
    c.setLineCap(0)
    c.line(P(x), P(y), P(x + w), P(y))
    if caps:
        for ex in (x, x + w):
            c.line(P(ex), P(y - 1.3), P(ex), P(y + 1.3))
    c.restoreState()


def tick_marks(c, xs, y, h, colour, lw=0.35, alpha=0.55):
    """Short verticals used to separate items on a row."""
    c.saveState()
    c.setStrokeColor(colour, alpha)
    c.setLineWidth(lw * MM)
    c.setLineCap(0)
    for xx in xs:
        c.line(P(xx), P(y), P(xx), P(y + h))
    c.restoreState()


def corner_brackets(c, x, y, w, h, arm, colour, lw=0.45, alpha=0.8,
                    which=("tl", "tr", "bl", "br")):
    """Crop-mark style angles. Right angles only - no radius, no arc."""
    c.saveState()
    c.setStrokeColor(colour, alpha)
    c.setLineWidth(lw * MM)
    c.setLineCap(0)
    pts = {"tl": (x, y + h, 1, -1), "tr": (x + w, y + h, -1, -1),
           "bl": (x, y, 1, 1), "br": (x + w, y, -1, 1)}
    for k in which:
        px, py, sx, sy = pts[k]
        c.line(P(px), P(py), P(px + sx * arm), P(py))
        c.line(P(px), P(py), P(px), P(py + sy * arm))
    c.restoreState()


def flanked_rule(c, cx, y, gap, length, colour, lw=0.3, alpha=0.7):
    c.saveState()
    c.setStrokeColor(colour, alpha)
    c.setLineWidth(lw * MM)
    c.setLineCap(1)
    c.line(P(cx - gap - length), P(y), P(cx - gap), P(y))
    c.line(P(cx + gap), P(y), P(cx + gap + length), P(y))
    c.restoreState()
    # diamonds, not triangles: a triangle on the end of a rule reads as an
    # arrowhead, which made the deck look like a dimension annotation
    for sx in (-1, 1):
        ex = cx + sx * (gap + length)
        poly(c, [(ex - 1.05, y), (ex, y + 0.82), (ex + 1.05, y),
                 (ex, y - 0.82)], colour, alpha=alpha)


def flag_4pack(c, x, y, w=40.0, h=15.0):
    poly(c, [(x + 2.4, y), (x + w, y), (x + w - 2.4, y + h), (x, y + h)], YELLOW)
    txt(c, x + 11.0, y + 4.6, "4", F["display"], 23, RED, "c")
    txt(c, x + 26.5, y + 8.2, "PACK", F["head"], 11.8, NAVY, "c")
    txt(c, x + 26.5, y + 3.2, "50 g each", F["bodysemi"], 6.4, NAVY, "c")


def benefit_row(c, cx, y, ink=WHITE, step=31.0):
    for i, (lab, kind) in enumerate((("CLEANS", "sparkle"),
                                     ("FRESHENS", "drop"),
                                     ("PROTECTS", "shield"))):
        bx = cx - step + i * step
        if kind == "sparkle":
            sparkle(c, bx, y, 4.0, ink)
        elif kind == "drop":
            droplet(c, bx, y, 7.8, ink, highlight=False)
        else:
            shield(c, bx, y, 4.2, ink)
        txt(c, bx, y - 11.6, lab, F["subhead"], 8.6, ink, "c", char_space=0.3)


def soft_plate(c, cx, cy, w, h, colour=NAVY_DK, peak=0.46, bands=9):
    """A feathered dark plate - legibility without a container. Stacked
    low-alpha rounded rects fade into the photograph instead of sitting on
    it as a shape the eye has to account for."""
    for i in range(bands, 0, -1):
        t = i / float(bands)
        rw = w * (1.0 + 0.38 * t)
        rh = h * (1.0 + 1.25 * t)
        pill(c, cx - rw / 2, cy - rh / 2, rw, rh, colour,
             r=rh / 2, alpha=peak / bands)


def seal(c, cx, cy, r=11.0):
    """The claim band is gone, so the face needed something to hold that
    zone and to carry the one number worth reading at arm's length.

    A disc, because every other element on the pack is a rectangle or a
    ribbon, and because it is the only shape that can sit over the product
    without looking like it was ruled there.
    """
    # soft contact shadow, so it lifts off the blocks behind it
    for k, a in ((1.14, 0.06), (1.07, 0.08), (1.0, 0.10)):
        circle(c, cx + 0.5, cy - 0.7, r * k, NAVY_DK, alpha=a)

    circle(c, cx, cy, r, WHITE, alpha=0.97)
    c.saveState()
    c.setStrokeColor(CYAN, 0.9)
    c.setLineWidth(0.7 * MM)
    c.circle(P(cx), P(cy), (r - 1.5) * MM, fill=0, stroke=1)
    c.setStrokeColor(BLUE_MID, 0.35)
    c.setLineWidth(0.25 * MM)
    c.circle(P(cx), P(cy), (r - 2.9) * MM, fill=0, stroke=1)
    c.restoreState()

    k = r / 13.6
    txt(c, cx, cy + 4.6 * k, "ONE BLOCK", F["subhead"], 5.6 * k, BLUE_MID,
        "c", char_space=0.5 * k)
    c.saveState()
    c.setStrokeColor(CYAN, 0.65)
    c.setLineWidth(0.3 * MM)
    c.line(P(cx - 5.4 * k), P(cy + 3.2 * k),
           P(cx + 5.4 * k), P(cy + 3.2 * k))
    c.restoreState()
    txt(c, cx, cy - 3.4 * k, "30", F["display"], 21 * k, NAVY, "c")
    txt(c, cx, cy - 8.2 * k, "DAYS", F["head"], 8.4 * k, BLUE_MID, "c",
        char_space=0.8 * k)


def front(c, key, wordmark_ink=WHITE, deck_ink=WHITE):
    x, y, w, h = X_FRNT, Y_BODY, W_FACE, H_BODY
    top, cx = y + h, x + w / 2
    panel("FRONT", x, y, w, h)

    scene(c, key, x, y, w, h)
    scrim(c, x, top - 62.0, w, 62.0, top=True, peak=0.92)
    scrim(c, x, y, w, 52.0, top=False, peak=0.95)

    # Sharp geometry only. The rings, swooshes, waves and vector bubbles are
    # gone: the photograph already supplies every curve on this face, and a
    # drawn curve laid over a photographed one reads as a scratch rather than
    # as design. What is left is measured - right angles and straight rules.
    corner_brackets(c, x + 12.5, y + 42.0, w - 25.0, 62.0, 6.0, CYAN,
                    0.45, 0.55, which=("tl", "tr"))
    hard_rule(c, x + 9.0, y + 15.5, w - 18.0, CYAN_LT, 0.40, 0.60)

    # Masthead spacing is derived, not guessed. The first pass put the
    # wordmark cap 2.4 mm above the logo bottom - they overlapped - because
    # the cap height of Outfit-900 at this size is 11.9 mm, not the ~8 mm the
    # layout assumed.
    logo_w = 42.0
    logo_h = logo_w * 361.0 / 720.0
    logo_cy = top - 4.0 - logo_h / 2.0 - 2.4
    swift_logo(c, x + 28.0, logo_cy, logo_w, shadow=False)
    flag_4pack(c, x + 58.0, logo_cy - 7.5)

    size = fit("Blue-Drop", F["display"], 76.0)
    cap = size * 0.72 / MM
    word_base = (logo_cy - logo_h / 2.0) - 5.0 - cap
    txt(c, cx - 5.0, word_base, "Blue-Drop", F["display"], size,
        wordmark_ink, "c")
    droplet_gloss(c, cx + 40.5, word_base + cap * 0.46, 14.0, light=True)
    deck_base = word_base - 8.6
    txt(c, cx, deck_base, "AUTOMATIC TOILET BOWL CLEANER", F["label"], 10.6,
        deck_ink, "c", char_space=0.6)
    _gap = sw("AUTOMATIC TOILET BOWL CLEANER", F["label"], 10.6) / MM / 2 + 3.5
    _len = max(0.0, (x + w - 9.5) - cx - _gap)
    if _len > 2.0:
        flanked_rule(c, cx, deck_base + 0.9, _gap, _len, CYAN_LT, 0.32,
                     alpha=0.75)

    benefit_row(c, cx, y + 42.0)
    tick_marks(c, (cx - 15.5, cx + 15.5), y + 33.5, 11.0, CYAN_LT, 0.35, 0.45)
    # pulled in off the mitres: a corner cut eats into the usable width, so
    # the bottom corners need more margin than the straight edges do
    # Tucked into the corner of the product zone, not centred on a block.
    # At 13.6 mm on the block it covered one of the four outright, and a
    # 4-pack that reads as three is worse than no seal at all.
    seal(c, x + 19.0, y + 58.0, r=11.0)
    txt(c, x + 10.5, y + 24.0, "NET WT. 50 g per block", F["bodysemi"], 8.0,
        CYAN_LT)
    txt(c, x + w - 10.5, y + 23.2, "TOTAL NET WT. 200 g", F["bodyblk"], 11.6,
        WHITE, "r")

    rect(c, x, y, w, 11.0, NAVY_DK)
    rect(c, x, y + 11.0, w, 0.6, CYAN, alpha=0.6)
    txt(c, x + 6.0, y + 3.8, EMAIL, F["bodymed"], 7.4, WHITE)
    txt(c, x + w - 6.0, y + 3.8, "VISTEX CHEMICALS LTD", F["bodyblk"], 7.8,
        WHITE, "r")

    # No drawn border. The guard still runs, now against the die safe area
    # rather than a keyline - the frame was what kept copy off the trim, and
    # removing the line must not remove the check.
    set_frame("FRONT", x, y, w, h, SAFE, clear=0.0, foot=y + 12.2, cut=0.0)


# ----------------------------------------------------------------------------
# BACK PANEL
# Rebuilt around the one thing that actually needs a picture: nobody can see
# inside a cistern, so "drop it in the tank" has to be drawn. Everything that
# competed with that for room was moved to a side panel.
# ----------------------------------------------------------------------------

def back(c, key):
    x, y, w, h = X_BACK, Y_BODY, W_FACE, H_BODY
    top, cx = y + h, x + w / 2
    m = 6.0
    cw = w - 2 * m
    panel("BACK", x, y, w, h)

    # --- ground: the same photograph, veiled back to a watermark ----------
    rect(c, x, y, w, h, WHITE)
    c.saveState()
    clip_rect(c, x, y, w, h)
    ox, oy = (SCENE_W - w) / 2.0, (SCENE_H - h) / 2.0
    c.drawImage(_img("scene-" + key), P(x - ox), P(y - oy),
                SCENE_W * MM, SCENE_H * MM, mask="auto")
    # a white veil, not a white box: the water stays legible as water while
    # losing the contrast that would fight small copy. Pulled back from 0.88
    # so the water actually reads, with a botanical in the corner for warmth.
    c.setFillColor(WHITE, 0.82)
    c.rect(P(x), P(y), w * MM, h * MM, fill=1, stroke=0)
    fl = _img("flower", 0.22)
    fiw, fih = fl.getSize()
    fw = 54.0
    c.drawImage(fl, P(x + w - fw * 0.62), P(y + h - fw * fih / fiw * 0.72),
                fw * MM, fw * fih / fiw * MM, mask="auto")
    fl2 = _img("flower", 0.14)
    fw2 = 40.0
    c.drawImage(fl2, P(x - fw2 * 0.34), P(y + 34.0),
                fw2 * MM, fw2 * fih / fiw * MM, mask="auto")
    c.restoreState()
    rect(c, x, top - 2.4, w, 2.4, NAVY)

    # --- layout -----------------------------------------------------------
    # Absolute anchors, not a relative chain. Chaining each block off the one
    # above meant a single height change pushed the composition copy behind
    # the navy foot, where it was invisible but still "passed" every check.
    # Re-budgeted for the taller foot and the larger type. The panel is
    # 155 mm and the content wanted 170, so WHY IT WORKS came off: the same
    # four claims already run on the front face AND down the left side
    # panel, and a third printing of them was the cheapest thing to lose.
    Y_TITLE = top - 13.0
    Y_SUB = top - 20.0
    Y_RULE = top - 24.0
    Y_HOWTO = top - 32.5          # pill baseline
    Y_STEPS = y + 73.0            # how_to_use origin
    Y_CAUTION = y + 67.0
    Y_SPEC = y + 48.0             # composition / storage rule
    FOOT_H = 30.0

    # --- header -----------------------------------------------------------
    txt(c, x + m, Y_TITLE, "Swift Blue-Drop", F["head"],
        fit("Swift Blue-Drop", F["head"], 58.0), NAVY)
    txt(c, x + m, Y_SUB, "Flush-Activated WC Cleaner", F["subhead"], 9.2,
        BLUE_BR)
    droplet_gloss(c, x + w - m - 5.0, top - 11.5, 15.0, light=False)
    line(c, x + m, Y_RULE, x + w - m, Y_RULE, NAVY, 0.35, alpha=0.35)

    # --- how to use -------------------------------------------------------
    pill(c, x + m, Y_HOWTO, cw, 6.4, NAVY)
    txt(c, cx, Y_HOWTO + 1.9, "HOW TO USE", F["subhead"], 8.2, WHITE, "c")
    ILL.how_to_use(c, x + m, Y_STEPS, cw)

    # --- caution ----------------------------------------------------------
    pill(c, x + m, Y_CAUTION, cw, 6.4, RED)
    txt(c, cx, Y_CAUTION + 1.9, "CAUTION", F["subhead"], 8.2, WHITE, "c")
    bullets(c, x + m + 1.0, Y_CAUTION - 3.4,
            ("Keep out of reach of children. Do not ingest.",
             "Avoid contact with skin and eyes; wash hands after use.",
             "Not for handling. Use only as directed."),
            cw - 2.0, size=6.4, leading=3.3, gap=1.1, dot=RED, dot_r=0.6)

    # --- composition / storage -------------------------------------------
    col = (cw - 6.0) / 2
    line(c, x + m, Y_SPEC, x + w - m, Y_SPEC, NAVY, 0.3, alpha=0.3)
    txt(c, x + m, Y_SPEC - 3.8, "COMPOSITION", F["subhead"], 6.2, NAVY,
        char_space=0.4)
    para(c, x + m, Y_SPEC - 7.4,
         "Anionic surfactants, dissolution modifiers, anti-redeposition "
         "agents, colourant, perfume.", F["body"], 5.9, GREY, col, 3.0)
    txt(c, x + m + col + 6.0, Y_SPEC - 3.8, "STORAGE", F["subhead"], 6.2,
        NAVY, char_space=0.4)
    para(c, x + m + col + 6.0, Y_SPEC - 7.4,
         "Upright, cool and dry. Keep the wrapper sealed until use.",
         F["body"], 5.9, GREY, col, 3.0)

    # --- foot: maker, data-sheet QR, recycling ----------------------------
    bh = FOOT_H
    rect(c, x, y, w, bh, NAVY)
    rect(c, x, y + bh, w, 0.6, CYAN, alpha=0.55)
    vl = _img("vistex-logo-white")
    iw, ih = vl.getSize()
    vw = 30.0
    vh = vw * ih / iw
    c.drawImage(vl, P(x + m), P(y + bh - 2.8 - vh), vw * MM, vh * MM,
                mask="auto")
    txt(c, x + m, y + 10.4, ADDRESS, F["body"], 5.6, WHITE)
    txt(c, x + m, y + 6.6, "Tel " + TEL + "   -   " + EMAIL, F["body"], 5.6,
        WHITE)
    txt(c, x + m, y + 2.8, WEBSITE, F["bodysemi"], 5.6, CYAN_LT)

    # QR to the live product data sheet
    qs = 17.0
    qx = x + w - m - qs - 17.0
    B.qr_code(c, qx, y + 9.0, qs, B.qr_url("blue-drop-wc"))
    txt(c, qx + qs / 2, y + 4.8, "SCAN FOR", F["bodysemi"], 5.0, CYAN_LT, "c")
    txt(c, qx + qs / 2, y + 1.4, "DATA SHEET", F["bodysemi"], 5.0, CYAN_LT,
        "c")

    rc = _tinted("recycle-outline", (255, 255, 255))
    riw, rih = rc.getSize()
    rw = 11.0
    c.drawImage(rc, P(x + w - m - rw), P(y + bh - 3.4 - rw * rih / riw),
                rw * MM, rw * rih / riw * MM, mask="auto")
    txt(c, x + w - m - rw / 2, y + 6.8, "RECYCLE", F["bodysemi"], 5.2,
        WHITE, "c")
    txt(c, x + w - m - rw / 2, y + 3.0, "CARTON", F["bodysemi"], 5.2,
        WHITE, "c")

    set_frame("BACK", x, y, w, h, SAFE, clear=0.0, foot=y + FOOT_H + 1.0,
              cut=0.0)


CONCEPTS = (("D", "Immersion", "immersion"),
            ("E", "Cascade", "cascade"),
            ("F", "Vortex", "vortex"))


def paint(c, key):
    rect(c, -BLEED, -BLEED, SHEET_W + 2 * BLEED, SHEET_H + 2 * BLEED, NAVY)
    B.flap_art(c)
    back(c, key)
    B.panel_end()
    B.panel_side(c, X_SIDL, "benefits")
    B.panel_end()
    front(c, key)
    B.panel_end()
    B.panel_side(c, X_SIDR, "legal")
    B.panel_end()
    B.vents_art(c)        # after the panels, or they paint over the holes
    B.glue_tab(c)


def build(key, path, guides=False):
    """guides=True emits the PLAN: the same flat blank on a larger sheet with
    the cut, crease, bleed and safe-area layers, panel labels and dimensions.
    For approval and for checking the die - never for printing."""
    from reportlab.pdfgen import canvas as _cv
    B.ORIGIN = 34.0 if guides else BLEED
    CURRENT[0] = key
    page = ((SHEET_W + 2 * B.ORIGIN) * MM, (SHEET_H + 2 * B.ORIGIN) * MM)
    c = _cv.Canvas(path, pagesize=page)
    c.setTitle("Swift Blue-Drop 4 x 50 g - %s%s"
               % (key, " - PLAN" if guides else ""))
    c.setAuthor("Vistex Chemicals Ltd")
    c.setCreator("packaging/swift_blue_drop_v2.py")
    if guides:
        from reportlab.lib.colors import CMYKColor as _C
        c.setFillColor(_C(0, 0, 0, 0.04))
        c.rect(0, 0, page[0], page[1], fill=1, stroke=0)
    paint(c, key)
    if guides:
        B.draw_guides(c)
    c.showPage()
    c.save()
    B.ORIGIN = BLEED
    return path


def main():
    register_fonts()
    need = ["scene-" + k for _, _, k in CONCEPTS]
    missing = [n for n in need
               if not os.path.exists(os.path.join(ART, n + ".png"))]
    if missing:
        raise SystemExit("missing scenes: %s\nrun: python packaging/make_scene.py"
                         % ", ".join(missing))

    out = os.path.join(DIST, "integrated")
    os.makedirs(out, exist_ok=True)
    for letter, name, key in CONCEPTS:
        B.BOXES[:] = []
        B.OVERFLOW[:] = []
        FRAME.clear()
        p = os.path.join(out, "Concept_%s_%s.pdf" % (letter, name))
        build(key, p)
        # measure the print build only; the plan re-draws every string and
        # would otherwise collide with its own duplicate
        hits = B.collisions() + frame_breaches()
        measured = list(B.BOXES), list(B.OVERFLOW)
        build(key, os.path.join(out, "Concept_%s_%s_PLAN.pdf" % (letter, name)),
              guides=True)
        B.BOXES[:], B.OVERFLOW[:] = measured
        flag = ""
        if B.OVERFLOW:
            flag += "  OVERFLOW:%d" % len(B.OVERFLOW)
        if hits:
            flag += "  COLLISIONS:%d" % len(hits)
        print("%s  %-11s %7.1f KB%s" %
              (letter, name, os.path.getsize(p) / 1024.0, flag or "  clean"))
        for o in sorted(set(B.OVERFLOW)):
            print("     " + o)
        for hh in sorted(set(hits)):
            print("     " + hh)
        B.preview(p, p[:-4] + ".png", dpi=150)
    print("")
    print("wrote", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
