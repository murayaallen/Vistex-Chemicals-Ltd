// ==========================================================
// VISTEX — Product detail (product-<id>.html)
// Renders the full interactive record over the static summary that
// tools/build-pages.js bakes into each page. Title, description,
// canonical, share tags and JSON-LD are all in that static HTML —
// Google advises against rewriting a canonical with JavaScript, and
// WhatsApp link previews never run it — so nothing here touches <head>.
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX, co = V.company, icon = window.icon, esc = window.vxEsc;
  var root = document.getElementById('productRoot');
  var id = document.body.dataset.pid || new URLSearchParams(location.search).get('id');
  var p = id ? V.getProduct(id) : null;

  // The old product.html?id=… address still works for links already shared
  // on WhatsApp or saved in enquiries: it forwards to the real page.
  if (p && !document.body.dataset.pid) {
    location.replace(V.productUrl(p));
    return;
  }

  if (!p) {
    root.innerHTML =
      '<div class="nf">' +
        '<div><div class="label">404</div>' +
        '<h1 class="h-section" style="margin-top:12px">We couldn’t find that product</h1>' +
        '<p class="lede" style="margin-top:10px">It may have been renamed or retired.</p>' +
        '<a class="btn btn-primary" href="systems.html" style="margin-top:24px">Browse the catalogue</a></div>' +
      '</div>';
    return;
  }

  var s = V.getSystem(p.system);
  var fullName = p.name + (p.code ? ' ' + p.code : '');

  // ---------- Scent variants ----------
  // Only the urinal mat has these today, but the shape is generic: any product
  // that ships in several colourways can declare `scents` and get the picker.
  var scents = p.scents && p.scents.length ? p.scents : null;
  function scentImg(sid) { return 'images/products/' + p.id + '-' + sid + '.jpeg'; }

  var picker = scents
    ? '<div class="scent" role="radiogroup" aria-label="Scent">' +
        '<div class="scent-head"><span class="label">Scent</span>' +
          '<span class="scent-now" id="scentNow">' + esc(scents[0].name) + '</span></div>' +
        '<div class="scent-chips">' + scents.map(function (sc, i) {
          return '<button type="button" class="scent-chip' + (i === 0 ? ' on' : '') + '"' +
            ' role="radio" aria-checked="' + (i === 0) + '"' +
            ' data-scent="' + esc(sc.id) + '" data-name="' + esc(sc.name) + '"' +
            ' style="--sw:' + esc(sc.hex) + '" title="' + esc(sc.name) + '">' +
            '<span class="visually-hidden">' + esc(sc.name) + '</span></button>';
        }).join('') + '</div>' +
      '</div>'
    : '';

  // ---------- Media ----------
  // A product with a `gallery` gets a thumbnail strip under the main image;
  // the first thumb is the main image itself so the visitor can always get
  // back to it. Thumbnails come from images/thumbs/, never the 800px files.
  var views = p.image
    ? [{ src: p.image, alt: fullName }].concat(p.gallery || [])
    : [];
  function thumbOf(src) { return src.replace(/^images\//, 'images/thumbs/'); }

  var media = p.image
    ? window.vxPicture(p.image, fullName, { w: 800, h: 800, eager: true })
    : '<div class="pcard-noimg" style="position:relative">' +
        '<span class="drop">' + icon('bottle', 52) + '</span>' +
        '<span class="nm" style="font-size:var(--step-1)">' + esc(p.name) + '</span>' +
        '<span class="swift-badge swift-badge--md sb-badge">' +
          window.vxPicture(co.productBrandLogo, co.productBrand, { w: 760, h: 425 }) +
        '</span>' +
      '</div>';

  var thumbs = views.length > 1
    ? '<div class="pd-thumbs" role="group" aria-label="Product views">' + views.map(function (v, i) {
        return '<button type="button" class="pd-thumb' + (i === 0 ? ' on' : '') + '"' +
          ' aria-pressed="' + (i === 0) + '" data-view="' + i + '"' +
          ' aria-label="View ' + (i + 1) + ' of ' + views.length + ': ' + esc(v.alt) + '">' +
          window.vxPicture(thumbOf(v.src), '', { w: 360, h: 360 }) +
        '</button>';
      }).join('') + '</div>'
    : '';

  // ---------- Spec table: only the rows that exist ----------
  var rows = [
    ['Pack size', p.pack, 'package'],
    ['Form', p.form, 'beaker'],
    ['pH', p.ph, 'droplet'],
    ['Dilution', p.dilution, 'scale'],
    ['Temperature', p.temp, 'thermometer'],
    ['Active ingredient', p.active, 'beaker'],
    ['Shelf life', p.shelfLife, 'clock'],
    ['Range', s.name, s.icon],
    ['Brand', null, 'sparkle']       // rendered as the badge below, not text
  ].filter(function (r) { return r[1]; });

  if (scents) rows.push(['Scents', String(scents.length) + ' available', 'sparkle']);

  var spec = '<dl class="spec">' + rows.map(function (r) {
    return '<div class="spec-row"><dt>' + esc(r[0]) + '</dt><dd>' + esc(r[1]) + '</dd></div>';
  }).join('') +
    // Brand is the one row that is a mark rather than a value
    '<div class="spec-row"><dt>Brand</dt><dd>' +
      '<span class="swift-badge swift-badge--md">' +
        window.vxPicture(co.productBrandLogo, co.productBrand + ' — ' + co.productBrandTagline, { w: 760, h: 425 }) +
      '</span>' +
      '<span class="spec-brand-note">' + (p.supplied ? 'Supplied by ' : 'Made by ') + esc(co.name) + '</span>' +
    '</dd></div>' +
  '</dl>';

  var features = (p.features && p.features.length)
    ? '<div class="row" style="gap:8px">' + p.features.map(function (f) {
        return '<span class="chip chip--accent">' + icon('check', 14) + esc(f) + '</span>';
      }).join('') + '</div>'
    : '';

  // ---------- Documents ----------
  // Generic and additive: a product declaring `docs: [{label, file, kind}]`
  // gets a download row. Files live in docs/ and are plain static assets, so
  // this needs no build step — the row simply does not render until one exists.
  // Procurement for hospitals and food plants often gates on an SDS being
  // available, so this is the slot it goes in.
  var docs = (p.docs && p.docs.length)
    ? '<div class="pd-docs">' +
        '<span class="label">Documents</span>' +
        '<div class="pd-docs-row">' + p.docs.map(function (d) {
          return '<a class="doc-chip" href="' + esc(d.file) + '" download>' +
            icon('download', 15) +
            '<span class="doc-name">' + esc(d.label) + '</span>' +
            '<span class="doc-kind">' + esc(d.kind || 'PDF') + '</span>' +
          '</a>';
        }).join('') + '</div>' +
      '</div>'
    : '';

  // ---------- Where it is used ----------
  // Generic: any product declaring `applications` (environments), `fabrics` /
  // `surfaces` (what it may be used on) or `notFor` gets this block. Columns
  // only render when they have content, so the grid never shows a blank.
  function useList(title, items, ico, mod) {
    if (!items || !items.length) return '';
    return '<div class="uses-col' + (mod ? ' uses-col--' + mod : '') + '">' +
      '<h3 class="uses-title">' + icon(ico, 16) + esc(title) + '</h3>' +
      '<ul class="uses-list">' + items.map(function (t) {
        return '<li>' + esc(t) + '</li>';
      }).join('') + '</ul>' +
    '</div>';
  }
  var suitable = (p.fabrics || []).concat(p.surfaces || []);
  var useCols = [
    useList('Ideal applications', p.applications, 'building'),
    useList('Suitable for', suitable, p.fabrics ? 'washer' : 'check'),
    useList('Not for use on', p.notFor, 'x', 'no')
  ].filter(Boolean);
  var usesBlock = useCols.length
    ? '<section class="uses uses--' + useCols.length + ' card card-pad" data-anim="up">' +
        useCols.join('') +
      '</section>'
    : '';

  // ---------- How to use + dosing ----------
  // Directions are numbered steps; `dilutions` is a two-column dosing table.
  // Both come verbatim from a TDS or label — see the source note in data.js.
  var howBlock = (p.directions && p.directions.length)
    ? '<div class="card card-pad pd-how" data-anim="up">' +
        '<h2 class="h-sub">How to use</h2>' +
        '<ol class="pd-steps">' + p.directions.map(function (d) {
          return '<li>' + esc(d) + '</li>';
        }).join('') + '</ol>' +
      '</div>'
    : '';
  var doseBlock = (p.dilutions && p.dilutions.length)
    ? '<div class="card card-pad pd-dose" data-anim="up">' +
        '<h2 class="h-sub">Dosing guide</h2>' +
        '<table class="dose-table"><thead><tr><th scope="col">Application</th><th scope="col">Dilution</th></tr></thead><tbody>' +
          p.dilutions.map(function (r) {
            return '<tr><th scope="row">' + esc(r[0]) + '</th><td>' + esc(r[1]) + '</td></tr>';
          }).join('') +
        '</tbody></table>' +
        '<p class="pd-note" style="margin-top:var(--s-4)">Product : water. Clean heavily soiled surfaces first, and allow full contact time before wiping.</p>' +
      '</div>'
    : '';
  var techBlock = (howBlock || doseBlock)
    ? '<section class="pd-tech' + (howBlock && doseBlock ? ' pd-tech--2' : '') + '">' + howBlock + doseBlock + '</section>'
    : '';

  // ---------- Safety ----------
  // A product with a supplied hazard statement shows it with the signal word
  // printed on its own label (Danger / Warning / Caution) and its "never mix"
  // list. Everything else keeps the general handling note.
  var hz = p.hazard;
  var safety = hz
    ? '<div class="pd-safety pd-safety--' + esc(hz.level) + '" role="note">' + icon('alert', 18) +
        '<div class="hz-body">' +
          '<strong class="hz-word">' + esc(hz.word || hz.level) + '</strong>' +
          '<p>' + esc(hz.text) + '</p>' +
          (p.neverMix && p.neverMix.length
            ? '<div class="hz-mix"><span class="hz-mix-label">Never mix with</span>' +
                p.neverMix.map(function (m) { return '<span class="hz-chip">' + esc(m) + '</span>'; }).join('') +
              '</div>'
            : '') +
          '<p class="hz-foot">For trained staff. Keep out of reach of children.</p>' +
        '</div>' +
      '</div>'
    // Guest amenities (slippers, dental kits, shower gel…) are not handled like
    // chemicals, so the gloves-and-goggles note would be nonsense on them.
    : p.system === 'toiletries' ? ''
    : '<div class="pd-safety">' + icon('alert', 18) +
        '<span><strong>Handling:</strong> ' + esc(co.safetyNote) + '</span></div>';

  // ---------- Render ----------
  root.innerHTML =
    '<nav class="crumbs" aria-label="Breadcrumb">' +
      '<a href="systems.html">Our Range</a><span class="sep">/</span>' +
      '<a href="' + V.rangeUrl(s) + '">' + esc(s.short) + '</a><span class="sep">/</span>' +
      '<span style="color:var(--text-2)">' + esc(p.name) + '</span>' +
    '</nav>' +

    '<div class="pd-grid" style="margin-top:var(--s-7)">' +
      '<div class="pd-media-col" data-anim="left">' +
        '<div class="pd-media">' + media + '</div>' +
        thumbs +
      '</div>' +

      '<div class="stack-6" data-anim="right">' +
        '<div>' +
          '<span class="eyebrow">' + esc(s.name) + '</span>' +
          '<h1 class="pd-title" style="margin-top:var(--s-4)">' + esc(p.name) + '</h1>' +
          (p.subtitle ? '<p class="pd-sub">' + esc(p.subtitle) + '</p>' : '') +
          (p.code ? '<div style="margin-top:var(--s-4)"><span class="badge badge--signal">' +
            icon('clipboard', 14) + 'Code ' + esc(p.code) + '</span></div>' : '') +
        '</div>' +

        '<p class="lede">' + esc(p.purpose) + '</p>' +
        features +
        picker +
        spec +

        '<div class="pd-buy">' +
          '<div class="qty pd-qty">' +
            '<button id="pdDec" aria-label="Decrease quantity">−</button>' +
            '<span id="pdQty" aria-live="polite">1</span>' +
            '<button id="pdInc" aria-label="Increase quantity">+</button>' +
          '</div>' +
          '<button class="btn btn-primary" id="pdAdd" style="flex:1;min-width:200px">' +
            icon('plus', 16) + 'Add to enquiry</button>' +
        '</div>' +

        '<p class="pd-note">Pricing is quoted per property. Add what you need and our team will come back with a costed programme — usually the same working day.</p>' +

        docs +
        safety +
      '</div>' +
    '</div>';

  // ---------- Technical detail + where it is used ----------
  [techBlock, usesBlock].forEach(function (html) {
    if (!html) return;
    var host = document.createElement('div');
    host.innerHTML = html;
    root.appendChild(host.firstChild);
  });

  // ---------- Gallery ----------
  if (thumbs) {
    var tBtns = [].slice.call(root.querySelectorAll('.pd-thumb'));
    var gImg = root.querySelector('.pd-media img');
    var gSrc = root.querySelector('.pd-media source');
    tBtns.forEach(function (b) {
      b.addEventListener('click', function () {
        var v = views[+b.dataset.view];
        tBtns.forEach(function (x) {
          var on = x === b;
          x.classList.toggle('on', on);
          x.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        if (gSrc) gSrc.srcset = v.src.replace(/\.(jpe?g|png)$/i, '.webp');
        if (gImg) { gImg.src = v.src; gImg.alt = v.alt; }
      });
    });
  }

  // ---------- Scent picker ----------
  if (scents) {
    var chips = [].slice.call(root.querySelectorAll('.scent-chip'));
    var nowEl = document.getElementById('scentNow');
    var mediaImg = root.querySelector('.pd-media img');
    var mediaSrc = root.querySelector('.pd-media source');

    // Warm the other scents so the swap is instant rather than a white flash.
    scents.slice(1).forEach(function (sc) {
      var pre = new Image();
      pre.src = scentImg(sc.id).replace('.jpeg', '.webp');
    });

    function pick(chip) {
      var sid = chip.dataset.scent;
      chips.forEach(function (c) {
        var on = c === chip;
        c.classList.toggle('on', on);
        c.setAttribute('aria-checked', on ? 'true' : 'false');
        c.tabIndex = on ? 0 : -1;
      });
      nowEl.textContent = chip.dataset.name;
      if (mediaSrc) mediaSrc.srcset = scentImg(sid).replace('.jpeg', '.webp');
      if (mediaImg) {
        mediaImg.src = scentImg(sid);
        mediaImg.alt = fullName + ' — ' + chip.dataset.name;
      }
    }
    chips.forEach(function (c, i) {
      c.tabIndex = i === 0 ? 0 : -1;
      c.addEventListener('click', function () { pick(c); });
    });
    // Arrow keys move within the group, which is what a radiogroup must do.
    root.querySelector('.scent-chips').addEventListener('keydown', function (e) {
      var i = chips.indexOf(document.activeElement);
      if (i < 0) return;
      var d = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1
            : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0;
      if (!d) return;
      e.preventDefault();
      var n = chips[(i + d + chips.length) % chips.length];
      n.focus(); pick(n);
    });
  }

  // ---------- Quantity + add ----------
  var qty = 1;
  var qEl = document.getElementById('pdQty');
  document.getElementById('pdInc').addEventListener('click', function () { qty++; qEl.textContent = qty; });
  document.getElementById('pdDec').addEventListener('click', function () { qty = Math.max(1, qty - 1); qEl.textContent = qty; });
  document.getElementById('pdAdd').addEventListener('click', function () {
    window.VistexCart.add(p.id, qty);
    window.VistexCart.open();
  });

  // ---------- Related ----------
  // Photographed products first — a row of four placeholders sells nothing.
  // Array.prototype.sort is stable, so catalogue order holds within each group.
  var related = V.bySystem(p.system).filter(function (x) { return x.id !== p.id; })
    .sort(function (a, b) { return (b.image ? 1 : 0) - (a.image ? 1 : 0); })
    .slice(0, 4);
  if (related.length) {
    var rel = document.createElement('section');
    rel.style.marginTop = 'var(--s-11)';
    rel.innerHTML =
      '<div class="sec-head" style="margin-bottom:var(--s-6)">' +
        '<span class="eyebrow">Same range</span>' +
        '<h2 class="h-sub">More from ' + esc(s.short) + '</h2>' +
      '</div>' +
      '<div class="grid grid-4 reveal-parent">' + related.map(window.productCardHtml).join('') + '</div>';
    root.appendChild(rel);
  }

  if (window.VistexMotion) window.VistexMotion.refresh(root);
})();
