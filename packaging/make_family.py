#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Family shot: the 12-count shipper beside the retail cartons it holds.

Reuses the projection and face-warping from make_mockup so the case and the
cartons share one camera - rendering them separately and pasting them
together is what makes a line-up look assembled rather than photographed.

Run:  python packaging/make_family.py
"""

import math
import os

import pymupdf
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import make_mockup as MK
import swift_shipper as SH
from swift_blue_drop_dieline import (MM, BLEED, DIST, ROOT, X_FRNT, X_SIDR,
                                     Y_BODY, Y_TOP, W_FACE, W_SIDE, H_BODY,
                                     H_TUCK, TUCK_TOP_X)

OUT = os.path.join(DIST, "family")

RETAIL_PDF = os.path.join(DIST, "integrated", "Concept_F_Vortex.pdf")
SHIPPER_PDF = os.path.join(DIST, "shipper",
                           "Swift_Blue-Drop_12ct_Shipper_PRINT.pdf")

CANVAS = [2400, 1500]
PAD = 120


def face(pdf, x_mm, y_mm, w_mm, h_mm, origin=BLEED, dpi=260):
    pg = pymupdf.open(pdf)[0]
    H = pg.rect.height
    r = pymupdf.Rect((x_mm + origin) * MM, H - (y_mm + h_mm + origin) * MM,
                     (x_mm + w_mm + origin) * MM, H - (y_mm + origin) * MM)
    px = pg.get_pixmap(dpi=dpi, clip=r)
    return Image.frombytes("RGB", (px.width, px.height), px.samples)


def corners(origin, W, H, D):
    ox, oz = origin
    hw, hd = W / 2.0, D / 2.0
    out = []
    for sx in (-1, 1):
        for sy in (0, H):
            for sz in (-1, 1):
                out.append((ox + sx * hw, sy, oz + sz * hd))
    return out


def box(scene, origin, faces, W, H, D, scale, shade):
    """Draw one box. origin is the ground-plane centre in mm, x to the right
    and z toward the camera, so two boxes can share one camera."""
    ox, oz = origin
    hw, hd = W / 2.0, D / 2.0

    def pr(px, py, pz):
        return MK.project((px + ox, py - MK.EYE_Y + MK.EYE_Y, pz + oz))

    # corners, y measured from the ground up
    def c3(sx, sy, sz):
        return (ox + sx * hw, sy, oz + sz * hd)

    ftl, ftr = c3(-1, H, 1), c3(1, H, 1)
    fbl, fbr = c3(-1, 0, 1), c3(1, 0, 1)
    btr, bbr = c3(1, H, -1), c3(1, 0, -1)
    btl = c3(-1, H, -1)

    quads = (("side", faces["side"],
              [MK.project(ftr), MK.project(btr), MK.project(bbr),
               MK.project(fbr)]),
             ("top", faces["top"],
              [MK.project(btl), MK.project(btr), MK.project(ftr),
               MK.project(ftl)]),
             ("front", faces["front"],
              [MK.project(ftl), MK.project(ftr), MK.project(fbr),
               MK.project(fbl)]))

    # contact shadow
    sh = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon(
        [MK.project(fbl), MK.project(fbr), MK.project(bbr),
         MK.project(c3(-1, 0, -1))], fill=(22, 36, 72, 115))
    sh = sh.transform(scene.size, Image.AFFINE, (1, 0, 12, 0, 1, 18))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    scene = Image.alpha_composite(scene, sh)

    for name, im, quad in quads:
        lay = MK.shade(MK.warp(im, quad, scene.size), shade[name])
        scene = Image.alpha_composite(scene, lay)
    return scene


def main():
    for p in (RETAIL_PDF, SHIPPER_PDF):
        if not os.path.exists(p):
            raise SystemExit("missing " + p)
    os.makedirs(OUT, exist_ok=True)

    # one camera for the whole line-up
    MK.SCALE = 2.7
    MK.FOCAL = 9000.0
    # above the case, not level with it, or no top face shows
    MK.EYE_Y = 255.0

    ship = {
        "front": face(SHIPPER_PDF, SH.X_FRONT, SH.Y_BODY, SH.CASE_L,
                      SH.CASE_H),
        "side": face(SHIPPER_PDF, SH.X_SIDE1, SH.Y_BODY, SH.CASE_W,
                     SH.CASE_H),
        "top": face(SHIPPER_PDF, SH.X_FRONT, SH.Y_TOP, SH.CASE_L, SH.FLAP),
    }
    retail = {
        "front": face(RETAIL_PDF, X_FRNT, Y_BODY, W_FACE, H_BODY),
        "side": face(RETAIL_PDF, X_SIDR, Y_BODY, W_SIDE, H_BODY),
        "top": face(RETAIL_PDF, TUCK_TOP_X, Y_TOP, W_FACE, H_TUCK),
    }

    # Fit the camera to the whole line-up before drawing anything. Guessing
    # an offset put the boxes below the canvas; the single-box mockup already
    # learned this and does the same fit.
    # the case sits back and left so its right flank stays visible past the
    # retail cartons standing in front of it
    layout = (((-170.0, -110.0), SH.CASE_L, SH.CASE_H, SH.CASE_W),
              ((150.0, 70.0), W_FACE, H_BODY, W_SIDE),
              ((262.0, 30.0), W_FACE, H_BODY, W_SIDE))
    MK.OFFSET[0], MK.OFFSET[1] = 0.0, 0.0
    pts = []
    for origin, W_, H_, D_ in layout:
        pts += [MK.project(cc) for cc in corners(origin, W_, H_, D_)]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    CANVAS[0] = int(max(xs) - min(xs)) + 2 * PAD
    CANVAS[1] = int(max(ys) - min(ys)) + 2 * PAD
    MK.CANVAS[0], MK.CANVAS[1] = CANVAS
    MK.OFFSET[0] = PAD - min(xs)
    MK.OFFSET[1] = PAD - min(ys)

    g = Image.new("RGB", tuple(CANVAS), (240, 244, 250))
    gd = ImageDraw.Draw(g)
    for i in range(CANVAS[1]):
        t = i / CANVAS[1]
        v = int(250 - 30 * t)
        gd.line([(0, i), (CANVAS[0], i)], fill=(v, v + 2, min(255, v + 8)))
    scene = g.convert("RGBA")

    shade_case = {"front": 0.96, "side": 0.70, "top": 1.10}
    shade_unit = {"front": 1.00, "side": 0.74, "top": 1.13}

    # back to front, so nearer boxes overlap further ones correctly
    scene = box(scene, layout[0][0], ship, SH.CASE_L, SH.CASE_H,
                SH.CASE_W, MK.SCALE, shade_case)
    for origin, W_, H_, D_ in layout[1:]:
        scene = box(scene, origin, retail, W_, H_, D_, MK.SCALE, shade_unit)

    out = os.path.join(OUT, "Swift_Blue-Drop_Family.png")
    scene.convert("RGB").save(out)
    print("wrote", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
