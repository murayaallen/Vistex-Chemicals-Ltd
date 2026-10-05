#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swift Blue-Drop 4 x 50 g - three front-panel concepts.

Built on the approved structure in swift_blue_drop_dieline.py (same die, same
back and side panels, same guard) and varying only the face, so the three can
be compared on art direction rather than on layout noise.

What changed from the first pass, and why
-----------------------------------------
  rays          gone. Replaced by real gradients with deliberate white relief.
  vector art    gone from the hero. The blocks, water and flower are now
                photographic cut-outs made by make_cutouts.py.
  type          every secondary size raised; the detail was reading too small.

  A  White Crown      white top, deep blue foot, water straddling the join
  B  Water Crown      full gradient, splash ring hero, white card for detail
  C  Botanical Fresh  light bokeh ground, flower, navy type, most white space

Run:  python packaging/make_cutouts.py        (once, to build the art)
      python packaging/swift_blue_drop_concepts.py
"""

import os

from PIL import Image

from reportlab.lib.utils import ImageReader

from swift_blue_drop_dieline import *            # noqa: F401,F403
import swift_blue_drop_dieline as B

ART = os.path.join(HERE, "art")
_CACHE = {}


# ----------------------------------------------------------------------------
# photographic placement
# ----------------------------------------------------------------------------

def _img(name, alpha=1.0):
    """ImageReader for an art asset, optionally faded. Faded copies are made
    in PIL because a PDF image cannot carry a constant alpha on its own."""
    key = (name, round(alpha, 3))
    if key in _CACHE:
        return _CACHE[key]
    im = Image.open(os.path.join(ART, name + ".png")).convert("RGBA")
    if alpha < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im.putalpha(a)
    r = ImageReader(im)
    _CACHE[key] = r
    return r


def photo(c, name, cx, cy, w, alpha=1.0, anchor="c"):
    """Place an art asset by width; height follows the aspect ratio."""
    img = _img(name, alpha)
    iw, ih = img.getSize()
    h = w * ih / iw
    px = cx if anchor == "l" else (cx - w if anchor == "r" else cx - w / 2)
    c.drawImage(img, P(px), P(cy - h / 2), w * MM, h * MM, mask="auto")
    return h


def vgrad(c, x, y, w, h, stops):
    """Vertical gradient clipped to a rect. stops = [(pos, colour), ...]."""
    c.saveState()
    clip_rect(c, x, y, w, h)
    c.linearGradient(P(x), P(y + h), P(x), P(y),
                     [s[1] for s in stops], [s[0] for s in stops],
                     extend=True)
    c.restoreState()


def ground_gradient(c, x, y, w, h, cx=None, cy=None, **kw):
    """Drop-in for the old burst(). Same signature, no spokes - a clean
    vertical gradient with the light held at the top."""
    vgrad(c, x, y, w, h, [(0.0, CYAN), (0.30, BLUE_BR),
                          (0.68, BLUE_MID), (1.0, NAVY)])


B.burst = ground_gradient          # the sides and flaps lose their rays too


SOLID = []        # bboxes of opaque artwork, for the copy-over-image check
OCCLUDE = []      # opaque shapes painted over it afterwards


def occlude(x, y, w, h):
    """Register an opaque shape drawn on top of the product. Copy sitting
    wholly inside one of these is on the shape, not on the photograph."""
    OCCLUDE.append((x, y, x + w, y + h))


def _covered(bx0, bx1, by0, by1):
    return any(ox0 <= bx0 and bx1 <= ox1 and oy0 <= by0 and by1 <= oy1
               for ox0, oy0, ox1, oy1 in OCCLUDE)


def solid_collisions(shrink=0.78, min_overlap=0.8):
    """Text sitting on an opaque photograph. The base guard only compares text
    against text, and every layout fault in these concepts was copy vanishing
    into the product instead."""
    hits = []
    for pi, sx0, sx1, sy0, sy1 in SOLID:
        cx, cy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
        hw, hh = (sx1 - sx0) / 2 * shrink, (sy1 - sy0) / 2 * shrink
        ax0, ax1, ay0, ay1 = cx - hw, cx + hw, cy - hh, cy + hh
        for pj, t, bx0, bx1, by0, by1 in B.BOXES:
            if pi != pj or not t.strip():
                continue
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > min_overlap and oy > min_overlap and                     not _covered(bx0, bx1, by0, by1):
                hits.append("%-10s %-34s on product art  %.1f x %.1f mm" %
                            (pi, t[:32], ox, oy))
    return hits


def discs(c, cx, cy, w, spread=0.56, lift=0.46):
    """The four blocks, back pair first so the front pair overlaps them.
    lift was 0.30, which buried the lower-left block behind the upper-left one
    and made a 4-pack look like a 3-pack."""
    dx, dy = w * spread, w * lift
    for name, ox, oy, sc in (("disc-3", -dx, dy, 0.93), ("disc-4", dx, dy, 0.93),
                             ("disc-1", -dx, -dy, 1.0), ("disc-2", dx, -dy, 1.0)):
        h = photo(c, name, cx + ox, cy + oy, w * sc)
        if B.PANEL is not None:
            SOLID.append((B.PANEL[0], cx + ox - w * sc / 2, cx + ox + w * sc / 2,
                          cy + oy - h / 2, cy + oy + h / 2))


def footer(c, x, y, w, left=None, h=13.0):
    rect(c, x, y, w, h, NAVY_DK)
    occlude(x, y, w, h)
    rect(c, x, y + h, w, 0.6, CYAN, alpha=0.6)
    txt(c, x + 6.0, y + h / 2 - 1.9, left or EMAIL,
        F["bodyblk"] if left else F["bodymed"], 7.6 if left else 6.6, WHITE)
    txt(c, x + w - 6.0, y + h / 2 - 1.9, "VISTEX CHEMICALS LTD",
        F["bodyblk"], 7.0, WHITE, "r")


def flag_4pack(c, x, y, w=40.0, h=15.0):
    poly(c, [(x + 2.4, y), (x + w, y), (x + w - 2.4, y + h), (x, y + h)], YELLOW)
    txt(c, x + 11.0, y + 4.6, "4", F["display"], 23, RED, "c")
    txt(c, x + 26.5, y + 8.0, "PACK", F["head"], 11.0, NAVY, "c")
    txt(c, x + 26.5, y + 3.4, "50 g each", F["bodysemi"], 5.8, NAVY, "c")


def benefit_row(c, cx, y, ink, step=31.0, icon_bg=None):
    for i, (lab, kind) in enumerate((("CLEANS", "sparkle"),
                                     ("FRESHENS", "drop"),
                                     ("PROTECTS", "shield"))):
        bx = cx - step + i * step
        if icon_bg is not None:
            circle(c, bx, y, 5.4, icon_bg, alpha=0.95)
        if kind == "sparkle":
            sparkle(c, bx, y, 3.9, ink)
        elif kind == "drop":
            droplet(c, bx, y, 7.6, ink, highlight=False)
        else:
            shield(c, bx, y, 4.1, ink)
        txt(c, bx, y - 11.0, lab, F["subhead"], 7.6, ink, "c", char_space=0.3)


def strapline(c, cx, y, ink=WHITE, bg=RED):
    s = "Fights Hard Water Stains"
    size = 8.6
    w_ = sw(s, F["head"], size) / MM
    pill(c, cx - (w_ + 13) / 2, y, w_ + 13, 8.6, bg)
    occlude(cx - (w_ + 13) / 2, y, w_ + 13, 8.6)
    txt(c, cx, y + 2.6, s, F["head"], size, ink, "c")


def weights(c, x_right, y, ink=WHITE, sub=None):
    txt(c, x_right, y + 6.4, "NET WT. 50 g per block", F["bodysemi"], 7.4,
        sub or ink, "r")
    txt(c, x_right, y, "TOTAL NET WT. 200 g", F["bodyblk"], 11.0, ink, "r")


# ----------------------------------------------------------------------------
# A - WHITE CROWN
# ----------------------------------------------------------------------------

def front_a(c):
    x, y, w, h = X_FRNT, Y_BODY, W_FACE, H_BODY
    top, cx = y + h, x + w / 2
    panel("FRONT", x, y, w, h)

    split = y + 66.0
    rect(c, x, split, w, h - 66.0, WHITE)
    vgrad(c, x, y, w, 66.0 + 2.0,
          [(0.0, CYAN_LT), (0.26, BLUE_BR), (0.68, BLUE_MID), (1.0, NAVY)])
    # the splash straddles the join so the two grounds meet on water, not on
    # a ruled line
    photo(c, "splash-arc", cx + 3, split + 2.0, 118.0, alpha=0.95)

    swift_logo(c, x + 31, top - 13.5, 50, shadow=False)
    flag_4pack(c, x + 60.5, top - 22.0)

    size = fit("Blue-Drop", F["display"], 84.0)
    txt(c, cx - 5.0, top - 44.0, "Blue-Drop", F["display"], size, NAVY, "c")
    droplet_gloss(c, cx + 44.0, top - 38.0, 15.0, light=False)
    txt(c, cx, top - 52.5, "AUTOMATIC TOILET BOWL CLEANER", F["label"], 9.6,
        BLUE_MID, "c", char_space=0.6)
    benefit_row(c, cx, top - 67.0, NAVY)

    # A trades product size for white space - that is the concept. The blocks
    # are sized to clear the copy rather than the copy shuffled around them.
    # They are laid in BEFORE the strapline: painted after, they buried it.
    discs(c, cx, y + 45.0, 25.0)
    # the strapline straddles the join, which is the one place on this layout
    # where a red pill reads as deliberate rather than dropped in
    strapline(c, cx, split - 4.5)
    weights(c, x + w - 6.5, y + 13.0, WHITE, CYAN_LT)
    footer(c, x, y, w, h=11.0)


# ----------------------------------------------------------------------------
# B - WATER CROWN
# ----------------------------------------------------------------------------

def front_b(c):
    x, y, w, h = X_FRNT, Y_BODY, W_FACE, H_BODY
    top, cx = y + h, x + w / 2
    panel("FRONT", x, y, w, h)

    vgrad(c, x, y, w, h, [(0.0, WHITE), (0.13, CYAN_LT), (0.38, BLUE_BR),
                          (0.72, BLUE_MID), (1.0, NAVY)])

    photo(c, "splash-ring", cx, y + 60.0, 106.0, alpha=0.80)
    discs(c, cx, y + 57.0, 30.0)

    swift_logo(c, x + 31, top - 13.0, 50)
    flag_4pack(c, x + 60.5, top - 21.5)

    size = fit("Blue-Drop", F["display"], 82.0)
    txt_outlined(c, cx - 5.0, top - 45.0, "Blue-Drop", F["display"], size,
                 WHITE, NAVY_DK, 0.0, "c", shadow=NAVY_DK,
                 shadow_off=(0.7, -0.75))
    droplet_gloss(c, cx + 43.0, top - 39.5, 15.0, light=True)
    txt(c, cx, top - 53.5, "AUTOMATIC TOILET BOWL CLEANER", F["label"], 9.6,
        WHITE, "c", char_space=0.6)

    # the white card is where every small detail lives, so none of it has to
    # fight the photograph for contrast
    # the card deliberately crosses the lower edge of the product, so the
    # blocks read as sitting behind it rather than floating in the gradient
    card_y, card_h = y + 16.0, 33.0
    pill(c, x + 4.5, card_y, w - 9.0, card_h, WHITE, r=4.0)
    occlude(x + 4.5, card_y, w - 9.0, card_h)
    strapline(c, cx, card_y + card_h - 11.5)
    benefit_row(c, cx, card_y + 13.5, NAVY)
    footer(c, x, y, w, left="NET 200 g  (4 x 50 g)")


# ----------------------------------------------------------------------------
# C - BOTANICAL FRESH
# ----------------------------------------------------------------------------

def front_c(c):
    x, y, w, h = X_FRNT, Y_BODY, W_FACE, H_BODY
    top, cx = y + h, x + w / 2
    panel("FRONT", x, y, w, h)

    rect(c, x, y, w, h, WHITE)
    c.saveState()
    clip_rect(c, x, y, w, h)
    img = _img("bokeh", 0.92)
    c.drawImage(img, P(x - 4), P(y - 4), (w + 8) * MM, (h + 8) * MM,
                mask="auto")
    c.restoreState()
    # a white veil over the masthead, faded out in bands rather than cut off
    # with a ruled edge, so the bokeh emerges instead of stopping
    for i in range(16):
        band_h = 62.0 - i * 3.4
        if band_h <= 0:
            break
        rect(c, x, top - band_h, w, band_h, WHITE, alpha=0.11)

    photo(c, "flower", x + w - 15.0, top - 16.0, 46.0, alpha=0.95)

    swift_logo(c, x + 30, top - 14.0, 48, shadow=False)

    size = fit("Blue-Drop", F["display"], 80.0)
    txt(c, x + 6.0, top - 48.0, "Blue-Drop", F["display"], size, NAVY)
    txt(c, x + 6.5, top - 56.5, "AUTOMATIC TOILET BOWL CLEANER", F["label"],
        9.4, BLUE_MID, char_space=0.6)
    strapline(c, cx, top - 70.0)

    # C carried a separate 4 PACK flag as well as a weight block and a benefit
    # row, and the face could not hold all three. The count folds into the
    # weight line in the footer, which buys the product real room.
    photo(c, "splash-arc", cx, y + 59.0, 112.0, alpha=0.62)
    discs(c, cx, y + 58.0, 26.0)

    benefit_row(c, cx, y + 25.0, NAVY, icon_bg=WHITE)
    footer(c, x, y, w, left="4 x 50 g    NET 200 g", h=11.0)


CONCEPTS = (("A", "White-Crown", front_a),
            ("B", "Water-Crown", front_b),
            ("C", "Botanical-Fresh", front_c))


# ----------------------------------------------------------------------------

def paint(c, front):
    rect(c, -BLEED, -BLEED, SHEET_W + 2 * BLEED, SHEET_H + 2 * BLEED, NAVY)
    B.flap_art(c)
    for fn in (B.panel_back,
               lambda cc: B.panel_side(cc, X_SIDL, "benefits"),
               front,
               lambda cc: B.panel_side(cc, X_SIDR, "legal")):
        fn(c)
        B.panel_end()
    B.glue_tab(c)


def build_concept(letter, name, front, path):
    from reportlab.pdfgen import canvas as _cv
    B.ORIGIN = BLEED
    page = ((SHEET_W + 2 * BLEED) * MM, (SHEET_H + 2 * BLEED) * MM)
    c = _cv.Canvas(path, pagesize=page)
    c.setTitle("Swift Blue-Drop 4 x 50 g - concept %s, %s" % (letter, name))
    c.setAuthor("Vistex Chemicals Ltd")
    c.setCreator("packaging/swift_blue_drop_concepts.py")
    paint(c, front)
    c.showPage()
    c.save()
    return path


def main():
    register_fonts()
    missing = [n for n in ("flower", "splash-arc", "splash-ring", "bokeh",
                           "disc-1", "disc-2", "disc-3", "disc-4")
               if not os.path.exists(os.path.join(ART, n + ".png"))]
    if missing:
        raise SystemExit("missing art: %s\nrun: python packaging/make_cutouts.py"
                         % ", ".join(missing))

    out = os.path.join(DIST, "concepts")
    os.makedirs(out, exist_ok=True)
    for letter, name, front in CONCEPTS:
        B.BOXES[:] = []
        B.OVERFLOW[:] = []
        SOLID[:] = []
        OCCLUDE[:] = []
        p = os.path.join(out, "Concept_%s_%s.pdf" % (letter, name))
        build_concept(letter, name, front, p)
        hits = B.collisions() + solid_collisions()
        flag = ""
        if B.OVERFLOW:
            flag += "  OVERFLOW:%d" % len(B.OVERFLOW)
        if hits:
            flag += "  COLLISIONS:%d" % len(hits)
        print("%s  %-16s %6.1f KB%s" %
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
