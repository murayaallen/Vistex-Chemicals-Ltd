"""Geometry and print-readiness checks on the generated carton PDF."""
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


def run(pdf, expect_die=True):
    global ok, fail
    d = pymupdf.open(pdf)
    pg = d[0]
    print(f"\n{pathlib.Path(pdf).name}")
    want_h = M["PAGE_H_PROOF"] if expect_die else M["PAGE_H"]
    w, h = pg.rect.width * MM, pg.rect.height * MM
    print(f"  page {w:.2f} x {h:.2f} mm  (want {M['PAGE_W']:.2f} x {want_h:.2f})")
    chk(abs(w - M["PAGE_W"]) < 0.35, f"page width {w:.2f}")
    chk(abs(h - want_h) < 0.35, f"page height {h:.2f}")

    drawings = pg.get_drawings()
    chk(len(drawings) > 120, f"vector paths only {len(drawings)}")
    chk(len(pg.get_images()) <= 1, f"{len(pg.get_images())} raster images (want <=1, the Vistex wordmark)")
    txt = pg.get_text()
    chk(len(txt.strip()) > 1200, "live text missing")

    if expect_die:
        best = None
        for dr in drawings:
            c = dr.get("color")
            if c and abs(c[0] - .902) < .06 and c[1] < .15 and abs(c[2] - .494) < .12:
                r = dr["rect"]
                if best is None or r.width * r.height > best.width * best.height:
                    best = r
        chk(best is not None, "no magenta cut line found")
        if best:
            bw, bh = best.width * MM, best.height * MM
            bx, by = best.x0 * MM, best.y0 * MM
            print(f"  flat outline {bw:.2f} x {bh:.2f} mm at ({bx:.2f}, {by:.2f})")
            chk(abs(bw - M["FLAT_W"]) < 0.6, f"flat width {bw:.2f} want {M['FLAT_W']}")
            chk(abs(bh - M["H"]) < 0.6, f"body height {bh:.2f} want {M['H']}")
            chk(abs(bx - M["BLEED"]) < 0.6, f"flat x {bx:.2f} want {M['BLEED']}")
    else:
        mag = [dr for dr in drawings if (c := dr.get("color")) and
               abs(c[0] - .902) < .06 and c[1] < .15 and abs(c[2] - .494) < .12]
        chk(not mag, f"artwork file still has {len(mag)} dieline marks")

    # Bleed must continue each panel's own colour past the trim, so a cutting
    # tolerance never exposes white. Compare just outside the trim against just
    # inside it, at the middle of several panels.
    dpi = 100
    pix = pg.get_pixmap(dpi=dpi)
    p = lambda xmm, ymm: pix.pixel(min(pix.width - 1, int(xmm / 25.4 * dpi)),
                                   min(pix.height - 1, int(ymm / 25.4 * dpi)))
    B, G = M["BLEED"], 1.2
    edges = [("top", M["W"] / 2 + 138, B - G, B + G, "v"),
             ("top-back", 50, B - G, B + G, "v"),
             ("bottom", M["W"] / 2 + 138, M["PAGE_H"] - B + G, M["PAGE_H"] - B - G, "v"),
             ("right", M["PAGE_W"] - B + G, 108, M["PAGE_W"] - B - G, "h")]
    for name, a, b1, b2, axis in edges:
        out = p(a, b1) if axis == "v" else p(b1, a)
        ins = p(a, b2) if axis == "v" else p(b2, a)
        chk(max(abs(x - y) for x, y in zip(out, ins)) < 26,
            f"bleed at {name}: outside {out} != inside {ins}")
    # The stamped Swift logos are placed from meta.json, independently of the
    # HTML, so a slot can drift onto type without anything else noticing.
    for s in M["swift_slots"]:
        sl = pymupdf.Rect(s["x"], s["y"], s["x"] + s["w"], s["y"] + s["h"])
        # word granularity: "blocks" merges the two logos' own captions across
        # panels into one box that belongs to neither slot
        for b in pg.get_text("words"):
            if not b[4].strip():
                continue
            tb = pymupdf.Rect(*[v * MM for v in b[:4]])
            # The logo carries its own live type ("Usafi Halisi"), which sits
            # wholly inside the slot; only type crossing the slot edge is a clash.
            if tb in sl:
                continue
            inter = tb & sl
            if inter.is_valid and inter.width > 0.5 and inter.height > 0.5:
                chk(False, f"Swift logo slot {s['id']!r} overlaps text {b[4].strip()[:34]!r}")

    # No text may sit in the bleed of the artwork area (the proof's legend band
    # lives below the page box and is excluded).
    for b in pg.get_text("blocks"):
        x0, y0, x1, y1 = [v * MM for v in b[:4]]
        if not b[4].strip() or y0 > M["PAGE_H"]:
            continue
        if (x1 < B or x0 > M["PAGE_W"] - B or y1 < B or y0 > M["PAGE_H"] - B):
            chk(False, f"text in bleed: {b[4].strip()[:46]!r}")
    d.close()


for a in sys.argv[1:]:
    run(a, expect_die="proof" in pathlib.Path(a).name)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
