# Vistex Chemicals — Website (v2)

A static website for **Vistex Chemicals Ltd**, a Kenyan manufacturer of professional
hygiene systems. **No framework, no npm, no build step** — the folder you see is the
folder you upload.

Art direction and the full reasoning behind the rebuild are in
[ARCHITECTURE.md](ARCHITECTURE.md). Start there before changing anything structural.

---

## Run it locally

```bash
python -m http.server 8080     # then open http://127.0.0.1:8080
```

A server is required — opening `index.html` over `file://` breaks the `?id=` and
`?system=` query routing.

## Deploy

**DirectAdmin** — upload the entire folder contents (including `.htaccess`) into
`public_html`.

**GitHub Pages** — Settings → Pages → Deploy from a branch → `main` / `(root)`.
`.nojekyll` is included. All paths are relative, so a project sub-path works too.

---

## How it works

Every page is plain HTML with `<body data-page="…">`. Scripts load in the same order
everywhere:

```
data.js → icons.js → partials.js → cart.js → <page>.js → motion.js
```

- **`js/data.js`** — the single source of truth. Company details, systems, industries
  and all 40 products live on `window.VISTEX`. **Edit content here, not in templates.**
- **`js/partials.js`** — injects the header, footer and enquiry drawer into every page;
  wires the theme toggle, mobile nav and page transitions. Also exposes
  `vxPicture()`, `vxToast()` and `productCardHtml()`.
- **`js/cart.js`** — the enquiry cart (localStorage) → a pre-filled WhatsApp message,
  with an email fallback.
- **`js/motion.js`** — the motion engine: scroll reveals, split-text headlines,
  parallax, sticky scrollytelling, counters, the velocity marquee, pointer effects.
  All of it disables itself under `prefers-reduced-motion: reduce`.

CSS loads `tokens → base → components → motion → pages → responsive`. Later files win,
so **`responsive.css` is where small-screen and touch corrections belong.**

---

## Editing content

| What | Where |
| --- | --- |
| Phone, email, address, hours | `js/data.js` → `company` |
| Products, codes, packs, dilution | `js/data.js` → `products` |
| Systems and their benefits | `js/data.js` → `systems` |
| Industries and client lists | `js/data.js` → `industries`, `clients` |
| Brand colours, type scale, spacing | `css/tokens.css` |
| Small-screen behaviour | `css/responsive.css` |

### Adding a product

Append an object to `products` in `js/data.js`. Only `id`, `system`, `name`, `pack`
and `purpose` are required — `code`, `image`, `form`, `dilution`, `temp` and
`features` are optional and are only rendered when present.

> ⚠️ **Never invent dilution, temperature or pH figures.** Only four products currently
> carry them because those are the only ones Vistex supplied. For an industrial
> chemical these are a safety matter — get the real values before publishing them.

If you add a product photo, also generate its `.webp` sibling (see below), or the
`<picture>` element will fall back silently to the larger original.

### Adding an image

Images are served as `<picture>` with a `.webp` source and a `.jpg`/`.png` fallback.
Both files must exist and share a basename. To regenerate the whole set after adding
originals, use `scratch/optimize.py` from the build session, or any WebP encoder —
target the width the asset is actually painted at, not the width of the file you were sent.

---

## After go-live

- [ ] Confirm HTTPS works on every subdomain, then uncomment the HSTS header in `.htaccess`.
- [ ] Regenerate `sitemap.xml` whenever products are added or removed.
- [ ] Get the remaining 30 product photos — those cards currently show a designed
      placeholder rather than a product shot.
- [ ] Get real dilution / temperature figures for the rest of the catalogue.
- [ ] Ask the client for vector (SVG) logos; the PNGs are now right-sized but a vector
      would be sharper on high-density screens.
