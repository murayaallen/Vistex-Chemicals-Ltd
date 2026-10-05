#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Every angle of the carton, and of the case, from one camera rig.

make_mockup renders a single hero three-quarter. A client approving a pack
needs to see the faces they have not been shown - the back, the far flank,
the top - because that is where the regulatory copy and the die features
live, and a pack only ever gets approved once.

Six views per subject, all from the same rig so they compare honestly:

    front 3/4 left   the hero
    front 3/4 right  the other flank
    front flat       no perspective, for checking proportion
    back 3/4         the panel carrying caution and the QR
    back flat        the same, square on
    top down         the closure and the hang tab

Output: dist/views/<subject>_<view>.png  plus a contact sheet per subject.

Run:  python packaging/make_views.py
"""

import math
import os

import pymupdf
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

import make_mockup as MK
import swift_shipper as SH
from swift_blue_drop_dieline import (MM, BLEED, DIST, ROOT, HERE, X_BACK,
                                     X_FRNT, X_SIDL, X_SIDR, Y_BODY, Y_TOP,
                                     W_FACE, W_SIDE, H_BODY, H_TUCK, H_HANG,
                                     TUCK_TOP_X, TAB_X0, TAB_W)

OUT = os.path.join(DIST, "views")
RETAIL = os.path.join(DIST, "integrated", "Concept_F_Vortex.pdf")
SHIPPER = os.path.join(DIST, "shipper",
                       "Swift_Blue-Drop_12ct_Shipper_PRINT.pdf")

PAD = 110

# yaw, eye height, label. Negative yaw shows the right-hand flank.
VIEWS = (("front-3q-left", -27.0, 104.0, "Front, three-quarter"),
         ("front-3q-right", 27.0, 104.0, "Front, opposite flank"),
         ("front-flat", -0.5, 82.0, "Front, square on"),
         ("back-3q", -27.0, 104.0, "Back, three-quarter"),
         ("back-flat", 0.5, 82.0, "Back, square on"),
         ("top-down", -24.0, 300.0, "From above"))


def face(pdf, x, y, w, h, origin=BLEED, dpi=300):
    pg = pymupdf.open(pdf)[0]
    H = pg.rect.height
    r = pymupdf.Rect((x + origin) * MM, H - (y + h + origin) * MM,
                     (x + w + origin) * MM, H - (y + origin) * MM)
    px = pg.get_pixmap(dpi=dpi, clip=r)
    return Image.frombytes("RGB", (px.width, px.height), px.samples)


def render(faces, W, H, D, yaw, eye, tab=None, scale=5.4, focal=5400.0):
    MK.YAW = math.radians(yaw)
    MK.EYE_Y = eye
    MK.SCALE = scale
    MK.FOCAL = focal
    hw, hh, hd = W / 2.0, H / 2.0, D / 2.0

    def c3(sx, sy, sz):
        return (sx * hw, sy, sz * hd)

    ftl, ftr = c3(-1, H, 1), c3(1, H, 1)
    fbl, fbr = c3(-1, 0, 1), c3(1, 0, 1)
    btr, bbr = c3(1, H, -1), c3(1, 0, -1)
    btl, bbl = c3(-1, H, -1), c3(-1, 0, -1)

    pts = [ftl, ftr, fbl, fbr, btr, bbr, btl, bbl]
    if tab is not None:
        htw = tab[1] / 2.0
        pts += [(-htw, H + tab[2], -hd), (htw, H + tab[2], -hd)]
    MK.OFFSET[0], MK.OFFSET[1] = 0.0, 0.0
    pp = [MK.project(q) for q in pts]
    xs, ys = [q[0] for q in pp], [q[1] for q in pp]
    cw = int(max(xs) - min(xs)) + 2 * PAD
    ch = int(max(ys) - min(ys)) + 2 * PAD
    MK.CANVAS[0], MK.CANVAS[1] = cw, ch
    MK.OFFSET[0] = PAD - min(xs)
    MK.OFFSET[1] = PAD - min(ys)
    canvas = (cw, ch)

    g = Image.new("RGB", canvas, (240, 244, 250))
    gd = ImageDraw.Draw(g)
    for i in range(ch):
        t = i / float(ch)
        v = int(250 - 28 * t)
        gd.line([(0, i), (cw, i)], fill=(v, v + 2, min(255, v + 8)))
    scene = g.convert("RGBA")

    sh = Image.new("RGBA", canvas, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon(
        [MK.project(fbl), MK.project(fbr), MK.project(bbr),
         MK.project(bbl)], fill=(24, 38, 76, 118))
    sh = sh.transform(canvas, Image.AFFINE, (1, 0, 11, 0, 1, 16))
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    scene = Image.alpha_composite(scene, sh)

    if tab is not None:
        htw = tab[1] / 2.0
        quad = [MK.project((-htw, H + tab[2], -hd)),
                MK.project((htw, H + tab[2], -hd)),
                MK.project((htw, H, -hd)), MK.project((-htw, H, -hd))]
        lay = MK.shade(MK.warp(tab[0], quad, canvas), 0.93)
        scene = Image.alpha_composite(scene, lay)

    right = MK.YAW < 0
    flank = ("side_r", [MK.project(ftr), MK.project(btr), MK.project(bbr),
                        MK.project(fbr)]) if right else \
            ("side_l", [MK.project(btl), MK.project(ftl), MK.project(fbl),
                        MK.project(bbl)])
    order = ((flank[0], flank[1], 0.74),
             ("top", [MK.project(btl), MK.project(btr), MK.project(ftr),
                      MK.project(ftl)], 1.13),
             ("front", [MK.project(ftl), MK.project(ftr), MK.project(fbr),
                        MK.project(fbl)], 1.0))
    for name, quad, sh_ in order:
        im = faces.get(name)
        if im is None:
            continue
        lay = MK.shade(MK.warp(im, quad, canvas), sh_)
        scene = Image.alpha_composite(scene, lay)
    return scene.convert("RGB")


def contact(images, labels, path, cols=3):
    try:
        fnt = ImageFont.truetype(os.path.join(HERE, "fonts", "Outfit-700.ttf"),
                                 30)
    except Exception:
        fnt = None
    th = 760
    sized = []
    for im in images:
        c = im.copy()
        c.thumbnail((th, th))
        sized.append(c)
    W = max(i.width for i in sized)
    H = max(i.height for i in sized)
    rows = (len(sized) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (W + 26) + 26, rows * (H + 56) + 26),
                      (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, (im, lab) in enumerate(zip(sized, labels)):
        cx = 26 + (i % cols) * (W + 26) + (W - im.width) // 2
        cy = 50 + (i // cols) * (H + 56)
        sheet.paste(im, (cx, cy))
        d.text((26 + (i % cols) * (W + 26), cy - 34), lab,
               fill=(15, 20, 45), font=fnt)
    sheet.save(path)
    return path


def subject(name, pdf, geom, faces_front, faces_back, tab=None):
    os.makedirs(OUT, exist_ok=True)
    W, H, D = geom
    made, labels = [], []
    for key, yaw, eye, label in VIEWS:
        f = faces_back if key.startswith("back") else faces_front
        t = tab if key in ("front-3q-left", "front-3q-right",
                           "top-down") else None
        im = render(f, W, H, D, yaw, eye, tab=t)
        p = os.path.join(OUT, "%s_%s.png" % (name, key))
        im.save(p)
        made.append(im)
        labels.append(label)
        print("  %-18s %s" % (key, os.path.basename(p)))
    contact(made, labels, os.path.join(OUT, "%s_ALL_VIEWS.png" % name))
    return made


def main():
    for f in (RETAIL, SHIPPER):
        if not os.path.exists(f):
            raise SystemExit("missing " + f)
    os.makedirs(OUT, exist_ok=True)

    print("retail carton")
    front = {
        "front": face(RETAIL, X_FRNT, Y_BODY, W_FACE, H_BODY),
        "side_r": face(RETAIL, X_SIDR, Y_BODY, W_SIDE, H_BODY),
        "side_l": face(RETAIL, X_SIDL, Y_BODY, W_SIDE, H_BODY),
        "top": face(RETAIL, TUCK_TOP_X, Y_TOP, W_FACE, H_TUCK),
    }
    back = dict(front)
    back["front"] = face(RETAIL, X_BACK, Y_BODY, W_FACE, H_BODY)
    tab_im = MK.tab_face(RETAIL)
    subject("Carton", RETAIL, (W_FACE, H_BODY, W_SIDE), front, back,
            tab=(tab_im, TAB_W, H_HANG))

    print("shipper")
    sfront = {
        "front": face(SHIPPER, SH.X_FRONT, SH.Y_BODY, SH.CASE_L, SH.CASE_H),
        "side_r": face(SHIPPER, SH.X_SIDE1, SH.Y_BODY, SH.CASE_W, SH.CASE_H),
        "side_l": face(SHIPPER, SH.X_SIDE2, SH.Y_BODY, SH.CASE_W, SH.CASE_H),
        "top": face(SHIPPER, SH.X_FRONT, SH.Y_TOP, SH.CASE_L, SH.FLAP),
    }
    sback = dict(sfront)
    sback["front"] = face(SHIPPER, SH.X_BACK, SH.Y_BODY, SH.CASE_L, SH.CASE_H)
    subject("Shipper", SHIPPER, (SH.CASE_L, SH.CASE_H, SH.CASE_W),
            sfront, sback)

    print("")
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
