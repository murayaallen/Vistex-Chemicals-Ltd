#!/usr/bin/env node
// ==========================================================
// VISTEX — static page generator
//
//   node tools/build-pages.js
//
// Run after editing js/data.js. No dependencies, no npm install.
// Writes, from the data:
//   product-<id>.html   one real page per product (68+)
//   <range-slug>.html   one landing page per range (laundry-chemicals.html …)
//   systems.html        the crawlable product list between the GEN markers
//   sitemap.xml         every indexable URL, with product images
//   *.html              ?v=<hash> on every css/js link (cache busting)
//
// Why static pages at all: Google advises against rewriting a canonical with
// JavaScript, and WhatsApp / Facebook / LinkedIn link previews never run
// JavaScript. Before this, all products shared one product.html whose
// canonical pointed at itself, so search engines saw one page, and every
// product link pasted into WhatsApp previewed as "Product — Vistex".
// The output is committed, so deploying is still "upload the folder".
// ==========================================================
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const rd = (f) => fs.readFileSync(path.join(ROOT, f), 'utf8');
const wr = (f, s) => fs.writeFileSync(path.join(ROOT, f), s);

// ---------- load the data exactly as the browser does ----------
const sandbox = { window: {} };
vm.runInNewContext(rd('js/data.js'), sandbox);
const V = sandbox.window.VISTEX;
const co = V.company;
const ORIGIN = co.origin;
const TODAY = new Date().toISOString().slice(0, 10);

const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;');
// Meta descriptions must survive Google's ~155-char snippet; cut on a word.
function clip(t, n) {
  if (t.length <= n) return t;
  const cut = t.slice(0, n);
  const sp = cut.lastIndexOf(' ');
  return (sp > n * 0.6 ? cut.slice(0, sp) : cut).replace(/[\s,;:.—-]+$/, '') + '…';
}
const fullName = (p) => p.name + (p.code ? ' ' + p.code : '');
const SMALL = /^(a|an|and|or|for|of|the|to|with|in|on|&|—)$/i;
const titleCase = (t) => t.split(' ').map((w, i) =>
  i && SMALL.test(w) ? w.toLowerCase() : w.replace(/(^|-)([a-z])/g, (m, a, b) => a + b.toUpperCase())).join(' ');
const abs = (u) => ORIGIN + '/' + u;

