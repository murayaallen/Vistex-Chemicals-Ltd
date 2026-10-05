# Packaging artwork

Print artwork for Vistex Chemicals, generated from source rather than drawn by
hand. The script **is** the artwork: to revise the pack, change a value and
re-run. Nothing here is part of the website deploy.

**The supplied imagery is not in this repo.** It is client photography and
sourced stock, and this repo is public and deploys via Pages, so none of it
is ours to republish. `make_cutouts.py` expects these in the project root:

```
flower.jpg   fresh.jpg   images.jfif   fresh blue.avif   recycle.avif
WhatsApp Image 2026-10-02 at 17.09.19.jpeg
```

Without them the build stops at the first step with a clear message. Drop
them back in and the whole chain reruns.

```
python packaging/make_cutouts.py          # photographic assets, once
python packaging/make_scene.py            # composited scenes, once
python packaging/swift_blue_drop_dieline.py   # baseline vector carton
python packaging/swift_blue_drop_v2.py        # the three concepts
python packaging/swift_shipper.py             # 12-count outer case
python packaging/make_mockup.py               # folded 3D renders
python packaging/make_family.py               # case + cartons line-up
python packaging/make_spec.py                 # dimensioned die drawings
python packaging/make_printplan.py            # artwork + die + content, 1:1
python packaging/make_views.py                # six angles of each subject
python packaging/make_document.py             # per-iteration documents
python packaging/verify_dimensions.py         # measure the output back
python packaging/make_release.py              # assemble + audit the release
```

## Swift Blue-Drop — Flush-Activated WC Cleaner, 50 g x 4

| | |
|---|---|
| Source | [swift_blue_drop_dieline.py](swift_blue_drop_dieline.py) |
| Carton | 105 W x 48 D x 155 H mm, straight tuck end |
| Hanging | euro hang tab, 62 x 26 mm, on the back panel |
| Venting | 5 droplet cut-outs per side panel, so the scent gets out |
| Flat blank | 321 x 245 mm + 3 mm bleed |
| Colour | CMYK process, no spot colours |
| Type | live text, embedded subsets — not outlined, not rasterised |
| Artwork | 100% vector; the only raster is the Swift logo |

Two files land in `dist/`:

- **`..._PRINT.pdf`** — artwork only, page = blank + bleed. This is what the
  converter gets.
- **`..._GUIDES.pdf`** — the same artwork on a larger page with the cut, crease,
  bleed and safe-area layers, panel labels, dimensions and a legend. For
  approval and for checking the die, **never** for printing.

### What replaced what

