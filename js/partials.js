// ==========================================================
// VISTEX — Shared shell
// Injects header / footer / enquiry drawer into every page and
// wires theme, mobile nav, focus management and the intro loader.
// Also exposes window.productCardHtml() and window.vxToast().
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX;
  var co = V.company;
  var icon = window.icon;
  var page = document.body.dataset.page || '';

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  window.vxEsc = esc;

  // ---------------------------------------------------------
  // <picture> helper — every raster asset has a .webp sibling.
  // Modern browsers take the webp (~73% smaller); everything else
  // falls back to the original jpeg/png with no extra request.
  // CSS targets the inner <img>, so `picture { display: contents }`
  // keeps this wrapper invisible to layout.
  // ---------------------------------------------------------
  window.vxPicture = function (src, alt, o) {
    o = o || {};
    var webp = src.replace(/\.(jpe?g|png)$/i, '.webp');
    var attrs =
      ' src="' + src + '" alt="' + esc(alt || '') + '"' +
      (o.cls ? ' class="' + o.cls + '"' : '') +
      (o.w ? ' width="' + o.w + '"' : '') +
      (o.h ? ' height="' + o.h + '"' : '') +
      ' loading="' + (o.eager ? 'eager' : 'lazy') + '" decoding="async"' +
      (o.eager ? ' fetchpriority="high"' : '') +
      (o.extra || '');
    return '<picture>' +
      '<source srcset="' + webp + '" type="image/webp">' +
      '<img' + attrs + '>' +
    '</picture>';
  };

  // "product" pages highlight the Systems nav item
  function navActive(name) {
    if (name === 'systems' && (page === 'systems' || page === 'product')) return 'active';
    return page === name ? 'active' : '';
  }
  function ariaCur(name) { return navActive(name) ? ' aria-current="page"' : ''; }

  // ---------------------------------------------------------
  // HEADER
  // ---------------------------------------------------------
  var NAV = [
    ['index.html',      'home',       'Home'],
    ['systems.html',    'systems',    'Our Systems'],
    ['industries.html', 'industries', 'Industries'],
    ['about.html',      'about',      'About'],
    ['contact.html',    'contact',    'Contact']
  ];

  var header =
    '<a href="#main" class="skip-to-content">Skip to content</a>' +
    '<header class="site-header">' +
      '<div class="container nav">' +
        '<a class="nav-logo" href="index.html" aria-label="' + esc(co.name) + ' — home">' +
          window.vxPicture('images/logo/vistex-logo-color-on-white.png', co.name, { cls: 'logo-light', w: 280, h: 89, eager: true }) +
          window.vxPicture('images/logo/vistex-logo-white-on-blue.png',  co.name, { cls: 'logo-dark',  w: 280, h: 89, eager: true }) +
        '</a>' +
        '<nav class="nav-links" id="navLinks" aria-label="Main">' +
          NAV.map(function (n) {
            return '<a href="' + n[0] + '" class="' + navActive(n[1]) + '"' + ariaCur(n[1]) + '>' + n[2] + '</a>';
          }).join('') +
        '</nav>' +
        '<div class="nav-actions">' +
          '<button class="icon-btn icon-btn--sq" id="themeToggle" aria-label="Switch to dark theme" title="Toggle theme">' +
            '<span id="themeIcon"></span></button>' +
          '<button class="icon-btn" id="cartOpen" aria-label="Open enquiry list" aria-haspopup="dialog" aria-expanded="false">' +
            icon('clipboard', 18) + '<span class="hide-sm">Enquiry</span>' +
            '<span class="cart-badge" id="cartBadge" hidden>0</span></button>' +
          '<button class="nav-toggle" id="navToggle" aria-label="Menu" aria-controls="navLinks" aria-expanded="false">' +
            '<span></span><span></span><span></span></button>' +
        '</div>' +
      '</div>' +
      '<div class="scroll-progress" aria-hidden="true"></div>' +
    '</header>';

  // ---------------------------------------------------------
  // FOOTER
  // ---------------------------------------------------------
  var year = new Date().getFullYear();

  var footer =
    '<footer class="site-footer">' +
      '<div class="footer-glow" aria-hidden="true"></div>' +
      '<div class="container footer-grid">' +
        '<div class="footer-brands">' +
          '<div>' +
            window.vxPicture('images/logo/vistex-logo-white-on-blue.png', co.name, { cls: 'footer-logo', w: 215, h: 68 }) +
            '<p style="margin-top:16px;max-width:32ch;color:rgba(255,255,255,.72);font-size:var(--step--1)">' + esc(co.tagline) + '</p>' +
          '</div>' +
          '<div>' +
            '<div class="brand-lockup__label">Our product brand</div>' +
            '<div class="footer-swift" style="margin-top:10px">' +
              '<span class="swift-badge">' +
                window.vxPicture(co.productBrandLogo, co.productBrand + ' — ' + co.productBrandTagline, { w: 720, h: 361 }) +
              '</span>' +
              '<p>Every drum, bucket and jerrican we manufacture carries it.</p>' +
            '</div>' +
          '</div>' +
        '</div>' +
        '<div><h4>Explore</h4><ul>' +
          '<li><a href="systems.html">Our Systems</a></li>' +
          '<li><a href="industries.html">Industries</a></li>' +
          '<li><a href="about.html">About</a></li>' +
          '<li><a href="contact.html">Contact</a></li>' +
        '</ul></div>' +
        '<div><h4>Systems</h4><ul>' +
          V.systems.map(function (s) {
            return '<li><a href="systems.html?system=' + s.key + '">' + esc(s.short) + '</a></li>';
          }).join('') +
        '</ul></div>' +
        '<div><h4>Get in touch</h4><ul>' +
          '<li>' + icon('phone', 16) + '<a href="tel:+' + co.phoneIntl + '">' + esc(co.phoneDisplay) + '</a></li>' +
          '<li>' + icon('chat', 16) + '<a href="' + V.wa(V.waText.quote) + '" target="_blank" rel="noopener">WhatsApp us</a></li>' +
          '<li>' + icon('mail', 16) + '<a href="mailto:' + esc(co.email) + '">' + esc(co.email) + '</a></li>' +
          '<li>' + icon('pin', 16) + '<span>' + esc(co.address) + '</span></li>' +
          '<li>' + icon('clock', 16) + '<span>' + esc(co.hours) + '</span></li>' +
        '</ul></div>' +
      '</div>' +
      '<div class="container"><div class="footer-bottom">' +
        '<span>© ' + year + ' ' + esc(co.name) + '. All rights reserved.</span>' +
        '<span class="footer-brandline">' + esc(co.slogan) + '</span>' +
      '</div></div>' +
    '</footer>';

  // ---------------------------------------------------------
  // ENQUIRY DRAWER
  // ---------------------------------------------------------
  var drawer =
    '<div class="cart-overlay" id="cartOverlay"></div>' +
    '<aside class="cart-drawer" id="cartDrawer" role="dialog" aria-modal="true"' +
      ' aria-label="Your enquiry list" tabindex="-1">' +
      '<div class="cart-head">' +
        '<h3>Your enquiry <span class="mono" style="color:var(--text-3)">(<span id="cartCount">0</span>)</span></h3>' +
        '<button class="cart-close" id="cartClose" aria-label="Close enquiry list">' + icon('x', 18) + '</button>' +
      '</div>' +
      '<div class="cart-items" id="cartItems"></div>' +
      '<div class="cart-foot" id="cartFoot" hidden>' +
        '<div class="row2">' +
          '<input id="cf-name" placeholder="Your name" autocomplete="name">' +
          '<input id="cf-biz" placeholder="Hotel / business" autocomplete="organization">' +
        '</div>' +
        '<input id="cf-phone" placeholder="Your phone" autocomplete="tel" inputmode="tel">' +
        '<textarea id="cf-notes" rows="2" placeholder="Notes — delivery location, timing…"></textarea>' +
        '<div class="cart-actions">' +
          '<button class="btn btn-wa btn-block" id="cartSend">' + icon('chat', 17) + 'Send on WhatsApp</button>' +
          '<button class="btn btn-ghost btn-block btn-sm" id="cartMail">' + icon('mail', 16) + 'Or send by email</button>' +
        '</div>' +
        '<button class="link-quiet" id="cartClear" style="justify-self:center">Clear list</button>' +
      '</div>' +
    '</aside>' +
    '<div class="toast-wrap" id="toastWrap" aria-live="polite" aria-atomic="true"></div>';

  document.body.insertAdjacentHTML('afterbegin', header);
  document.body.insertAdjacentHTML('beforeend', footer + drawer);
  if (window.hydrateIcons) window.hydrateIcons(document);

  // ---------------------------------------------------------
  // THEME
  // ---------------------------------------------------------
  var themeBtn = document.getElementById('themeToggle');
  function paintThemeIcon() {
    var dark = document.documentElement.getAttribute('data-theme') === 'dark';
    var el = document.getElementById('themeIcon');
    if (el) el.innerHTML = icon(dark ? 'sun' : 'moon', 18);
    themeBtn.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
  }
  themeBtn.addEventListener('click', function () {
    var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('vx-theme', next); } catch (e) {}
    paintThemeIcon();

  // Until the visitor picks a theme, the default keeps following the device:
  // light on phones/tablets, dark on laptops and desktops. Once they toggle,
  // their choice is stored and this stops interfering.
  (function () {
    var mq = window.matchMedia('(max-width: 820px)');
    function follow() {
      var stored = null;
      try { stored = localStorage.getItem('vx-theme'); } catch (e) {}
      if (stored) return;                       // explicit choice wins
      document.documentElement.setAttribute('data-theme', mq.matches ? 'light' : 'dark');
      paintThemeIcon();
    }
    if (mq.addEventListener) mq.addEventListener('change', follow);
    else if (mq.addListener) mq.addListener(follow);
  })();
  });
  paintThemeIcon();

  // ---------------------------------------------------------
  // MOBILE NAV — aria-expanded, Escape, outside click
  // ---------------------------------------------------------
  var navToggle = document.getElementById('navToggle');
  var navLinks = document.getElementById('navLinks');

  function setNav(open) {
    navLinks.classList.toggle('open', open);
    navToggle.setAttribute('aria-expanded', String(open));
  }
  navToggle.addEventListener('click', function () {
    setNav(navToggle.getAttribute('aria-expanded') !== 'true');
  });
  navLinks.addEventListener('click', function (e) {
    if (e.target.closest('a')) setNav(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && navLinks.classList.contains('open')) {
      setNav(false); navToggle.focus();
    }
  });
  window.addEventListener('resize', function () {
    if (window.innerWidth > 920) setNav(false);
  }, { passive: true });

  // ---------------------------------------------------------
  // INTRO LOADER — once per session, capped, never blocks paint
  // ---------------------------------------------------------
  // The hero reveal must not play behind an opaque loader. This flag + event
  // let motion.js wait until the intro is actually lifting before it animates.
  window.__vxIntro = { done: false };
  function introDone() {
    if (window.__vxIntro.done) return;
    window.__vxIntro.done = true;
    document.dispatchEvent(new CustomEvent('vx:intro-done'));
  }

  (function () {
    var loader = document.getElementById('vx-loader');
    if (!loader) { introDone(); return; }     // pages without an intro reveal at once

    // Spawn the loader's bubbles here rather than waiting for motion.js — the
    // loader is gone before that script's DOMContentLoaded work would land.
    var box = loader.querySelector('.bubbles');
    if (box && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      var frag = document.createDocumentFragment();
      for (var i = 0; i < 16; i++) {
        var b = document.createElement('span');
        b.className = 'bubble';
        var size = 7 + Math.random() * 26;
        b.style.width = size + 'px'; b.style.height = size + 'px';
        b.style.left = (Math.random() * 100).toFixed(1) + '%';
        b.style.animationDuration = (2.2 + Math.random() * 2.6).toFixed(1) + 's';
        b.style.animationDelay = (-Math.random() * 3).toFixed(1) + 's';
        frag.appendChild(b);
      }
      box.appendChild(frag);
    }

    // ---------- intro timing ----------
    // MIN lets the CSS fill animation read; MAX is a hard cap so the loader can
    // never strand a visitor. Home page only, once per session.
    var MIN = 1500, MAX = 2400;
    var start = Date.now();
    var done = false;

    function hide(afterMs) {
      if (done) return; done = true;
      setTimeout(function () {
        loader.classList.add('hide');
        setTimeout(introDone, 300);
        setTimeout(function () { if (loader.parentNode) loader.remove(); }, 600);
        try { sessionStorage.setItem('vx-seen', '1'); } catch (e) {}
      }, afterMs != null ? afterMs : Math.max(0, MIN - (Date.now() - start)));
    }

    if (document.readyState === 'complete') hide();
    else window.addEventListener('load', function () { hide(); });
    setTimeout(hide, MAX);
  })();

  // ---------------------------------------------------------
  // REVEAL FAILSAFE
  // [data-anim] and [data-split] start at opacity 0 and are revealed by
  // motion.js. If that request is blocked or fails, the page would stay
  // permanently blank. This flag is cleared by motion.js on boot; if it is
  // still set a few seconds later, reveal everything unconditionally.
  // ---------------------------------------------------------
  window.__vxMotionPending = true;
  setTimeout(function () {
    if (!window.__vxMotionPending) return;
    document.querySelectorAll('[data-anim]').forEach(function (el) { el.classList.add('is-in'); });
    document.querySelectorAll('[data-split]').forEach(function (el) { el.classList.add('is-in', 'split-ready'); });
  }, 2500);

  // ---------------------------------------------------------
  // TOAST
  // ---------------------------------------------------------
  window.vxToast = function (msg, iconName) {
    var wrap = document.getElementById('toastWrap');
    if (!wrap) return;
    var t = document.createElement('div');
    t.className = 'toast';
    t.innerHTML = icon(iconName || 'check-circle', 17) + '<span>' + esc(msg) + '</span>';
    wrap.appendChild(t);
    setTimeout(function () { t.remove(); }, 2900);
  };

  // ---------------------------------------------------------
  // PRODUCT CARD (shared by catalog, product page, search)
  // ---------------------------------------------------------
  window.productCardHtml = function (p) {
    var media = p.image
      ? '<div class="pcard-media">' +
          window.vxPicture(p.image, p.name + (p.code ? ' ' + p.code : ''), { w: 400, h: 300 }) +
        '</div>'
      : '<div class="pcard-media"><div class="pcard-noimg">' +
          '<span class="drop">' + icon('bottle', 30) + '</span>' +
          '<span class="nm">' + esc(p.name) + '</span>' +
          '<span class="swift-badge swift-badge--sm sb-badge">' +
            window.vxPicture(co.productBrandLogo, co.productBrand, { w: 720, h: 361 }) +
          '</span>' +
        '</div></div>';

    return (
      '<article class="card card-hover card-glow pcard" data-anim="up" data-pid="' + p.id + '">' +
        '<a href="product.html?id=' + encodeURIComponent(p.id) + '" tabindex="-1" aria-hidden="true">' + media + '</a>' +
        '<div class="pcard-body">' +
          '<div class="pcard-top">' +
            '<h3 class="pcard-name"><a href="product.html?id=' + encodeURIComponent(p.id) + '">' + esc(p.name) + '</a></h3>' +
            (p.code ? '<span class="pcard-code">' + esc(p.code) + '</span>' : '') +
          '</div>' +
          '<p class="pcard-desc">' + esc(p.purpose) + '</p>' +
          '<div class="pcard-foot">' +
            '<span class="pcard-pack">' + esc(p.pack) + '</span>' +
            '<button class="pcard-add" data-add="' + p.id + '" aria-label="Add ' + esc(p.name) + ' to enquiry">' +
              icon('plus', 14) + 'Add</button>' +
          '</div>' +
        '</div>' +
      '</article>'
    );
  };

  // ---------------------------------------------------------
  // PAGE TRANSITION — soft fade out on internal navigation
  // ---------------------------------------------------------
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a) return;
      var href = a.getAttribute('href');
      if (!href || a.target === '_blank' || e.metaKey || e.ctrlKey || e.shiftKey) return;
      if (!/\.html($|\?|#)/.test(href) && href !== '/') return;
      if (href.indexOf('#') === 0) return;
      e.preventDefault();
      document.body.classList.add('is-leaving');
      setTimeout(function () { location.href = href; }, 190);
    });
  }
})();
