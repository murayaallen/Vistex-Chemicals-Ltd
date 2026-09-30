// ==========================================================
// VISTEX — Catalogue (systems.html + one static page per range)
// Live search over the product list. Each range has its own
// generated page (laundry-chemicals.html, …) with its own title and
// canonical, so the range filter is a set of real links between
// those pages rather than a query string Google cannot index.
// The search term lives in the URL (?q=…) so results are linkable.
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX, icon = window.icon, esc = window.vxEsc;
  var $ = function (id) { return document.getElementById(id); };

  var params = new URLSearchParams(location.search);
  // The old systems.html?system=… address forwards to the range's own page.
  var legacy = params.get('system');
  if (legacy && V.getSystem(legacy) && !document.body.dataset.system) {
    var q0 = params.get('q');
    location.replace(V.rangeUrl(legacy) + (q0 ? '?q=' + encodeURIComponent(q0) : ''));
    return;
  }
  var state = {
    system: document.body.dataset.system || '',
    q: (params.get('q') || '').trim()
  };
  if (state.system && !V.getSystem(state.system)) state.system = '';

  // ---------- Page heading reflects the active system ----------
  // The heading is static HTML on every page (range pages get theirs from the
  // generator); only the lede is filled here.
  function paintHead() {
    var s = state.system ? V.getSystem(state.system) : null;
    // The tagline already heads the range band below, so the lede is the
    // description alone.
    $('catLede').textContent = s ? s.description
      : 'Our full range across laundry, housekeeping, kitchen, pool, guest care and industrial hygiene. Add what you need to your enquiry and we’ll send a quote.';
  }

  // ---------- Filter chips: links between the range pages ----------
  function paintFilters() {
    var keep = state.q ? '?q=' + encodeURIComponent(state.q) : '';
    var html = '<a class="chip ' + (!state.system ? 'chip--on' : '') + '" href="systems.html' + keep + '"' +
      (!state.system ? ' aria-current="page"' : '') + '>' +
      'All <span class="mono" style="opacity:.7">' + V.products.length + '</span></a>';
    html += V.systems.map(function (s) {
      var on = state.system === s.key;
      return '<a class="chip ' + (on ? 'chip--on' : '') + '" href="' + V.rangeUrl(s) + keep + '"' +
        (on ? ' aria-current="page"' : '') + '>' +
        icon(s.icon, 15) + esc(s.short) +
        ' <span class="mono" style="opacity:.7">' + V.bySystem(s.key).length + '</span></a>';
    }).join('');
    $('catFilters').innerHTML = html;
  }

  // ---------- Matching ----------
  function matches(p) {
    if (state.system && p.system !== state.system) return false;
    if (!state.q) return true;
    var hay = [p.name, p.code, p.subtitle, p.purpose, p.pack, p.form, p.active,
               (p.features || []).join(' '), (p.applications || []).join(' '),
               (p.surfaces || []).join(' '), V.getSystem(p.system).name]
      .filter(Boolean).join(' ').toLowerCase();
    return state.q.toLowerCase().split(/\s+/).every(function (t) { return hay.indexOf(t) > -1; });
  }

  // ---------- Body ----------
  function systemBand(s, list) {
    // Same reasoning as the industry bands: built at runtime, decorated here.
    return '<section class="syscat" id="sys-' + s.key + '" data-decor="bubbles glow" data-bubbles="6">' +
      '<header class="syscat-head" data-anim="up">' +
        '<div class="syscat-bg" style="background-image:url(\'' + s.img + '\')"></div>' +
        '<div class="syscat-head-top">' +
          '<h2 class="syscat-title"><span class="sys-emblem">' + icon(s.icon, 24) + '</span>' +
            '<span>' + esc(s.name) + '</span></h2>' +
          '<span class="sys-count">' + list.length + ' product' + (list.length === 1 ? '' : 's') + '</span>' +
        '</div>' +
        '<p class="syscat-tag">' + esc(s.tagline) + '</p>' +
        '<div class="syscat-benefits">' +
          s.benefits.map(function (b) {
            return '<span class="chip chip--glass">' + icon('check', 14) + esc(b) + '</span>';
          }).join('') +
        '</div>' +
      '</header>' +
      '<div class="grid grid-4 reveal-parent">' +
        list.map(window.productCardHtml).join('') +
      '</div>' +
    '</section>';
  }

  function render() {
    var hits = V.products.filter(matches);

    var pool = state.system ? V.bySystem(state.system).length : V.products.length;
    $('catMeta').textContent = hits.length + ' of ' + pool + ' products' +
      (state.q ? ' matching “' + state.q + '”' : '');

    if (!hits.length) {
      $('catBody').innerHTML =
        '<div class="cat-empty">' + icon('search', 44) +
        '<h3 class="h-sub">Nothing matched that search</h3>' +
        '<p style="margin-top:8px">Try a product name, a code like <span class="mono">S-020</span>, or clear the filters.</p>' +
        '<button class="btn btn-ghost btn-sm" id="catReset" style="margin-top:20px">Reset filters</button></div>';
      $('catReset').addEventListener('click', function () {
        if (state.system) { location.href = 'systems.html'; return; }
        state.q = '';
        $('catSearch').value = '';
        sync(); paintFilters(); render();
      });
      return;
    }

    // Searching flattens the view; browsing keeps the system bands.
    if (state.q) {
      $('catBody').innerHTML =
        '<div class="grid grid-4 reveal-parent">' + hits.map(window.productCardHtml).join('') + '</div>';
    } else {
      var shown = state.system ? [V.getSystem(state.system)] : V.systems;
      $('catBody').innerHTML = shown.map(function (s) {
        return systemBand(s, hits.filter(function (p) { return p.system === s.key; }));
      }).join('');
    }

    if (window.VistexMotion) window.VistexMotion.refresh($('catBody'));
  }

  // ---------- URL sync (no page reload) ----------
  function sync() {
    history.replaceState(null, '', state.q ? '?q=' + encodeURIComponent(state.q) : location.pathname);
  }

  // ---------- Wire up ----------
  var search = $('catSearch');
  search.value = state.q;
  $('catClear').hidden = !state.q;

  var debounce;
  search.addEventListener('input', function () {
    clearTimeout(debounce);
    debounce = setTimeout(function () {
      state.q = search.value.trim();
      $('catClear').hidden = !state.q;
      sync(); paintFilters(); render();
    }, 180);
  });
  search.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { search.value = ''; search.dispatchEvent(new Event('input')); }
  });
  $('catClear').addEventListener('click', function () {
    search.value = ''; state.q = ''; $('catClear').hidden = true;
    sync(); paintFilters(); render(); search.focus();
  });

  document.getElementById('catWa').href = V.wa(V.waText.advice);

  paintHead();
  paintFilters();
  render();
})();
