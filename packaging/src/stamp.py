"""Stamp the supplied vector Swift logo onto the front card.

Chrome cannot keep the logo's gradients vector through an <img>, so the slot is
left empty in the HTML and the original vector PDF is placed here instead. The
front card sits at (BLEED, BLEED) in both the single page and the proof sheet,
so one offset serves both.
"""
import json, pathlib, sys
import pymupdf

HERE = pathlib.Path(__file__).parent
M = json.loads((HERE / "meta.json").read_text())
LOGO = pymupdf.open(r"D:\Projects\Vistex\Swift Logo.pdf")
MM = 72 / 25.4

src, dst = sys.argv[1], sys.argv[2]
doc = pymupdf.open(src)
page = doc[0]
lr = LOGO[0].rect
ar = lr.width / lr.height
n = 0
for s in M["swift_slots"]:
    w, h = s["w"], s["h"]
    if w / h > ar:
        w = h * ar
    else:
        h = w / ar
    x = M["BLEED"] + s["x"] + (s["w"] - w) / 2
    y = M["BLEED"] + s["y"] + (s["h"] - h) / 2
    page.show_pdf_page(pymupdf.Rect(x * MM, y * MM, (x + w) * MM, (y + h) * MM), LOGO, 0)
    n += 1

doc.set_metadata({
    "title": "Swift Toilet Blocks 4 x 50 g — euro-slot hang card",
    "author": "Vistex Chemicals Ltd",
    "subject": f"Hang card {M['CARD_W']:.0f} x {M['CARD_H']:.0f} mm + {M['BLEED']:.0f} mm bleed",
    "keywords": "packaging, dieline, hang card, Swift, Vistex Chemicals",
})
doc.save(dst, garbage=4, deflate=True)
print(f"  stamped {n} vector Swift logo -> {pathlib.Path(dst).name} "
      f"({pathlib.Path(dst).stat().st_size // 1024} KB)")
