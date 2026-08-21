// ==========================================================
// VISTEX — Catalogue (systems.html)
// Live search + system filter over 40 products.
// State lives in the URL (?system=…&q=…) so results are linkable.
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX, icon = window.icon, esc = window.vxEsc;
  var $ = function (id) { return document.getElementById(id); };

  var params = new URLSearchParams(location.search);
  var state = {
    system: params.get('system') || '',
    q: (params.get('q') || '').trim()
  };
  if (state.system && !V.getSystem(state.system)) state.system = '';

  // ---------- Page heading reflects the active system ----------
  function paintHead() {
    var s = state.system ? V.getSystem(state.system) : null;
    $('catTitle').textContent = s ? s.name : 'Complete hygiene systems';
    $('catLede').textContent = s ? s.tagline
      : 'Our full range across laundry, housekeeping, kitchen, pool and guest care. Add what you need to your enquiry and we’ll send a quote.';
    document.title = (s ? s.name : 'Our Hygiene Systems') + ' — Vistex Chemicals Ltd';
  }

  // ---------- Filter chips ----------
  function paintFilters() {
    var html = '<button class="chip ' + (!state.system ? 'chip--on' : '') + '" data-sys="">' +
      'All <span class="mono" style="opacity:.7">' + V.products.length + '</span></button>';
    html += V.systems.map(function (s) {
      var on = state.system === s.key;
      return '<button class="chip ' + (on ? 'chip--on' : '') + '" data-sys="' + s.key + '">' +
        icon(s.icon, 15) + esc(s.short) +
        ' <span class="mono" style="opacity:.7">' + V.bySystem(s.key).length + '</span></button>';
    }).join('');
    $('catFilters').innerHTML = html;
  }

  // ---------- Matching ----------
  function matches(p) {
    if (state.system && p.system !== state.system) return false;
    if (!state.q) return true;
    var hay = [p.name, p.code, p.purpose, p.pack, p.form, (p.features || []).join(' ')]
      .filter(Boolean).join(' ').toLowerCase();
    return state.q.toLowerCase().split(/\s+/).every(function (t) { return hay.indexOf(t) > -1; });
  }

  // ---------- Body ----------
  function systemBand(s, list) {
    return '<section class="syscat" id="sys-' + s.key + '">' +
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

    $('catMeta').textContent = hits.length + ' of ' + V.products.length + ' products' +
      (state.q ? ' matching “' + state.q + '”' : '');

    if (!hits.length) {
      $('catBody').innerHTML =
        '<div class="cat-empty">' + icon('search', 44) +
        '<h3 class="h-sub">Nothing matched that search</h3>' +
        '<p style="margin-top:8px">Try a product name, a code like <span class="mono">S-020</span>, or clear the filters.</p>' +
        '<button class="btn btn-ghost btn-sm" id="catReset" style="margin-top:20px">Reset filters</button></div>';
      $('catReset').addEventListener('click', function () {
        state.q = ''; state.system = '';
        $('catSearch').value = '';
        sync(); paintHead(); paintFilters(); render();
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
    var q = new URLSearchParams();
    if (state.system) q.set('system', state.system);
    if (state.q) q.set('q', state.q);
    var s = q.toString();
    history.replaceState(null, '', s ? '?' + s : location.pathname);
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
      sync(); render();
    }, 180);
  });
  search.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { search.value = ''; search.dispatchEvent(new Event('input')); }
  });
  $('catClear').addEventListener('click', function () {
    search.value = ''; state.q = ''; $('catClear').hidden = true;
    sync(); render(); search.focus();
  });

  $('catFilters').addEventListener('click', function (e) {
    var b = e.target.closest('[data-sys]');
    if (!b) return;
    state.system = b.dataset.sys;
    sync(); paintHead(); paintFilters(); render();
  });

  document.getElementById('catWa').href = V.wa(V.waText.advice);

  paintHead();
  paintFilters();
  render();
})();