// ---------- head rewriting ----------
// Each helper swaps one tag's value in a template head. They throw if the tag
// is missing, so a template edit that drops a tag fails the build loudly.
function setTag(html, re, replacement, label) {
  if (!re.test(html)) throw new Error('template is missing ' + label);
  return html.replace(re, replacement);
}
function setHead(html, h) {
  html = setTag(html, /<title>[^<]*<\/title>/, '<title>' + esc(h.title) + '</title>', 'title');
  html = setTag(html, /<meta name="description" content="[^"]*">/, '<meta name="description" content="' + esc(h.desc) + '">', 'description');
  html = setTag(html, /<meta name="keywords" content="[^"]*">/, '<meta name="keywords" content="' + esc(h.keywords) + '">', 'keywords');
  html = setTag(html, /<link rel="canonical" href="[^"]*">/, '<link rel="canonical" href="' + h.url + '">', 'canonical');
  html = html.replace(/<link rel="alternate" hreflang="([^"]+)" href="[^"]*">/g, '<link rel="alternate" hreflang="$1" href="' + h.url + '">');
  html = setTag(html, /<meta property="og:type" content="[^"]*">/, '<meta property="og:type" content="' + h.ogType + '">', 'og:type');
  html = html.replace(/<meta property="og:url" content="[^"]*">\n?/, '');
  html = html.replace('<meta property="og:site_name"', '<meta property="og:url" content="' + h.url + '">\n<meta property="og:site_name"');
  html = setTag(html, /<meta property="og:title" content="[^"]*">/, '<meta property="og:title" content="' + esc(h.ogTitle) + '">', 'og:title');
  html = setTag(html, /<meta property="og:description" content="[^"]*">/, '<meta property="og:description" content="' + esc(h.ogDesc) + '">', 'og:description');
  html = setTag(html, /<meta property="og:image" content="[^"]*">/, '<meta property="og:image" content="' + h.img + '">', 'og:image');
  html = setTag(html, /<meta property="og:image:alt" content="[^"]*">/, '<meta property="og:image:alt" content="' + esc(h.imgAlt) + '">', 'og:image:alt');
  html = setTag(html, /<meta property="og:image:height" content="[^"]*">/, '<meta property="og:image:height" content="' + h.imgH + '">', 'og:image:height');
  html = setTag(html, /<meta property="og:image:width" content="[^"]*">/, '<meta property="og:image:width" content="' + h.imgW + '">', 'og:image:width');
  html = setTag(html, /<meta name="twitter:card" content="[^"]*">/, '<meta name="twitter:card" content="' + h.card + '">', 'twitter:card');
  html = setTag(html, /<meta name="twitter:image" content="[^"]*">/, '<meta name="twitter:image" content="' + h.img + '">', 'twitter:image');
  html = setTag(html, /<meta name="twitter:image:alt" content="[^"]*">/, '<meta name="twitter:image:alt" content="' + esc(h.imgAlt) + '">', 'twitter:image:alt');
  // one JSON-LD block, replacing whatever the template carried
  html = html.replace(/\n?<script type="application\/ld\+json">[\s\S]*?<\/script>\n?/g, '\n');
  html = html.replace('</head>', '<script type="application/ld+json">\n' + JSON.stringify(h.ld, null, 1) + '\n</script>\n</head>');
  // a generated page is never the noindex forwarder its template may be —
  // drop the robots tag and the template note that explains it
  html = html.replace(/<meta name="robots" content="[^"]*">\n?/, '');
  html = html.replace(/<!-- This file is two things\.[\s\S]*?-->\n?/, '');
  return html;
}

const ORG = { '@type': 'Organization', '@id': ORIGIN + '/#org', name: co.name, url: ORIGIN + '/' };
function crumbs(list) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: list.map((c, i) => ({ '@type': 'ListItem', position: i + 1, name: c[0], item: c[1] }))
  };
}

// ---------- product pages ----------
const productTpl = rd('product.html');
const written = [];

