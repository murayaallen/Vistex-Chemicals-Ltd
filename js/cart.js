// ==========================================================
// VISTEX — Enquiry Cart
// Stores the enquiry list in localStorage, renders the drawer,
// and turns the list into a pre-filled WhatsApp message.
// Listens for clicks on any [data-add="<productId>"] button.
// ==========================================================
(function () {
  'use strict';
  var V = window.VISTEX;
  var KEY = 'vistex-cart';

  var items = load();
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) {} }

  var $ = function (id) { return document.getElementById(id); };
  var overlay, drawer, badge, countEl, itemsEl, footEl;

  function add(id, qty) {
    qty = qty || 1;
    var p = V.getProduct(id); if (!p) return;
    var ex = items.filter(function (i){return i.id===id;})[0];
    if (ex) ex.qty += qty;
    else items.push({ id:p.id, name:p.name, code:p.code, pack:p.pack, qty:qty });
    save(); render(); open();
  }
  function remove(id) { items = items.filter(function (i){return i.id!==id;}); save(); render(); }
  function setQty(id, q) {
    items.forEach(function (i){ if(i.id===id) i.qty = Math.max(1,q); });
    save(); render();
  }
  function clear() { items = []; save(); render(); }
  function count() { return items.reduce(function (s,i){return s+i.qty;},0); }

  function open() { overlay.classList.add('open'); drawer.classList.add('open'); document.body.classList.add('no-scroll'); }
  function close() { overlay.classList.remove('open'); drawer.classList.remove('open'); document.body.classList.remove('no-scroll'); }

  function waLink() {
    var co = V.company;
    var name = $('cf-name').value.trim(), biz = $('cf-biz').value.trim(),
        phone = $('cf-phone').value.trim(), notes = $('cf-notes').value.trim();
    var L = ['*New enquiry — Vistex Chemicals*',''];
    if (name) L.push('Name: ' + name);
    if (biz) L.push('Business: ' + biz);
    if (phone) L.push('Phone: ' + phone);
    L.push('', '*Products requested:*');
    items.forEach(function (i,n){
      L.push((n+1) + '. ' + i.name + (i.code ? ' ('+i.code+')':'') + ' — Qty: ' + i.qty + ' × ' + i.pack);
    });
    if (notes) { L.push('', 'Notes: ' + notes); }
    return 'https://wa.me/' + co.phoneIntl + '?text=' + encodeURIComponent(L.join('\n'));
  }

  function render() {
    var c = count();
    countEl.textContent = c;
    badge.textContent = c;
    badge.hidden = c === 0;
    if (!items.length) {
      itemsEl.innerHTML = '<p class="cart-empty">Your enquiry list is empty.<br>Add products and request a quote on WhatsApp.</p>';
      footEl.hidden = true;
      return;
    }
    footEl.hidden = false;
    itemsEl.innerHTML = items.map(function (i){
      return '<div class="cart-item">' +
        '<div style="flex:1"><div class="ci-name">' + i.name + (i.code?' <span style="color:var(--red)">('+i.code+')</span>':'') + '</div>' +
        '<div class="ci-pack">' + i.pack + '</div></div>' +
        '<div class="qty"><button data-dec="'+i.id+'">−</button><span>'+i.qty+'</span><button data-inc="'+i.id+'">+</button></div>' +
        '<button class="ci-remove" data-rm="'+i.id+'" aria-label="Remove">'+window.icon('trash',18)+'</button>' +
      '</div>';
    }).join('');
  }

  function init() {
    overlay = $('cartOverlay'); drawer = $('cartDrawer'); badge = $('cartBadge');
    countEl = $('cartCount'); itemsEl = $('cartItems'); footEl = $('cartFoot');

    $('cartOpen').addEventListener('click', open);
    $('cartClose').addEventListener('click', close);
    overlay.addEventListener('click', close);
    $('cartClear').addEventListener('click', clear);
    $('cartSend').addEventListener('click', function(){ window.open(waLink(), '_blank'); });

    // Delegate clicks: add buttons anywhere + qty/remove inside drawer
    document.addEventListener('click', function (e) {
      var t = e.target.closest('[data-add],[data-inc],[data-dec],[data-rm]');
      if (!t) return;
      if (t.dataset.add) add(t.dataset.add, 1);
      else if (t.dataset.inc) { var i=findQty(t.dataset.inc); setQty(t.dataset.inc, i+1); }
      else if (t.dataset.dec) { var j=findQty(t.dataset.dec); setQty(t.dataset.dec, j-1); }
      else if (t.dataset.rm) remove(t.dataset.rm);
    });

    render();
    // expose for product page "Add to enquiry" with custom qty
    window.VistexCart = { add: add, open: open };
  }
  function findQty(id){ var x=items.filter(function(i){return i.id===id;})[0]; return x?x.qty:1; }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
