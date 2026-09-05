// ==========================================================
// VISTEX — Product detail (product.html?id=…)
// Renders the record, prints only the spec rows that exist,
// and updates title / description / canonical / JSON-LD so the
// page is meaningful when shared or crawled.
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX, co = V.company, icon = window.icon, esc = window.vxEsc;
  var root = document.getElementById('productRoot');
  var id = new URLSearchParams(location.search).get('id');
  var p = id ? V.getProduct(id) : null;

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

  // ---------- Head: title, description, canonical, JSON-LD ----------
  document.title = fullName + ' — ' + s.short + ' — Vistex Chemicals Ltd';
  function meta(sel, attr, val) {
    var el = document.head.querySelector(sel);
    if (el) el.setAttribute(attr, val);
  }
  meta('meta[name="description"]', 'content', p.purpose);
  meta('meta[property="og:title"]', 'content', fullName + ' — Vistex Chemicals');
  meta('meta[property="og:description"]', 'content', p.purpose);
  meta('link[rel="canonical"]', 'href', co.origin + '/product.html?id=' + encodeURIComponent(p.id));
  if (p.image) {
    meta('meta[property="og:image"]', 'content', co.origin + '/' + p.image);
    meta('meta[name="twitter:image"]', 'content', co.origin + '/' + p.image);
  }

  var ld = document.createElement('script');
  ld.type = 'application/ld+json';
  ld.textContent = JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: fullName,
    sku: p.code || p.id,
    description: p.purpose,
    category: s.name,
    brand: { '@type': 'Brand', name: co.productBrand },
    manufacturer: { '@type': 'Organization', name: co.name, url: co.origin + '/' },
    image: p.image ? co.origin + '/' + p.image : co.origin + '/images/logo/vistex-logo-color-on-white.png',
    offers: {
      '@type': 'Offer',
      availability: 'https://schema.org/InStock',
      priceCurrency: 'KES',
      price: '0',
      priceValidUntil: new Date(new Date().getFullYear() + 1, 0, 1).toISOString().slice(0, 10),
      url: co.origin + '/product.html?id=' + encodeURIComponent(p.id),
      seller: { '@type': 'Organization', name: co.name }
    }
  });
  document.head.appendChild(ld);

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
  var media = p.image
    ? window.vxPicture(p.image, fullName, { w: 800, h: 800, eager: true })
    : '<div class="pcard-noimg" style="position:relative">' +
        '<span class="drop">' + icon('bottle', 52) + '</span>' +
        '<span class="nm" style="font-size:var(--step-1)">' + esc(p.name) + '</span>' +
        '<span class="swift-badge swift-badge--md sb-badge">' +
          window.vxPicture(co.productBrandLogo, co.productBrand, { w: 720, h: 361 }) +
        '</span>' +
      '</div>';

  // ---------- Spec table: only the rows that exist ----------
  var rows = [
    ['Pack size', p.pack, 'package'],
    ['Form', p.form, 'beaker'],
    ['Dilution', p.dilution, 'scale'],
    ['Temperature', p.temp, 'thermometer'],
    ['System', s.name, s.icon],
    ['Brand', null, 'sparkle']       // rendered as the badge below, not text
  ].filter(function (r) { return r[1]; });

  if (scents) rows.push(['Scents', String(scents.length) + ' available', 'sparkle']);

  var spec = '<dl class="spec">' + rows.map(function (r) {
    return '<div class="spec-row"><dt>' + esc(r[0]) + '</dt><dd>' + esc(r[1]) + '</dd></div>';
  }).join('') +
    // Brand is the one row that is a mark rather than a value
    '<div class="spec-row"><dt>Brand</dt><dd>' +
      '<span class="swift-badge swift-badge--md">' +
        window.vxPicture(co.productBrandLogo, co.productBrand + ' — ' + co.productBrandTagline, { w: 720, h: 361 }) +
      '</span>' +
      '<span class="spec-brand-note">Made by ' + esc(co.name) + '</span>' +
    '</dd></div>' +
  '</dl>';

  var features = (p.features && p.features.length)
    ? '<div class="row" style="gap:8px">' + p.features.map(function (f) {
        return '<span class="chip chip--accent">' + icon('check', 14) + esc(f) + '</span>';
      }).join('') + '</div>'
    : '';

  // ---------- Where it is used ----------
  // Generic: any product declaring `applications` (environments) or `fabrics`
  // (what it may be used on) gets this block. Only SP-021 carries them today,
  // straight from the supplied product sheet.
  function useList(title, items, ico) {
    if (!items || !items.length) return '';
    return '<div class="uses-col">' +
      '<h3 class="uses-title">' + icon(ico, 16) + esc(title) + '</h3>' +
      '<ul class="uses-list">' + items.map(function (t) {
        return '<li>' + esc(t) + '</li>';
      }).join('') + '</ul>' +
    '</div>';
  }
  var usesBlock = (p.applications || p.fabrics)
    ? '<section class="uses card card-pad" data-anim="up">' +
        useList('Ideal applications', p.applications, 'building') +
        useList('Suitable for', p.fabrics, 'washer') +
      '</section>'
    : '';

  // ---------- Render ----------
  root.innerHTML =
    '<nav class="crumbs" aria-label="Breadcrumb">' +
      '<a href="systems.html">Systems</a><span class="sep">/</span>' +
      '<a href="systems.html?system=' + s.key + '">' + esc(s.short) + '</a><span class="sep">/</span>' +
      '<span style="color:var(--text-2)">' + esc(p.name) + '</span>' +
    '</nav>' +

    '<div class="pd-grid" style="margin-top:var(--s-7)">' +
      '<div class="pd-media" data-anim="left">' + media + '</div>' +

      '<div class="stack-6" data-anim="right">' +
        '<div>' +
          '<span class="eyebrow">' + esc(s.name) + '</span>' +
          '<h1 class="pd-title" style="margin-top:var(--s-4)">' + esc(p.name) + '</h1>' +
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

        '<div class="pd-safety">' + icon('alert', 18) +
          '<span><strong>Handling:</strong> ' + esc(co.safetyNote) + '</span></div>' +
      '</div>' +
    '</div>';

  // ---------- Where it is used ----------
  if (usesBlock) {
    var uses = document.createElement('div');
    uses.innerHTML = usesBlock;
    root.appendChild(uses.firstChild);
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
  var related = V.bySystem(p.system).filter(function (x) { return x.id !== p.id; }).slice(0, 4);
  if (related.length) {
    var rel = document.createElement('section');
    rel.style.marginTop = 'var(--s-11)';
    rel.innerHTML =
      '<div class="sec-head" style="margin-bottom:var(--s-6)">' +
        '<span class="eyebrow">Same system</span>' +
        '<h2 class="h-sub">More from ' + esc(s.short) + '</h2>' +
      '</div>' +
      '<div class="grid grid-4 reveal-parent">' + related.map(window.productCardHtml).join('') + '</div>';
    root.appendChild(rel);
  }

  if (window.VistexMotion) window.VistexMotion.refresh(root);
})();
