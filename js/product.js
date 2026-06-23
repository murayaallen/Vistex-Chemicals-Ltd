// ==========================================================
// VISTEX — Product detail page
// Reads ?id=<productId>, renders detail + related products.
// ==========================================================
(function () {
  'use strict';
  var V = window.VISTEX;
  var root = document.getElementById('productRoot');
  var id = new URLSearchParams(location.search).get('id');
  var p = id ? V.getProduct(id) : null;

  if (!p) {
    root.innerHTML = '<div class="center" style="padding:60px 0">' +
      '<h1 class="h-section">Product not found</h1>' +
      '<a class="btn btn-primary" href="systems.html" style="margin-top:20px">Back to catalog</a></div>';
    return;
  }

  var s = V.getSystem(p.system);
  document.title = p.name + (p.code ? ' ' + p.code : '') + ' — Vistex Chemicals Ltd';

  var media = p.image
    ? '<img src="'+p.image+'" alt="'+p.name+'" width="600" height="600">'
    : '<div class="pcard-noimg" style="aspect-ratio:1/1"><span class="drop">'+window.icon('bottle',52)+'</span>' +
      '<span class="nm" style="font-size:18px">'+p.name+'</span><span class="sb">Swift · Usafi Halisi</span></div>';
  var code = p.code ? '<span class="badge-soft" style="background:rgba(237,30,38,.1);color:var(--red)">Code: '+p.code+'</span>' : '';

  root.innerHTML =
    '<nav style="font-size:14px;color:var(--text-3)">' +
      '<a href="systems.html" style="color:var(--text-3)">Systems</a> / ' +
      '<a href="systems.html?system='+s.key+'" style="color:var(--text-3)">'+s.short+'</a> / ' +
      '<span style="color:var(--text-2)">'+p.name+'</span></nav>' +
    '<div class="grid grid-2" style="margin-top:24px;gap:48px;align-items:start">' +
      '<div class="card" data-anim="left" style="overflow:hidden;border-radius:var(--radius-xl)">'+media+'</div>' +
      '<div data-anim="right">' +
        '<span class="eyebrow">'+s.name+'</span>' +
        '<h1 class="h-display" style="font-size:clamp(1.9rem,4vw,2.6rem);margin-top:10px">'+p.name+'</h1>' +
        '<div style="margin-top:12px">'+code+'</div>' +
        '<p class="lede" style="margin-top:18px">'+p.purpose+'</p>' +
        '<div class="grid grid-2" style="margin-top:24px;gap:14px">' +
          '<div class="card" style="padding:16px"><div class="pcard-pack">Pack size</div><div style="font-weight:700;margin-top:4px">'+p.pack+'</div></div>' +
          '<div class="card" style="padding:16px"><div class="pcard-pack">Brand</div><div style="font-weight:700;margin-top:4px">Swift — Usafi Halisi</div></div>' +
        '</div>' +
        '<div style="display:flex;align-items:center;gap:12px;margin-top:24px">' +
          '<div class="qty" style="border:1px solid var(--border);border-radius:12px;padding:4px">' +
            '<button id="pdDec">−</button><span id="pdQty">1</span><button id="pdInc">+</button></div>' +
          '<button class="btn btn-accent" id="pdAdd" style="flex:1">Add to enquiry</button>' +
        '</div>' +
        '<p style="margin-top:14px;font-size:12.5px;color:var(--text-3)">Pricing is provided on request. Add products to your enquiry and our team will send a quote.</p>' +
      '</div>' +
    '</div>';

  // Quantity controls
  var qty = 1;
  var qEl = document.getElementById('pdQty');
  document.getElementById('pdInc').addEventListener('click', function(){ qty++; qEl.textContent = qty; });
  document.getElementById('pdDec').addEventListener('click', function(){ qty = Math.max(1, qty-1); qEl.textContent = qty; });
  document.getElementById('pdAdd').addEventListener('click', function(){ window.VistexCart.add(p.id, qty); });

  // Related
  var related = V.bySystem(p.system).filter(function (x){ return x.id !== p.id; }).slice(0,4);
  if (related.length) {
    var rel = document.createElement('section');
    rel.style.marginTop = '64px';
    rel.innerHTML = '<h2 class="h-section sys-title" style="font-size:1.6rem">More from '+s.short+'</h2>' +
      '<div class="grid grid-4 reveal-parent" style="margin-top:22px">' +
      related.map(function (x){ return window.productCardHtml(x); }).join('') + '</div>';
    root.appendChild(rel);
  }
})();
