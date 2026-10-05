# Swift Toilet Blocks — 4 × 50 g folding carton

Print artwork for the Swift Toilet Blocks carton, built October 2026. Not part
of the website; `.htaccess` returns 404 for this folder so it is never served.

| File | What it is |
|---|---|
| `Swift-Toilet-Blocks-4x50g-ARTWORK.pdf` | **To the printer.** Flat carton, 261 × 216 mm. |
| `Swift-Toilet-Blocks-4x50g-PROOF-dieline.pdf` | For checking and sign-off: the same artwork with cut and crease lines, panel labels and a spec legend. **Do not print from this one** — the die marks would print. |
| `preview/` | PNGs for viewing and for sending to the client. |
| `src/` | The generator. Re-run it to make changes — see below. |

---

## Specification

Built on the client's `Swift_Toilet_Blocks_4PCS_Printable_Dieline` as the
template: the same flat carton, the same panel order, the same content on each
panel.

```
glue │ SIDE A │ FRONT │ SIDE B │ BACK
```

- **Side A** — "Why it works": the four benefits, with the pack seal
- **Front** — Swift mark, product name, the blocks, pack contents
- **Side B** — "How to use": the three directions, and "Ideal for"
- **Back** — description, caution, ingredients, Vistex, QR

| | |
|---|---|
| Carton | straight tuck end, **68 (w) × 118 (h) × 52 (d) mm** |
| Flat | 255 × 210 mm · page 261 × 216 mm (3 mm bleed all round) |
| Glue flap | 15 mm, deliberately unprinted — ink there weakens the bond |
| Tuck flaps | 46 mm |
| Colour | RGB; the printer converts to CMYK. Match brand blue to **Pantone 2738 C** (nearest to `#2E3995`) if printing spot. |
| Fonts | Outfit and Plus Jakarta Sans, embedded as subsets — the faces the website uses, so pack and site match |

Everything is vector except the Vistex wordmark, a 755 px PNG placed 28 mm wide
(~690 dpi). The Swift oval is true vector, placed from `Swift Logo.pdf`.

### Why the carton is this size

The supplied dieline had **no dimensions to copy** — it is a single 1536 × 1024
image with no vector geometry, so nothing in it was measurable. The carton is
therefore sized from the product: four blocks about 50 mm across and 28 mm
thick, stacked in a column (4 × 28 = 112 mm inside a 118 mm height).

> **Confirm this against the real blocks before the die is cut.** If they
> differ, change `W_PANEL`, `H_PANEL` and `D_PANEL` at the top of
> `src/build.py` and re-run.

### The premium devices

A double platinum keyline frame with corner diamonds on every panel; hairline-
and-diamond ornament rules between blocks of content; a platinum roundel seal
carrying the pack count; concentric arcs behind the product for depth; and a
layered gradient with a vignette instead of one flat blue.

> The platinum prints CMYK — it reads as metal but is not metallic. **For real
> metal, specify silver foil or a metallic spot ink** for the frames, rules,
> seals and corner diamonds. They are already separate elements, so the printer
> can pull them to a foil layer without redrawing anything.

---

## Two things the client must supply

1. **The GTIN / barcode number.** There is no barcode on the carton yet. It
   normally goes on the back panel, bottom; an EAN-13 needs 37.3 × 25.9 mm at
   100 % magnification, which does not fit alongside the current back-panel
   content — expect to move the contact block to make room.
2. **Confirmation of the active ingredient.** The back states *sodium
   dichloroisocyanurate, anionic & non-ionic surfactants, fragrance,
   colourant*, carried over from the previous artwork. It has **not** been
   checked against a formulation sheet or an SDS.

---

## What changed from the file originally supplied

`Swift_Toilet_Blocks_4PCS_Printable_Dieline.pdf` could not be printed. It was a
single 1536 × 1024 pixel image stretched across 432 mm — about **90 dpi**, where
a printer needs 300 — with no vector paths, no live text and no dieline; the
pink edges were decoration, not cut lines. Nothing in it could be corrected, so
it was rebuilt.

- **The logos were wrong.** Both were invented: a green-and-blue starburst in
  place of the Swift oval, and a green tick in place of the Vistex VC mark.
- **Pack contents moved to the front**, and repeated on both side panels and the
  bottom flap.
- **Batch / manufacture / expiry fields removed.**
- **Typography rebuilt** in the brand faces on one consistent scale.
- **Decluttered.** The original showed the same four benefits on the front *and*
  a side panel; they now appear once, on Side A.
- **The QR code works.** The original's was an AI-drawn pattern that does not
  decode. This one resolves to `https://vistexchemicals.co.ke`, tested to 150 dpi.
- **Added** proper bleed, a real dieline, and an unprinted glue flap.

---

## Making changes

Needs Node and Python with `pymupdf`, `pillow` and `qrcode`.

```bash
cd src
python assets.py        # only after changing the QR target or the logos
pwsh make.ps1           # build + render + stamp + verify + previews
```

`make.ps1` runs the whole pipeline and 33 checks: page size, flat geometry, that
the artwork file carries no die marks, that every panel bleeds its own colour
past the trim, that no type sits in the bleed, and that the stamped Swift logos
do not land on other type. It also reports the gap between each panel's flowing
copy and its pinned footer.

Edit copy and layout in `src/build.py`. The back and Side B are laid out in
**normal document flow**, so adding a line pushes the rest down instead of
overlapping it; the front and Side A are positioned absolutely in millimetres.

> Four traps, all of which bit during the build and are now guarded by checks:
> Chrome silently shrinks the page to 76 % if any element overflows the
> viewport; the Swift logo positions live in `meta.json` *as well as* the HTML,
> so changing one means changing the other; a panel only clips at its own edge,
> so flowing copy can run into a pinned footer with no clipping warning; and a
> 3 mm bleed strip beside a gradient panel samples a different part of that
> gradient, so the flaps are drawn oversized into the bleed instead.
