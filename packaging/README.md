# Swift Toilet Blocks — 4 × 50 g euro-slot hang card

Print artwork for the Swift Toilet Blocks pack, built October 2026. Not part of
the website; `.htaccess` returns 404 for this folder so it is never served.

| File | What it is |
|---|---|
| `Swift-Toilet-Blocks-4x50g-FRONT.pdf` | **To the printer.** Front face, 136 × 186 mm. |
| `Swift-Toilet-Blocks-4x50g-BACK.pdf` | **To the printer.** Back face, same size. |
| `Swift-Toilet-Blocks-4x50g-PROOF-dieline.pdf` | For checking and sign-off: both faces side by side with the cut line and a spec legend. **Do not print from this one** — the die marks would print. |
| `preview/` | PNGs for viewing and for sending to the client. |
| `src/` | The generator. Re-run it to make changes — see below. |

---

## Specification

- **Format:** euro-slot hang card, **130 × 180 mm**, 6 mm corner radius
- **Hanger:** sombrero euro punch — 34 × 6.2 mm slot with a 12.8 mm round hole,
  centred, top of the punch 3.8 mm from the card edge
- **Page:** 136 × 186 mm per face (3 mm bleed all round)
- **Die matches the Blue-Drop card**, so one cutting tool serves both SKUs.
- **Colour:** RGB. The printer converts to CMYK; ask them to match the brand
  blue to **Pantone 2738 C** (nearest to `#2E3995`) if printing spot.
- **Fonts:** Outfit and Plus Jakarta Sans, embedded as subsets — the same faces
  the website uses, so pack and site match.
- **Vector:** everything except the Vistex wordmark, a 755 px PNG placed 36 mm
  wide (~530 dpi). The Swift oval is true vector, placed from `Swift Logo.pdf`.

### The premium devices

- A double platinum keyline frame with corner diamonds, on both faces
- Hairline-and-diamond ornament rules separating each block of content
- A platinum roundel seal carrying `50 g × 4`
- Concentric arcs behind the product, at 7 % opacity, for depth without pattern
- Deep layered gradient with a vignette, rather than one flat blue

> The platinum is printed CMYK — it reads as metal but is not metallic.
> **If you want real metal, specify silver foil or a metallic spot ink** for the
> frame, rules, seal ring and corner diamonds; they are already separate
> elements, so the printer can pull them to a foil layer without redrawing.

---

## Two things the client must supply

1. **The GTIN / barcode number.** There is no barcode on the card yet. A euro
   hang card normally carries an EAN-13 on the back, bottom-left; the space is
   there, and it takes 37.3 × 25.9 mm at 100 % magnification.
2. **Confirmation of the active ingredient.** The back states *sodium
   dichloroisocyanurate, anionic & non-ionic surfactants, fragrance, colourant*,
   carried over from the previous artwork. It has **not** been checked against a
   formulation sheet or an SDS.

## One thing to confirm with the printer

If the blocks ship in a **clear blister** rather than loose behind the card, the
blister footprint lands over the product illustration in the middle of the front.
Tell the printer which it is: a blister means the illustration is covered by the
real product and may be dropped.

---

## What changed from the file originally supplied

`Swift_Toilet_Blocks_4PCS_Printable_Dieline.pdf` could not be printed. It was a
single 1536 × 1024 pixel image stretched across 432 mm — about **90 dpi**, where
a printer needs 300 — with no vector paths, no live text and no dieline; the pink
edges were decoration, not cut lines. Nothing in it could be corrected, so it was
rebuilt.

- **The logos were wrong.** Both were invented: a green-and-blue starburst in
  place of the Swift oval, and a green tick in place of the Vistex VC mark.
- **Format changed** from a tuck-end carton to this hang card, to match the
  sample.
- **Pack contents on the front** — in the seal, and again on the bottom bar.
- **Batch / manufacture / expiry fields removed**, as asked.
- **Typography rebuilt** in the brand faces on one consistent scale.
- **Decluttered:** benefits appear once, not twice.
- **The QR code works.** The original's was an AI-drawn pattern that does not
  decode. This one resolves to `https://vistexchemicals.co.ke`, tested to 150 dpi.

---

## Making changes

Needs Node and Python with `pymupdf`, `pillow`, `qrcode` (and `opencv-python-headless`
only if you want to re-test the QR).

```bash
cd src
python assets.py        # only after changing the QR target or the logos
pwsh make.ps1           # build + render + stamp + verify + previews
```

`make.ps1` runs the whole pipeline and 242 checks: page size, bleed on all four
sides of both faces, that the artwork files carry no die marks, that no type sits
in the bleed or under the hanger punch, that type clears the die edge, and that
the stamped Swift logo does not land on other type. It also reports the gap
between the back's flowing copy and its pinned footer.

Edit copy and layout in `src/build.py`. The back is laid out in **normal document
flow**, so adding a line pushes the rest down instead of overlapping it; the
front is positioned absolutely in millimetres.

> Three traps, all of which bit during the build and are now guarded:
> Chrome silently shrinks the page to 76 % if any element overflows the viewport;
> the Swift logo position lives in `meta.json` *as well as* the HTML, so changing
> one means changing the other; and a `.card` only clips at its own edge, so the
> back's copy could run into the footer without any clipping warning — hence the
> explicit gap check.