function productStatic(p, s) {
  // The crawlable, no-JavaScript version of the page. product.js replaces it
  // with the interactive one on load; the content is the same record.
  const rows = [
    ['Pack size', p.pack], ['Form', p.form], ['pH', p.ph], ['Dilution', p.dilution],
    ['Temperature', p.temp], ['Active ingredient', p.active], ['Shelf life', p.shelfLife],
    ['Range', s.name], ['Brand', co.productBrand + (p.supplied ? ' — supplied by ' : ' — made by ') + co.name]
  ].filter((r) => r[1]);
  const list = (title, items) => items && items.length
    ? '<h2 class="h-sub" style="margin-top:32px">' + esc(title) + '</h2><ul class="uses-list">' +
      items.map((t) => '<li>' + esc(t) + '</li>').join('') + '</ul>' : '';
  return (
    '<nav class="crumbs" aria-label="Breadcrumb"><a href="systems.html">Our Range</a><span class="sep">/</span>' +
      '<a href="' + V.rangeUrl(s) + '">' + esc(s.short) + '</a><span class="sep">/</span><span>' + esc(p.name) + '</span></nav>' +
    '<article class="pd-static" style="margin-top:32px;max-width:72ch">' +
      '<span class="eyebrow">' + esc(s.name) + '</span>' +
      '<h1 class="pd-title" style="margin-top:16px">' + esc(p.name) + '</h1>' +
      (p.subtitle ? '<p class="pd-sub">' + esc(p.subtitle) + '</p>' : '') +
      (p.image ? '<img src="' + p.image + '" alt="' + esc(fullName(p)) + '" width="800" height="800" style="max-width:320px;height:auto;margin-top:24px;border-radius:16px">' : '') +
      '<p class="lede" style="margin-top:24px">' + esc(p.purpose) + '</p>' +
      '<dl class="spec" style="margin-top:24px">' + rows.map((r) =>
        '<div class="spec-row"><dt>' + esc(r[0]) + '</dt><dd>' + esc(r[1]) + '</dd></div>').join('') + '</dl>' +
      list('Features', p.features) +
      (p.directions ? '<h2 class="h-sub" style="margin-top:32px">How to use</h2><ol class="pd-steps">' +
        p.directions.map((d) => '<li>' + esc(d) + '</li>').join('') + '</ol>' : '') +
      (p.dilutions ? '<h2 class="h-sub" style="margin-top:32px">Dosing guide</h2><table class="dose-table"><tbody>' +
        p.dilutions.map((r) => '<tr><th scope="row">' + esc(r[0]) + '</th><td>' + esc(r[1]) + '</td></tr>').join('') + '</tbody></table>' : '') +
      list('Ideal applications', p.applications) +
      list('Suitable for', (p.fabrics || []).concat(p.surfaces || [])) +
      list('Not for use on', p.notFor) +
      (p.hazard ? '<p class="pd-safety" style="margin-top:32px"><strong>' + esc(p.hazard.word || p.hazard.level) + ':</strong> ' + esc(p.hazard.text) + '</p>' : '') +
      (p.docs ? '<p style="margin-top:24px">' + p.docs.map((d) => '<a href="' + d.file + '">' + esc(d.label) + ' (' + esc(d.kind || 'PDF') + ')</a>').join(' · ') + '</p>' : '') +
      '<p style="margin-top:32px">' + (p.supplied ? 'Supplied across Kenya by ' + esc(co.name) + ', Nairobi, as part of the ' + esc(co.productBrand) + ' guest range.'
        : 'Manufactured in Nairobi, Kenya by ' + esc(co.name) + ' under the ' + esc(co.productBrand) + ' brand.') +
        ' <a href="contact.html">Request a quote</a> or call <a href="tel:+' + co.phoneIntl + '">' + esc(co.phoneDisplay) + '</a>.</p>' +
    '</article>'
  );
}

