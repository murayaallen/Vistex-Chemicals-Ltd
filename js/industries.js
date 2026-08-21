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
    '</section>';
  }).join('');

  // ---------- CTA links ----------
  $('indWa').href = V.wa(V.waText.advice);
  $('indMail').href = V.mailto('Hygiene system advice', V.waText.advice);

  if (window.VistexMotion) window.VistexMotion.refresh(document);
})();
