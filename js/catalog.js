// ==========================================================
// VISTEX — Catalog (systems page)
// Reads ?system=<key>; shows all systems or one filtered.
// ==========================================================
(function () {
  'use strict';
  var V = window.VISTEX;
  var $ = function (id){ return document.getElementById(id); };
  var key = new URLSearchParams(location.search).get('system');
  var active = key ? V.getSystem(key) : null;

  // Header text
  if (active) {
    $('catTitle').textContent = active.name;
    $('catLede').textContent = active.tagline;
    document.title = active.name + ' — Vistex Chemicals Ltd';
  }

  // Tabs
  function tab(href, label, on) {
    return '<a href="'+href+'" class="chip '+(on?'chip--blue':'')+'" '+
      'style="'+(on?'':'')+'">'+label+'</a>';
  }
  var tabs = [tab('systems.html','All', !key)];
  V.systems.forEach(function (s){ tabs.push(tab('systems.html?system='+s.key, s.short, key===s.key)); });
  $('catTabs').innerHTML = tabs.join('');

  // Body — each system is a sector-image band with liquid-glass product cards
  function block(s) {
    var items = V.bySystem(s.key);
    var benefits = s.benefits.map(function (b){ return '<span class="chip glass-chip">✓ '+b+'</span>'; }).join('');
    var cards = items.map(function (p){ return window.productCardHtml(p); }).join('');
    return (
      '<section class="syscat" data-anim="up">' +
        '<div class="syscat-bg" style="background-image:url(\''+s.img+'\')"></div>' +
        '<div class="syscat-head">' +
          '<div><h2 class="syscat-title">'+window.icon(s.icon,28)+'<span>'+s.name+'</span></h2>' +
          '<p class="syscat-tag">'+s.tagline+'</p></div>' +
          '<span class="syscat-count">'+items.length+' products</span>' +
        '</div>' +
        '<div class="syscat-benefits">'+benefits+'</div>' +
        '<div class="grid grid-4 glass-grid reveal-parent">'+cards+'</div>' +
      '</section>'
    );
  }

  var html = active ? block(active) : V.systems.map(block).join('');
  $('catBody').innerHTML = html;
})();