V.products.forEach((p) => {
  const s = V.getSystem(p.system);
  const file = V.productUrl(p);
  const url = abs(file);
  const name = fullName(p);
  // "Drain Care — Heavy-Duty Powder Drain Opener | Vistex Kenya": the product,
  // what it is in the buyer's own words, and where. Falls back to the range
  // name when the subtitle would push past what Google shows (~65 chars).
  // First candidate that fits in ~68 characters wins.
  const sub = p.subtitle ? titleCase(p.subtitle) : null;
  const title = [
    sub && name + ' — ' + sub + ' | Vistex Kenya',
    sub && name + ' — ' + sub + ' | Vistex',
    sub && name + ' — ' + sub,
    name + ' — ' + s.short + ' | Vistex Kenya'
  ].filter((t) => t && t.length <= 68)[0] || name + ' | Vistex Kenya';
  // Name + what it is + the first sentence of the purpose + where it is made,
  // so the snippet ends on the Kenyan-manufacturer line rather than an ellipsis.
  // The subtitle is the first thing dropped when the sentence needs the room.
  const first = p.purpose.split(/(?<=[.!?])\s+/)[0];
  const tail = p.supplied ? ' Supplied across Kenya by Vistex Chemicals.' : ' Made in Kenya by Vistex Chemicals.';
  const desc = [
    p.subtitle && name + ': ' + p.subtitle + '. ' + first + tail,
    name + '. ' + first + tail
  ].filter((d) => d && d.length <= 160)[0] || clip(name + '. ' + first, 158 - tail.length) + tail;
  const keywords = [p.name, p.subtitle, p.name + ' Kenya', (p.subtitle || s.short) + ' Nairobi',
    s.short.toLowerCase() + ' chemicals Kenya', 'Swift ' + p.name, 'Vistex Chemicals'].filter(Boolean).join(', ');
  // Square packshots go out as a square "summary" card; the 1200x630 branded
  // banner is kept for products without a photograph.
  const img = p.image
    ? { img: abs(p.image), imgW: 800, imgH: 800, card: 'summary' }
    : { img: abs('images/share/share-range.jpg'), imgW: 1200, imgH: 630, card: 'summary_large_image' };
  const ld = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'Product', '@id': url + '#product', name, url,
        sku: p.code || p.id,
        description: p.purpose,
        category: s.name,
        brand: { '@type': 'Brand', name: co.productBrand },
        // Only claim manufacture for what Vistex makes; bought-in amenities are sold, not made.
        [p.supplied ? 'seller' : 'manufacturer']: ORG,
        image: p.image ? [abs(p.image)].concat((p.gallery || []).map((g) => abs(g.src))) : abs('images/share/share-range.jpg'),
        additionalProperty: [
          ['Pack size', p.pack], ['Form', p.form], ['pH', p.ph], ['Dilution', p.dilution],
          ['Temperature', p.temp], ['Active ingredient', p.active], ['Shelf life', p.shelfLife]
        ].filter((r) => r[1] && r[1] !== 'On request').map((r) => ({ '@type': 'PropertyValue', name: r[0], value: r[1] }))
        // No `offers`: pricing is quoted per property and Offer requires a price.
      },
      crumbs([['Home', ORIGIN + '/'], ['Our Range', abs('systems.html')], [s.name, abs(V.rangeUrl(s))], [p.name, url]])
    ]
  };
  let html = setHead(productTpl, {
    title, desc, keywords, url, ogType: 'product',
    ogTitle: name + ' — ' + co.productBrand + ' by Vistex Chemicals',
    ogDesc: clip(p.purpose, 200),
    imgAlt: name + ' — a ' + co.productBrand + (p.supplied ? ' guest amenity supplied by ' : ' product made by ') + co.name + ' in Nairobi',
    ld, ...img
  });
  html = html.replace('<body data-page="product">', '<body data-page="product" data-pid="' + p.id + '">');
  html = html.replace(/<div class="container" id="productRoot">[\s\S]*?<\/div>\n<\/main>/,
    '<div class="container" id="productRoot">' + productStatic(p, s) + '</div>\n</main>');
  wr(file, html);
  written.push(file);
});

// ---------- range pages ----------
const systemsTpl = rd('systems.html');
function staticList(list) {
  return '<ul class="gen-list">' + list.map((p) =>
    '<li><a href="' + V.productUrl(p) + '">' + esc(fullName(p)) + '</a>' +
    (p.subtitle ? ' — ' + esc(p.subtitle) : '') + '</li>').join('') + '</ul>';
}
function fillList(html, inner) {
  const re = /<!-- GEN:list -->[\s\S]*?<!-- \/GEN:list -->/;
  if (!re.test(html)) throw new Error('systems.html is missing the GEN:list markers');
  return html.replace(re, '<!-- GEN:list -->' + inner + '<!-- /GEN:list -->');
}

V.systems.forEach((s) => {
  const file = V.rangeUrl(s);
  const url = abs(file);
  const list = V.bySystem(s.key);
  const ld = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'CollectionPage', '@id': url + '#page', url, name: s.seoTitle, description: s.seoDesc,
        isPartOf: { '@id': ORIGIN + '/#site' }, about: s.name,
        mainEntity: {
          '@type': 'ItemList', numberOfItems: list.length,
          itemListElement: list.map((p, i) => ({ '@type': 'ListItem', position: i + 1, name: fullName(p), url: abs(V.productUrl(p)) }))
        }
      },
      crumbs([['Home', ORIGIN + '/'], ['Our Range', abs('systems.html')], [s.name, url]])
    ]
  };
  let html = setHead(systemsTpl, {
    title: s.seoTitle + ' | Vistex', desc: s.seoDesc,
    keywords: [s.seoTitle.split(' — ')[0], s.short.toLowerCase() + ' chemicals Kenya', s.short.toLowerCase() + ' supplies Nairobi',
      list.slice(0, 6).map((p) => p.name).join(', '), 'Swift', 'Vistex Chemicals'].join(', '),
    url, ogType: 'website', ogTitle: s.name + ' — Vistex Chemicals', ogDesc: s.seoDesc,
    img: abs('images/share/share-range.jpg'), imgW: 1200, imgH: 630, card: 'summary_large_image',
    imgAlt: s.name + ' — ' + list.length + ' Swift products made in Nairobi by ' + co.name, ld
  });
  html = html.replace('<body data-page="systems">', '<body data-page="systems" data-system="' + s.key + '">');
  html = setTag(html, /(<h1 class="h-display" id="catTitle"[^>]*>)[^<]*(<\/h1>)/, '$1' + esc(s.name) + '$2', 'catTitle');
  html = setTag(html, /(<p class="lede measure" id="catLede"[^>]*>)[^<]*(<\/p>)/, '$1' + esc(s.description) + '$2', 'catLede');
  html = fillList(html, staticList(list));
  wr(file, html);
  written.push(file);
});

