#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swift Blue-Drop 95 x 95 x 20 mm - views and folding guide.

The companion to the print file. Everything here is derived from the same
geometry and the same printed PDF, so the guide cannot describe a different
carton from the one that is printed.

    p1  3D views of the finished pack (rendered from the print PDF)
    p2  orthographic views at 1:1 with finished dimensions
    p3  dieline at 1:1, fully dimensioned
    p4  artwork on the die, panel map
    p5  folding and filling instructions
    p6  specification and pre-press checks

Run after swift_blue_drop_95.py:
      python packaging/swift_blue_drop_95_guide.py
"""

import math
import os

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter
from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as _canvas

import make_mockup as MK
import swift_blue_drop_dieline as B
import swift_blue_drop_95 as C

MM = C.MM
PAGE = (297.0, 210.0)
PRINT = os.path.join(C.OUT, C.STEM + "_PRINT.pdf")
GUIDE = os.path.join(C.OUT, C.STEM + "_VIEWS_AND_FOLDING.pdf")
VIEWS_DIR = os.path.join(C.OUT, "views")

INK = Color(0.08, 0.11, 0.24)
MUTED = Color(0.38, 0.42, 0.52)
NAVY = Color(0.004, 0.137, 0.42)
CYANC = Color(0.0, 0.62, 0.86)
MAG = Color(0.89, 0.0, 0.55)
RULE = Color(0.82, 0.85, 0.9)
OUTSIDE = Color(0.80, 0.87, 0.97)       # printed face in the diagrams
INSIDE = Color(0.97, 0.96, 0.93)        # unprinted board
EDGE = Color(0.12, 0.2, 0.42)
GLUE = Color(1.0, 0.78, 0.0)
ACCENT = Color(0.93, 0.12, 0.15)

FT = {"h": "Outfit-800", "s": "Outfit-700", "b": "Jakarta-400",
      "m": "Jakarta-600", "k": "Jakarta-800"}


# ----------------------------------------------------------------------------
# page helpers (page coordinates in mm, origin bottom-left)
# ----------------------------------------------------------------------------

def t(c, x, y, s, font="b", size=8.0, col=INK, align="l"):
    f = FT.get(font, font)
    c.setFont(f, size)
    c.setFillColor(col)
    if align == "c":
        c.drawCentredString(x * MM, y * MM, s)
    elif align == "r":
        c.drawRightString(x * MM, y * MM, s)
    else:
        c.drawString(x * MM, y * MM, s)


def page_frame(c, n, title, sub):
    c.setFillColor(Color(1, 1, 1))
    c.rect(0, 0, PAGE[0] * MM, PAGE[1] * MM, fill=1, stroke=0)
    t(c, 12, 199, title, "h", 15, NAVY)
    t(c, 12, 193.2, sub, "b", 8.2, MUTED)
    t(c, 285, 199, "SWIFT BLUE-DROP  ·  4 × 50 g  ·  95 × 95 × 20 mm",
      "s", 8, NAVY, "r")
    t(c, 285, 193.2, "Vistex Chemicals Ltd  ·  sheet %d of 6" % n, "b", 7.6,
      MUTED, "r")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.line(12 * MM, 190 * MM, 285 * MM, 190 * MM)


def arrowhead(c, x, y, ang, size=2.0, col=INK):
    c.setFillColor(col)
    p = c.beginPath()
    p.moveTo(x * MM, y * MM)
    for da in (2.7, -2.7):
        p.lineTo((x - size * math.cos(ang + da * 0.15)) * MM,
                 (y - size * math.sin(ang + da * 0.15)) * MM)
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def dim_h(c, x0, x1, y, label, ext_from=None, col=INK, size=7.0, above=True):
    """Horizontal dimension with extension lines from ext_from (y) if given."""
    c.saveState()
    c.setStrokeColor(col)
    c.setLineWidth(0.35)
    if ext_from is not None:
        for xx in (x0, x1):
            c.line(xx * MM, ext_from * MM, xx * MM, (y + (1.2 if y > ext_from
                                                           else -1.2)) * MM)
    c.line(x0 * MM, y * MM, x1 * MM, y * MM)
    c.restoreState()
    arrowhead(c, x0, y, math.pi, 1.6, col)
    arrowhead(c, x1, y, 0.0, 1.6, col)
    ty = y + 1.2 if above else y - 3.2
    c.setFillColor(Color(1, 1, 1))
    wd = c.stringWidth(label, FT["m"], size) / MM
    c.rect(((x0 + x1) / 2 - wd / 2 - 0.8) * MM, (ty - 0.6) * MM,
           (wd + 1.6) * MM, (size * 0.36 + 1.0) * MM, fill=1, stroke=0)
    t(c, (x0 + x1) / 2, ty, label, "m", size, col, "c")


def dim_v(c, y0, y1, x, label, ext_from=None, col=INK, size=7.0, left=True):
    c.saveState()
    c.setStrokeColor(col)
    c.setLineWidth(0.35)
    if ext_from is not None:
        for yy in (y0, y1):
            c.line(ext_from * MM, yy * MM, (x + (1.2 if x > ext_from
                                                 else -1.2)) * MM, yy * MM)
    c.line(x * MM, y0 * MM, x * MM, y1 * MM)
    c.restoreState()
    arrowhead(c, x, y0, -math.pi / 2, 1.6, col)
    arrowhead(c, x, y1, math.pi / 2, 1.6, col)
    c.saveState()
    c.translate((x - 1.2 if left else x + 3.4) * MM, ((y0 + y1) / 2) * MM)
    c.rotate(90)
    wd = c.stringWidth(label, FT["m"], size)
    c.setFillColor(Color(1, 1, 1))
    c.rect(-wd / 2 - 0.8 * MM, -0.6 * MM, wd + 1.6 * MM,
           (size * 0.36 + 1.0) * MM, fill=1, stroke=0)
    c.setFillColor(col)
    c.setFont(FT["m"], size)
    c.drawCentredString(0, 0, label)
    c.restoreState()


def place_img(c, im, x, y, w, h=None):
    if h is None:
        h = w * im.height / float(im.width)
    c.drawImage(ImageReader(im), x * MM, y * MM, w * MM, h * MM,
                mask="auto")
    return h


# ----------------------------------------------------------------------------
# faces lifted from the print PDF
# ----------------------------------------------------------------------------

def face(x, y, w, h, dpi=300, page=0):
    pg = pymupdf.open(PRINT)[page]
    H = pg.rect.height
    o = C.BLEED
    r = pymupdf.Rect((x + o) * MM, H - (y + h + o) * MM, (x + w + o) * MM,
                     H - (y + o) * MM)
    px = pg.get_pixmap(dpi=dpi, clip=r)
    return Image.frombytes("RGB", (px.width, px.height), px.samples)


def tab_mask(im):
    """Alpha for the tab: chamfered shoulders and the punched euro slot."""
    sx, sy = im.width / C.TAB_W, im.height / C.H_HANG
    m = Image.new("L", im.size, 255)
    d = ImageDraw.Draw(m)
    ch = C.TAB_CH * sx
    d.polygon([(0, 0), (ch, 0), (0, im.height)], fill=0)
    d.polygon([(im.width, 0), (im.width - ch, 0), (im.width, im.height)],
              fill=0)
    cx = im.width / 2.0
    eye = (C.H_HANG - C.SLOT_Y) * sy
    top = (C.H_HANG - C.SLOT_Y - C.SLOT_RISE) * sy
    r, hw = C.SLOT_R * sx, C.SLOT_W / 2.0 * sx
    d.ellipse((cx - r, eye - r, cx + r, eye + r), fill=0)
    d.rectangle((cx - hw, top, cx + hw, eye), fill=0)
    d.ellipse((cx - hw, top - hw, cx + hw, top + hw), fill=0)
    return m


def faces():
    f = {
        "front": face(C.X_FRNT, C.Y_BODY, C.W_FACE, C.H_BODY),
        "back": face(C.X_BACK, C.Y_BODY, C.W_FACE, C.H_BODY),
        "side_l": face(C.X_SIDL, C.Y_BODY, C.W_SIDE, C.H_BODY),
        "side_r": face(C.X_SIDR, C.Y_BODY, C.W_SIDE, C.H_BODY),
        "top": face(C.X_FRNT, C.Y_TOP, C.W_FACE, C.H_CLOSE),
        "bottom": face(C.X_FRNT, C.Y_BODY - C.H_CLOSE, C.W_FACE, C.H_CLOSE),
    }
    tab = face(C.TAB_X0, C.Y_TOP, C.TAB_W, C.H_HANG).convert("RGBA")
    m = tab_mask(tab)
    tab.putalpha(m)
    f["tab"] = tab
    # the reverse of the tab is bare board: that is what a shopper standing
    # in front of the peg actually sees
    rev = Image.new("RGBA", tab.size, (236, 234, 228, 255))
    rev.putalpha(m.transpose(Image.FLIP_LEFT_RIGHT))
    f["tab_rev"] = rev
    return f


# ----------------------------------------------------------------------------
# 3D renders (same camera rig as make_views.py)
# ----------------------------------------------------------------------------
PAD = 90


def render(fc, yaw, eye, from_back=False, scale=8.0, focal=8000.0):
    W, H, D = C.W_FACE, C.H_BODY, C.W_SIDE
    MK.YAW = math.radians(yaw)
    MK.EYE_Y = eye
    MK.SCALE = scale
    MK.FOCAL = focal
    hw, hd = W / 2.0, D / 2.0

    def c3(sx, sy, sz):
        return (sx * hw, sy, sz * hd)

    ftl, ftr, fbl, fbr = c3(-1, H, 1), c3(1, H, 1), c3(-1, 0, 1), c3(1, 0, 1)
    btr, bbr, btl, bbl = c3(1, H, -1), c3(1, 0, -1), c3(-1, H, -1), \
        c3(-1, 0, -1)
    htw = C.TAB_W / 2.0
    tz = hd if from_back else -hd
    tq3 = [(-htw, H + C.H_HANG, tz), (htw, H + C.H_HANG, tz), (htw, H, tz),
           (-htw, H, tz)]
    pts = [ftl, ftr, fbl, fbr, btr, bbr, btl, bbl] + tq3
    MK.OFFSET[0], MK.OFFSET[1] = 0.0, 0.0
    pp = [MK.project(q) for q in pts]
    xs, ys = [q[0] for q in pp], [q[1] for q in pp]
    cw = int(max(xs) - min(xs)) + 2 * PAD
    ch = int(max(ys) - min(ys)) + 2 * PAD
    MK.OFFSET[0] = PAD - min(xs)
    MK.OFFSET[1] = PAD - min(ys)
    canvas = (cw, ch)

    g = Image.new("RGB", canvas, (240, 244, 250))
    gd = ImageDraw.Draw(g)
    for i in range(ch):
        v = int(250 - 26 * i / float(ch))
        gd.line([(0, i), (cw, i)], fill=(v, v + 2, min(255, v + 8)))
    scene = g.convert("RGBA")
    sh = Image.new("RGBA", canvas, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([MK.project(q) for q in (fbl, fbr, bbr, bbl)],
                               fill=(24, 38, 76, 120))
    sh = sh.transform(canvas, Image.AFFINE, (1, 0, 9, 0, 1, 12))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    scene = Image.alpha_composite(scene, sh)

    if from_back:
        front, top = fc["back"], fc["top"].rotate(180)
        side_r, side_l = fc["side_l"], fc["side_r"]
        tab = fc["tab"]
    else:
        front, top = fc["front"], fc["top"]
        side_r, side_l = fc["side_r"], fc["side_l"]
        tab = fc["tab_rev"]
    tquad = [MK.project(q) for q in tq3]

    def paint_tab(sc):
        return Image.alpha_composite(
            sc, MK.shade(MK.warp(tab, tquad, canvas), 0.95))

    if not from_back:
        scene = paint_tab(scene)
    right = MK.YAW < 0
    flank = (side_r, [MK.project(q) for q in (ftr, btr, bbr, fbr)]) if right \
        else (side_l, [MK.project(q) for q in (btl, ftl, fbl, bbl)])
    for im, quad, k in ((flank[0], flank[1], 0.76),
                        (top, [MK.project(q) for q in (btl, btr, ftr, ftl)],
                         1.12),
                        (front, [MK.project(q) for q in (ftl, ftr, fbr, fbl)],
                         1.0)):
        scene = Image.alpha_composite(scene, MK.shade(MK.warp(im, quad,
                                                              canvas), k))
    if from_back:
        scene = paint_tab(scene)
    return scene.convert("RGB")


VIEWS = (("front-3q-left", -28.0, 78.0, False, "Front, three-quarter"),
         ("front-3q-right", 28.0, 78.0, False, "Front, other flank"),
         ("front-flat", -0.5, 60.0, False, "Front, square on"),
         ("back-3q", -28.0, 78.0, True, "Back, three-quarter"),
         ("back-flat", 0.5, 60.0, True, "Back with hang tab, square on"),
         ("top", -22.0, 260.0, False, "From above: top closure"))


# ----------------------------------------------------------------------------
# folding diagrams: a small orthographic 3D engine drawn as vectors
# ----------------------------------------------------------------------------
YAW_D = math.radians(32.0)
PITCH_D = math.radians(24.0)


def pj(p):
    x, y, z = p
    xr = x * math.cos(YAW_D) + z * math.sin(YAW_D)
    zr = z * math.cos(YAW_D) - x * math.sin(YAW_D)
    v = y * math.cos(PITCH_D) + zr * math.sin(PITCH_D)
    depth = zr * math.cos(PITCH_D) - y * math.sin(PITCH_D)
    return xr, v, depth


def rot(p, a, axis, ang):
    """Rotate point p about the line through a with unit direction axis."""
    v = np.array(p, float) - np.array(a, float)
    k = np.array(axis, float)
    v = (v * math.cos(ang) + np.cross(k, v) * math.sin(ang)
         + k * np.dot(k, v) * (1 - math.cos(ang)))
    return tuple(v + np.array(a, float))


def _normal(pts):
    n = np.zeros(3)
    for i in range(len(pts)):
        a, b = np.array(pts[i]), np.array(pts[(i + 1) % len(pts)])
        n += np.cross(a, b)
    return n


def face3(pts, out_n, fill_out=OUTSIDE, fill_in=INSIDE):
    """A polygon with its printed side marked by out_n."""
    if np.dot(_normal(pts), out_n) < 0:
        pts = list(reversed(pts))
    return {"pts": pts, "out": fill_out, "in": fill_in}


def box_polys(top=(0, 0, 0), bot=(0, 0, 0), tab=True, D=None):
    """top/bot = (closure angle, lip angle, dust angle) in degrees, 0 = open
    flat, 90 = folded home."""
    W, H = C.W_FACE, C.H_BODY
    D = D or C.W_SIDE
    P = []
    P.append(face3([(0, 0, 0), (W, 0, 0), (W, H, 0), (0, H, 0)], (0, 0, -1)))
    P.append(face3([(0, 0, D), (W, 0, D), (W, H, D), (0, H, D)], (0, 0, 1)))
    P.append(face3([(0, 0, 0), (0, H, 0), (0, H, D), (0, 0, D)], (-1, 0, 0)))
    P.append(face3([(W, 0, 0), (W, H, 0), (W, H, D), (W, 0, D)], (1, 0, 0)))
    if tab:
        x0 = (W - C.TAB_W) / 2
        P.append(face3([(x0, H, D), (x0 + C.TAB_W, H, D),
                        (x0 + C.TAB_W - C.TAB_CH, H + C.H_HANG, D),
                        (x0 + C.TAB_CH, H + C.H_HANG, D)], (0, 0, 1)))
    for end, (ac, al, ad) in (("top", top), ("bot", bot)):
        s = 1 if end == "top" else -1
        yh = H if end == "top" else 0.0
        a_c = math.radians(ac) * s          # +x rotation folds top to +z
        # closure + lip
        cl = [(0, yh, 0), (W, yh, 0), (W, yh + s * C.H_CLOSE, 0),
              (0, yh + s * C.H_CLOSE, 0)]
        lip = [(C.LIP_IN, yh + s * C.H_CLOSE, 0),
               (W - C.LIP_IN, yh + s * C.H_CLOSE, 0),
               (W - C.LIP_IN, yh + s * C.H_TUCK, 0),
               (C.LIP_IN, yh + s * C.H_TUCK, 0)]
        lip = [rot(q, (0, yh + s * C.H_CLOSE, 0), (1, 0, 0),
                   math.radians(al) * s) for q in lip]
        ln = rot((0, 0, -1), (0, 0, 0), (1, 0, 0),
                 math.radians(al) * s + a_c)
        cl = [rot(q, (0, yh, 0), (1, 0, 0), a_c) for q in cl]
        lip = [rot(q, (0, yh, 0), (1, 0, 0), a_c) for q in lip]
        cn = rot((0, 0, -1), (0, 0, 0), (1, 0, 0), a_c)
        P.append(face3(cl, cn))
        P.append(face3(lip, ln))
        # dust flaps
        for xs, sgn in ((0.0, 1), (W, -1)):
            dp = [(xs, yh, 0.6), (xs, yh, D - 0.6),
                  (xs, yh + s * C.H_DUST, D - 0.6 - C.DT * 0.5),
                  (xs, yh + s * C.H_DUST, 0.6 + C.DT * 0.5)]
            ang = -sgn * s * math.radians(ad)
            dp = [rot(q, (xs, yh, 0), (0, 0, 1), ang) for q in dp]
            dn = rot((-sgn, 0, 0), (0, 0, 0), (0, 0, 1), ang)
            P.append(face3(dp, dn))
    return P


def draw3(c, polys, ox, oy, s, extra=None):
    """Painter's algorithm in projected space. extra: callables drawn after
    polygons whose depth is greater than their key."""
    items = []
    for p in polys:
        pr = [pj(q) for q in p["pts"]]
        dep = sum(q[2] for q in pr) / len(pr)
        items.append((dep, p, pr))
    items.sort(key=lambda it: -it[0])
    for dep, p, pr in items:
        area = 0.0
        for i in range(len(pr)):
            a, b = pr[i], pr[(i + 1) % len(pr)]
            area += a[0] * b[1] - b[0] * a[1]
        fill = p["out"] if area < 0 else p["in"]
        c.setFillColor(fill)
        c.setStrokeColor(EDGE)
        c.setLineWidth(0.55)
        c.setLineJoin(1)
        path = c.beginPath()
        path.moveTo((ox + pr[0][0] * s) * MM, (oy + pr[0][1] * s) * MM)
        for q in pr[1:]:
            path.lineTo((ox + q[0] * s) * MM, (oy + q[1] * s) * MM)
        path.close()
        c.drawPath(path, fill=1, stroke=1)


def to_page(p, ox, oy, s):
    u, v, _ = pj(p)
    return ox + u * s, oy + v * s


def arc_arrow(c, pts3, ox, oy, s, col=ACCENT, lw=1.3):
    pts = [to_page(q, ox, oy, s) for q in pts3]
    c.saveState()
    c.setStrokeColor(col)
    c.setLineWidth(lw)
    c.setLineCap(1)
    p = c.beginPath()
    p.moveTo(pts[0][0] * MM, pts[0][1] * MM)
    for q in pts[1:]:
        p.lineTo(q[0] * MM, q[1] * MM)
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    arrowhead(c, x1, y1, math.atan2(y1 - y0, x1 - x0), 2.4, col)


def arc3(centre, axis_pt_fn, n=14):
    return [axis_pt_fn(i / float(n - 1)) for i in range(n)]


def block3(cx, cy, z0, r=21.0, th=17.0, n=40):
    """A cistern block standing on edge: two discs and the wall between."""
    out = []
    ring = lambda z: [(cx + r * math.cos(2 * math.pi * i / n),
                       cy + r * math.sin(2 * math.pi * i / n), z)
                      for i in range(n)]
    out.append(face3(ring(z0 + th), (0, 0, 1), Color(0.1, 0.3, 0.75),
                     Color(0.1, 0.3, 0.75)))
    out.append(face3(ring(z0), (0, 0, -1), Color(0.2, 0.45, 0.9),
                     Color(0.2, 0.45, 0.9)))
    return out


# 2D blank, inside up (mirrored), for the first steps
def blank2d(c, ox, oy, s, highlight=None, glue=False):
    W = C.SHEET_W

    def m(p):
        return ox + (W - p[0]) * s, oy + p[1] * s

    pts = [m(p) for p in C.blank_outline()]
    c.setFillColor(INSIDE)
    c.setStrokeColor(EDGE)
    c.setLineWidth(0.6)
    p = c.beginPath()
    p.moveTo(pts[0][0] * MM, pts[0][1] * MM)
    for q in pts[1:]:
        p.lineTo(q[0] * MM, q[1] * MM)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    if glue:
        x0, y0 = m((C.X_GLUE + 2.0, C.Y_BODY + C.GT + 3))
        x1, y1 = m((C.X_GLUE + C.W_GLUE - 3.0, C.Y_TOP - C.GT - 3))
        c.setFillColor(GLUE)
        c.rect(min(x0, x1) * MM, y0 * MM, abs(x1 - x0) * MM, (y1 - y0) * MM,
               fill=1, stroke=0)
    c.saveState()
    c.setDash([1.6 * MM, 1.0 * MM], 0)
    c.setLineWidth(0.5)
    for seg in C.creases():
        a, b = m(seg[0]), m(seg[1])
        hl = highlight is not None and abs(seg[0][0] - seg[1][0]) < 1e-6 \
            and abs(seg[0][0] - highlight) < 1e-6
        c.setStrokeColor(ACCENT if hl else CYANC)
        c.setLineWidth(1.2 if hl else 0.5)
        c.line(a[0] * MM, a[1] * MM, b[0] * MM, b[1] * MM)
    c.restoreState()
    return m


# ----------------------------------------------------------------------------
# pages
# ----------------------------------------------------------------------------

def p_views(c, fc):
    page_frame(c, 1, "Finished pack - 3D views",
               "Rendered from the print file itself, so what you see here "
               "is what will be printed. 95 W × 95 H × 20 D mm; the hang tab "
               "takes the back to 115 mm.")
    os.makedirs(VIEWS_DIR, exist_ok=True)
    cols, cw, chh = 3, 89.0, 79.0
    x0, ytop = 12.0, 186.0
    for i, (key, yaw, eye, back, label) in enumerate(VIEWS):
        im = render(fc, yaw, eye, from_back=back)
        im.save(os.path.join(VIEWS_DIR, "%s.png" % key))
        col, row = i % cols, i // cols
        cx = x0 + col * (cw + 3.0)
        cy = ytop - (row + 1) * (chh + 7.0)
        c.setFillColor(Color(0.95, 0.96, 0.98))
        c.roundRect(cx * MM, cy * MM, cw * MM, chh * MM, 2 * MM, fill=1,
                    stroke=0)
        iw, ih = im.size
        k = min((cw - 4) / iw, (chh - 4) / ih)
        place_img(c, im, cx + (cw - iw * k) / 2, cy + (chh - ih * k) / 2,
                  iw * k, ih * k)
        t(c, cx + 1, cy + chh + 1.6, label, "s", 8.2, NAVY)
    t(c, 12, 8.5, "The tab is a single ply of board, so from the front its "
      "unprinted reverse shows above the carton (left and top views). "
      "Printing that reverse is optional; see sheet 6.", "b", 7.4, MUTED)


def p_ortho(c, fc):
    page_frame(c, 2, "Panel views at 1:1 with finished dimensions",
               "Print this sheet at 100% (no 'fit to page') and every panel "
               "measures true. All dimensions in mm, outside of carton.")
    oy = 50.0                                   # body bottom line
    xb = 22.0                                   # back left
    gap = 9.0
    xl = xb + C.W_FACE + gap
    xf = xl + C.W_SIDE + gap
    xr = xf + C.W_FACE + gap
    # back + tab as one picture
    back = fc["back"]
    tab = fc["tab"]
    place_img(c, back, xb, oy, C.W_FACE, C.H_BODY)
    place_img(c, tab, xb + (C.W_FACE - C.TAB_W) / 2, oy + C.H_BODY, C.TAB_W,
              C.H_HANG)
    place_img(c, fc["side_l"], xl, oy, C.W_SIDE, C.H_BODY)
    place_img(c, fc["front"], xf, oy, C.W_FACE, C.H_BODY)
    place_img(c, fc["side_r"], xr, oy, C.W_SIDE, C.H_BODY)
    place_img(c, fc["top"], xf, oy + C.H_BODY + gap, C.W_FACE, C.H_CLOSE)
    place_img(c, fc["bottom"], xf, oy - gap - C.H_CLOSE, C.W_FACE, C.H_CLOSE)
    for x, lab in ((xb + 1.0, "BACK"), (xl + C.W_SIDE / 2, "LEFT"),
                   (xf + C.W_FACE / 2, "FRONT"), (xr + C.W_SIDE / 2, "RIGHT")):
        t(c, x, oy + C.H_BODY + 2.6, lab, "s", 8, NAVY,
          "l" if lab == "BACK" else "c")
    t(c, xf - 2.0, oy + C.H_BODY + gap + 8.0, "TOP", "s", 8, NAVY, "r")
    t(c, xf - 2.0, oy - gap - 12.0, "BOTTOM", "s", 8, NAVY, "r")
    # widths
    dim_h(c, xb, xb + C.W_FACE, oy - 6.0, "95", ext_from=oy - 0.5,
          above=False)
    dim_h(c, xl, xl + C.W_SIDE, oy - 6.0, "20", ext_from=oy - 0.5,
          above=False)
    dim_h(c, xr, xr + C.W_SIDE, oy - 6.0, "20", ext_from=oy - 0.5,
          above=False)
    dim_h(c, xf, xf + C.W_FACE, oy - gap - C.H_CLOSE - 6.0, "95",
          ext_from=oy - gap - C.H_CLOSE - 0.5, above=False)
    tx0 = xb + (C.W_FACE - C.TAB_W) / 2
    dim_h(c, tx0, tx0 + C.TAB_W, oy + C.H_BODY + C.H_HANG + 5.0, "tab 60",
          ext_from=oy + C.H_BODY + 0.5)
    # heights
    dim_v(c, oy, oy + C.H_BODY, xb - 5.0, "95", ext_from=xb - 0.5)
    dim_v(c, oy, oy + C.H_BODY + C.H_HANG, xb - 12.0, "115 with tab",
          ext_from=xb - 0.5)
    dim_v(c, oy + C.H_BODY, oy + C.H_BODY + C.H_HANG,
          xb + C.W_FACE + 4.0, "20", ext_from=tx0 + C.TAB_W, left=False)
    dim_v(c, oy, oy + C.H_BODY, xr + C.W_SIDE + 5.0, "95",
          ext_from=xr + C.W_SIDE + 0.5, left=False)
    dim_v(c, oy + C.H_BODY + gap, oy + C.H_BODY + gap + C.H_CLOSE,
          xf + C.W_FACE + 5.0, "20", ext_from=xf + C.W_FACE + 0.5,
          left=False)
    t(c, 12, 8.5, "Type is held to a 1.2 mm minimum x-height throughout "
      "(EU 1169/2011 for packs over 80 cm²). The smallest copy on the pack "
      "is 6.6 pt Plus Jakarta Sans.", "b", 7.4, MUTED)


def p_die(c):
    page_frame(c, 3, "Dieline at 1:1 - straight tuck end with euro hang tab",
               "Viewed from the printed side. Magenta = cut, cyan dashed = "
               "crease. Print at 100% to check against the die.")
    ox, oy = 24.0, 22.0
    B.ORIGIN = 0.0
    c.saveState()
    c.translate(ox * MM, oy * MM)
    C.draw_die(c, cut=MAG, crease=CYANC, lw=0.6, dash=(3.0, 1.8))
    c.restoreState()

    def X(v):
        return ox + v

    def Y(v):
        return oy + v

    top = Y(C.SHEET_H)
    # panel widths along the top
    xs = (C.X_GLUE, C.X_BACK, C.X_SIDL, C.X_FRNT, C.X_SIDR, C.SHEET_W)
    labs = ("13", "95", "20", "95", "20")
    for a, b, lab in zip(xs[:-1], xs[1:], labs):
        dim_h(c, X(a), X(b), top + 4.5, lab, ext_from=Y(C.Y_TOP))
    dim_v(c, Y(0), Y(C.SHEET_H), X(C.SHEET_W) + 15.0, "161 overall",
          ext_from=X(C.SHEET_W) + 0.5, left=False)
    # heights at the right
    ys = (0.0, C.H_LIP, C.H_TUCK, C.Y_TOP, C.Y_TOP + C.H_CLOSE, C.SHEET_H)
    for a, b, lab in zip(ys[:-1], ys[1:], ("13", "20", "95", "20", "13")):
        dim_v(c, Y(a), Y(b), X(C.SHEET_W) + 6.0, lab,
              ext_from=X(C.X_SIDR) + 0.5, left=False)
    # back + tab
    dim_v(c, Y(C.Y_BODY), Y(C.Y_TOP + C.H_HANG), X(0) - 6.0, "115",
          ext_from=X(C.X_BACK) - 0.5)
    dim_v(c, Y(C.Y_TOP), Y(C.Y_TOP + C.H_HANG), X(C.TAB_X0) - 4.0, "20",
          ext_from=X(C.TAB_X0) + 2.0)
    dim_h(c, X(C.TAB_X0), X(C.TAB_X1), Y(C.Y_TOP + C.H_HANG) + 4.0, "60",
          ext_from=Y(C.Y_TOP + C.H_HANG) + 0.5)
    dim_v(c, Y(C.Y_TOP), Y(C.Y_TOP + C.H_DUST), X(C.X_SIDL) - 3.5, "15",
          ext_from=X(C.X_SIDL) - 0.5)
    dim_h(c, X(0), X(C.SHEET_W), Y(0) - 7.0, "243 overall",
          ext_from=Y(C.Y_BODY), above=False)
    # callouts
    sx = X(C.TAB_X0 + C.TAB_W / 2)
    t(c, sx, Y(C.Y_TOP) - 5.0,
      "euro slot Ø6, %.1f mm headroom" % C.TAB_HEADROOM, "m", 6.6, MAG, "c")
    vx = X(C.X_SIDR + C.W_SIDE / 2)
    t(c, X(C.X_SIDL) - 2.5, Y(C.Y_TOP - C.VENT_DY) - 1.0,
      "3 scent vents per side", "m", 6.6, MAG, "r")
    t(c, X(C.X_GLUE + C.W_GLUE / 2), Y(C.Y_BODY + C.H_BODY / 2),
      "GLUE", "s", 7, MUTED, "c")
    for xx, lab in ((C.X_BACK + C.W_FACE / 2, "BACK"),
                    (C.X_SIDL + C.W_SIDE / 2, "SIDE L"),
                    (C.X_FRNT + C.W_FACE / 2, "FRONT"),
                    (C.X_SIDR + C.W_SIDE / 2, "SIDE R")):
        t(c, X(xx), Y(C.Y_BODY + C.H_BODY / 2), lab, "s", 8, MUTED, "c")
    t(c, X(C.X_FRNT + C.W_FACE / 2), Y(C.Y_TOP + C.H_CLOSE / 2) - 1,
      "TOP CLOSURE", "s", 7, MUTED, "c")
    t(c, X(C.X_FRNT + C.W_FACE / 2), Y(C.Y_TOP + C.H_CLOSE + 5.0),
      "tuck lip", "b", 6.6, MUTED, "c")
    t(c, X(C.X_FRNT + C.W_FACE / 2), Y(C.H_LIP + C.H_CLOSE / 2) - 1,
      "BOTTOM CLOSURE", "s", 7, MUTED, "c")
    t(c, X(C.X_FRNT + C.W_FACE / 2), Y(5.0), "tuck lip", "b", 6.6, MUTED,
      "c")
    for sxx in (C.X_SIDL, C.X_SIDR):
        t(c, X(sxx + C.W_SIDE / 2), Y(C.Y_TOP + 6.0), "dust", "b", 6.2,
          MUTED, "c")
        t(c, X(sxx + C.W_SIDE / 2), Y(C.Y_BODY - 9.0), "dust", "b", 6.2,
          MUTED, "c")
    # legend
    ly = 9.0
    c.setStrokeColor(MAG)
    c.setLineWidth(0.8)
    c.line(12 * MM, (ly + 1) * MM, 22 * MM, (ly + 1) * MM)
    t(c, 24, ly, "CUT", "s", 7, MAG)
    c.saveState()
    c.setStrokeColor(CYANC)
    c.setDash([3 * MM, 1.8 * MM], 0)
    c.line(36 * MM, (ly + 1) * MM, 46 * MM, (ly + 1) * MM)
    c.restoreState()
    t(c, 48, ly, "CREASE", "s", 7, CYANC)
    t(c, 70, ly, "Lip corners R5, 1 mm shoulders. Glue flap tapers 3 mm. "
      "No crease at the tab base, so the peg hole cannot tear the tab off.",
      "b", 6.8, MUTED)
    B.ORIGIN = C.BLEED


def p_map(c):
    page_frame(c, 4, "Artwork on the die - panel map",
               "Page 1 of the print file with the die laid over it, 1:1. "
               "The artwork carries 3 mm bleed past every cut.")
    ox, oy = 24.0, 22.0
    pg = pymupdf.open(PRINT)[0]
    px = pg.get_pixmap(dpi=200)
    im = Image.frombytes("RGB", (px.width, px.height), px.samples)
    place_img(c, im, ox - C.BLEED, oy - C.BLEED, C.SHEET_W + 2 * C.BLEED,
              C.SHEET_H + 2 * C.BLEED)
    B.ORIGIN = 0.0
    c.saveState()
    c.translate(ox * MM, oy * MM)
    C.draw_die(c, cut=MAG, crease=Color(1, 1, 1), lw=0.7, dash=(2.4, 1.6))
    c.restoreState()
    B.ORIGIN = C.BLEED
    labels = ((C.X_GLUE + C.W_GLUE / 2, "GLUE"),
              (C.X_BACK + C.W_FACE / 2, "BACK"),
              (C.X_SIDL + C.W_SIDE / 2, "SIDE L"),
              (C.X_FRNT + C.W_FACE / 2, "FRONT"),
              (C.X_SIDR + C.W_SIDE / 2, "SIDE R"))
    for xx, lab in labels:
        t(c, ox + xx, oy + C.SHEET_H + 4.5, lab, "s", 8, NAVY, "c")
    t(c, 12, 9.0, "Glue flap is left unprinted and unvarnished. Tuck lips "
      "and dust flaps are flat ink; they are hidden once closed.", "b", 7.4,
      MUTED)


def p_fold(c):
    page_frame(c, 5, "Folding and filling instructions",
               "Eight steps from flat blank to hanging pack. Blank shown "
               "printed side DOWN in steps 1-3.")
    cols, cw, chh = 4, 66.0, 82.0
    x0, ytop = 12.0, 186.0
    W, H, D = C.W_FACE, C.H_BODY, C.W_SIDE

    def cell(i):
        col, row = i % cols, i // cols
        cx = x0 + col * (cw + 3.0)
        cy = ytop - (row + 1) * (chh + 4.0)
        c.setFillColor(Color(0.965, 0.972, 0.985))
        c.roundRect(cx * MM, cy * MM, cw * MM, chh * MM, 2 * MM, fill=1,
                    stroke=0)
        c.setFillColor(NAVY)
        c.circle((cx + 5.5) * MM, (cy + chh - 5.5) * MM, 3.4 * MM, fill=1,
                 stroke=0)
        t(c, cx + 5.5, cy + chh - 6.9, str(i + 1), "k", 9, Color(1, 1, 1),
          "c")
        return cx, cy

    def caption(cx, cy, head, lines):
        t(c, cx + 11.0, cy + chh - 6.9, head, "s", 8.6, NAVY)
        yy = cy + 12.0
        for ln in lines:
            t(c, cx + 3.5, yy, ln, "b", 7.0, INK)
            yy -= 3.6

    # 1 pre-crease
    cx, cy = cell(0)
    s = 0.25
    blank2d(c, cx + (cw - C.SHEET_W * s) / 2, cy + 20.0, s)
    caption(cx, cy, "Pre-break the creases", (
        "Lay the blank printed side down.",
        "Fold every crease 180° and back",
        "so the board folds cleanly."))

    # 2 glue
    cx, cy = cell(1)
    m = blank2d(c, cx + (cw - C.SHEET_W * s) / 2, cy + 20.0, s, glue=True)
    gx, gy = m((C.X_GLUE + C.W_GLUE / 2, C.Y_BODY + C.H_BODY / 2))
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.1)
    c.circle(gx * MM, gy * MM, 6 * MM, fill=0, stroke=1)
    caption(cx, cy, "Glue the side seam", (
        "Apply glue to the narrow glue",
        "flap (yellow), on its unprinted",
        "face, 2-3 mm in from each edge."))

    # 3 fold over
    cx, cy = cell(2)
    ox_ = cx + (cw - C.SHEET_W * s) / 2
    m = blank2d(c, ox_, cy + 20.0, s, highlight=C.X_FRNT)
    a = m((C.X_SIDR + C.W_SIDE / 2, C.Y_TOP + 2))
    b = m((C.X_BACK + 8.0, C.Y_TOP + 2))
    c.saveState()
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.3)
    p = c.beginPath()
    p.moveTo(a[0] * MM, a[1] * MM)
    p.curveTo(a[0] * MM, (a[1] + 22) * MM, b[0] * MM, (b[1] + 22) * MM,
              b[0] * MM, (b[1] + 3) * MM)
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()
    arrowhead(c, b[0], b[1] + 2.4, -math.pi / 2, 2.4, ACCENT)
    caption(cx, cy, "Fold and press", (
        "Fold on the red crease so the",
        "right side panel lands on the glue",
        "flap. Press flat and let it set."))

    # 4 open the sleeve
    cx, cy = cell(3)
    s3 = 0.30
    ox3, oy3 = cx + 18.0, cy + 21.0
    draw3(c, box_polys(top=(0, 0, 0), bot=(0, 0, 0)), ox3, oy3, s3)
    caption(cx, cy, "Open the sleeve", (
        "Squeeze the folded edges so the",
        "glued sleeve opens square.",
        "All flaps still stand open."))

    # 5 close the bottom
    cx, cy = cell(4)
    draw3(c, box_polys(top=(0, 0, 0), bot=(55, 40, 90)), cx + 18.0,
          cy + 25.0, s3)
    arc_arrow(c, [(W / 2, -C.H_CLOSE * math.cos(a_) - 2,
                   C.H_CLOSE * math.sin(a_) - 6)
                  for a_ in np.linspace(math.radians(25), math.radians(85),
                                        10)],
              cx + 18.0, cy + 25.0, s3)
    caption(cx, cy, "Close the bottom", (
        "Fold both bottom dust flaps in,",
        "then the bottom closure. Tuck the",
        "lip in behind the back panel."))

    # 6 load
    cx, cy = cell(5)
    ox6, oy6 = cx + 18.0, cy + 21.0
    polys = box_polys(top=(0, 0, 15), bot=(90, 90, 90))
    draw3(c, polys, ox6, oy6, s3)
    blocks = block3(W * 0.30, H + 34.0, 1.5) + block3(W * 0.70, H + 52.0,
                                                       1.5)
    draw3(c, blocks, ox6, oy6, s3)
    arc_arrow(c, [(W * 0.5, H + 70.0 - k * 30, D / 2) for k in
                  np.linspace(0, 1, 6)], ox6, oy6, s3)
    caption(cx, cy, "Load four blocks", (
        "Stand the four 50 g blocks on",
        "edge, two by two, wrappers on.",
        "Pack holds 4 × 50 g = 200 g."))

    # 7 close the top
    cx, cy = cell(6)
    ox7, oy7 = cx + 18.0, cy + 19.0
    draw3(c, box_polys(top=(62, 70, 90), bot=(90, 90, 90)), ox7, oy7, s3)
    arc_arrow(c, [(W / 2, H + C.H_CLOSE * math.cos(a_) + 3,
                   C.H_CLOSE * math.sin(a_) - 6)
                  for a_ in np.linspace(math.radians(10), math.radians(70),
                                        10)], ox7, oy7, s3)
    caption(cx, cy, "Close the top", (
        "Fold the top dust flaps in, then",
        "the top closure. Tuck the lip in",
        "behind the back panel and tab."))

    # 8 done, on the peg
    cx, cy = cell(7)
    ox8, oy8 = cx + 18.0, cy + 19.0
    draw3(c, box_polys(top=(90, 90, 90), bot=(90, 90, 90)), ox8, oy8, s3)
    # the peg, through the slot
    sx, sy = to_page((W / 2, H + C.SLOT_Y, D), ox8, oy8, s3)
    ex, ey = to_page((W / 2, H + C.SLOT_Y, D + 60.0), ox8, oy8, s3)
    c.saveState()
    c.setStrokeColor(Color(0.55, 0.58, 0.64))
    c.setLineWidth(2.2)
    c.setLineCap(1)
    c.line(sx * MM, sy * MM, ex * MM, ey * MM)
    c.restoreState()
    hx, hy = to_page((W / 2, H + C.SLOT_Y, D), ox8, oy8, s3)
    c.setFillColor(Color(0.3, 0.33, 0.4))
    c.circle(hx * MM, hy * MM, 0.9 * MM, fill=1, stroke=0)
    caption(cx, cy, "Hang or stand", (
        "Finished: 95 × 95 × 20 mm.",
        "Hang from the euro slot on a",
        "peg, or stand it on a shelf."))
    t(c, 12, 8.5, "Diagram colours: blue = printed outside, cream = "
      "unprinted inside of the board, yellow = glue, red = the fold or "
      "move in that step.", "b", 7.4, MUTED)


def p_spec(c, results):
    page_frame(c, 6, "Specification and pre-press checks",
               "For the printer / converter. Everything below was measured "
               "from the build, not estimated.")
    rows = (
        ("Product", "Swift Blue-Drop flush-activated WC cleaner, 4 × 50 g "
                    "blocks, net 200 g"),
        ("Carton style", "Straight tuck end (STE); both tucks hinge from the "
                         "front; euro hang tab on the back"),
        ("Finished size", "95 W × 95 H × 20 D mm (outside). Back panel with "
                          "tab 95 × 115 mm"),
        ("Flat blank", "%.0f × %.0f mm; artwork page %.0f × %.0f mm "
                       "including 3 mm bleed" % (C.SHEET_W, C.SHEET_H,
                                                 C.SHEET_W + 6,
                                                 C.SHEET_H + 6)),
        ("Flaps", "Closures 20 mm + 13 mm tuck lip (R5 corners), dust flaps "
                  "15 mm, glue flap 13 mm"),
        ("Hang tab", "60 × 20 mm, 6 mm shoulder chamfers, euro slot Ø6 mm "
                     "eye + 4 mm riser, %.1f mm board above the slot"
                     % C.TAB_HEADROOM),
        ("Scent vents", "3 droplet cut-outs per side panel, 4.4 mm tall, "
                        "8 mm below the top crease"),
        ("Board", "Recommended 300-350 g/m² folding boxboard (GC1/GC2), "
                  "white reverse"),
        ("Colour", "CMYK process. Vector type and graphics in CMYK; the "
                   "water photograph is an RGB image at 305 dpi - convert "
                   "with the printer's own CMYK profile"),
        ("Fonts", "Outfit and Plus Jakarta Sans (SIL Open Font Licence), "
                  "embedded"),
        ("Print file", os.path.basename(PRINT) + " - p1 artwork, p2 die "
                       "(spot colours CutContour / Crease), in register"),
    )
    y = 182.0
    for k, v in rows:
        t(c, 14, y, k, "s", 8.4, NAVY)
        t(c, 52, y, v, "b", 8.0, INK)
        y -= 6.4
    y -= 2.0
    c.setStrokeColor(RULE)
    c.line(14 * MM, (y + 3) * MM, 285 * MM, (y + 3) * MM)
    t(c, 14, y - 2, "Pre-press checks (from the build)", "h", 10.5, NAVY)
    y -= 9.0
    for k, v, ok in results:
        c.setFillColor(Color(0.1, 0.6, 0.3) if ok else ACCENT)
        c.circle(16 * MM, (y + 1.1) * MM, 1.5 * MM, fill=1, stroke=0)
        t(c, 19.5, y, k, "s", 8.0, INK)
        t(c, 90, y, v, "b", 8.0, INK)
        y -= 5.6
    y -= 2.0
    t(c, 14, y - 2, "Notes", "h", 10.5, NAVY)
    y -= 9.0
    notes = (
        "Dimensions are the finished outside sizes supplied. The converter "
        "should apply its usual board-caliper allowance when cutting the "
        "die.",
        "The hang tab is single ply. Its reverse is bare board and shows "
        "from the front above the carton; it can be printed navy as a "
        "second-side job if wanted.",
        "Claim wording: front seal reads ONE BLOCK · 300 FLUSHES; back copy "
        "reads 'Each block lasts up to 300 flushes'. Confirm against "
        "product testing before plates.",
        "Contact details are unchanged: 0739 446 655 · "
        "info@vistexchemicals.co.ke · P.O. Box 218 – 00606, Industrial "
        "Area, Nairobi.",
    )
    for n in notes:
        for ln in B.wrap(n, FT["b"], 8.0, 268.0):
            t(c, 14, y, ln, "b", 8.0, INK)
            y -= 4.0
        y -= 1.4


def checks():
    """Re-run the print build's guard and package the answers."""
    C.ELEMS[:] = []
    B.OVERFLOW[:] = []
    # measure a fresh build, written aside so an open copy of the print
    # file (locked by a PDF viewer on Windows) does not block the guide
    import tempfile
    C.build_print(os.path.join(tempfile.gettempdir(), "bd95_check.pdf"))
    hits, safe, small, cont = C.check()
    smallest = min(C.xh_mm(e["font"], e["size"]) for e in C.ELEMS
                   if e["kind"] == "text")
    pg = pymupdf.open(PRINT)
    p0 = pg[0].rect
    size_ok = (abs(p0.width / MM - (C.SHEET_W + 6)) < 0.05 and
               abs(p0.height / MM - (C.SHEET_H + 6)) < 0.05)
    fonts = sorted({f[3] for f in pg[0].get_fonts()})
    emb = all(f[1] != "n/a" for f in pg[0].get_fonts())
    return [
        ("Overlapping elements", "%d found across %d registered elements "
         "(text, logos, seal, icons, QR, product, vents)"
         % (len(hits), len(C.ELEMS)), not hits),
        ("Safe area", "%d breaches (4 mm front/back, 3 mm sides/closures)"
         % len(safe), not safe),
        ("Type size", "smallest x-height %.2f mm, minimum 1.20 mm; "
         "%d strings under" % (smallest, len(small)), not small),
        ("Badge containment", "%d strings outside their seal/flag/pill"
         % len(cont), not cont),
        ("Page size", "%.1f × %.1f mm = blank + 2 × 3 mm bleed"
         % (p0.width / MM, p0.height / MM), size_ok),
        ("Fonts", "%d embedded subsets: %s" % (len(fonts), ", ".join(
            sorted({f.split("+")[-1] for f in fonts}))[:80]), emb),
        ("Hang tab", "%.1f mm board above slot (min 6)" % C.TAB_HEADROOM,
         C.TAB_HEADROOM >= 6.0),
        ("Tuck closure", "closure %.0f mm = carton depth %.0f mm, lip %.0f mm"
         % (C.H_CLOSE, C.W_SIDE, C.H_LIP), C.H_CLOSE == C.W_SIDE),
    ]


def main():
    C.register_fonts()
    results = checks()
    fc = faces()
    W, H = PAGE
    c = _canvas.Canvas(GUIDE, pagesize=(W * MM, H * MM),
                       initialFontName=FT["b"], initialFontSize=8)
    c.setTitle("Swift Blue-Drop 95 x 95 x 20 mm - views and folding guide")
    c.setAuthor("Vistex Chemicals Ltd")
    c.setCreator("packaging/swift_blue_drop_95_guide.py")
    for fn in (lambda: p_views(c, fc), lambda: p_ortho(c, fc),
               lambda: p_die(c), lambda: p_map(c), lambda: p_fold(c),
               lambda: p_spec(c, results)):
        fn()
        c.showPage()
    c.save()
    for k, v, ok in results:
        print("%-4s %-22s %s" % ("ok" if ok else "FAIL", k, v))
    print("wrote", os.path.relpath(GUIDE, C.ROOT),
          "(%.0f KB)" % (os.path.getsize(GUIDE) / 1024.0))
    return 0 if all(r[2] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
