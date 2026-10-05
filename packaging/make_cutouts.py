#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turn the supplied reference photographs into cut-out RGBA assets the carton
artwork can composite over a dark ground.

Everything supplied was shot on white. Dropping white out needs two different
transforms depending on what the subject is, and using the wrong one is why
naive background removal ruins water:

  unmultiply  - for opaque, saturated subjects (the flower). Treats the pixel
                as the subject composited over white and solves back for the
                subject colour, which keeps soft edges and the real hue.

  luminance   - for water. A splash on white carries its information as
                darker-than-white refraction. Over a dark pack that same water
                should read as bright highlights, so the detail (255 - luma)
                becomes the alpha and the colour is painted light. Unmultiply
                here would turn every bright droplet black.

Run:  python packaging/make_cutouts.py
"""

import os

from PIL import Image, ImageFilter, ImageChops

try:                      # the supplied .avif needs a plugin
    import pillow_avif    # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "art")

# light cyan and white, the two ends of the water tint
WATER_LO = (150, 205, 240)
WATER_HI = (255, 255, 255)


def _load(name):
    return Image.open(os.path.join(ROOT, name)).convert("RGB")


def unmultiply_white(im, thresh=248, feather=0.6):
    """Opaque subject shot on white -> RGBA with the white solved out."""
    r, g, b = im.split()
    mn = ImageChops.lighter(ImageChops.lighter(r, g), b)      # max channel
    mn = ImageChops.darker(ImageChops.darker(r, g), b)        # min channel
    px = im.load()
    w, h = im.size
    out = Image.new("RGBA", (w, h))
    op = out.load()
    mp = mn.load()
    for y in range(h):
        for x in range(w):
            m = mp[x, y]
            if m >= thresh:
                op[x, y] = (0, 0, 0, 0)
                continue
            a = 1.0 - m / 255.0
            pr, pg, pb = px[x, y]
            base = 255.0 * (1.0 - a)
            cr = int(max(0, min(255, (pr - base) / a)))
            cg = int(max(0, min(255, (pg - base) / a)))
            cb = int(max(0, min(255, (pb - base) / a)))
            op[x, y] = (cr, cg, cb, int(a * 255))
    if feather:
        alpha = out.getchannel("A").filter(ImageFilter.GaussianBlur(feather))
        out.putalpha(alpha)
    return out


def water_from_white(im, gain=2.05, floor=10, feather=0.4):
    """Water shot on white -> luminous RGBA for compositing over a dark pack."""
    g = im.convert("L")
    w, h = im.size
    out = Image.new("RGBA", (w, h))
    op = out.load()
    gp = g.load()
    for y in range(h):
        for x in range(w):
            d = 255 - gp[x, y]              # how far from white
            a = int(min(255, d * gain))
            if a <= floor:
                op[x, y] = (0, 0, 0, 0)
                continue
            # denser water reads whiter, thin refraction reads cyan
            t = min(1.0, d / 90.0)
            cr = int(WATER_LO[0] + (WATER_HI[0] - WATER_LO[0]) * t)
            cg = int(WATER_LO[1] + (WATER_HI[1] - WATER_LO[1]) * t)
            cb = int(WATER_LO[2] + (WATER_HI[2] - WATER_LO[2]) * t)
            op[x, y] = (cr, cg, cb, a)
    if feather:
        out.putalpha(out.getchannel("A").filter(ImageFilter.GaussianBlur(feather)))
    return out


def trim(im, pad=2):
    """Crop to the non-transparent bounds so placement is predictable."""
    bb = im.getchannel("A").point(lambda v: 255 if v > 4 else 0).getbbox()
    if not bb:
        return im
    x0, y0, x1, y1 = bb
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
    return im.crop((x0, y0, x1, y1))


def upscale(im, factor):
    """Lanczos upscale. The supplied files are small; this buys print dpi at
    the cost of softness, which water tolerates far better than type does."""
    if factor <= 1:
        return im
    return im.resize((int(im.width * factor), int(im.height * factor)),
                     Image.LANCZOS)




# ----------------------------------------------------------------------------
# Product discs, lifted from the client card
# ----------------------------------------------------------------------------
# The blister on the client artwork is real product photography, so the four
# blocks come from there rather than being redrawn. Each disc is isolated with
# a feathered circular mask and upscaled 2x.
#
# RESOLUTION WARNING: at source each disc is ~190 px, which is about 160 dpi at
# 30 mm on the pack. Fine for concepts, NOT fine for press. A 300 dpi shot of
# the real product on white has to replace these before plates are cut.

CARD = "WhatsApp Image 2026-10-02 at 17.09.19.jpeg"
DISCS = ((253, 508, 97), (511, 503, 97), (256, 768, 94), (516, 763, 94))


def disc_cutouts():
    path = os.path.join(ROOT, CARD)
    if not os.path.exists(path):
        print("skip discs (card not found)")
        return
    card = Image.open(path).convert("RGB")
    for i, (cx, cy, r) in enumerate(DISCS, 1):
        box = (cx - r, cy - r, cx + r, cy + r)
        sub = card.crop(box).convert("RGBA")
        n = sub.width
        mask = Image.new("L", (n * 4, n * 4), 0)
        from PIL import ImageDraw
        ImageDraw.Draw(mask).ellipse((6, 6, n * 4 - 6, n * 4 - 6), fill=255)
        mask = mask.resize((n, n), Image.LANCZOS)
        mask = mask.filter(ImageFilter.GaussianBlur(0.8))
        sub.putalpha(mask)
        sub = upscale(sub, 2.0)
        dst = os.path.join(OUT, "disc-%d.png" % i)
        sub.save(dst)
        print("%-14s disc-%d        %sx%s" % (CARD[:14], i, sub.width, sub.height))


def disc_master(source="disc-1", inset=0.055):
    """One block, cleaned, to be cloned at four rotations.

    Four different photographs of four different blocks read as four different
    products. A real pack shows one product four times, so the best capture is
    promoted to a master and the variety comes from rotation instead.

    disc-1 is the pick: the most even ribbing and the least blister-rim
    contamination. 2 and 4 carry a bright rim arc, 3 a dark patch.
    """
    from PIL import ImageDraw, ImageEnhance
    src_path = os.path.join(OUT, source + ".png")
    if not os.path.exists(src_path):
        print("skip master (no %s)" % source)
        return
    im = Image.open(src_path).convert("RGBA")
    n = im.width

    # tighten the circular mask to crop any blister rim caught at the edge
    pad = int(n * inset)
    mask = Image.new("L", (n * 4, n * 4), 0)
    ImageDraw.Draw(mask).ellipse((pad * 4, pad * 4, (n - pad) * 4,
                                  (n - pad) * 4), fill=255)
    mask = mask.resize((n, n), Image.LANCZOS)
    mask = mask.filter(ImageFilter.GaussianBlur(1.0))
    im.putalpha(ImageChops.darker(im.getchannel("A"), mask))
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 6 else 0)
                 .getbbox())

    rgb = im.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(1.10)
    rgb = ImageEnhance.Color(rgb).enhance(1.14)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=3))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))

    dst = os.path.join(OUT, "disc-master.png")
    out.save(dst)
    print("%-14s disc-master   %sx%s  (from %s)" %
          ("", out.width, out.height, source))


def recycle_icons():
    """Three recycle marks on one white sheet: solid, outline, two-tone.
    Cut each so the pack can use whichever suits its ground."""
    src_name = "recycle.avif"
    if not os.path.exists(os.path.join(ROOT, src_name)):
        print("skip recycle (not found)")
        return
    im = _load(src_name)
    w, h = im.size
    boxes = (("recycle-solid", 0.03, 0.40),
             ("recycle-outline", 0.34, 0.66),
             ("recycle-duo", 0.62, 0.99))
    for name, x0, x1 in boxes:
        sub = im.crop((int(w * x0), 0, int(w * x1), h))
        cut = trim(unmultiply_white(sub, thresh=244, feather=0.5))
        cut = upscale(cut, 2.4)
        cut.save(os.path.join(OUT, name + ".png"))
        print("%-14s %-13s %sx%s" % (src_name[:14], name, cut.width, cut.height))


def bokeh_ground():
    """fresh blue.avif is a soft bokeh field, not a splash. It is a ground."""
    src = "fresh blue.avif"
    if not os.path.exists(os.path.join(ROOT, src)):
        return
    im = _load(src)
    im = upscale(im.convert("RGBA"), 2.2).convert("RGB")
    im.save(os.path.join(OUT, "bokeh.png"))
    print("%-14s bokeh         %sx%s" % (src[:14], im.width, im.height))


JOBS = (
    ("flower.jpg",        "flower",       unmultiply_white, 3.0),
    ("fresh.jpg",         "splash-arc",   water_from_white, 2.0),
    ("images.jfif",       "splash-ring",  water_from_white, 2.4),
)


def main():
    os.makedirs(OUT, exist_ok=True)
    for src, stem, fn, scale in JOBS:
        path = os.path.join(ROOT, src)
        if not os.path.exists(path):
            print("skip (missing)", src)
            continue
        im = _load(src)
        cut = trim(fn(im))
        cut = upscale(cut, scale)
        dst = os.path.join(OUT, stem + ".png")
        cut.save(dst)
        print("%-14s %-13s %sx%s  ->  %sx%s" %
              (src[:14], stem, im.width, im.height, cut.width, cut.height))
    disc_cutouts()
    disc_master()
    recycle_icons()
    bokeh_ground()
    print("")
    print("wrote to", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
