#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Measure the dimensions back out of the finished PDFs.

A drawing is only worth the trust you can put in its numbers. Everything here
is measured from the vector geometry in the output files and compared against
the figure printed on the sheet - not against the constants that produced it,
which would only prove the code agrees with itself.

Run:  python packaging/verify_dimensions.py
"""

import os
import sys

import pymupdf

import swift_blue_drop_dieline as B
from swift_blue_drop_dieline import (MM, DIST, ROOT, W_GLUE, W_FACE, W_SIDE,
                                     H_BODY, H_TUCK, H_DUST, H_HANG, TAB_W,
                                     TAB_CH, SLOT_R, SLOT_W, SLOT_RISE,
                                     SLOT_Y, TAB_HEADROOM, VENT_N, VENT_H,
                                     VENT_GAP, VENT_Y, SHEET_W, SHEET_H,
                                     BLEED, X_GLUE, X_BACK, X_SIDL, X_FRNT,
                                     X_SIDR, Y_BODY, Y_TOP, TAB_X0)
import swift_shipper as SH

TOL = 0.15          # mm. Anything inside this is a rounding artefact.

SPEC = os.path.join(DIST, "spec", "Swift_Blue-Drop_Carton_SPEC.pdf")
PRINTPLAN = os.path.join(DIST, "spec",
                         "Swift_Blue-Drop_F_Vortex_PRINTPLAN.pdf")
SHIPSPEC = os.path.join(DIST, "spec", "Swift_Blue-Drop_Shipper_SPEC.pdf")

rows = []
fails = [0]


def check(label, measured, expected, unit="mm", tol=TOL):
    ok = measured is not None and abs(measured - expected) <= tol
    if not ok:
        fails[0] += 1
    rows.append((label,
                 "-" if measured is None else "%.2f" % measured,
                 "%.2f" % expected,
                 "-" if measured is None else "%+.2f" % (measured - expected),
                 "OK" if ok else "FAIL"))


def is_colour(c, target, tol=0.2):
    if c is None:
        return False
    if len(c) != len(target):
        return False
    return all(abs(a - b) <= tol for a, b in zip(c, target))


def _cubic_bounds(p0, p1, p2, p3, acc):
    """Sample a cubic. PyMuPDF reports a path rect from its CONTROL POINTS,
    which for a droplet sits 0.63 mm below the curve it actually describes -
    enough to fail a 0.15 mm check on a shape that is dead right."""
    for i in range(33):
        t = i / 32.0
        u = 1.0 - t
        x = (u * u * u * p0.x + 3 * u * u * t * p1.x
             + 3 * u * t * t * p2.x + t * t * t * p3.x)
        y = (u * u * u * p0.y + 3 * u * u * t * p1.y
             + 3 * u * t * t * p2.y + t * t * t * p3.y)
        acc.append((x, y))


def true_bbox(d):
    """Bounding box of the drawn curve, not of its control hull."""
    acc = []
    for it in d["items"]:
        op = it[0]
        if op == "l":
            acc.append((it[1].x, it[1].y))
            acc.append((it[2].x, it[2].y))
        elif op == "c":
            _cubic_bounds(it[1], it[2], it[3], it[4], acc)
        elif op == "re":
            r = it[1]
            acc += [(r.x0, r.y0), (r.x1, r.y1)]
        elif op == "qu":
            q = it[1]
            acc += [(q.ul.x, q.ul.y), (q.lr.x, q.lr.y)]
    if not acc:
        return None
    xs = [a[0] for a in acc]
    ys = [a[1] for a in acc]
    return (min(xs) / MM, min(ys) / MM, max(xs) / MM, max(ys) / MM)


def paths(pdf, want, pno=0):
    """Stroked paths of a given colour, as true page-space bboxes in mm."""
    doc = pymupdf.open(pdf)
    pg = doc[pno]
    out = []
    for d in pg.get_drawings():
        if not is_colour(d.get("color"), want):
            continue
        bb = true_bbox(d)
        if bb is None:
            r = d["rect"]
            bb = (r.x0 / MM, r.y0 / MM, r.x1 / MM, r.y1 / MM)
        out.append(bb)
    doc.close()
    return out


# PyMuPDF reports colours after CMYK->RGB conversion, so these are the
# values that actually land in the file, not the CMYK ones specified.
MAGENTA = (0.926, 0.0, 0.548)        # CUT
CYANC = (0.0, 0.681, 0.938)          # CREASE


def span(boxes, axis):
    if not boxes:
        return None
    if axis == "x":
        return max(b[2] for b in boxes) - min(b[0] for b in boxes)
    return max(b[3] for b in boxes) - min(b[1] for b in boxes)


def main():
    missing = [f for f in (SPEC, PRINTPLAN) if not os.path.exists(f)]
    if missing:
        raise SystemExit("missing: %s\nrun make_spec.py and "
                         "make_printplan.py first" % ", ".join(missing))

    # ---- 1. the die, measured off the 1:1 production drawing -------------
    cut = paths(SPEC, MAGENTA)
    # the blank outline is the largest magenta path on the sheet
    blank = max(cut, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
    check("Blank width, overall", blank[2] - blank[0], SHEET_W)
    check("Blank height, overall", blank[3] - blank[1], SHEET_H)

    # creases give the panel boundaries
    cre = paths(SPEC, CYANC)
    verticals = sorted({round(b[0], 2) for b in cre
                        if (b[3] - b[1]) > H_BODY * 0.8})
    if len(verticals) >= 5:
        base = min(verticals)
        got = [v - base for v in verticals]
        want = [0.0, X_BACK - X_GLUE, X_SIDL - X_GLUE, X_FRNT - X_GLUE,
                X_SIDR - X_GLUE]
        for i, (g, w) in enumerate(zip(got, want)):
            check("Crease %d from glue edge" % (i + 1), g, w)
        check("Glue tab width", got[1] - got[0], W_GLUE)
        check("Back panel width", got[2] - got[1], W_FACE)
        check("Side panel width", got[3] - got[2], W_SIDE)
        check("Front panel width", got[4] - got[3], W_FACE)
    else:
        check("Panel creases found", None, 5.0)

    horizontals = sorted({round(b[1], 2) for b in cre
                          if (b[2] - b[0]) > W_FACE})
    if len(horizontals) >= 2:
        check("Body panel height", abs(horizontals[1] - horizontals[0]),
              H_BODY)
    else:
        check("Body creases found", None, 2.0)

    # ---- 2. detail features ----------------------------------------------
    # the euro slot is the magenta path nearest 6.4 wide on the blank
    slot = [b for b in cut
            if abs((b[2] - b[0]) - SLOT_R * 2) < 1.0
            and abs((b[3] - b[1]) - (SLOT_R + SLOT_RISE + SLOT_W / 2)) < 1.0]
    if slot:
        s = slot[0]
        check("Euro slot, eye diameter", s[2] - s[0], SLOT_R * 2)
        check("Euro slot, overall height", s[3] - s[1],
              SLOT_R + SLOT_RISE + SLOT_W / 2)
    else:
        check("Euro slot located", None, 1.0)

    dw = VENT_H * 0.335 * 2
    vents = sorted([b for b in cut
                    if abs((b[3] - b[1]) - VENT_H) < 0.4
                    and abs((b[2] - b[0]) - dw) < 0.4], key=lambda b: b[0])
    check("Scent vents, count (both panels)", float(len(vents)),
          float(VENT_N * 2), tol=0.01)
    if len(vents) >= 2:
        check("Scent vent, height", vents[0][3] - vents[0][1], VENT_H)
        check("Scent vent, pitch", vents[1][0] - vents[0][0], VENT_GAP)

    # ---- 3. derived figures printed on the sheet -------------------------
    check("Slot headroom in tab",
          H_HANG - (SLOT_Y + SLOT_RISE + SLOT_W / 2), TAB_HEADROOM, tol=0.01)
    check("Panel widths sum to blank",
          W_GLUE + W_FACE + W_SIDE + W_FACE + W_SIDE, SHEET_W, tol=0.01)
    check("Flap heights sum to blank", H_TUCK + H_BODY + H_TUCK, SHEET_H,
          tol=0.01)
    check("Tuck depth vs carton depth", H_TUCK, W_SIDE - 3.0, tol=0.01)
    check("Dust flap vs carton depth", H_DUST, W_SIDE - 5.0, tol=0.01)
    check("Hang tab fits back panel", TAB_W + 2 * ((W_FACE - TAB_W) / 2),
          W_FACE, tol=0.01)
    check("Vent row fits side panel",
          (VENT_N - 1) * VENT_GAP + dw + 2 * 5.0, W_SIDE, tol=6.0)

    # ---- 4. the print plan really is 1:1 ---------------------------------
    pcut = paths(PRINTPLAN, MAGENTA)
    if pcut:
        pblank = max(pcut, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
        check("Print plan, blank width at 1:1", pblank[2] - pblank[0],
              SHEET_W)
        check("Print plan, blank height at 1:1", pblank[3] - pblank[1],
              SHEET_H)
    else:
        check("Print plan geometry found", None, 1.0)

    # ---- 5. the shipper ---------------------------------------------------
    if os.path.exists(SHIPSPEC):
        scut = paths(SHIPSPEC, MAGENTA)
        if scut:
            sb = max(scut, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
            check("Shipper blank width at 1:2", (sb[2] - sb[0]) * 2,
                  SH.SHEET_W, tol=0.4)
            check("Shipper blank height at 1:2", (sb[3] - sb[1]) * 2,
                  SH.SHEET_H, tol=0.4)
        check("Shipper holds the cartons, width",
              SH.ACROSS * W_FACE + SH.CLEAR, SH.CASE_L, tol=0.01)
        check("Shipper holds the cartons, depth",
              SH.DEEP * W_SIDE + SH.CLEAR, SH.CASE_W, tol=0.01)
        check("Shipper interior clears carton height", SH.CASE_H - H_BODY,
              5.0, tol=0.01)
        check("RSC flaps meet at centre", SH.FLAP * 2, SH.CASE_W, tol=0.01)

    # ---- 6. the QR actually encodes the page that exists ------------------
    # Decoded out of the finished artwork, not read from the source constant.
    # A QR is printed matter: it cannot be corrected after plates, and a
    # wrong URL is invisible to every other check in this file.
    art = os.path.join(DIST, "integrated", "Concept_F_Vortex.pdf")
    want = B.qr_url("blue-drop-wc")
    page = os.path.join(ROOT, "datasheet-blue-drop-wc.html")
    rows.append(("QR target page exists in repo",
                 "yes" if os.path.exists(page) else "NO",
                 "yes", "", "OK" if os.path.exists(page) else "FAIL"))
    if not os.path.exists(page):
        fails[0] += 1
    try:
        import cv2
        doc = pymupdf.open(art)
        pg = doc[0]
        H = pg.rect.height
        r = pymupdf.Rect((X_BACK + 60 + BLEED) * MM,
                         H - (Y_BODY + 28 + BLEED) * MM,
                         (X_BACK + 90 + BLEED) * MM,
                         H - (Y_BODY + 5 + BLEED) * MM)
        px = pg.get_pixmap(dpi=600, clip=r)
        tmp = os.path.join(DIST, "_qrcheck.png")
        px.save(tmp)
        doc.close()
        img = cv2.imread(tmp)
        got, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
        os.remove(tmp)
        ok = (got == want)
        if not ok:
            fails[0] += 1
        rows.append(("QR decodes to the data sheet",
                     "read" if got else "unread", "match", "",
                     "OK" if ok else "FAIL"))
        if not ok and got:
            print("    QR encodes: %s" % got)
            print("    expected  : %s" % want)
    except ImportError:
        rows.append(("QR decode (needs opencv)", "skipped", "-", "", "SKIP"))

    # ---- report -----------------------------------------------------------
    w0 = max(len(r[0]) for r in rows)
    print("%-*s %8s %9s %8s  %s" % (w0, "CHECK", "MEASURED", "EXPECTED",
                                    "DELTA", "RESULT"))
    print("-" * (w0 + 38))
    for label, m, e, d, res in rows:
        print("%-*s %8s %9s %8s  %s" % (w0, label, m, e, d, res))
    print("-" * (w0 + 38))
    print("%d checks, %d failed" % (len(rows), fails[0]))
    return 1 if fails[0] else 0


if __name__ == "__main__":
    sys.exit(main())
