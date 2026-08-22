# Vistex Chemicals — Site Architecture (v2)

> Zero-build static site. No framework, no npm, no compile step.
> Upload the folder to `public_html` (DirectAdmin) or point GitHub Pages at the root.

---

## 1. The brief, restated

Vistex Chemicals Ltd manufactures professional hygiene systems in Nairobi under the
**Swift — *Usafi Halisi*** product brand. The buyer is not a consumer: it is a hotel GM,
a housekeeping manager, a hospital infection-control lead, a procurement officer.

That buyer needs three things from a website, in this order:

1. **Credibility** — is this a real manufacturer, or a reseller with a logo?
2. **Specificity** — what exactly does this product do, at what dilution, in what pack?
3. **A frictionless way to ask** — a quote, a demo, a site visit.

The v1 site did (1) reasonably, (2) poorly, and (3) via WhatsApp only.
v2 rebuilds around that hierarchy.

### Art direction: **"Clinical Depth"**

v1's direction was *bright clinical clean* — and it worked, but the decoration
(bubbles + morphing blobs on nearly every section) was applied uniformly, so it
read as texture rather than intent, and it competed with the content.

v2 keeps the water motif but makes it **structural instead of decorative**:

| v1 | v2 |
| --- | --- |
| Bubbles + blobs on every section | Three background *systems*, each used once or twice with purpose |
| Uniform decoration density | Decoration density falls as information density rises |
| Red used everywhere as accent | Red demoted to a **signal** colour (codes, alerts, one CTA per page) |
| One display face doing all jobs | Three registers: editorial display / neutral body / technical mono |
| Reveal-on-scroll only | A motion *system*: split-text, parallax, scrub, counters, velocity marquee |

The result should read as *an engineering company that hired a real designer* —
not a template.

---

## 2. Type system

Four families, three registers. Loaded from Google Fonts with `preconnect` + `display=swap`.

| Role | Family | Why |
| --- | --- | --- |
| **Display** | Space Grotesk (500/600/700) | Technical authority with actual character. Reads industrial, not corporate-generic. |
| **Body** | Inter (400/500/600/700) | Unmatched at 14–18px. Already in v1 — the one thing worth keeping. |
| **Technical** | JetBrains Mono (400/600) | Product codes, section numbers, stat labels, dilution figures. Gives the site a *laboratory* register that a chemicals brand earns. |
| **Editorial** | Instrument Serif (italic) | Pull quotes only. One warm, human note against an otherwise cool system. |

Scale is fluid and modular (`--step--2` → `--step-8`), built on `clamp()` so nothing
needs a breakpoint. Display sizes use tight negative tracking; mono uses positive.

---

## 3. Colour

Rebuilt from three brand anchors into full perceptual ramps so shades are chosen,
not invented ad hoc.

- **Blue** `#2E3995` → ramp `blue-50 … blue-950`. Structure, trust, nav, primary CTA.
- **Aqua** `#00A6E6` → ramp `aqua-50 … aqua-900`. Water, energy, links, dark-mode accent.
- **Red** `#ED1E26` → **signal only**: product codes, one hero CTA, destructive actions.
- **Neutrals** — a cool-cast paper ramp (`#FBFCFE` → `#070A16`) so light mode is warm
  enough to read long-form and dark mode is deep enough for the aurora to glow.

Both themes are token-swaps on `[data-theme]`; every component reads semantic tokens
(`--surface`, `--text-2`, `--border`), never raw ramp values.

---

## 4. Motion system

`js/motion.js` is no longer a reveal helper — it is a small engine of nine modules
sharing one `requestAnimationFrame` loop.
**Every module short-circuits under `prefers-reduced-motion: reduce`.**

