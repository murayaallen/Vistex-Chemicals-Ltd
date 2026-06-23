# Vistex Chemicals — Website (HTML / CSS / JS)

A plain static website (no framework, no build step) for **Vistex Chemicals Ltd**.
Bright "clinical clean" art direction with a light/dark theme toggle, scroll
animations, and a WhatsApp enquiry cart. Inspired by the Cloud Paints V2 build.

## How it works (no React, but still DRY)
- Every page is plain HTML with `<body data-page="...">`.
- `js/partials.js` **injects** the shared header, footer and cart drawer into every
  page, and wires the theme toggle + mobile menu.
- `js/data.js` holds all company info, systems and products on `window.VISTEX`.
- `js/cart.js` is the enquiry cart (localStorage) → builds a pre-filled WhatsApp
  message. `js/motion.js` does scroll reveals + hero bubbles.
- Catalog/product pages render from the data: `js/catalog.js`, `js/product.js`.

## Run locally
No build needed. Just serve the folder, e.g.:
```bash
python -m http.server 8080     # then open http://127.0.0.1:8080
```
(Opening index.html directly via file:// also mostly works, but a server is better.)

## Deploy to DirectAdmin
Upload the **entire contents of this folder** (including `.htaccess`) into
`public_html`. Done — it's all static files.

## Files
- `index.html` (home), `systems.html`, `product.html`, `industries.html`,
  `about.html`, `contact.html`, `404.html`
- `css/` → `main.css` (design system + components), `motion.css`, `home.css`
- `js/`  → `data.js`, `partials.js`, `cart.js`, `motion.js`, `catalog.js`, `product.js`, `home.js`
- `images/` → logos + product photos

## Edit content
- Company details / WhatsApp number: `js/data.js` (`company`).
- Products & systems: `js/data.js` (`products`, `systems`).
- Brand colours: CSS variables in `css/main.css` `:root` (and `[data-theme="dark"]`).

## TODO before go-live
- Vector/transparent logos from client.
- Product photos for housekeeping, kitchen, pool & toiletries.
- Confirm canonical SKU list & contact details.
- Generate a real `sitemap.xml`.
