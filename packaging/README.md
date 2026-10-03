# Swift Toilet Blocks — 4 × 50 g folding carton

Print artwork for the Swift Toilet Blocks carton, rebuilt from scratch in
October 2026. Not part of the website; `.htaccess` returns 404 for this folder
so it is never served.

| File | What it is |
|---|---|
| `Swift-Toilet-Blocks-4x50g-ARTWORK.pdf` | **Send this to the printer.** Artwork only, 261 × 216 mm. |
| `Swift-Toilet-Blocks-4x50g-PROOF-dieline.pdf` | For checking and sign-off. Same artwork plus cut/crease lines, panel labels and a spec legend. **Do not print from this one** — the dieline marks would print. |
| `preview/` | PNGs for quick viewing and for sending to the client. |
| `src/` | The generator. Re-run it to make changes — see below. |

---

## Specification

- **Carton:** straight tuck end (STE), **68 (w) × 118 (h) × 52 (d) mm**
- **Flat:** 255 × 210 mm · **page:** 261 × 216 mm (3 mm bleed all round)
- **Glue flap:** 15 mm, deliberately left unprinted — ink weakens the bond
- **Tuck flaps:** 46 mm
- **Colour:** RGB. The printer will convert to CMYK; ask them to match the
  brand blue to **Pantone 2738 C** (nearest to `#2E3995`) if printing spot.
- **Fonts:** Outfit and Plus Jakarta Sans, embedded as subsets. The same
  faces the website uses, so pack and site match.
- **Vector:** everything except the Vistex wordmark, which is a 755 px PNG
  placed 27 mm wide — about 700 dpi, comfortably above the 300 dpi minimum.
  The Swift oval is true vector, placed from `Swift Logo.pdf`.

### Why the carton is this size

Four 50 g cistern blocks, each roughly 50 mm across and 28 mm thick, stacked
in a column: 4 × 28 = 112 mm, inside a 118 mm internal height, with 50 mm
across fitting the 68 × 52 mm footprint. **Confirm against the real block
dimensions before the die is cut** — if they differ, change `W_PANEL`,
`H_PANEL` and `D_PANEL` at the top of `src/build.py` and re-run.

---

## Two things the client must supply

1. **The GTIN / barcode number.** The right side panel carries a correctly
   sized EAN-13 area (37.29 × 25.93 mm at 100 % magnification) marked as a
   placeholder. It cannot be filled in without the number.
2. **Confirmation of the active ingredient.** The back panel currently states
   *sodium dichloroisocyanurate, anionic & non-ionic surfactants, fragrance,
   colourant*, carried over from the previous artwork. It has not been checked
   against a formulation sheet or an SDS.

---

## What changed from the previous file

The supplied `Swift_Toilet_Blocks_4PCS_Printable_Dieline.pdf` could not be
printed. It was a single 1536 × 1024 pixel image stretched across 432 mm —
about **90 dpi**, against the 300 dpi a printer needs. It had no vector paths,
no live text and no actual dieline; the pink edges were decoration, not cut
lines. Nothing in it could be corrected, so it was rebuilt rather than edited.

Beyond that:

- **The logos were wrong.** Both were invented: a green-and-blue starburst in
  place of the Swift oval, and a green tick in place of the Vistex VC mark.
  Both are now the real artwork.
- **Pack contents moved to the front**, as asked — `50 g × 4 · NET WT. 200 g`
  on a white panel under the product, and repeated on the side and bottom flap.
- **Typography rebuilt** in the brand faces, on a consistent scale, replacing
  the mix of sizes and styles in the original.
- **Decluttered.** The original repeated the same four benefits on the front
  *and* the left panel. Benefits now appear once, on the left panel; the front
  carries three short claims. "Ideal for" moved to the right panel.
- **The QR code now works.** The original's was an AI-drawn pattern that does
  not decode. This one resolves to `https://vistexchemicals.co.ke` and was
  tested down to 150 dpi.
- **Added:** proper bleed, a real dieline, a barcode area, batch/date fields,
  and an unprinted glue flap.

---

## Making changes

Needs Node and Python with `pymupdf`, `pillow` and `qrcode`.

```bash
cd src
python assets.py        # only after changing the QR target or the logos
pwsh make.ps1           # build + render + stamp + verify + previews
```

`make.ps1` does the whole pipeline and runs 23 checks: page size, flat
geometry, that the artwork file carries no dieline marks, that every panel
bleeds its own colour past the trim, that no text sits in the bleed, and that
the stamped Swift logos do not land on type.

Edit copy and layout in `src/build.py` — the panel functions (`front`, `back`,
`side_left`, `side_right`, `flaps`) are laid out in millimetres from each
panel's top-left corner.

> Two traps, both of which bit during the build and are now guarded by checks:
> Chrome silently shrinks the page to 76 % if any element overflows the
> viewport, and the Swift logo positions live in `meta.json` *and* in the HTML
> — change one and you must change the other.