This supersedes `Swift_Toilet_Blocks_4PCS_Printable_Dieline.pdf`, which was a
single flat raster dropped into a PDF — no live text, no vector cut paths, the
wrong Swift mark, and a green/yellow palette that read as laundry powder. It
also carried the name "Toilet Blocks / Maxi", which contradicts the product
record in [`js/data.js`](../js/data.js) (`blue-drop-wc`, "Blue-Drop
Flush-Activated WC Cleaner", 50 g x 4). The name here follows the catalogue.

### Art direction

Follows the iteration the client approved over WhatsApp: deep navy ground,
the real blue-oval Swift mark, a single yellow accent, red reserved for signal.

| Role | CMYK | Was |
|---|---|---|
| Ground | 100 / 85 / 10 / 15 | `#01236B` |
| Burst edge | 100 / 90 / 15 / 40 | — |
| Swift oval, dark | 100 / 70 / 0 / 5 | `#00459A` |
| Swift oval, light | 85 / 40 / 0 / 0 | `#0079C4` |
| Water | 65 / 10 / 0 / 0 | `#33BFF3` |
| Accent | 0 / 12 / 100 / 0 | `#FEDA00` |
| Signal | 0 / 95 / 90 / 0 | `#ED1E26` |

Mixes are hand-specified, not machine-converted from RGB: a naive conversion of
the navy prints muddy. Total ink stays under 300% everywhere. The printer should
still soft-proof against their own profile.

### Typography

Outfit (display, headings) and Plus Jakarta Sans (body), the same faces as the
website. Both are SIL Open Font License 1.1, so they can be embedded in
commercial packaging without a foundry licence — see [fonts/OFL.txt](fonts/OFL.txt).
Arial and Segoe UI were deliberately avoided: they are Microsoft-licensed and
murkier on client artwork.

### The hang tab

A peg hole needs unbroken material to pull against, so the tab is a straight
extension of the **back panel with no crease at its base** - creasing it there
is what makes hang tabs tear off in store. That choice pushes both tuck ends
onto the front panel, which is why this is a straight tuck end rather than the
reverse tuck the first version used.

The eye is a standard euro slot: 6.4 mm hole, 5 mm riser, 12.9 mm overall. It
leaves **7.8 mm of headroom** above the slot - under about 6 mm a peg hole
tears out, so that figure is worth re-checking if `H_HANG` or `SLOT_*` change.
`TAB_HEADROOM` is computed, not hard-coded, so the build always reports the
real number in the plan.

The slot is knocked out white in the artwork. The die removes it either way;
printing it white simply means previews and mockups read as a hole.

### Scent vents

The product is bought on smell and a sealed carton releases none of it, so
each side panel carries five droplet-shaped cut-outs. Droplets rather than
drilled holes, so the die feature doubles as a brand mark. They sit in a
horizontal band kept clear of copy on both sides - a vertical column down the
middle of a 48 mm panel ran straight through the text.

They are knocked out white in the artwork so previews and mockups read as
holes; the die removes them in any case.

### The 12-count shipper

[swift_shipper.py](swift_shipper.py) builds the outer case. A regular slotted
container: one blank, four panels, eight flaps, every flap half the case depth
so the top pair meet and one taped seam closes it.

Sized **from** the retail carton rather than guessed - 3 across x 4 deep gives
the squarest footprint for a 105 x 48 mm carton. 4 x 3 and 2 x 6 both produce
long thin cases that pallet badly and crush in the middle.

| | |
|---|---|
| Case | 319 L x 196 W x 160 H mm internal |
| Holds | 12 retail cartons, 2.4 kg of product |
| Blank | 1070 x 356 mm + 3 mm bleed |

Print is deliberately plainer than the retail pack: a shipper is read from
three metres away in a stockroom, so it carries identity, count and handling
marks and nothing else. Full-bleed photography on an outer is money spent
where no shopper ever looks. Handling symbols are drawn, not set - ISO 780
marks are not a typeface.

### Instruction illustrations

[illustration.py](illustration.py) draws the three how-to-use steps. A cistern
is a box nobody looks inside, so "drop it in the tank" is the one instruction
that genuinely needs a picture; the tank is drawn as a cutaway with the float
and inlet visible, because the instruction is specifically to keep the block
clear of them.

Flat vector on a restricted palette with one stroke weight scaled off the
artwork size, so the three read as a family. No gradients and no soft shadows:
those are what make instruction art look clip-arty and print badly at small
size on uncoated board.

### Changing the die

Every dimension is a constant at the top of the script. Set them to the
converter's actual die spec and the whole pack re-flows:

```python
W_FACE = 105.0   # front / back panel width
W_SIDE = 48.0    # side panel width (carton depth)
H_BODY = 155.0   # panel height
W_GLUE = 15.0    # glue tab
H_TUCK = 45.0    # tuck flap depth
H_HANG = 26.0    # hang tab height above the closed carton
TAB_W  = 62.0    # hang tab width
VENT_N = 5       # scent vents per side panel
VENT_Y = 100.0   # vent row centre
BLEED  = 3.0
SAFE   = 5.0
```

The dimensions above are a sensible retail carton for 4 x 50 g, **not** a
measured die. Confirm them with the converter before plates are cut.

### Layout guard

Dense panels are easy to overrun by a millimetre, and the damage is invisible
until it is on press. Every string drawn is measured against the panel it went
into and against every other string, so the build reports anything that escapes
a panel or lands on top of something else:

```
layout clean - every string inside its panel
```

If that line changes to `LAYOUT OVERFLOW` or `TEXT COLLISIONS`, the build is
telling you the copy no longer fits — fix it before sending the file out.

### Presentation documents

[make_document.py](make_document.py) builds one A3 document per iteration -
cover, panels, flaps and die features, flat blank, dieline, specification -
plus a three-page document for the outer case.

Built in two passes, which is the point: ReportLab lays out the pages, then
PyMuPDF stamps the artwork in with `show_pdf_page`, so every panel and every
dieline in the document is **vector**, clipped straight out of the print file.
Rasterising at 400 dpi would have been half the code, but then the client
would have a picture of the design rather than the design, and nobody could
zoom into the type to check it.

### Production drawings

[make_spec.py](make_spec.py) draws the dimensioned die specification - the
sheet a toolmaker works from, as opposed to the plan, which shows where the
ink goes. Dimension chains, detail views at 4:1, notes and a title block.

| | |
|---|---|
| Carton | A2 landscape, **1:1** |
| Shipper | A2 landscape, **1:2** (its blank is 1070 mm wide) |

Geometry is read from the build scripts, never retyped: a drawing that
disagrees with the artwork is worse than no drawing. Setting the source
module ORIGIN to zero makes its own path helpers emit raw millimetres, which
a canvas transform then places and scales - so the slot and vents in the
detail views are the same paths the die will cut.

Both drawings are reproduced in the presentation documents at reduced size;
the 1:1 and 1:2 sheets live in `dist/spec/`.

### Print plan - die and content on one sheet

[make_printplan.py](make_printplan.py) puts the artwork at **1:1 under the
dieline**, dimensions it, and schedules every panel against what it carries.
The plan alone shows where ink goes; the production drawing alone shows what
the die cuts. Neither answers "what prints on which panel, at what size" -
the question a printer and a client both actually ask.

A1 landscape, 1:1, with a content schedule, process inks, finish spec, notes
and a title block. Composed in three passes, because PDF compositing only
stacks forward: furniture, then artwork, then an unpainted overlay of
dielines and dimensions. Drawing the overlay first would have buried it.

### Verifying the dimensions

[verify_dimensions.py](verify_dimensions.py) measures the numbers back out of
the finished PDFs and compares them to the figure printed on the sheet - not
to the constants that produced them, which would only prove the code agrees
with itself.

```
32 checks, 0 failed
```

One subtlety it had to handle: PyMuPDF reports a path bounding box from its
**control points**, and a bezier droplet has control points 0.63 mm below the
curve they describe. The vent check failed on geometry that was dead right
until the verifier started flattening curves to find their true bounds.

Run it after any change to the die.

### The QR code and the data sheet

The back panel carries a QR to
`vistexchemicals.co.ke/datasheet.html?id=blue-drop-wc`, which is a **real page
in this repo** - [datasheet.html](../datasheet.html) and
[js/datasheet.js](../js/datasheet.js), driven by the `datasheet` block added to
the product record in [js/data.js](../js/data.js). A QR that lands on a 404 is
worse than no QR, so the page was written before the code was placed.

It prints on its own white plate. Modules straight onto the navy band would
halve the contrast a phone camera has to work with, and a code that needs
three attempts in a store room may as well not be there.

Figures that have not been measured - pH, shelf life - say "on request" rather
than carrying a number nobody has verified.

### Views

[make_views.py](make_views.py) renders six angles of the carton and of the
case from one camera rig: front three-quarter both ways, front square on,
back three-quarter, back square on, and from above. A pack is approved once,
so the faces nobody has been shown - the back, the far flank, the top - go in
front of the client rather than being discovered on press.

### The release

[make_release.py](make_release.py) splits the output in two, because only one
half should ever reach a press:

```
dist/release/print-ready/   artwork only, safe to output
dist/release/reference/     plans, drawings, documents, renders
dist/release/MANIFEST.txt   what each file is, and the checks that passed
```

Every print-ready file is **audited for guide layers** before it is released -
a stray magenta cut line or cyan crease in an artwork file would output, so
their absence is checked rather than assumed. The manifest records that audit
and the dimension verification alongside the file list, so the folder can be
handed on without a covering email.

### Still outstanding

- **Barcode.** The back panel reserves a 30 x 15.6 mm box marked "EAN-13 to be
  supplied". Drop the real symbol in once GS1 issues the number.
- **Regulatory copy.** The composition, caution and storage wording is drafted,
  not legally reviewed. Have it checked before it goes to print.
