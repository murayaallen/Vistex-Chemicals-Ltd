#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export the water vector shapes as clean SVG files for the website.

Draws each shape to a tiny ReportLab PDF, then converts to SVG via PyMuPDF.
Output goes to ../images/vectors/ so the site can reference them directly.

Run:  python packaging/export_svg_assets.py
"""

import os
import sys

import pymupdf
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "images", "vectors")

sys.path.insert(0, HERE)

from swift_blue_drop_dieline import (
    droplet_gloss, water_swirl, BLUE_MID, CYAN_LT, WHITE
)
from illustration import wave_top

os.makedirs(OUT, exist_ok=True)


def make_pdf(w_mm, h_mm, draw_fn):
    """Draw to an in-memory PDF and return bytes."""
    import io
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(w_mm * mm, h_mm * mm))
    draw_fn(c, w_mm, h_mm)
    c.showPage()
    c.save()
    return buf.getvalue()


def pdf_to_svg(pdf_bytes, crop=None):
    """Convert first page of a PDF to SVG string via PyMuPDF."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    if crop:
        page.set_cropbox(pymupdf.Rect(*crop))
    svg = page.get_svg_image(matrix=pymupdf.Identity)
    doc.close()
    return svg


# ── 1. Droplet gloss (hero mark, semi-transparent dark ground) ───────────────

def draw_droplet(c, w, h):
    from reportlab.lib.colors import HexColor
    # transparent background
    cx, cy = w / 2, h / 2
    droplet_gloss(c, cx, cy, h * 0.88, light=True, alpha=1.0, shadow=False)


pdf = make_pdf(64, 80, draw_droplet)
svg = pdf_to_svg(pdf)
path = os.path.join(OUT, "droplet.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.relpath(path, ROOT))


# ── 2. Water swirl (vortex, flush cue) ──────────────────────────────────────

def draw_swirl(c, w, h):
    water_swirl(c, w / 2, h / 2, min(w, h) * 0.44, alpha=0.9)


pdf = make_pdf(80, 80, draw_swirl)
svg = pdf_to_svg(pdf)
path = os.path.join(OUT, "water-swirl.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.relpath(path, ROOT))


# ── 3. Wave divider (full-width stripe, 1200 × 60 mm) ───────────────────────

def draw_wave(c, w, h):
    wave_top(c, 0, h * 0.55, w, h * 0.28, CYAN_LT, alpha=0.18)
    wave_top(c, 0, h * 0.45, w, h * 0.22, WHITE, alpha=0.10)


pdf = make_pdf(1200, 60, draw_wave)
svg = pdf_to_svg(pdf)
path = os.path.join(OUT, "wave-divider.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.relpath(path, ROOT))


# ── 4. Droplet watermark (large, very light — for section backgrounds) ───────

def draw_watermark(c, w, h):
    droplet_gloss(c, w / 2, h / 2, h * 0.82, light=True, alpha=0.15, shadow=False)


pdf = make_pdf(200, 250, draw_watermark)
svg = pdf_to_svg(pdf)
path = os.path.join(OUT, "droplet-watermark.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.relpath(path, ROOT))


print("\ndone — %d files in images/vectors/" % 4)
