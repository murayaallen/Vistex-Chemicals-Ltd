// ==========================================================
// VISTEX — Industries page
// Quick-nav chips + one alternating editorial band per sector.
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX, icon = window.icon, esc = window.vxEsc;
  var $ = function (id) { return document.getElementById(id); };

  // ---------- Quick nav ----------
  $('indNav').innerHTML = V.industries.map(function (ind) {
    return '<a class="chip" href="#ind-' + ind.key + '">' + icon(ind.icon, 15) + esc(ind.name) + '</a>';
  }).join('');

  // The rail slot is 92px tall, so it takes the thumbnail rather than the hero
  // artwork — pointing it at the full cut-outs pulled 967K of image to fill 21
  // thumbnails. See images/thumbs/.
  // Mirror the source folder, do not flatten it: cutouts/x.png and
  // products/x.jpeg would otherwise both resolve to thumbs/x.webp, and since
  // <picture> prefers webp the rails would quietly show a packshot where a
  // cut-out was intended.
  function thumb(path) { return path.replace(/^images\//, 'images/thumbs/'); }

  // ---------- Bands ----------
  $('indSections').innerHTML = V.industries.map(function (ind, idx) {
    var odd = idx % 2 === 1;

    var points = ind.points.map(function (p) {
      return '<li><span class="fi">' + icon('check', 14) + '</span><span>' + esc(p) + '</span></li>';
    }).join('');

    var sysChips = ind.systems.map(function (k) {
      var s = V.getSystem(k);
      return '<a class="chip" href="systems.html?system=' + k + '">' + icon(s.icon, 15) + esc(s.short) + '</a>';
    }).join('');

    var clients = ind.clients.length
      ? '<div class="ind-clients"><strong>Trusted by</strong>' + esc(ind.clients.join(' · ')) + '</div>'
      : '<div class="ind-clients"><strong>References</strong>Available on request.</div>';

    // ---------- Recommended products ----------
    // Cut-outs, not packshots: a transparent product floating on the glass
    // panel reads as a specification for this sector rather than a catalogue
    // tile, and it is the same artwork the hero conveyor uses.
    var recs = (ind.recommend || []).map(function (id) { return V.getProduct(id); })
      .filter(Boolean).map(function (p, n) {
        var art = p.cutout
          ? '<span class="rec-cut">' + window.vxPicture(thumb(p.cutout), '', { w: 209, h: 240 }) + '</span>'
          : '<span class="rec-cut rec-cut--photo">' + window.vxPicture(thumb(p.image), '', { w: 360, h: 360 }) + '</span>';
        return '<a class="rec-card glass" href="product.html?id=' + encodeURIComponent(p.id) + '"' +
                 ' style="--i:' + n + '" data-rec>' +
            '<span class="rec-glow" aria-hidden="true"></span>' +
            art +
            '<span class="rec-name">' + esc(p.name) + '</span>' +
            '<span class="rec-meta">' + esc(p.code || p.pack || '') + '</span>' +
          '</a>';
      }).join('');

    var recBlock = recs
      ? '<div class="ind-recs" data-anim="up">' +
          '<div class="ind-recs-head">' +
            '<span class="eyebrow">Recommended for ' + esc(ind.name) + '</span>' +
            '<a class="rec-all" href="systems.html">See the full range' +
              icon('arrow-right', 14) + '</a>' +
          '</div>' +
          '<div class="rec-rail" data-rail>' + recs + '</div>' +
        '</div>'
      : '';

    return '<section id="ind-' + ind.key + '" class="section ind-band cv-auto' + (odd ? ' section--tint' : '') + '">' +
      '<div class="container split' + (odd ? ' reverse' : '') + '">' +
        '<div class="split-media" data-anim="' + (odd ? 'right' : 'left') + '">' +
          '<figure class="photo photo--parallax" style="--ar: 4/3">' +
            window.vxPicture(ind.img, ind.imgHint, { w: 900, h: 675, extra: ' data-parallax="0.04" onerror="this.remove()"' }) +
            '<figcaption class="photo-caption">' + esc(ind.name) + '</figcaption>' +
          '</figure>' +
        '</div>' +
        '<div class="split-copy stack-6" data-anim="' + (odd ? 'left' : 'right') + '">' +
          '<span class="eyebrow">' + String(idx + 1).padStart(2, '0') + ' · ' + esc(ind.name) + '</span>' +
          '<h2 class="h-section">' + esc(ind.headline) + '</h2>' +
          '<p class="lede">' + esc(ind.blurb) + '</p>' +
          '<ul class="feature-list">' + points + '</ul>' +
          '<div class="row"><span class="label" style="margin-right:4px">Systems</span>' + sysChips + '</div>' +
          clients +
        '</div>' +
      '</div>' +
      (recBlock ? '<div class="container">' + recBlock + '</div>' : '') +
    '</section>';
  }).join('');

  // ---------- Scroll-linked drift on each recommendation rail ----------
  // The rail leans into the page as it comes past: a small, scroll-scrubbed
  // parallax that stops the five bands feeling like five copies of one band.
  // Driven by IntersectionObserver + rAF rather than a scroll listener, so
  // nothing is computed for a rail that is nowhere near the viewport.
  (function () {
    var rails = [].slice.call(document.querySelectorAll('[data-rail]'));
    if (!rails.length || matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var live = [], ticking = false;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var i = live.indexOf(e.target);
        if (e.isIntersecting && i < 0) live.push(e.target);
        else if (!e.isIntersecting && i >= 0) { live.splice(i, 1); e.target.style.removeProperty('--drift'); }
      });
      if (live.length) request();
    }, { rootMargin: '15% 0px' });
    rails.forEach(function (r) { io.observe(r); });

    function request() { if (!ticking) { ticking = true; requestAnimationFrame(tick); } }
    function tick() {
      ticking = false;
      var vh = window.innerHeight;
      live.forEach(function (r) {
        var b = r.getBoundingClientRect();
        // -1 entering from below … +1 leaving through the top
        var t = 1 - (b.top + b.height / 2) / (vh / 2 + b.height / 2);
        r.style.setProperty('--drift', Math.max(-1, Math.min(1, t)).toFixed(3));
      });
      if (live.length) request();
    }
  })();

  // ---------- CTA links ----------
  $('indWa').href = V.wa(V.waText.advice);
  $('indMail').href = V.mailto('Hygiene system advice', V.waText.advice);

  if (window.VistexMotion) window.VistexMotion.refresh(document);
})();
