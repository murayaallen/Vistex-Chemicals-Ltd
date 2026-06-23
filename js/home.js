// ==========================================================
// VISTEX — Home page render
// Fills the data-driven sections from window.VISTEX.
// ==========================================================
(function () {
  'use strict';
  var V = window.VISTEX, co = V.company;
  var $ = function (id){ return document.getElementById(id); };

  // Marquee — product names drifting (doubled for a seamless loop)
  var names = V.products.map(function (p){ return p.name + (p.code ? ' '+p.code : ''); });
  var uniq = names.filter(function (n,i){ return names.indexOf(n)===i; }).slice(0,18);
  var span = uniq.map(function (n){ return '<span>'+n+'</span>'; }).join('');
  $('marquee').innerHTML = span + span;

  // Animated wave SVG (periodic so it loops seamlessly when translated)
  var WAVE = '<svg class="sys-wave" viewBox="0 0 1440 60" preserveAspectRatio="none" aria-hidden="true">' +
    '<path fill="currentColor" d="M0,40 C60,15 120,15 180,40 C240,65 300,65 360,40 C420,15 480,15 540,40 ' +
    'C600,65 660,65 720,40 C780,15 840,15 900,40 C960,65 1020,65 1080,40 C1140,15 1200,15 1260,40 ' +
    'C1320,65 1380,65 1440,40 L1440,60 L0,60 Z"/></svg>';

  // Systems showcase — water-filled headers
  $('sysGrid').innerHTML = V.systems.map(function (s){
    var n = V.bySystem(s.key).length;
    var media =
      '<div class="sys-water">' +
        '<div class="bubbles" data-count="7"></div>' +
        '<span class="sys-emblem">'+window.icon(s.icon,52)+'</span>' +
        '<div class="sys-shot"><img src="'+s.img+'" alt="'+s.name+'" loading="lazy" ' +
          'onerror="this.parentNode.remove()"><span class="sys-tint"></span></div>' +
        WAVE +
      '</div>';
    return '<a class="card card-hover sys-card2" data-anim="up" href="systems.html?system='+s.key+'">' +
      media +
      '<div class="sys-card2-body">' +
        '<span class="sys-badge">'+window.icon(s.icon,26)+'</span>' +
        '<h3>'+s.name+'</h3><p>'+s.description+'</p>' +
        '<span class="more">View '+n+' products →</span>' +
      '</div></a>';
  }).join('');

  // Stats
  $('statsGrid').innerHTML = V.stats.map(function (s){
    return '<div class="stat" data-anim="up"><div class="n">'+s.n+'</div><div class="l">'+s.label+'</div></div>';
  }).join('');

  // Differentiators
  $('diffGrid').innerHTML = V.differentiators.map(function (d){
    return '<div class="card diff-card" data-anim="up"><div class="ico">'+window.icon(d.icon,26)+'</div><h3>'+d.title+'</h3><p>'+d.text+'</p></div>';
  }).join('');

  // Clients
  var all = V.clients.hotels.concat(V.clients.hospitals);
  $('clientRow').innerHTML = all.map(function (c){ return '<span class="chip">'+c+'</span>'; }).join('');

  // CTA WhatsApp link
  $('ctaWa').href = 'https://wa.me/' + co.phoneIntl +
    '?text=' + encodeURIComponent('Hello Vistex — I would like a hygiene assessment for my property.');

  // Fill every static [data-ico] placeholder (hero chips, emblems, feature checks)
  document.querySelectorAll('[data-ico]').forEach(function (el) {
    var size = parseInt(el.dataset.size || '18', 10);
    el.insertAdjacentHTML('afterbegin', window.icon(el.dataset.ico, size));
  });

  // Hero sector word — smooth "wash away" swap (single element, no layout jump)
  (function washRotate() {
    var el = document.getElementById('heroWord');
    if (!el || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var words = ['hotels','hospitals','schools','kitchens','laundries','pools','institutions'];
    var i = 0;
    setInterval(function () {
      el.classList.add('washing');               // wash out (fade + drip + blur)
      setTimeout(function () {
        i = (i + 1) % words.length;
        el.textContent = words[i];               // swap while invisible
        el.classList.remove('washing');          // wash back in
      }, 500);
    }, 2800);
  })();
})();
