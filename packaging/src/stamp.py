"""Stamp the supplied vector Swift logo into its reserved slots.

Chrome cannot keep the logo's gradients vector through an <img>, so the slots
are left empty in the HTML and the original vector PDF is placed here instead.
The result is a fully vector Swift mark at every size on the carton.
"""
import json, pathlib, sys
import pymupdf

HERE = pathlib.Path(__file__).parent
meta = json.loads((HERE / "meta.json").read_text())
LOGO = pymupdf.open(r"D:\Projects\Vistex\Swift Logo.pdf")
MM = 72 / 25.4

src, dst = sys.argv[1], sys.argv[2]
doc = pymupdf.open(src)
page = doc[0]
lr = LOGO[0].rect
ar = lr.width / lr.height

for s in meta["swift_slots"]:
    # fit inside the slot, centred, preserving aspect
    w, h = s["w"], s["h"]
    if w / h > ar:
        w = h * ar
    else:
        h = w / ar
    x = s["x"] + (s["w"] - w) / 2
    y = s["y"] + (s["h"] - h) / 2
    rect = pymupdf.Rect(x * MM, y * MM, (x + w) * MM, (y + h) * MM)
    page.show_pdf_page(rect, LOGO, 0)

doc.set_metadata({
    "title": "Swift Toilet Blocks 4 x 50 g — folding carton artwork",
    "author": "Vistex Chemicals Ltd",
    "subject": f"STE carton {meta['W']:.0f} x {meta['H']:.0f} x {meta['D']:.0f} mm, "
               f"flat {meta['FLAT_W']:.0f} x {meta['FLAT_H']:.0f} mm + {meta['BLEED']:.0f} mm bleed",
    "keywords": "packaging, dieline, Swift, Vistex Chemicals",
})
doc.save(dst, garbage=4, deflate=True)
print("stamped", len(meta["swift_slots"]), "vector Swift logos ->", pathlib.Path(dst).name,
      f"({pathlib.Path(dst).stat().st_size // 1024} KB)")