| Module | Attribute | Behaviour |
| --- | --- | --- |
| **Reveal** | `data-anim="up\|fade\|scale\|blur\|clip\|left\|right"` | IntersectionObserver, staggered inside `.reveal-parent` |
| **Split text** | `data-split="words\|chars\|lines"` | Splits into spans, masked slide-up with per-unit stagger. This is the headline animation. |
| **Parallax** | `data-parallax="0.15"` | rAF-driven translate on scroll; used on imagery and background layers |
| **Steps** | `data-steps` | Sticky scrollytelling: marks the step nearest the viewport focal point active and drives the pinned numeral |
| **Counter** | `data-count="40"` | Eased count-up when the stat enters view |
| **Marquee** | `.marquee` | Base drift + scroll-velocity boost, direction follows scroll |
| **Tilt / glow** | `data-tilt`, `.card-glow` | Pointer-tracked 3D tilt and a cursor-following aqua glow; both off on touch |
| **Chrome** | `.scroll-progress` | Header scroll-progress hairline + solidify-on-scroll |
| **Decor** | `.aurora`, `.bubbles` | Spawns the background layers only when motion is allowed |

`partials.js` adds a **fast page transition** in place of v1's hardcoded 1.8-second
loader block, plus a **reveal failsafe**: `[data-anim]` starts at `opacity: 0`, so if
`motion.js` ever fails to load the page would stay blank. A flag set in `partials.js`
and cleared by `motion.js` reveals everything unconditionally after 2.5s if it never ran.

### Background systems (three, used sparingly)

1. **Aurora** — a slow mesh-gradient field, GPU-cheap (transform + opacity only).
   Used on the hero and the closing CTA. Nowhere else.
2. **Caustics** — a layered water-surface shimmer. Used behind the stats band only.
3. **Grain** — a 1-tile SVG noise overlay at 2–4% opacity across the whole site.
   Kills gradient banding and gives the flat colour some tooth.

---

## 4b. Home page order & the mobile split

The home page runs: **hero → ticker → the five systems → "more than detergent"
→ problem/solution ledger → how we work → what makes us different → film band
→ clients → CTA.** Systems sit directly after the hero because that is what a
buyer arriving cold actually wants to see.

Two sections change shape on phones rather than shrinking:

| Section | Desktop | ≤820px |
| --- | --- | --- |
| How we work | Sticky photo stage + 4 step cards | **Swipe deck** — one step per card, image above narration |
| What makes us different | 6-card bento | **Swipe deck** — one card per screen |
| Problem/solution ledger | Full ledger | Hidden |

The decks use native horizontal `scroll-snap`. Vertical page scrolling is never
intercepted — reaching the last slide simply hands scrolling back, so there is
no scroll-jacking.

The hero reorders on phones to **headline → products → buttons**, and the lede
is dropped: the headline and the product line-up already carry the message, and
keeping it pushed the CTAs below the fold.

There is no metrics band. The four figures were shown twice and were removed;
the brand film that had lived behind them now carries the pull quote instead,
lazily armed 1200px before it scrolls into view and played only on
`canplaythrough`.

---

## 4c. Dark mode is the default

`--bg-sunk` used to sit *below* `--bg` in dark mode — a 0.0013 luminance
difference, invisible, so every tinted band looked identical to the page and
the whole site read as one flat dark field. It is now a real elevation ladder:

```
--bg #070a16 → --bg-sunk #0c1224 → --surface #131b34 → --surface-2 #1a2443 → --surface-3 #223055
```

Raising those surfaces pushed several small labels under AA, so `--text-3` and
`--text-4` moved with them in both themes. Contrast is audited by script across
6 pages × 2 themes; see `scratch/audit.js` from the build session. It resolves
`color(srgb …)` (the form `color-mix()` serialises to) and skips text sitting on
gradient or photo bands rather than mis-measuring it.

---

## 5. File map

