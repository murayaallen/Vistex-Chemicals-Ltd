"""Geometry and print-readiness checks on the generated carton PDFs."""
import json, pathlib, sys
import pymupdf

HERE = pathlib.Path(__file__).parent
M = json.loads((HERE / "meta.json").read_text())
MM = 25.4 / 72
ok = fail = 0


def chk(cond, msg):
    global ok, fail
    if cond:
        ok += 1
    else:
        fail += 1
        print("  FAIL", msg)


def run(pdf):
    name = pathlib.Path(pdf).name
    is_proof = "proof" in name
    d = pymupdf.open(pdf)
    pg = d[0]
    print(f"\n{name}")
    want_h = M["PAGE_H_PROOF"] if is_proof else M["PAGE_H"]
    w, h = pg.rect.width * MM, pg.rect.height * MM
    print(f"  page {w:.2f} x {h:.2f} mm  (want {M['PAGE_W']:.2f} x {want_h:.2f})")
    chk(abs(w - M["PAGE_W"]) < 0.4, f"page width {w:.2f}")
    chk(abs(h - want_h) < 0.4, f"page height {h:.2f}")

    drawings = pg.get_drawings()
    chk(len(drawings) > 150, f"vector paths only {len(drawings)}")
    chk(len(pg.get_images()) <= 1, f"{len(pg.get_images())} raster images (want <=1)")
    chk(len(pg.get_text().strip()) > 1000, f"live text {len(pg.get_text().strip())} chars")

    mag = [dr for dr in drawings if (c := dr.get("color")) and
           abs(c[0] - .902) < .06 and c[1] < .15 and abs(c[2] - .494) < .12]
    if is_proof:
        chk(len(mag) >= 9, f"dieline incomplete: {len(mag)} magenta paths")
        best = max(mag, key=lambda r: r["rect"].width * r["rect"].height)["rect"]
        bw, bh = best.width * MM, best.height * MM
        bx, by = best.x0 * MM, best.y0 * MM
        print(f"  flat outline {bw:.2f} x {bh:.2f} mm at ({bx:.2f}, {by:.2f})")
        chk(abs(bw - M["FLAT_W"]) < 0.6, f"flat width {bw:.2f} want {M['FLAT_W']}")
        chk(abs(bh - M["H"]) < 0.6, f"body height {bh:.2f} want {M['H']}")
        chk(abs(bx - M["BLEED"]) < 0.6, f"flat x {bx:.2f} want {M['BLEED']}")
    else:
        chk(not mag, f"artwork file carries {len(mag)} dieline marks")

    # Bleed: each strip must carry its own panel's colour past the trim, so a
    # cutting tolerance never exposes white board.
    dpi = 100
    pix = pg.get_pixmap(dpi=dpi)
    p = lambda x, y: pix.pixel(min(pix.width - 1, int(x / 25.4 * dpi)),
                               min(pix.height - 1, int(y / 25.4 * dpi)))
    B, G = M["BLEED"], 1.2
    mid_y = M["PAGE_H"] / 2
    panels = [("front", 70 + M["W"] / 2), ("sideA", 18 + M["D"] / 2),
              ("sideB", 138 + M["D"] / 2), ("back", 190 + M["W"] / 2)]
    for label, cx in panels:
        for edge, out_y, in_y in (("top", B - G, B + G),
                                  ("bottom", M["PAGE_H"] - B + G, M["PAGE_H"] - B - G)):
            a, b = p(cx, out_y), p(cx, in_y)
            chk(max(abs(u - v) for u, v in zip(a, b)) < 28,
                f"bleed {label} {edge}: outside {a} != inside {b}")
    a, b = p(M["PAGE_W"] - B + G, mid_y), p(M["PAGE_W"] - B - G, mid_y)
    chk(max(abs(u - v) for u, v in zip(a, b)) < 28, f"bleed right: {a} != {b}")

    # no type in the bleed of the artwork area (the proof legend sits below it)
    for bk in pg.get_text("blocks"):
        x0, y0, x1, y1 = [v * MM for v in bk[:4]]
        if not bk[4].strip() or y0 > M["PAGE_H"]:
            continue
        if x1 < B or x0 > M["PAGE_W"] - B or y1 < B or y0 > M["PAGE_H"] - B:
            chk(False, f"text in bleed: {bk[4].strip()[:46]!r}")

    # The stamped logos are placed from meta.json, independently of the HTML,
    # so a slot can drift onto type without anything else noticing.
    for s in M["swift_slots"]:
        sl = pymupdf.Rect(s["x"], s["y"], s["x"] + s["w"], s["y"] + s["h"])
        for bk in pg.get_text("words"):
            if not bk[4].strip():
                continue
            tb = pymupdf.Rect(*[v * MM for v in bk[:4]])
            if tb in sl:
                continue          # the logo's own "Usafi Halisi"
            i = tb & sl
            if i.is_valid and i.width > 0.5 and i.height > 0.5:
                chk(False, f"Swift logo slot {s['id']!r} overlaps text {bk[4]!r}")
    d.close()


for a in sys.argv[1:]:
    run(a)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
