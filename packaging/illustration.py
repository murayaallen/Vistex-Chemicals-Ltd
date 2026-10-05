#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instruction illustrations for the Swift Blue-Drop carton.

A cistern is a box people never look inside, so "drop it in the tank" is not
self-explanatory. These draw the inside of the tank and show the block going
in, which is the one instruction that actually needs a picture.

Drawn as flat vector on a restricted palette - two blues, one cyan, one ink -
with a single stroke weight scaled off the artwork size, so the set reads as
one family rather than three unrelated drawings. No gradients and no soft
shadows: those are what make instruction art look clip-arty and print badly
at small size on uncoated board.
"""

from math import pi, sin, cos

from swift_blue_drop_dieline import (P, MM, poly, circle, rect, pill, txt, F,
                                     sw, NAVY, NAVY_DK, NAVY_MID, BLUE_MID,
                                     BLUE_BR, CYAN, CYAN_LT, WHITE, INK, GREY,
                                     RED)


# ---------------------------------------------------------------------------
# primitives shared by every step
# ---------------------------------------------------------------------------

def _stroke(c, colour, lw, cap=1, join=1, alpha=1.0):
    c.setStrokeColor(colour, alpha)
    c.setLineWidth(lw * MM)
    c.setLineCap(cap)
    c.setLineJoin(join)


def rrect(c, x, y, w, h, r, fill=None, stroke=None, lw=0.3, alpha=1.0):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill, alpha)
    if stroke is not None:
        _stroke(c, stroke, lw, alpha=alpha)
    c.roundRect(P(x), P(y), w * MM, h * MM, r * MM,
                fill=1 if fill is not None else 0,
                stroke=1 if stroke is not None else 0)
    c.restoreState()


def wave_top(c, x, y, w, amp, colour, alpha=1.0, lw=None):
    """A water surface. Drawn as a filled sliver so it reads as a surface
    rather than a drawn line."""
    c.saveState()
    c.setFillColor(colour, alpha)
    p = c.beginPath()
    p.moveTo(P(x), P(y))
    p.curveTo(P(x + w * 0.28), P(y + amp), P(x + w * 0.56), P(y - amp),
              P(x + w), P(y + amp * 0.35))
    p.lineTo(P(x + w), P(y - amp * 1.4))
    p.lineTo(P(x), P(y - amp * 1.4))
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def tablet_flat(c, cx, cy, r, squash=0.42):
    """The block, drawn flat to match the illustration rather than the
    photograph used on the face."""
    c.saveState()
    c.translate(P(cx), P(cy))
    c.scale(1.0, squash)
    c.setFillColor(BLUE_MID)
    c.circle(0, 0, r * MM, fill=1, stroke=0)
    c.setFillColor(BLUE_BR)
    c.circle(0, 0, r * 0.82 * MM, fill=1, stroke=0)
    c.restoreState()
    # ribs, kept few: more than ten turns to mush at 10 mm
    c.saveState()
    c.translate(P(cx), P(cy))
    c.scale(1.0, squash)
    _stroke(c, BLUE_MID, r * 0.09)
    for i in range(10):
        a = i * pi / 5.0
        p = c.beginPath()
        p.moveTo(r * 0.30 * cos(a) * MM, r * 0.30 * sin(a) * MM)
        p.lineTo(r * 0.78 * cos(a) * MM, r * 0.78 * sin(a) * MM)
        c.drawPath(p, fill=0, stroke=1)
    c.restoreState()
    c.saveState()
    c.translate(P(cx), P(cy))
    c.scale(1.0, squash)
    c.setFillColor(CYAN_LT)
    c.circle(0, 0, r * 0.24 * MM, fill=1, stroke=0)
    c.restoreState()


def arrow_down(c, x, y0, y1, colour, lw, head=None):
    head = head if head is not None else lw * 3.2
    c.saveState()
    _stroke(c, colour, lw)
    c.line(P(x), P(y0), P(x), P(y1 + head * 0.9))
    c.restoreState()
    poly(c, [(x, y1), (x - head * 0.62, y1 + head),
             (x + head * 0.62, y1 + head)], colour)


def step_badge(c, cx, cy, n, r=3.4):
    circle(c, cx, cy, r, NAVY)
    txt(c, cx, cy - r * 0.42, str(n), F["bodyblk"], r * 4.1, WHITE, "c")


# ---------------------------------------------------------------------------
# step 1 - take the block out of its wrapper
# ---------------------------------------------------------------------------

def step_unwrap(c, x, y, w):
    """A foil sachet with the top peeled back and the block coming out.

    The first attempt curved the wrapper outward at the top, which read as a
    tub or a bucket. A sachet is straight-sided with a torn head - that is
    what makes it legible as packaging at 25 mm.
    """
    h = w * 0.86
    cx = x + w * 0.46
    lw = w * 0.018
    sw_, sh = w * 0.44, h * 0.56
    sx, sy = cx - sw_ / 2, y + h * 0.10

    # sachet body
    rrect(c, sx, sy, sw_, sh, w * 0.012, fill=CYAN_LT, stroke=BLUE_MID,
          lw=lw, alpha=0.95)
    # seal ribs down each edge
    c.saveState()
    _stroke(c, BLUE_MID, lw * 0.7, alpha=0.55)
    for k in (0.10, 0.90):
        c.line(P(sx + sw_ * k), P(sy + sh * 0.04),
               P(sx + sw_ * k), P(sy + sh * 0.92))
    c.restoreState()

    # torn head, peeled back and over
    c.saveState()
    c.setFillColor(WHITE)
    _stroke(c, BLUE_MID, lw)
    p = c.beginPath()
    p.moveTo(P(sx), P(sy + sh))
    p.curveTo(P(sx + sw_ * 0.30), P(sy + sh + h * 0.14),
              P(sx + sw_ * 0.92), P(sy + sh + h * 0.17),
              P(sx + sw_ * 1.26), P(sy + sh + h * 0.03))
    p.lineTo(P(sx + sw_ * 1.18), P(sy + sh - h * 0.07))
    p.curveTo(P(sx + sw_ * 0.86), P(sy + sh + h * 0.05),
              P(sx + sw_ * 0.34), P(sy + sh + h * 0.02),
              P(sx + sw_ * 0.02), P(sy + sh - h * 0.05))
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.restoreState()
    # zigzag tear edge
    c.saveState()
    _stroke(c, BLUE_MID, lw * 0.8, cap=0, join=0, alpha=0.9)
    pts, n = [], 9
    for i in range(n + 1):
        t = i / float(n)
        px = sx + sw_ * (0.02 + 1.24 * t)
        py = sy + sh - h * 0.05 + h * 0.10 * t + (h * 0.018 if i % 2 else 0)
        pts.append((px, py))
    pth = c.beginPath()
    pth.moveTo(P(pts[0][0]), P(pts[0][1]))
    for px, py in pts[1:]:
        pth.lineTo(P(px), P(py))
    c.drawPath(pth, fill=0, stroke=1)
    c.restoreState()

    # the block, half out of the sachet
    tablet_flat(c, cx + w * 0.02, sy + sh * 0.62, w * 0.165, squash=0.92)
    return h


# ---------------------------------------------------------------------------
# step 2 - the tank, cut away, with the block going in
# ---------------------------------------------------------------------------

def step_tank(c, x, y, w):
    """The hero of the three: a cutaway so the inside is visible.

    The float and the inlet are drawn in because the instruction is
    specifically to keep the block clear of them - without them on the page,
    "clear of the inlet and float" means nothing. They are pushed to the
    right so the block has an unobstructed drop lane on the left, which is
    also what the copy is telling you to do.
    """
    h = w * 0.86
    lw = w * 0.019
    tx, tw = x + w * 0.05, w * 0.90
    tb, th = y + h * 0.08, h * 0.58
    water = tb + th * 0.52

    # lid, lifted clear
    rrect(c, tx + tw * 0.04, tb + th + h * 0.17, tw * 0.92, h * 0.050,
          h * 0.020, fill=WHITE, stroke=NAVY, lw=lw)
    c.saveState()
    _stroke(c, NAVY, lw * 0.75, alpha=0.35)
    c.setDash([lw * 2.6, lw * 2.6], 0)
    for k in (0.08, 0.92):
        c.line(P(tx + tw * k), P(tb + th + h * 0.15),
               P(tx + tw * k), P(tb + th + h * 0.02))
    c.restoreState()

    # shell
    rrect(c, tx, tb, tw, th, h * 0.028, fill=WHITE, stroke=NAVY, lw=lw)
    # flush handle, outside front left
    rrect(c, tx - tw * 0.07, tb + th * 0.70, tw * 0.08, th * 0.09,
          tw * 0.015, fill=WHITE, stroke=NAVY, lw=lw * 0.8)

    # water
    c.saveState()
    pth = c.beginPath()
    pth.rect(P(tx + lw), P(tb + lw), (tw - 2 * lw) * MM,
             (water - tb - lw) * MM)
    c.clipPath(pth, stroke=0, fill=0)
    c.setFillColor(CYAN_LT, 0.80)
    c.rect(P(tx), P(tb), tw * MM, (water - tb) * MM, fill=1, stroke=0)
    wave_top(c, tx, water, tw, h * 0.014, CYAN, alpha=0.95)
    c.restoreState()

    # ---- right third: inlet stack, float on its arm ----------------------
    ix = tx + tw * 0.78
    rrect(c, ix, tb + th * 0.10, tw * 0.065, th * 0.76, tw * 0.018,
          fill=WHITE, stroke=NAVY, lw=lw * 0.8)
    c.saveState()
    _stroke(c, NAVY, lw * 0.8)
    c.line(P(ix), P(tb + th * 0.66), P(tx + tw * 0.635), P(tb + th * 0.62))
    c.restoreState()
    circle(c, tx + tw * 0.585, tb + th * 0.615, tw * 0.052, WHITE,
           stroke=NAVY, lw=lw * 0.8)

    # ---- bottom: flush valve --------------------------------------------
    c.saveState()
    c.setFillColor(WHITE)
    _stroke(c, NAVY, lw * 0.8)
    pth = c.beginPath()
    pth.moveTo(P(tx + tw * 0.42), P(tb + lw))
    pth.curveTo(P(tx + tw * 0.42), P(tb + th * 0.19),
                P(tx + tw * 0.64), P(tb + th * 0.19),
                P(tx + tw * 0.64), P(tb + lw))
    pth.close()
    c.drawPath(pth, fill=1, stroke=1)
    c.restoreState()

    # ---- left third: the clear drop lane ---------------------------------
    drop_x = tx + tw * 0.26
    c.saveState()
    _stroke(c, BLUE_MID, lw * 0.85, alpha=0.45)
    c.setDash([lw * 2.2, lw * 2.2], 0)
    c.line(P(drop_x), P(tb + th + h * 0.12), P(drop_x), P(tb + th * 0.86))
    c.restoreState()
    tablet_flat(c, drop_x, tb + th * 0.78, tw * 0.105, squash=0.46)
    arrow_down(c, drop_x, tb + th * 0.70, tb + th * 0.60, BLUE_MID, lw * 1.2)
    # ripples where it lands
    c.saveState()
    _stroke(c, CYAN, lw * 0.75, alpha=0.8)
    for k in (1.0, 1.7, 2.4):
        c.saveState()
        c.translate(P(drop_x), P(water))
        c.scale(1.0, 0.28)
        c.circle(0, 0, tw * 0.055 * k * MM, fill=0, stroke=1)
        c.restoreState()
    c.restoreState()
    return h


# ---------------------------------------------------------------------------
# step 3 - every flush runs blue
# ---------------------------------------------------------------------------

def step_flush(c, x, y, w):
    h = w * 0.86
    lw = w * 0.019
    cx = x + w * 0.50

    # cistern behind
    rrect(c, cx - w * 0.30, y + h * 0.52, w * 0.60, h * 0.30, h * 0.03,
          fill=WHITE, stroke=NAVY, lw=lw)
    # bowl
    c.saveState()
    c.setFillColor(WHITE)
    _stroke(c, NAVY, lw)
    p = c.beginPath()
    p.moveTo(P(cx - w * 0.30), P(y + h * 0.46))
    p.curveTo(P(cx - w * 0.30), P(y + h * 0.10),
              P(cx + w * 0.30), P(y + h * 0.10),
              P(cx + w * 0.30), P(y + h * 0.46))
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.restoreState()
    # rim
    c.saveState()
    c.setFillColor(WHITE)
    _stroke(c, NAVY, lw)
    c.translate(P(cx), P(y + h * 0.46))
    c.scale(1.0, 0.30)
    c.circle(0, 0, w * 0.31 * MM, fill=1, stroke=1)
    c.restoreState()
    # blue water
    c.saveState()
    c.setFillColor(CYAN, 0.95)
    c.translate(P(cx), P(y + h * 0.455))
    c.scale(1.0, 0.30)
    c.circle(0, 0, w * 0.235 * MM, fill=1, stroke=0)
    c.restoreState()
    # swirl
    c.saveState()
    _stroke(c, WHITE, lw * 1.1, alpha=0.9)
    c.translate(P(cx), P(y + h * 0.455))
    c.scale(1.0, 0.30)
    p = c.beginPath()
    first = True
    for i in range(46):
        t = i / 45.0
        a = t * 3.4 * pi
        rr = w * 0.20 * (1.0 - t * 0.78)
        px, py = rr * cos(a) * MM, rr * sin(a) * MM
        (p.moveTo if first else p.lineTo)(px, py)
        first = False
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()
    # pedestal
    # pedestal, closed with one path so the outline is continuous
    c.saveState()
    c.setFillColor(WHITE)
    _stroke(c, NAVY, lw)
    pth = c.beginPath()
    pth.moveTo(P(cx - w * 0.15), P(y + h * 0.20))
    pth.curveTo(P(cx - w * 0.13), P(y + h * 0.10),
                P(cx - w * 0.12), P(y + h * 0.05),
                P(cx - w * 0.11), P(y + h * 0.02))
    pth.lineTo(P(cx + w * 0.11), P(y + h * 0.02))
    pth.curveTo(P(cx + w * 0.12), P(y + h * 0.05),
                P(cx + w * 0.13), P(y + h * 0.10),
                P(cx + w * 0.15), P(y + h * 0.20))
    c.drawPath(pth, fill=1, stroke=1)
    c.restoreState()
    # freshness marks
    for sx, sy, sr in ((0.36, 0.62, 0.030), (0.42, 0.52, 0.020),
                       (-0.38, 0.58, 0.024)):
        k = w * sr
        poly(c, [(cx + w * sx, y + h * sy + k), (cx + w * sx + k * 0.3, y + h * sy + k * 0.3),
                 (cx + w * sx + k, y + h * sy), (cx + w * sx + k * 0.3, y + h * sy - k * 0.3),
                 (cx + w * sx, y + h * sy - k), (cx + w * sx - k * 0.3, y + h * sy - k * 0.3),
                 (cx + w * sx - k, y + h * sy), (cx + w * sx - k * 0.3, y + h * sy + k * 0.3)],
             CYAN)
    return h


# Titles are short because the column is only ~28 mm wide and the badge eats
# 8 mm of it. Detail belongs in the body line, which can wrap.
STEPS = ((step_unwrap, "Unwrap", "Take one block from its wrapper."),
         (step_tank, "Drop in",
          "Lift the lid and drop it into the tank, clear of the inlet and "
          "the float."),
         (step_flush, "Runs blue",
          "Replace the lid. Every flush cleans, for up to 30 days."))


def how_to_use(c, x, y, w, gap=4.0, ink=INK, head=NAVY):
    """The three steps in a row, returning the height consumed."""
    cw = (w - gap * 2) / 3.0
    art_h = cw * 0.86
    cap_y = y + 15.0
    for i, (fn, title, body) in enumerate(STEPS):
        cx0 = x + i * (cw + gap)
        fn(c, cx0, cap_y + 2.0, cw)
        step_badge(c, cx0 + 3.8, cap_y + art_h + 5.4, i + 1, r=3.4)
        txt(c, cx0 + 9.0, cap_y + art_h + 4.2, title, F["subhead"], 7.0, head)
        yy = cap_y - 1.0
        from swift_blue_drop_dieline import wrap
        for ln in wrap(body, F["body"], 6.2, cw - 1.0):
            txt(c, cx0, yy, ln, F["body"], 6.2, ink)
            yy -= 3.2
    return art_h + 22.0
