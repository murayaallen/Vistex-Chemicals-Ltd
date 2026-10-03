"""Geometry and print-readiness checks on the generated hang-card PDFs."""
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


def magenta(drawings):
    out = []
    for dr in drawings:
        c = dr.get("color")
        if c and abs(c[0] - .902) < .06 and c[1] < .15 and abs(c[2] - .494) < .12:
            out.append(dr)
    return out


def run(pdf):
    name = pathlib.Path(pdf).name
    is_proof = "proof" in name
    is_front = "front" in name
    is_back = "back" in name
    d = pymupdf.open(pdf)
    pg = d[0]
    print(f"\n{name}")
    w, h = pg.rect.width * MM, pg.rect.height * MM
    wantw = M["PROOF_W"] if is_proof else M["PAGE_W"]
    wanth = M["PROOF_H"] if is_proof else M["PAGE_H"]
    print(f"  page {w:.2f} x {h:.2f} mm  (want {wantw:.2f} x {wanth:.2f})")
    chk(abs(w - wantw) < 0.4, f"page width {w:.2f}")
    chk(abs(h - wanth) < 0.4, f"page height {h:.2f}")

    # The front is nearly all artwork, the back nearly all copy, so each is
    # held to its own floor rather than one threshold that suits neither.
    min_paths, min_text = (60, 50) if is_front else (20, 800) if is_back else (150, 900)
    drawings = pg.get_drawings()
    chk(len(drawings) >= min_paths, f"vector paths only {len(drawings)} (want >= {min_paths})")
    chk(len(pg.get_images()) <= 1, f"{len(pg.get_images())} raster images (want <=1)")
    chk(len(pg.get_text().strip()) >= min_text,
        f"live text {len(pg.get_text().strip())} chars (want >= {min_text})")

    mg = magenta(drawings)
    if is_proof:
        # outline + hanger slot + hanger bump, on each of the two cards
        chk(len(mg) >= 6, f"dieline incomplete: {len(mg)} magenta paths (want >= 6)")
        xs = sorted(r["rect"].x0 * MM for r in mg)
        chk(min(xs) < M["PAGE_W"] and max(xs) > M["PAGE_W"], "dieline missing on one card")
    else:
        chk(not mg, f"artwork file carries {len(mg)} dieline marks")

    # Bleed: the card colour must continue past the trim on all four sides, so a
    # die-cut tolerance never reveals white board.
    if not is_proof:
        dpi = 100
        pix = pg.get_pixmap(dpi=dpi)
        p = lambda x, y: pix.pixel(min(pix.width - 1, int(x / 25.4 * dpi)),
                                   min(pix.height - 1, int(y / 25.4 * dpi)))
        B, G = M["BLEED"], 1.2
        mid_x, mid_y = M["PAGE_W"] / 2, M["PAGE_H"] / 2
        for label, out_pt, in_pt in [
                ("top", (mid_x, B - G), (mid_x, B + G)),
                ("bottom", (mid_x, M["PAGE_H"] - B + G), (mid_x, M["PAGE_H"] - B - G)),
                ("left", (B - G, mid_y), (B + G, mid_y)),
                ("right", (M["PAGE_W"] - B + G, mid_y), (M["PAGE_W"] - B - G, mid_y))]:
            a, b = p(*out_pt), p(*in_pt)
            chk(max(abs(x - y) for x, y in zip(a, b)) < 28,
                f"bleed {label}: outside {a} != inside {b}")

        # nothing may be trimmed off: no text in the bleed, none under the hanger
        die = M["die"]
        cx = M["BLEED"] + M["CARD_W"] / 2
        hang = pymupdf.Rect(cx - die["slot_w"] / 2, M["BLEED"] + die["bump_cy"] - die["bump_r"],
                            cx + die["slot_w"] / 2,
                            M["BLEED"] + die["slot_y"] + die["slot_h"] / 2)
        for b in pg.get_text("words"):
            tb = pymupdf.Rect(*[v * MM for v in b[:4]])
            if not b[4].strip():
                continue
            if (tb.x1 < B or tb.x0 > M["PAGE_W"] - B or
                    tb.y1 < B or tb.y0 > M["PAGE_H"] - B):
                chk(False, f"text in bleed: {b[4]!r}")
            i = tb & hang
            if i.is_valid and i.width > 0.4 and i.height > 0.4:
                chk(False, f"text under the hanger punch: {b[4]!r}")

        # type must clear the die edge by a safety margin, allowing for cutting
        # tolerance on a rounded corner
        SAFE = M["BLEED"] + 3.0
        for b in pg.get_text("words"):
            if not b[4].strip():
                continue
            tb = pymupdf.Rect(*[v * MM for v in b[:4]])
            chk(tb.x0 > SAFE - 0.6 and tb.x1 < M["PAGE_W"] - SAFE + 0.6 and
                tb.y0 > SAFE - 0.6 and tb.y1 < M["PAGE_H"] - SAFE + 0.6,
                f"text too close to the die edge: {b[4]!r}")

    # The stamped logo is positioned from meta.json, independently of the HTML.
    # Only the front carries it; the back's heading is live type in that area.
    for s in (M["swift_slots"] if (is_front or is_proof) else []):
        sl = pymupdf.Rect(M["BLEED"] + s["x"], M["BLEED"] + s["y"],
                          M["BLEED"] + s["x"] + s["w"], M["BLEED"] + s["y"] + s["h"])
        for b in pg.get_text("words"):
            if not b[4].strip():
                continue
            tb = pymupdf.Rect(*[v * MM for v in b[:4]])
            if tb in sl:
                continue          # the logo's own "Usafi Halisi"
            i = tb & sl
            if i.is_valid and i.width > 0.5 and i.height > 0.5:
                chk(False, f"Swift logo overlaps text {b[4]!r}")
    d.close()


for a in sys.argv[1:]:
    run(a)
print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
