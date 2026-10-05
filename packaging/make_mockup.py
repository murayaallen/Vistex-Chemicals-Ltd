#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fold the flat blank into a 3D carton mockup.

The dieline has always been a folding carton - glue tab, two side panels, tuck
ends - but a flat blank is hard to judge, so this lifts the printed faces off
the PDF and assembles them as the closed, glued box.

How it works
------------
Each face is cropped from the artwork at its true panel coordinates, then
warped into a quad computed from an actual 3D projection (yaw, then tilt, then
a mild perspective divide) rather than hand-placed corners - so the three faces
share one vanishing behaviour and the box does not look pasted together.

Per-face shading is applied because a real carton never shows three faces at
the same brightness: the front takes the key light, the side falls away, the
top catches most.

Run:  python packaging/make_mockup.py [concept.pdf ...]
"""

import glob
import math
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import pymupdf

from swift_blue_drop_dieline import (X_FRNT, X_SIDR, Y_BODY, Y_TOP, W_FACE,
                                     W_SIDE, H_BODY, H_TUCK, TUCK_TOP_X,
                                     TAB_X0, TAB_W, TAB_CH, H_HANG, SLOT_R, SLOT_W,
                                     SLOT_RISE, SLOT_Y,
                                     BLEED, MM, HERE, ROOT, DIST)

OUT = os.path.join(DIST, "mockups")

# view
# Negative yaw. With a positive one the face at x=+hw rotates AWAY from the
# camera, so the right-hand side panel was being drawn behind the box and all
# that showed was front and top.
YAW = math.radians(-27.0)
# Camera HEIGHT above the box centre, not a tilt angle. Rotating the camera
# about X sheared the verticals, so the face read as rotated in-plane. Raising
# the eye instead gives two-point perspective: verticals stay vertical, the
# horizontals converge, and the top shows because we are above it.
EYE_Y = 104.0                 # mm above box centre (box half-height is 77.5)
FOCAL = 5400.0                # longer lens; 1750 was wide-angle and
                              # stretched the near edge of the face
SCALE = 5.6                   # px per mm at the box centre
# Raising the eye puts the box far below the old fixed centre, so the frame is
# fitted to the projected geometry instead of being guessed.
OFFSET = [0.0, 0.0]
CANVAS = [1500, 1750]
PAD = 150

SHADE = {"front": 1.00, "side": 0.74, "top": 1.13, "tab": 0.93}


# ----------------------------------------------------------------------------

def face_image(pdf, x_mm, y_mm, w_mm, h_mm, dpi=300):
    """Crop one printed panel out of the artwork."""
    pg = pymupdf.open(pdf)[0]
    H = pg.rect.height
    r = pymupdf.Rect((x_mm + BLEED) * MM, H - (y_mm + h_mm + BLEED) * MM,
                     (x_mm + w_mm + BLEED) * MM, H - (y_mm + BLEED) * MM)
    px = pg.get_pixmap(dpi=dpi, clip=r)
    return Image.frombytes("RGB", (px.width, px.height), px.samples)


def tab_face(pdf):
    """The hang tab, with the euro slot punched out of its alpha so the peg
    hole reads as a hole rather than as a white shape."""
    im = face_image(pdf, TAB_X0, Y_TOP, TAB_W, H_HANG).convert("RGBA")
    sx, sy = im.width / TAB_W, im.height / H_HANG
    cx = im.width / 2.0
    # image rows run top-down; the slot is measured up from the tab base
    eye_y = (H_HANG - SLOT_Y) * sy
    top_y = (H_HANG - SLOT_Y - SLOT_RISE) * sy
    hole = Image.new("L", im.size, 255)
    hd_ = ImageDraw.Draw(hole)
    r, hw = SLOT_R * sx, SLOT_W / 2.0 * sx
    hd_.ellipse((cx - r, eye_y - r, cx + r, eye_y + r), fill=0)
    hd_.rectangle((cx - hw, top_y, cx + hw, eye_y), fill=0)
    hd_.ellipse((cx - hw, top_y - hw, cx + hw, top_y + hw), fill=0)
    # chamfered shoulders, so the mockup matches the die rather than showing
    # a plain rectangle
    ch = TAB_CH * sx
    hd_.polygon([(0, 0), (ch, 0), (0, im.height)], fill=0)
    hd_.polygon([(im.width, 0), (im.width - ch, 0),
                 (im.width, im.height)], fill=0)
    im.putalpha(ImageChops.darker(im.getchannel("A"), hole))
    return im


def project(p):
    """3D point (x, y, z) in mm -> 2D screen point in px."""
    x, y, z = p
    # yaw about the vertical axis
    xr = x * math.cos(YAW) + z * math.sin(YAW)
    zr = -x * math.sin(YAW) + z * math.cos(YAW)
    # +zr is TOWARD the camera, so divide by (FOCAL - zr). Adding instead drew
    # the back of the box larger than the front and flared the top out.
    k = FOCAL / (FOCAL - zr * SCALE)
    return (OFFSET[0] + xr * SCALE * k,
            OFFSET[1] - (y - EYE_Y) * SCALE * k)


def find_coeffs(dest, src):
    """PIL PERSPECTIVE coefficients mapping dest quad back to src quad."""
    m = []
    for (dx, dy), (sx, sy) in zip(dest, src):
        m.append([dx, dy, 1, 0, 0, 0, -sx * dx, -sx * dy])
        m.append([0, 0, 0, dx, dy, 1, -sy * dx, -sy * dy])
    A = np.array(m, dtype=float)
    B = np.array(src, dtype=float).reshape(8)
    return np.linalg.solve(A.T @ A, A.T @ B)


def warp(face, quad, canvas_size):
    """Warp a face image into a screen quad on a transparent canvas."""
    w, h = face.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    coeffs = find_coeffs(quad, src)
    rgba = face.convert("RGBA")
    out = rgba.transform(canvas_size, Image.PERSPECTIVE, coeffs,
                         Image.BICUBIC)
    # Keep only what falls inside the quad, but COMBINE with the alpha the
    # face already carries. Replacing it outright filled the punched euro slot
    # and the chamfered shoulders back in as black.
    mask = Image.new("L", canvas_size, 0)
    ImageDraw.Draw(mask).polygon(quad, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.6))
    out.putalpha(ImageChops.darker(out.getchannel("A"), mask))
    return out


def shade(im, k):
    if k == 1.0:
        return im
    r, g, b, a = im.split()
    f = lambda v: min(255, int(v * k))
    return Image.merge("RGBA", (r.point(f), g.point(f), b.point(f), a))


def fit_frame(corners):
    """Size the canvas to the box and centre it, before anything is drawn."""
    OFFSET[0], OFFSET[1] = 0.0, 0.0
    pts = [project(c) for c in corners]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    CANVAS[0] = int(max(xs) - min(xs)) + 2 * PAD
    CANVAS[1] = int(max(ys) - min(ys)) + 2 * PAD + 60
    OFFSET[0] = PAD - min(xs)
    OFFSET[1] = PAD - min(ys)


def build(pdf, out_png):
    W, H, D = W_FACE, H_BODY, W_SIDE
    hw, hh, hd = W / 2.0, H / 2.0, D / 2.0

    # corners, origin at the box centre, +z toward the viewer
    ftl, ftr = (-hw, hh, hd), (hw, hh, hd)
    fbl, fbr = (-hw, -hh, hd), (hw, -hh, hd)
    btr, bbr = (hw, hh, -hd), (hw, -hh, -hd)
    btl = (-hw, hh, -hd)
    fit_frame([ftl, ftr, fbl, fbr, btr, bbr, btl,
               (-TAB_W / 2.0, hh + H_HANG, -hd),
               (TAB_W / 2.0, hh + H_HANG, -hd)])
    canvas = (CANVAS[0], CANVAS[1])

    # the tab sits in the back plane and stands above the closed carton, so
    # it is laid in before the body and the box occludes its base
    htw = TAB_W / 2.0
    tab_quad = [project((-htw, hh + H_HANG, -hd)),
                project((htw, hh + H_HANG, -hd)),
                project((htw, hh, -hd)), project((-htw, hh, -hd))]

    faces = [
        ("tab", tab_face(pdf), tab_quad),
        ("side", face_image(pdf, X_SIDR, Y_BODY, W_SIDE, H_BODY),
         [project(ftr), project(btr), project(bbr), project(fbr)]),
        ("top", face_image(pdf, TUCK_TOP_X, Y_TOP, W_FACE, H_TUCK),
         [project(btl), project(btr), project(ftr), project(ftl)]),
        ("front", face_image(pdf, X_FRNT, Y_BODY, W_FACE, H_BODY),
         [project(ftl), project(ftr), project(fbr), project(fbl)]),
    ]

    # ground
    g = Image.new("RGB", canvas, (238, 242, 248))
    gd = ImageDraw.Draw(g)
    for i in range(canvas[1]):
        t = i / canvas[1]
        v = int(248 - 34 * t)
        gd.line([(0, i), (canvas[0], i)], fill=(v, v + 3, min(255, v + 10)))
    scene = g.convert("RGBA")

    # contact shadow on the ground
    sh = Image.new("RGBA", canvas, (0, 0, 0, 0))
    base = [project((-hw, -hh, hd)), project((hw, -hh, hd)),
            project((hw, -hh, -hd)), project((-hw, -hh, -hd))]
    ImageDraw.Draw(sh).polygon(base, fill=(26, 40, 78, 120))
    sh = sh.transform(canvas, Image.AFFINE, (1, 0, 10, 0, 1, 16))
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    scene = Image.alpha_composite(scene, sh)

    for name, im, quad in faces:
        lay = shade(warp(im, quad, canvas), SHADE[name])
        scene = Image.alpha_composite(scene, lay)

    # crisp the two visible folds so the box reads as folded board
    d = ImageDraw.Draw(scene)
    d.line([project(ftr), project(fbr)], fill=(255, 255, 255, 70), width=2)
    d.line([project(ftl), project(ftr)], fill=(255, 255, 255, 60), width=2)

    scene.convert("RGB").save(out_png)
    return out_png


def main():
    args = sys.argv[1:]
    if not args:
        # the PLAN builds sit on a larger sheet with a different origin, so
        # cropping faces out of them by panel coordinate gives nonsense
        args = [f for f in sorted(glob.glob(os.path.join(
            DIST, "integrated", "Concept_*.pdf")))
            if not f.endswith("_PLAN.pdf")]
    if not args:
        raise SystemExit("no concept PDFs found; run swift_blue_drop_v2.py")
    os.makedirs(OUT, exist_ok=True)
    for pdf in args:
        stem = os.path.splitext(os.path.basename(pdf))[0]
        p = build(pdf, os.path.join(OUT, stem + "_3D.png"))
        print("%-34s -> %s" % (stem, os.path.relpath(p, ROOT)))


if __name__ == "__main__":
    main()
