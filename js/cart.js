// ==========================================================
// VISTEX — Enquiry cart
// localStorage list → a pre-filled WhatsApp message, with an
// email fallback for desktop visitors and blocked popups.
// Listens for [data-add="<productId>"] clicks anywhere on the page.
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX;
  var KEY = 'vistex-cart';
  var esc = window.vxEsc;
  var icon = window.icon;

  var items = load();
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; } }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) {} }

  var $ = function (id) { return document.getElementById(id); };
  var overlay, drawer, openBtn, badge, countEl, itemsEl, footEl;
  var lastFocused = null;

  // ---------- mutations ----------
  function add(id, qty) {
    qty = qty || 1;
    var p = V.getProduct(id);
    if (!p) return;
    var ex = items.filter(function (i) { return i.id === id; })[0];
    if (ex) ex.qty += qty;
    else items.push({ id: p.id, name: p.name, code: p.code, pack: p.pack, qty: qty });
    save(); render();
    if (window.vxToast) window.vxToast(p.name + ' added to your enquiry');
  }
  function remove(id) { items = items.filter(function (i) { return i.id !== id; }); save(); render(); }
  function setQty(id, q) {
    if (q < 1) return remove(id);
    items.forEach(function (i) { if (i.id === id) i.qty = q; });
    save(); render();
  }
  function clear() { items = []; save(); render(); }
  function count() { return items.reduce(function (s, i) { return s + i.qty; }, 0); }
  function findQty(id) { var x = items.filter(function (i) { return i.id === id; })[0]; return x ? x.qty : 1; }

  // ---------- open / close with focus management ----------
  function open() {
    lastFocused = document.activeElement;
    overlay.classList.add('open');
    drawer.classList.add('open');
    document.body.classList.add('no-scroll');
    openBtn.setAttribute('aria-expanded', 'true');
    setTimeout(function () { drawer.focus(); }, 60);
  }
  function close() {
    overlay.classList.remove('open');
    drawer.classList.remove('open');
    document.body.classList.remove('no-scroll');
    openBtn.setAttribute('aria-expanded', 'false');
    if (lastFocused && lastFocused.focus) lastFocused.focus();
  }
  function isOpen() { return drawer.classList.contains('open'); }

  var FOCUSABLE = 'a[href],button:not([disabled]),input,textarea,select,[tabindex]:not([tabindex="-1"])';
  function trap(e) {
    if (e.key !== 'Tab' || !isOpen()) return;
    var f = Array.prototype.filter.call(
      drawer.querySelectorAll(FOCUSABLE),
      function (el) { return el.offsetParent !== null; }
    );
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  // ---------- message building ----------
  function lines() {
    var L = [];
    var name = $('cf-name').value.trim(),
        biz = $('cf-biz').value.trim(),
        phone = $('cf-phone').value.trim(),
        notes = $('cf-notes').value.trim();
    if (name)  L.push('Name: ' + name);
    if (biz)   L.push('Business: ' + biz);
    if (phone) L.push('Phone: ' + phone);
    if (L.length) L.push('');
    L.push('Products requested:');
    items.forEach(function (i, n) {
      L.push((n + 1) + '. ' + i.name + (i.code ? ' (' + i.code + ')' : '') +
             ' — Qty ' + i.qty + ' × ' + i.pack);
    });
    if (notes) L.push('', 'Notes: ' + notes);
    return L;
  }
  function waLink()   { return V.wa('*New enquiry — Vistex Chemicals*\n\n' + lines().join('\n')); }
  function mailLink() { return V.mailto('Product enquiry — ' + ($('cf-biz').value.trim() || 'Website'), lines().join('\n')); }

  // ---------- render ----------
  function render() {
    var c = count();
    countEl.textContent = c;
    badge.textContent = c;
    badge.hidden = c === 0;

    if (!items.length) {
      itemsEl.innerHTML =
        '<p class="cart-empty">' + icon('clipboard', 40) +
        'Your enquiry list is empty.<br>Add products and we’ll send you a quote.</p>';
      footEl.hidden = true;
      return;
    }
    footEl.hidden = false;
    itemsEl.innerHTML = items.map(function (i) {
      return '<div class="cart-item">' +
        '<div style="flex:1;min-width:0">' +
          '<div class="ci-name">' + esc(i.name) +
            (i.code ? ' <span class="ci-code">' + esc(i.code) + '</span>' : '') + '</div>' +
          '<div class="ci-pack">' + esc(i.pack) + '</div>' +
        '</div>' +
        '<div class="qty">' +
          '<button data-dec="' + i.id + '" aria-label="Decrease quantity of ' + esc(i.name) + '">−</button>' +
          '<span>' + i.qty + '</span>' +
          '<button data-inc="' + i.id + '" aria-label="Increase quantity of ' + esc(i.name) + '">+</button>' +
        '</div>' +
        '<button class="ci-remove" data-rm="' + i.id + '" aria-label="Remove ' + esc(i.name) + '">' +
          icon('trash', 17) + '</button>' +
      '</div>';
    }).join('');
  }

  // ---------- init ----------
  function init() {
    overlay = $('cartOverlay'); drawer = $('cartDrawer'); badge = $('cartBadge');
    openBtn = $('cartOpen'); countEl = $('cartCount');
    itemsEl = $('cartItems'); footEl = $('cartFoot');
    if (!drawer) return;

    openBtn.addEventListener('click', open);
    $('cartClose').addEventListener('click', close);
    overlay.addEventListener('click', close);
    $('cartClear').addEventListener('click', clear);

    $('cartSend').addEventListener('click', function () {
      var w = window.open(waLink(), '_blank', 'noopener');
      // Popup blocked → fall back to same-tab navigation rather than dead-ending.
      if (!w) location.href = waLink();
    });
    $('cartMail').addEventListener('click', function () { location.href = mailLink(); });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen()) close();
      trap(e);
    });

    // Delegate: add buttons anywhere, qty/remove inside the drawer.
    document.addEventListener('click', function (e) {
      var t = e.target.closest('[data-add],[data-inc],[data-dec],[data-rm]');
      if (!t) return;
      if (t.dataset.add) {
        add(t.dataset.add, 1);
        t.classList.add('added');
        t.innerHTML = icon('check', 14) + 'Added';
        setTimeout(function () {
          t.classList.remove('added');
          t.innerHTML = icon('plus', 14) + 'Add';
        }, 1400);
      }
      else if (t.dataset.inc) setQty(t.dataset.inc, findQty(t.dataset.inc) + 1);
      else if (t.dataset.dec) setQty(t.dataset.dec, findQty(t.dataset.dec) - 1);
      else if (t.dataset.rm)  remove(t.dataset.rm);
    });

    render();
    window.VistexCart = { add: add, open: open, close: close, count: count };
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
