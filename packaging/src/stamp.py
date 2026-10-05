"""Stamp the supplied vector Swift logo into its reserved slots.

Chrome cannot keep the logo's gradients vector through an <img>, so the slots
are left empty in the HTML and the original vector PDF is placed here instead.
Slot coordinates in meta.json are absolute on the flat (they already include
the bleed), so nothing is added to them.
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
ar = LOGO[0].rect.width / LOGO[0].rect.height
for s in M["swift_slots"]:
    w, h = s["w"], s["h"]
    if w / h > ar:
        w = h * ar
    else:
        h = w / ar
    x = s["x"] + (s["w"] - w) / 2
    y = s["y"] + (s["h"] - h) / 2
    page.show_pdf_page(pymupdf.Rect(x * MM, y * MM, (x + w) * MM, (y + h) * MM), LOGO, 0)

doc.set_metadata({
    "title": "Swift Toilet Blocks 4 x 50 g — folding carton artwork",
    "author": "Vistex Chemicals Ltd",
    "subject": f"STE carton {M['W']:.0f} x {M['H']:.0f} x {M['D']:.0f} mm, "
               f"flat {M['FLAT_W']:.0f} x {M['FLAT_H']:.0f} mm + {M['BLEED']:.0f} mm bleed",
    "keywords": "packaging, dieline, carton, Swift, Vistex Chemicals",
})
doc.save(dst, garbage=4, deflate=True)
print(f"  stamped {len(M['swift_slots'])} vector Swift logos -> {pathlib.Path(dst).name} "
      f"({pathlib.Path(dst).stat().st_size // 1024} KB)")
