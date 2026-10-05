#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assemble the release: the clean files that go to the machine, separated
from everything that exists to be read by a human.

Two kinds of file have been getting mixed in one folder, and only one of
them should ever reach a press:

  print-ready/   artwork only. No guide layers, no dimensions, no notes.
                 Everything here is safe to output.
  reference/     plans, production drawings, print plans, documents and
                 renders. All of it carries live annotation objects that
                 would print, so none of it is.

A MANIFEST names every file, says which is which, and records the checks
that passed when it was built - so the folder can be handed on without a
covering email.

Run:  python packaging/make_release.py
"""

import os
import shutil
import subprocess
import sys
from datetime import date

import pymupdf

from swift_blue_drop_dieline import (DIST, ROOT, HERE, W_FACE, W_SIDE,
                                     H_BODY, SHEET_W, SHEET_H, BLEED, SAFE,
                                     TAB_W, H_HANG, TAB_HEADROOM, VENT_N)
import swift_shipper as SH

OUT = os.path.join(DIST, "release")
PRINT = os.path.join(OUT, "print-ready")
REF = os.path.join(OUT, "reference")

# (source, destination name, what it is)
PRINT_FILES = (
    ("integrated/Concept_F_Vortex.pdf",
     "01_Carton_Blue-Drop_4x50g_ARTWORK.pdf",
     "Retail carton, concept F. Artwork only, 327 x 251 mm incl. 3 mm bleed."),
    ("integrated/Concept_D_Immersion.pdf",
     "02_Carton_ALT_Immersion_ARTWORK.pdf",
     "Retail carton, alternative concept D."),
    ("integrated/Concept_E_Cascade.pdf",
     "03_Carton_ALT_Cascade_ARTWORK.pdf",
     "Retail carton, alternative concept E."),
    ("shipper/Swift_Blue-Drop_12ct_Shipper_PRINT.pdf",
     "04_Shipper_12ct_ARTWORK.pdf",
     "12-count outer case. Artwork only, 1076 x 362 mm incl. 3 mm bleed."),
)

REF_FILES = (
    ("documents/Swift_Blue-Drop_F_Vortex.pdf",
     "Document_Carton_F_Vortex.pdf", "Presentation document, 8 pp."),
    ("documents/Swift_Blue-Drop_D_Immersion.pdf",
     "Document_Carton_D_Immersion.pdf", "Presentation document, 8 pp."),
    ("documents/Swift_Blue-Drop_E_Cascade.pdf",
     "Document_Carton_E_Cascade.pdf", "Presentation document, 8 pp."),
    ("documents/Swift_Blue-Drop_Shipper_12ct.pdf",
     "Document_Shipper_12ct.pdf", "Presentation document, 5 pp."),
    ("spec/Swift_Blue-Drop_Carton_SPEC.pdf",
     "Drawing_Carton_DIE_1to1_A2.pdf",
     "Dimensioned production drawing, 1:1 at A2."),
    ("spec/Swift_Blue-Drop_Shipper_SPEC.pdf",
     "Drawing_Shipper_DIE_1to2_A2.pdf",
     "Dimensioned production drawing, 1:2 at A2."),
    ("spec/Swift_Blue-Drop_F_Vortex_PRINTPLAN.pdf",
     "PrintPlan_Carton_F_1to1_A1.pdf",
     "Artwork, die and content schedule on one sheet, 1:1 at A1."),
    ("integrated/Concept_F_Vortex_PLAN.pdf",
     "Plan_Carton_F_cut_and_fold.pdf", "Cut and fold plan."),
    ("shipper/Swift_Blue-Drop_12ct_Shipper_PLAN.pdf",
     "Plan_Shipper_cut_and_fold.pdf", "Cut, slot and fold plan."),
    ("views/Carton_ALL_VIEWS.png", "Views_Carton_six_angles.png",
     "Six rendered angles of the carton."),
    ("views/Shipper_ALL_VIEWS.png", "Views_Shipper_six_angles.png",
     "Six rendered angles of the case."),
    ("family/Swift_Blue-Drop_Family.png", "Views_Family_case_and_cartons.png",
     "Case with retail cartons, one camera."),
)


def copy(group, dest):
    os.makedirs(dest, exist_ok=True)
    out = []
    for rel, name, note in group:
        src = os.path.join(DIST, rel)
        if not os.path.exists(src):
            print("  MISSING %s" % rel)
            continue
        shutil.copy2(src, os.path.join(dest, name))
        out.append((name, note, os.path.getsize(src)))
    return out


def audit_clean(path):
    """A print file must carry no guide layer. Magenta and cyan rules in the
    artwork would output, so their absence is checked rather than assumed."""
    doc = pymupdf.open(path)
    bad = 0
    for pno in range(doc.page_count):
        for d in doc[pno].get_drawings():
            col = d.get("color")
            if not col:
                continue
            r, g, b = col
            if r > 0.80 and g < 0.18 and b > 0.40:      # cut magenta
                bad += 1
            elif r < 0.18 and g > 0.55 and b > 0.80:    # crease cyan
                bad += 1
    doc.close()
    return bad


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    print("print-ready")
    pf = copy(PRINT_FILES, PRINT)
    print("reference")
    rf = copy(REF_FILES, REF)

    print("")
    print("auditing print files for guide layers")
    audit = []
    for name, _, _ in pf:
        n = audit_clean(os.path.join(PRINT, name))
        audit.append((name, n))
        print("  %-46s %s" % (name, "clean" if n == 0 else
                              "%d GUIDE OBJECTS" % n))

    try:
        v = subprocess.run([sys.executable,
                            os.path.join(HERE, "verify_dimensions.py")],
                           capture_output=True, text=True, timeout=600)
        vline = [l for l in v.stdout.strip().splitlines()
                 if "checks," in l]
        vsum = vline[-1] if vline else "not run"
    except Exception as e:
        vsum = "not run (%s)" % e

    lines = []
    lines.append("SWIFT BLUE-DROP  -  PACKAGING RELEASE")
    lines.append("Vistex Chemicals Ltd  -  %s" % date.today().isoformat())
    lines.append("")
    lines.append("CARTON   %g W x %g D x %g H mm, straight tuck end,"
                 % (W_FACE, W_SIDE, H_BODY))
    lines.append("         euro hang tab %g x %g mm (%.1f mm headroom),"
                 % (TAB_W, H_HANG, TAB_HEADROOM))
    lines.append("         %d scent vents per side panel." % VENT_N)
    lines.append("         Blank %g x %g mm plus %g mm bleed."
                 % (SHEET_W, SHEET_H, BLEED))
    lines.append("SHIPPER  %g x %g x %g mm internal, regular slotted"
                 % (SH.CASE_L, SH.CASE_W, SH.CASE_H))
    lines.append("         container, holds %d cartons (%d x %d), net %.1f kg."
                 % (SH.COUNT, SH.ACROSS, SH.DEEP, SH.NET_KG))
    lines.append("         Blank %g x %g mm plus %g mm bleed."
                 % (SH.SHEET_W, SH.SHEET_H, BLEED))
    lines.append("COLOUR   CMYK process, no spot colours. Total ink < 300%.")
    lines.append("TYPE     Live text, embedded subsets. Outfit and Plus")
    lines.append("         Jakarta Sans, both SIL OFL 1.1.")
    lines.append("SAFE     Live copy %g mm inside every cut and crease."
                 % SAFE)
    lines.append("")
    lines.append("-" * 72)
    lines.append("PRINT-READY  -  artwork only, safe to output")
    lines.append("-" * 72)
    for name, note, size in pf:
        lines.append("%s   (%.1f MB)" % (name, size / 1048576.0))
        lines.append("    %s" % note)
    lines.append("")
    lines.append("-" * 72)
    lines.append("REFERENCE  -  NOT for printing; guide layers are live")
    lines.append("-" * 72)
    for name, note, size in rf:
        lines.append("%s   (%.1f MB)" % (name, size / 1048576.0))
        lines.append("    %s" % note)
    lines.append("")
    lines.append("-" * 72)
    lines.append("CHECKS AT BUILD")
    lines.append("-" * 72)
    lines.append("Dimensions measured back out of the PDFs: %s" % vsum)
    for name, n in audit:
        lines.append("Guide-layer audit, %-42s %s"
                     % (name, "clean" if n == 0 else "%d FOUND" % n))
    lines.append("")
    lines.append("-" * 72)
    lines.append("BEFORE PLATES")
    lines.append("-" * 72)
    for t in ("Replace the product photography. The blocks are ~160 dpi at",
              "   pack size, lifted from the client card.",
              "Barcode: removed on request. Most retailers require an EAN-13.",
              "Regulatory copy is drafted, not legally reviewed.",
              "Carton and case dimensions are design intent, not measured",
              "   dies. Confirm with the converter before tooling.",
              "QR resolves to vistexchemicals.co.ke/datasheet.html. Confirm",
              "   the domain is live before the artwork is committed."):
        lines.append(("  - " if not t.startswith("   ") else "    ") +
                     t.strip())

    man = os.path.join(OUT, "MANIFEST.txt")
    with open(man, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("")
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    print("  print-ready  %d files" % len(pf))
    print("  reference    %d files" % len(rf))
    print("  %s" % vsum)
    return 0 if all(n == 0 for _, n in audit) else 1


if __name__ == "__main__":
    sys.exit(main())