// ---------- systems.html: its own crawlable list + live counts ----------
{
  let html = fillList(systemsTpl, staticList(V.products));
  const n = V.products.length;
  html = html.replace(/\b\d+\+? professional products\b/g, n + ' professional products');
  html = html.replace(/"numberOfItems": ?\d+/, '"numberOfItems": ' + n);
  wr('systems.html', html);
}

// ---------- sitemap ----------
{
  const pages = [
    ['', '1.0', 'monthly'], ['systems.html', '0.9', 'monthly'], ['industries.html', '0.8', 'monthly'],
    ['about.html', '0.7', 'yearly'], ['contact.html', '0.8', 'yearly']
  ];
  const url = (loc, pr, cf, imgs) =>
    '  <url><loc>' + esc(loc) + '</loc><lastmod>' + TODAY + '</lastmod><changefreq>' + cf + '</changefreq><priority>' + pr + '</priority>' +
    (imgs || []).map((i) => '<image:image><image:loc>' + esc(i) + '</image:loc></image:image>').join('') + '</url>';
  const out = ['<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'];
  pages.forEach((p) => out.push(url(abs(p[0]), p[1], p[2])));
  V.systems.forEach((s) => out.push(url(abs(V.rangeUrl(s)), '0.8', 'monthly')));
  V.products.forEach((p) => out.push(url(abs(V.productUrl(p)), p.image ? '0.7' : '0.5', 'monthly',
    p.image ? [abs(p.image)].concat((p.gallery || []).map((g) => abs(g.src))) : [])));
  out.push('</urlset>', '');
  wr('sitemap.xml', out.join('\n'));
}

// ---------- cache busting ----------
// .htaccess caches css/js for a month, so without this a returning visitor
// would pair new HTML with last month's stylesheet. The hash only changes
// when the assets actually change.
{
  const assets = fs.readdirSync(path.join(ROOT, 'css')).map((f) => 'css/' + f)
    .concat(fs.readdirSync(path.join(ROOT, 'js')).map((f) => 'js/' + f));
  const h = crypto.createHash('sha1');
  assets.sort().forEach((a) => h.update(rd(a)));
  const ver = h.digest('hex').slice(0, 10);
  const htmlFiles = fs.readdirSync(ROOT).filter((f) => f.endsWith('.html') && !f.startsWith('preview-'));
  htmlFiles.forEach((f) => {
    const s = rd(f);
    const t = s.replace(/((?:href|src)="(?:css|js)\/[\w.-]+\.(?:css|js))(?:\?v=[\w]+)?"/g, '$1?v=' + ver + '"');
    if (t !== s) wr(f, t);
  });
  console.log('asset version', ver, 'stamped on', htmlFiles.length, 'pages');
}

// ---------- tidy: remove pages for products that no longer exist ----------
fs.readdirSync(ROOT).filter((f) => /^product-.+\.html$/.test(f) && written.indexOf(f) < 0)
  .forEach((f) => { fs.unlinkSync(path.join(ROOT, f)); console.log('removed stale', f); });

console.log('wrote', written.length, 'pages +', 'systems.html, sitemap.xml —', V.products.length, 'products,', V.systems.length, 'ranges');
