// ==========================================================
// VISTEX — Page Partials
// Injects the shared header, footer and cart drawer into every
// page, wires the theme toggle + mobile nav, and exposes
// window.productCardHtml() used by catalog/product pages.
// ==========================================================
(function () {
  'use strict';
  var V = window.VISTEX;
  var co = V.company;
  var icon = window.icon;
  var page = document.body.dataset.page || '';

  // ---------- Loader: fast rush of bubbles behind the logo ----------
  (function loaderBubbles() {
    var box = document.getElementById('vxLoaderBubbles');
    if (!box || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    for (var i = 0; i < 22; i++) {
      var b = document.createElement('span');
      var size = 5 + Math.random() * 22;
      b.style.width = size + 'px';
      b.style.height = size + 'px';
      b.style.left = (Math.random() * 100) + '%';
      b.style.animationDuration = (0.9 + Math.random() * 1.4) + 's'; // brisk but smooth
      b.style.animationDelay = (Math.random() * 1.3) + 's';
      box.appendChild(b);
    }
  })();

  function active(name) { return page === name ? 'active' : ''; }
  // product detail counts as "systems" for nav highlighting
  function navActive(name) {
    if (name === 'systems' && (page === 'systems' || page === 'product')) return 'active';
    return active(name);
  }

  // ---------- HEADER ----------
  var header =
    '<a href="#main" class="skip-to-content">Skip to content</a>' +
    '<header class="site-header"><div class="container nav">' +
      '<a class="nav-logo" href="index.html" aria-label="' + co.name + ' home">' +
        '<img class="logo-light" src="images/logo/vistex-logo-color-on-white.png" alt="' + co.name + '">' +
        '<img class="logo-dark" src="images/logo/vistex-logo-white-on-blue.png" alt="' + co.name + '">' +
      '</a>' +
      '<nav class="nav-links" id="navLinks">' +
        '<a href="index.html" class="' + navActive('home') + '">Home</a>' +
        '<a href="systems.html" class="' + navActive('systems') + '">Our Systems</a>' +
        '<a href="industries.html" class="' + navActive('industries') + '">Industries</a>' +
        '<a href="about.html" class="' + navActive('about') + '">About</a>' +
        '<a href="contact.html" class="' + navActive('contact') + '">Contact</a>' +
      '</nav>' +
      '<div class="nav-actions">' +
        '<button class="icon-btn" id="themeToggle" aria-label="Toggle dark mode" title="Toggle theme">' +
          '<span id="themeIcon"></span></button>' +
        '<button class="icon-btn" id="cartOpen" aria-label="Open enquiry">' + icon('clipboard',18) + ' <span class="hide-sm">Enquiry</span>' +
          '<span class="cart-badge" id="cartBadge" hidden>0</span></button>' +
        '<button class="nav-toggle" id="navToggle" aria-label="Menu"><span></span><span></span><span></span></button>' +
      '</div>' +
    '</div></header>';

  // ---------- FOOTER ----------
  var year = new Date().getFullYear();
  var footer =
    '<footer class="site-footer">' +
    '<div class="footer-wave"><svg viewBox="0 0 1440 56" preserveAspectRatio="none" aria-hidden="true">' +
      '<path fill="currentColor" d="M0,28 C240,0 480,0 720,28 C960,56 1200,56 1440,28 L1440,56 L0,56 Z"/></svg></div>' +
    '<div class="container footer-grid">' +
      '<div>' +
        '<img class="footer-logo" src="images/logo/vistex-logo-white-on-blue.png" alt="' + co.name + '">' +
        '<p style="margin-top:16px;max-width:34ch;color:rgba(255,255,255,.78)">' + co.tagline + '</p>' +
        '<p style="margin-top:12px;font-weight:700;color:var(--aqua-2)">' + co.slogan + '</p>' +
      '</div>' +
      '<div><h4>Explore</h4><ul>' +
        '<li><a href="systems.html">Our Systems</a></li>' +
        '<li><a href="industries.html">Industries</a></li>' +
        '<li><a href="about.html">About</a></li>' +
        '<li><a href="contact.html">Contact</a></li>' +
      '</ul></div>' +
      '<div><h4>Get in touch</h4><ul>' +
        '<li><a href="tel:' + co.phoneIntl + '">' + icon('phone',16) + ' ' + co.phoneDisplay + '</a></li>' +
        '<li><a href="https://wa.me/' + co.phoneIntl + '" target="_blank" rel="noreferrer">' + icon('chat',16) + ' WhatsApp us</a></li>' +
        '<li><a href="mailto:' + co.email + '">' + icon('mail',16) + ' ' + co.email + '</a></li>' +
        '<li>' + icon('pin',16) + ' ' + co.address + '</li>' +
      '</ul></div>' +
    '</div>' +
    '<div class="footer-bottom">© ' + year + ' ' + co.name + '. All rights reserved. · ' +
      co.productBrand + ' — ' + co.productBrandTagline + '</div>' +
    '</footer>';

  // ---------- CART DRAWER ----------
  var drawer =
    '<div class="cart-overlay" id="cartOverlay"></div>' +
    '<aside class="cart-drawer" id="cartDrawer" aria-label="Enquiry list">' +
      '<div class="cart-head"><h3>Your Enquiry (<span id="cartCount">0</span>)</h3>' +
        '<button class="cart-close" id="cartClose" aria-label="Close">×</button></div>' +
      '<div class="cart-items" id="cartItems"></div>' +
      '<div class="cart-foot" id="cartFoot" hidden>' +
        '<div class="row2"><input id="cf-name" placeholder="Your name"><input id="cf-biz" placeholder="Hotel / business"></div>' +
        '<input id="cf-phone" placeholder="Your phone">' +
        '<textarea id="cf-notes" rows="2" placeholder="Notes (delivery location, timing…)"></textarea>' +
        '<button class="btn btn-wa" id="cartSend" style="width:100%">Send enquiry on WhatsApp</button>' +
        '<button class="link-quiet" id="cartClear">Clear list</button>' +
      '</div>' +
    '</aside>';

  // Insert header at top of body, footer + drawer at end.
  document.body.insertAdjacentHTML('afterbegin', header);
  document.body.insertAdjacentHTML('beforeend', footer + drawer);

  // ---------- Theme toggle ----------
  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    var el = document.getElementById('themeIcon');
    if (el) el.innerHTML = icon(t === 'dark' ? 'sun' : 'moon', 18);
    try { localStorage.setItem('vistex-theme', t); } catch (e) {}
  }
  document.getElementById('themeToggle').addEventListener('click', function () {
    var cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    applyTheme(cur === 'dark' ? 'light' : 'dark');
  });
  // reflect the already-applied theme on the icon
  (function () {
    var t = document.documentElement.getAttribute('data-theme') || 'light';
    var el = document.getElementById('themeIcon');
    if (el) el.innerHTML = icon(t === 'dark' ? 'sun' : 'moon', 18);
  })();

  // ---------- Header solidify on scroll (home overlay nav) ----------
  (function () {
    var hdr = document.querySelector('.site-header');
    if (!hdr) return;
    function onScroll() { hdr.classList.toggle('scrolled', window.scrollY > 40); }
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  })();

  // ---------- Mobile nav ----------
  var navToggle = document.getElementById('navToggle');
  var navLinks = document.getElementById('navLinks');
  navToggle.addEventListener('click', function () { navLinks.classList.toggle('open'); });
  navLinks.addEventListener('click', function (e) { if (e.target.tagName === 'A') navLinks.classList.remove('open'); });

  // ---------- Loading screen: hide once everything has loaded ----------
  (function () {
    var loader = document.getElementById('vx-loader');
    if (!loader) return;
    var start = Date.now();
    var MIN = 1800; // keep it visible at least this long so it doesn't flash
    function hide() {
      var wait = Math.max(0, MIN - (Date.now() - start));
      setTimeout(function () {
        loader.classList.add('hide');
        setTimeout(function () { if (loader.parentNode) loader.remove(); }, 600);
      }, wait);
    }
    if (document.readyState === 'complete') hide();
    else window.addEventListener('load', hide);
    // safety net: never let the loader get stuck
    setTimeout(function () { if (document.getElementById('vx-loader')) hide(); }, 4000);
  })();

  // ---------- Product card HTML (shared) ----------
  window.productCardHtml = function (p) {
    var media = p.image
      ? '<div class="pcard-media"><img src="' + p.image + '" alt="' + p.name + '" loading="lazy"></div>'
      : '<div class="pcard-media"><div class="pcard-noimg"><span class="drop">' + icon('bottle',32) + '</span>' +
        '<span class="nm">' + p.name + '</span><span class="sb">Swift · Usafi Halisi</span></div></div>';
    var code = p.code ? '<span class="pcard-code">' + p.code + '</span>' : '';
    return (
      '<article class="card card-hover pcard" data-anim="up">' +
        '<a href="product.html?id=' + p.id + '">' + media + '</a>' +
        '<div class="pcard-body">' +
          '<div class="pcard-top"><h3 class="pcard-name">' +
            '<a href="product.html?id=' + p.id + '">' + p.name + '</a></h3>' + code + '</div>' +
          '<p class="pcard-desc">' + p.purpose + '</p>' +
          '<div class="pcard-foot"><span class="pcard-pack">' + p.pack + '</span>' +
            '<button class="btn btn-accent" style="padding:9px 16px;font-size:13px" data-add="' + p.id + '">+ Add</button>' +
          '</div>' +
        '</div>' +
      '</article>'
    );
  };
})();