```
/
├── index.html            home        — the narrative arc
├── systems.html          catalog     — 5 systems, 40 products, search + filter
├── product.html          detail      — ?id=<productId>
├── industries.html       5 sectors, alternating editorial bands
├── about.html            company, mission, clients
├── contact.html          WhatsApp + email fallback
├── 404.html
├── sitemap.xml           50 URLs, generated from data.js
├── site.webmanifest
├── robots.txt  .htaccess  .nojekyll
│
├── css/                  loaded in this order — later files win
│   ├── tokens.css        colour ramps, type scale, space, motion, elevation
│   ├── base.css          reset, typography, layout primitives, utilities
│   ├── components.css    button, card, chip, field, nav, footer, drawer, product card
│   ├── motion.css        keyframes, animation primitives, background systems
│   ├── pages.css         home hero, catalog bands, product detail, industry bands
│   └── responsive.css    small-screen, touch and notch corrections (loaded last)
│
└── js/
    ├── data.js           single source of truth (company, systems, products, industries)
    ├── icons.js          inline SVG icon set + hydrateIcons()
    ├── partials.js       header / footer / drawer, vxPicture(), vxToast(), productCardHtml()
    ├── cart.js           enquiry cart (localStorage → WhatsApp + email)
    ├── motion.js         the motion engine (9 modules)
    ├── home.js           home page render
    ├── catalog.js        systems page: filter, live search, URL state
    ├── product.js        product detail, spec table, dynamic meta + JSON-LD
    ├── industries.js     industry bands
    ├── about.js          about page render
    └── contact.js        contact form → WhatsApp, with mailto fallback
```

There is no `boot.js`. The theme has to be applied **before first paint** or the page
flashes, and a separate `<script src>` cannot beat the parser to it — so each page
carries the same four-line inline snippet in `<head>`, and nothing else is duplicated.
Per-page `<meta>` stays in the HTML too, because that is the only place a crawler
will look for it.

### Load order (identical on every page)

```
data.js → icons.js → partials.js → cart.js → <page>.js → motion.js
```

`motion.js` runs last so it observes everything the page scripts injected.

---

## 6. Data model

`js/data.js` remains the single source of truth on `window.VISTEX`. Product records
gain the fields a technical buyer actually asks for:

```js
{
  id, system, name, code, image, pack,
  purpose,                       // what it does
  dilution:  '10–15 g / kg linen',   // ← new
  temp:      '50–70 °C',             // ← new
  ph:        '11.5 ± 0.5',           // ← new
  form:      'powder' | 'liquid',    // ← new
  packs:     ['20 kg', '5 kg'],      // ← new
  features:  [ ... ],                // ← new
  safety:    'Wear gloves…'          // ← new
}
```

Everything is optional — the renderer only prints the rows that exist, so the data can
be filled in progressively without touching a template.

---

## 7. What v2 fixes from v1

**Performance**
- Removed the hardcoded `MIN = 1800` ms loader block on *every* navigation.
  The intro now shows once per session, capped at ~700 ms, and never blocks paint.
- Explicit `width`/`height` + `decoding="async"` on every image → no layout shift.
- Every raster asset re-encoded at the width it is actually painted at, with a `.webp`
  sibling served through `<picture>`: **4.38 MB → 1.18 MB on the WebP path (−73%)**,
  2.33 MB on the jpeg/png fallback. The logos alone were 996px wide for a 180px slot.
- Hero art preloaded via `imagesrcset` with a 900w phone variant; everything below
  the fold is lazy.
- `content-visibility: auto` on off-screen sections.

**SEO**
- Per-page `canonical`, Open Graph and Twitter cards on all seven pages (v1 had them on one).
- JSON-LD: `Organization` + `LocalBusiness` site-wide, `ItemList` on the catalog,
  `Product` on detail, `BreadcrumbList` where relevant.
- A real `sitemap.xml` — `robots.txt` had been advertising one that returned 404.

**Accessibility**
- `aria-expanded` on the nav toggle; drawer gets Escape-to-close, a focus trap and
  focus return.
- Visible focus rings on every interactive element.
- Every motion module honours `prefers-reduced-motion`.

**Conversion**
- Catalog gains live search + system filter + sort (40 products, previously unfiltered).
- Product pages show dilution, temperature, pH, pack options and safety notes.
- Contact and the enquiry drawer both offer **WhatsApp primary + email fallback**,
  so a popup-blocked desktop visitor is no longer dead-ended.
```
