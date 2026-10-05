#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Composite the supplied photographs into ONE integrated scene per concept.

The previous pass cut each asset out and laid it on a flat ground, which read
as pasted layers. This builds a single blended image instead, so the water,
the depth field, the flower and the product belong to the same photograph.

Two things do the heavy lifting:

  invert + screen   A splash shot on white is pure white plus darker-than-white
                    refraction. Invert it and the white becomes black; screened
                    over a dark scene, black contributes nothing and the
                    refraction glows. No alpha channel, so no cut-out edge at
                    all - this is why the water now sits IN the scene.

  water last        The splashes are screened AFTER the blocks are placed, so
                    water crosses in front of the product. That single ordering
                    choice is most of what sells it as one image rather than a
                    stack.

Output: packaging/art/scene-<key>.png at 300 dpi, panel sized.

Run:  python packaging/make_scene.py
"""

import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageEnhance, ImageOps

try:
    import pillow_avif    # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ART = os.path.join(HERE, "art")

DPI = 300.0
PX = DPI / 25.4                      # pixels per mm

# the front panel, plus 1 mm of overlap on each edge so no seam can show
PANEL_W, PANEL_H = 107.0, 157.0
W, H = int(PANEL_W * PX), int(PANEL_H * PX)

NAVY = (1, 28, 86)
NAVY_DEEP = (1, 16, 54)
BLUE = (0, 86, 170)
CYAN = (86, 190, 240)


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def art(name):
    return Image.open(os.path.join(ART, name + ".png"))


def src(name):
    return Image.open(os.path.join(ROOT, name))


def vgradient(size, stops):
    """stops = [(pos 0..1 from TOP, (r,g,b)), ...]"""
    w, h = size
    g = Image.new("RGB", (1, h))
    px = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        lo = stops[0]
        hi = stops[-1]
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                lo, hi = stops[i], stops[i + 1]
                break
        span = max(1e-6, hi[0] - lo[0])
        k = (t - lo[0]) / span
        px[0, y] = tuple(int(lo[1][c] + (hi[1][c] - lo[1][c]) * k) for c in range(3))
    return g.resize((w, h), Image.BILINEAR)


def cover(im, size):
    """Scale to cover the target box, centre-cropped."""
    tw, th = size
    s = max(tw / im.width, th / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))),
                   Image.LANCZOS)
    x = (im.width - tw) // 2
    y = (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))


def place(canvas_size, layer, cx_mm, cy_mm, w_mm, rotate=0, flip=False):
    """Put a layer on a black canvas of canvas_size at a mm position."""
    if flip:
        layer = ImageOps.mirror(layer)
    tw = int(w_mm * PX)
    th = max(1, int(tw * layer.height / layer.width))
    layer = layer.resize((tw, th), Image.LANCZOS)
    if rotate:
        layer = layer.rotate(rotate, expand=True, resample=Image.BICUBIC)
    base = Image.new("RGB", canvas_size, (0, 0, 0))
    base.paste(layer, (int(cx_mm * PX - layer.width / 2),
                       int(cy_mm * PX - layer.height / 2)))
    return base


def screen_in(scene, layer_black_bg, opacity=1.0):
    """Screen a black-background layer onto the scene."""
    if opacity < 1.0:
        layer_black_bg = layer_black_bg.point(lambda v: int(v * opacity))
    return ImageChops.screen(scene, layer_black_bg)


# The invert+screen path MUST read the original white-background photographs.
# Feeding it the RGBA cut-outs makes their transparent area black, inverting
# that to white, and screening white blows the whole frame out - which is
# exactly what the first attempt did.
WATER_SRC = {"arc": "fresh.jpg", "ring": "images.jfif"}


# Inverting a blue-grey splash yields ORANGE, and screening orange light over
# the pack tinted both the water and the blocks warm. Neutralise the inverted
# layer to luminance first, then tint it cool, so screening can only add
# white-to-cyan light.
WATER_TINT = (0.78, 0.92, 1.00)


def water_layer(key, cx, cy, w_mm, rotate=0, flip=False):
    """Load a splash from source, invert so white becomes black, position it."""
    im = src(WATER_SRC[key]).convert("RGB")
    lum = ImageOps.invert(im).convert("L")
    im = Image.merge("RGB", tuple(
        lum.point(lambda v, k=k: int(v * k)) for k in WATER_TINT))
    return place((W, H), im, cx, cy, w_mm, rotate, flip)


def pool(scene, cx, cy, rx, ry, colour=(120, 195, 240), strength=0.40):
    """A soft light pool so the dark blocks separate from a dark ground."""
    m = soft_mask(scene.size, cx * PX, cy * PX, rx * PX, ry * PX, rx * PX * 0.42)
    tint = Image.new("RGB", scene.size, colour)
    return Image.composite(Image.blend(scene, tint, strength), scene, m)


def soft_mask(size, cx, cy, rx, ry, blur):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur))


def paste_rgba(scene, name, cx_mm, cy_mm, w_mm, opacity=1.0, shadow=0.0,
               rotate=0):
    """Alpha-composite an asset, optionally with a soft drop shadow beneath."""
    im = art(name).convert("RGBA")
    tw = int(w_mm * PX)
    th = max(1, int(tw * im.height / im.width))
    im = im.resize((tw, th), Image.LANCZOS)
    if rotate:
        im = im.rotate(rotate, expand=True, resample=Image.BICUBIC)
    x, y = int(cx_mm * PX - im.width / 2), int(cy_mm * PX - im.height / 2)

    if shadow > 0:
        sh = Image.new("RGBA", scene.size, (0, 0, 0, 0))
        blob = Image.new("RGBA", im.size, (0, 6, 24, 0))
        blob.putalpha(im.getchannel("A").point(lambda v: int(v * shadow)))
        sh.paste(blob, (x + int(1.2 * PX), y + int(2.0 * PX)), blob)
        sh = sh.filter(ImageFilter.GaussianBlur(5.0 * PX / 10))
        scene = Image.alpha_composite(scene.convert("RGBA"), sh)

    lay = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    if opacity < 1.0:
        im.putalpha(im.getchannel("A").point(lambda v: int(v * opacity)))
    lay.paste(im, (x, y), im)
    return Image.alpha_composite(scene.convert("RGBA"), lay).convert("RGB")


def vignette(scene, strength=0.42):
    w, h = scene.size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse((-int(w * 0.18), -int(h * 0.12),
                               int(w * 1.18), int(h * 1.12)), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(w * 0.09))
    dark = Image.new("RGB", (w, h), NAVY_DEEP)
    return Image.composite(scene, Image.blend(scene, dark, strength), m)


def bloom(scene, amount=0.30, thresh=170):
    g = scene.convert("L").point(lambda v: v if v > thresh else 0)
    glow = Image.merge("RGB", (g, g, g)).filter(
        ImageFilter.GaussianBlur(W * 0.018))
    return ImageChops.screen(scene, glow.point(lambda v: int(v * amount)))


def grade(scene, sat=1.06, contrast=1.05, blue=1.03):
    scene = ImageEnhance.Color(scene).enhance(sat)
    scene = ImageEnhance.Contrast(scene).enhance(contrast)
    r, g, b = scene.split()
    b = b.point(lambda v: min(255, int(v * blue)))
    return Image.merge("RGB", (r, g, b))


# One master block, cloned. Four different captures read as four different
# products; the variety has to come from rotation, not from a different photo
# in every well. Angles are deliberately not multiples of 90 so the ribbing
# never lines up and reveals the clone.
DISC_ANGLES = (0, 97, 203, 288)


def discs_into(scene, cx, cy, w, spread=0.56, lift=0.46):
    dx, dy = w * spread, w * lift
    spots = ((-dx, -dy, 0.94), (dx, -dy, 0.94), (-dx, dy, 1.0), (dx, dy, 1.0))
    for (ox, oy, sc), ang in zip(spots, DISC_ANGLES):
        scene = paste_rgba(scene, "disc-master", cx + ox, cy + oy, w * sc,
                           shadow=0.55, rotate=ang)
    return scene


# ----------------------------------------------------------------------------
# the three integrated scenes
# ----------------------------------------------------------------------------

def _base(stops, bokeh_alpha=0.22):
    s = vgradient((W, H), stops)
    bk = cover(src("fresh blue.avif").convert("RGB"), (W, H))
    return Image.blend(s, bk, bokeh_alpha)


def scene_immersion():
    """Water wraps the product from both sides; depth from the bokeh field.

    The three water passes are keyed to the product rather than scattered:
    a crown centred on it, a spray above, and one arc crossing its base in
    front. That reads as a single splash instead of three photographs."""
    s = _base([(0.0, CYAN), (0.26, BLUE), (0.66, NAVY), (1.0, NAVY_DEEP)], 0.20)
    s = screen_in(s, water_layer("ring", 53.5, 82.0, 126.0), 0.44)
    s = screen_in(s, water_layer("arc", 62.0, 56.0, 92.0, flip=True), 0.26)
    s = pool(s, 53.5, 82.0, 41.0, 33.0, strength=0.22)
    s = discs_into(s, 53.5, 82.0, 29.0)
    s = screen_in(s, water_layer("arc", 48.0, 106.0, 124.0), 0.62)
    s = paste_rgba(s, "flower", 95.0, 146.0, 32.0, opacity=0.22)
    return grade(vignette(s, 0.34))


def scene_cascade():
    """Water falls from the masthead; the product sits in the pool it makes."""
    s = _base([(0.0, (120, 205, 242)), (0.30, CYAN), (0.62, BLUE),
               (1.0, NAVY)], 0.24)
    s = screen_in(s, water_layer("arc", 52.0, 44.0, 128.0, rotate=186), 0.34)
    s = screen_in(s, water_layer("ring", 53.5, 84.0, 116.0), 0.36)
    s = pool(s, 53.5, 82.0, 40.0, 32.0, strength=0.20)
    s = discs_into(s, 53.5, 82.0, 29.0)
    s = screen_in(s, water_layer("arc", 50.0, 108.0, 128.0), 0.64)
    s = paste_rgba(s, "flower", 13.0, 146.0, 30.0, opacity=0.22)
    return grade(vignette(s, 0.28), sat=1.08)


def scene_vortex():
    """The ring splash becomes a whirlpool the blocks are dropping into."""
    s = _base([(0.0, BLUE), (0.34, (0, 62, 140)), (0.72, NAVY),
               (1.0, NAVY_DEEP)], 0.18)
    s = screen_in(s, water_layer("ring", 53.5, 82.0, 144.0), 0.56)
    s = screen_in(s, water_layer("ring", 53.5, 82.0, 96.0, rotate=140), 0.34)
    s = pool(s, 53.5, 82.0, 42.0, 34.0, strength=0.24)
    s = discs_into(s, 53.5, 82.0, 29.0, spread=0.58, lift=0.44)
    s = screen_in(s, water_layer("arc", 54.0, 106.0, 132.0), 0.58)
    s = paste_rgba(s, "flower", 16.0, 148.0, 32.0, opacity=0.24)
    return grade(vignette(s, 0.40), sat=1.06, contrast=1.06)


SCENES = (("immersion", scene_immersion),
          ("cascade", scene_cascade),
          ("vortex", scene_vortex))


def main():
    os.makedirs(ART, exist_ok=True)
    need = ("disc-1", "disc-2", "disc-3", "disc-4", "flower",
            "splash-arc", "splash-ring")
    missing = [n for n in need if not os.path.exists(os.path.join(ART, n + ".png"))]
    if missing:
        raise SystemExit("missing art: %s\nrun: python packaging/make_cutouts.py"
                         % ", ".join(missing))

    for key, fn in SCENES:
        im = fn()
        p = os.path.join(ART, "scene-%s.png" % key)
        im.save(p)
        print("scene-%-10s %sx%s px  (%.0f x %.0f mm @ %d dpi)  %.1f MB" %
              (key, im.width, im.height, PANEL_W, PANEL_H, DPI,
               os.path.getsize(p) / 1048576.0))


if __name__ == "__main__":
    main()
