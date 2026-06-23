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

  // Body
  function block(s) {
    var items = V.bySystem(s.key);
    var benefits = s.benefits.map(function (b){ return '<span class="chip chip--blue">✓ '+b+'</span>'; }).join('');
    var cards = items.map(function (p){ return window.productCardHtml(p); }).join('');
    return (
      '<section style="margin-top:48px">' +
        '<div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:8px;border-bottom:1px solid var(--border);padding-bottom:14px">' +
          '<div><h2 class="h-section sys-title" style="font-size:1.6rem;display:flex;align-items:center;gap:10px">'+window.icon(s.icon,26)+'<span>'+s.name+'</span></h2>' +
          '<p style="color:var(--text-3);font-size:14.5px;margin-top:4px">'+s.tagline+'</p></div>' +
          '<span style="color:var(--text-3);font-size:14px">'+items.length+' products</span>' +
        '</div>' +
        '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:16px">'+benefits+'</div>' +
        '<div class="grid grid-4 reveal-parent" style="margin-top:22px">'+cards+'</div>' +
      '</section>'
    );
  }

  var html = active ? block(active) : V.systems.map(block).join('');
  $('catBody').innerHTML = html;
})();
