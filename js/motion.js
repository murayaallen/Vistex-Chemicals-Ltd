// ==========================================================
// VISTEX — Motion
// Reveals [data-anim] elements as they scroll into view, sets
// stagger index on children, and spawns hero bubbles.
// Pure vanilla JS, no dependencies.
// ==========================================================
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 1) Scroll reveal via IntersectionObserver
  function initReveal() {
    var els = document.querySelectorAll('[data-anim]');
    if (reduce || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    // give each child within a .reveal-parent its stagger index
    document.querySelectorAll('.reveal-parent').forEach(function (parent) {
      parent.querySelectorAll('[data-anim]').forEach(function (el, i) {
        el.style.setProperty('--i', i);
      });
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  }

  // 2) Hero bubbles — spawn into any .bubbles container
  function initBubbles() {
    if (reduce) return;
    document.querySelectorAll('.bubbles').forEach(function (box) {
      var n = parseInt(box.dataset.count || '14', 10);
      for (var i = 0; i < n; i++) {
        var b = document.createElement('span');
        b.className = 'bubble';
        var size = 8 + Math.random() * 34;
        b.style.width = size + 'px';
        b.style.height = size + 'px';
        b.style.left = Math.random() * 100 + '%';
        b.style.animationDuration = (7 + Math.random() * 10) + 's';
        b.style.animationDelay = (Math.random() * 8) + 's';
        box.appendChild(b);
      }
    });
  }

  // 3) Decor — morphing gradient blobs + floating drops in any .vx-decor host
  function initDecor() {
    if (reduce) return;
    document.querySelectorAll('.vx-decor').forEach(function (host) {
      if (host.querySelector('.decor')) return;
      var decor = document.createElement('div');
      decor.className = 'decor';
      var blobs = parseInt(host.dataset.blobs || '3', 10);
      for (var i = 0; i < blobs; i++) {
        var b = document.createElement('span');
        b.className = 'blob c' + (i % 3);
        var size = 160 + Math.random() * 220;
        b.style.width = size + 'px';
        b.style.height = size * (0.8 + Math.random() * 0.4) + 'px';
        b.style.left = (Math.random() * 80 - 5) + '%';
        b.style.top = (Math.random() * 80 - 5) + '%';
        b.style.animationDelay = (-Math.random() * 16) + 's, ' + (-Math.random() * 24) + 's';
        decor.appendChild(b);
      }
      var drops = parseInt(host.dataset.drops || '0', 10);
      for (var j = 0; j < drops; j++) {
        var d = document.createElement('span');
        d.className = 'deco-drop';
        var ds = 9 + Math.random() * 12;
        d.style.width = ds + 'px';
        d.style.height = ds + 'px';
        d.style.left = (8 + Math.random() * 84) + '%';
        d.style.top = (8 + Math.random() * 78) + '%';
        d.style.animationDelay = (-Math.random() * 7) + 's';
        d.style.animationDuration = (5 + Math.random() * 4) + 's';
        decor.appendChild(d);
      }
      host.insertBefore(decor, host.firstChild);
    });
  }

  function init() { initDecor(); initReveal(); initBubbles(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
