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

A server is required — opening `index.html` over `file://` blocks the scripts that
render the catalogue.

## Deploy

**DirectAdmin** — upload the folder contents (including `.htaccess`) into `public_html`.
Leave out `Updates/`, `new/`, `jerricans/`, `Urinal Mat Scents/`, `tools/` and the loose
`.pdf` / `.docx` / `.zip` files: they are client source material. `.htaccess` answers 404 for
all of them anyway, as a safety net.

**GitHub Pages** — Settings → Pages → Deploy from a branch → `main` / `(root)`.
`.nojekyll` is included. All paths are relative, so a project sub-path works too.

---

## How it works

Every page is plain HTML with `<body data-page="…">`. Scripts load in the same order
everywhere:

```
data.js → icons.js → partials.js → cart.js → <page>.js → motion.js
```

- **`js/data.js`** — the single source of truth. Company details, six ranges, industries
  and all 68 products live on `window.VISTEX`. **Edit content here, not in templates.**
- **`tools/build-pages.js`** — turns `data.js` into one static page per product
  (`product-<id>.html`) and per range (`laundry-chemicals.html` …), plus `sitemap.xml`
  and the cache-busting `?v=` on every CSS/JS link. **Run it after any content or code
  change:** `node tools/build-pages.js`. No npm install; plain Node 18+.
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

Append an object to `products` in `js/data.js`, then run `node tools/build-pages.js`.
Only `id`, `system`, `name`, `pack` and `purpose` are required. Everything else —
`subtitle`, `code`, `image`, `form`, `ph`, `dilution`, `temp`, `active`, `shelfLife`,
`features`, `applications`, `surfaces`, `notFor`, `directions`, `dilutions`, `hazard`,
`neverMix`, `gallery`, `docs` — is optional and only rendered when present. The field
list with examples is at the top of `data.js`.

> ⚠️ **Never invent dilution, temperature, pH or hazard figures.** Every value in
> `data.js` comes from a Vistex label, TDS or product sheet, and each record notes its
> source. For an industrial chemical these are a safety matter.

Set `supplied: true` on anything Vistex sells but does not manufacture (the dental
kit, slippers, shower caps…) — the pages then say "supplied by", never "made by".

### Adding an image

Images are served as `<picture>` with a `.webp` source and a `.jpg`/`.png` fallback,
sharing a basename. The sizes the templates expect:

| Asset | Size | Folder |
| --- | --- | --- |
| Product shot | 800 × 800 | `images/products/` + 360 × 360 in `images/thumbs/products/` |
| Cut-out | 406 × 466, transparent, subject centred, 17 px above the bottom edge | `images/cutouts/` + 209 × 240 in `images/thumbs/cutouts/` |

A product with a cut-out **and** a `vessel` (`bucket`, `jerrican`, `bottle`) joins the
hero conveyor; bottles keep their true size next to 20 L drums, so do not scale a
500 ml bottle to fill the frame.

### Adding a data sheet

Put the PDF in `docs/tds/` and add `docs: [{ label, file, kind }]` to the product.
`.gitignore` excludes PDFs everywhere *except* `docs/`. Keep sheets under ~500 KB:
the client's image-only PDFs arrive at 2–3 MB and re-encode at 170 dpi to about 450 KB
with no visible loss.

---

## Search (Google Search Console)

The site is built to be indexed page by page:

- **79 indexable pages**: home, catalogue, industries, about, contact, six range pages
  and 68 product pages — each with its own title, description, canonical, share image
  and JSON-LD (Organization, Product, CollectionPage, BreadcrumbList).
- Every product page carries its full content in the HTML, so it reads the same to
  Google, Bing and a WhatsApp link preview with or without JavaScript.
- `sitemap.xml` lists all 79 with their product images; `robots.txt` points to it.
- The old `product.html?id=…` / `systems.html?system=…` addresses redirect to the new
  pages, and `product.html` itself is `noindex`.

**One-time setup, after go-live:**

1. Go to <https://search.google.com/search-console> and sign in with the company's
   Google account.
2. Add a **Domain** property for `vistexchemicals.co.ke`. Google shows a TXT record —
   add it in DirectAdmin → DNS Management, then press Verify. (DNS verification covers
   `www`, the bare domain and https in one property. If DNS is not available, use a
   **URL-prefix** property for `https://www.vistexchemicals.co.ke/` with the *HTML tag*
   method — paste the tag where the comment in `index.html` says.)
3. **Sitemaps** → submit `sitemap.xml`.
4. **URL inspection** → inspect the home page and a product page (e.g.
   `/product-drain-care.html`) → *Request indexing*.
5. Also add the site to **Bing Webmaster Tools** (it can import the Search Console
   property in one click) — Bing also feeds DuckDuckGo and ChatGPT search.
6. Create / claim the **Google Business Profile** for Vistex Chemicals Ltd at the
   Industrial Area address, with the same phone number and the website link. For
   "cleaning chemicals Nairobi"-type searches the map pack sits above every
   ordinary result, and it is driven by the Business Profile, not the website.

**Then, monthly:** Search Console → *Performance* shows which searches bring
impressions; *Pages* shows anything excluded and why. After any content change run
`node tools/build-pages.js`, upload, and resubmit the sitemap.

---

## After go-live

- [ ] Search Console + Bing + Google Business Profile, as above.
- [ ] Confirm HTTPS works on every subdomain, then uncomment the HSTS header in `.htaccess`.
- [ ] Get the remaining 38 product photos — see `PHOTO-BRIEF.md`.
- [ ] Ask Vistex for the SDS (safety data sheet) of each product; hospital and food-plant
      procurement asks for it, and only TDS have been supplied so far.
- [ ] Ask for corrected **Drain Care** and **Toilet Cleaner** TDS (see `Updates/INTAKE.md`)
      so they can be published like the other three.
- [ ] Get real dilution / temperature figures for the rest of the catalogue.
- [ ] Ask the client for vector (SVG) logos; the PNGs are now right-sized but a vector
      would be sharper on high-density screens.