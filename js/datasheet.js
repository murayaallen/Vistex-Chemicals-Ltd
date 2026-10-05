// ==========================================================
// VISTEX — Product data sheet (datasheet.html?id=…)
//
// This is the page a carton QR code lands on, so it has to work for
// someone standing in a store room on a phone: no hero, no scroll
// theatre, the directions first and the specification right behind them.
//
// It reads the SAME fields product.js already renders — directions,
// applications, features, hazard — rather than a parallel block, so the
// catalogue stays one source of truth. Only `sheet` (specification table,
// composition, storage) holds what that schema has no slot for.
//
// Where a product declares none of it, the page still renders from the
// catalogue record rather than 404-ing: a QR that resolves to nothing is
// worse than a thin page.
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX, co = V.company, esc = window.vxEsc;
  var root = document.getElementById('dsRoot');
  if (!root) return;

  var id = new URLSearchParams(location.search).get('id') || 'blue-drop-wc';
  var p = V.getProduct(id);

  if (!p) {
    root.innerHTML =
      '<div class="nf"><div>' +
        '<div class="label">404</div>' +
        '<h1 class="h-section" style="margin-top:12px">No data sheet for that code</h1>' +
        '<p class="lede" style="margin-top:10px">The product may have been renamed or retired. ' +
          'Our team can send the current sheet.</p>' +
        '<a class="btn btn-primary" href="contact.html" style="margin-top:24px">Ask us for it</a> ' +
        '<a class="btn btn-ghost" href="systems.html" style="margin-top:24px">Browse the catalogue</a>' +
      '</div></div>';
    return;
  }

  var d = p.sheet || {};
  var brand = co.productBrand || '';

  function section(title, inner) {
    return '<section class="ds-sec"><h2>' + esc(title) + '</h2>' + inner + '</section>';
  }
  function list(items, cls) {
    if (!items || !items.length) return '';
    return '<ul class="' + cls + '">' +
      items.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') +
      '</ul>';
  }
  function rows(pairs) {
    if (!pairs || !pairs.length) return '';
    return '<table class="ds-table"><tbody>' +
      pairs.map(function (r) {
        return '<tr><th>' + esc(r[0]) + '</th><td>' + esc(r[1]) + '</td></tr>';
      }).join('') + '</tbody></table>';
  }

  // the spec table always carries what the catalogue already knows, even
  // when a product has no bespoke datasheet block
  var spec = (d.spec || []).slice();
  if (!spec.length) {
    if (p.form) spec.push(['Form', p.form]);
    if (p.pack) spec.push(['Pack', p.pack]);
    if (p.code) spec.push(['Code', p.code]);
  }

  var html =
    '<header class="ds-head">' +
      '<div>' +
        (brand ? '<div class="ds-brand">' + esc(brand) + '</div>' : '') +
        '<h1 class="ds-title">' + esc(p.name) + '</h1>' +
        '<p class="ds-strap">' + esc(p.purpose) + '</p>' +
      '</div>' +
      '<div style="text-align:right">' +
        '<div class="ds-brand">Data sheet</div>' +
        '<div class="ds-code">' + esc(p.id) + (p.code ? ' &middot; ' + esc(p.code) : '') + '</div>' +
      '</div>' +
    '</header>';

  if (p.directions && p.directions.length) {
    html += section('Directions for use', list(p.directions, 'ds-steps'));
  }

  html += '<div class="ds-grid">';
  if (p.features && p.features.length) {
    html += section('Key benefits', list(p.features, 'ds-list'));
  }
  if (p.applications && p.applications.length) {
    html += section('Where it is used', list(p.applications, 'ds-list'));
  }
  html += '</div>';
  if (p.notFor && p.notFor.length) {
    html += section('Not for', list(p.notFor, 'ds-list'));
  }

  if (spec.length) html += section('Specification', rows(spec));

  html += '<div class="ds-grid">';
  if (d.composition) {
    html += section('Composition', '<p style="margin-top:var(--s-4)">' +
      esc(d.composition) + '</p>');
  }
  if (d.storage) {
    html += section('Storage and handling', '<p style="margin-top:var(--s-4)">' +
      esc(d.storage) + '</p>');
  }
  html += '</div>';

  // hazard uses the catalogue's own shape, so the warning on this sheet and
  // the one on the product page can never drift apart
  if (p.hazard && p.hazard.text) {
    html += '<div class="ds-care"><section class="ds-sec" style="margin-top:0">' +
      '<h2>' + esc(p.hazard.word || 'Caution') + '</h2>' +
      '<p style="margin-top:var(--s-3)">' + esc(p.hazard.text) + '</p>' +
      (p.neverMix && p.neverMix.length
        ? '<p style="margin-top:var(--s-3)"><strong>Never mix with:</strong> ' +
          esc(p.neverMix.join(', ')) + '</p>' : '') +
      '</section></div>';
  }

  html += section('Manufactured by',
    '<p style="margin-top:var(--s-4)"><strong>' + esc(co.name) + '</strong><br>' +
    esc(co.address || 'P.O. Box 218 - 00606, Industrial Area, Nairobi, Kenya') + '<br>' +
    '<a href="tel:+' + esc(co.phoneIntl || '254739446655') + '">' +
      esc(co.phoneDisplay || '0739 446 655') + '</a> &middot; ' +
    '<a href="mailto:' + esc(co.email || 'info@vistexchemicals.co.ke') + '">' +
      esc(co.email || 'info@vistexchemicals.co.ke') + '</a></p>');

  if (d.note) html += '<p class="ds-note">' + esc(d.note) + '</p>';

  html +=
    '<div class="ds-actions">' +
      '<a class="btn btn-primary" href="contact.html">Request a quotation</a>' +
      '<a class="btn btn-ghost" href="product.html?id=' + encodeURIComponent(p.id) + '">Product page</a>' +
      '<button class="btn btn-ghost" type="button" id="dsPrint">Print this sheet</button>' +
    '</div>';

  root.innerHTML = html;

  var btn = document.getElementById('dsPrint');
  if (btn) btn.addEventListener('click', function () { window.print(); });

  // make the page meaningful when shared or crawled
  document.title = p.name + ' — data sheet — ' + co.name;
  var desc = document.querySelector('meta[name="description"]');
  if (desc) desc.setAttribute('content', (p.purpose || '').slice(0, 300));
  var can = document.querySelector('link[rel="canonical"]');
  if (can) can.setAttribute('href',
    'https://www.vistexchemicals.co.ke/datasheet.html?id=' + encodeURIComponent(p.id));
})();
