// ==========================================================
// VISTEX — About page
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX, co = V.company, icon = window.icon, esc = window.vxEsc;
  var $ = function (id) { return document.getElementById(id); };

  $('aboutIntro').textContent = co.intro;
  $('aboutMeta').textContent = 'Founded ' + co.founded + ' · Nairobi, Kenya';
  $('mission').textContent = co.mission;
  $('vision').textContent = co.vision;

  // ---------- Timeline / process ----------
  $('aboutProcess').innerHTML = V.process.map(function (p, i) {
    return '<div class="card card-pad card-glow" data-anim="up">' +
      '<div class="label">' + String(i + 1).padStart(2, '0') + '</div>' +
      '<h3 class="h-sub" style="margin-top:8px">' + esc(p.title) + '</h3>' +
      '<p style="margin-top:10px;color:var(--text-3);font-size:var(--step--1);line-height:1.65">' + esc(p.text) + '</p>' +
    '</div>';
  }).join('');

  // ---------- Differentiators ----------
  $('diffGrid').innerHTML = V.differentiators.map(function (d) {
    return '<div class="card card-glow diff-card" data-anim="up">' +
      '<div class="ico">' + icon(d.icon, 24) + '</div>' +
      '<h3>' + esc(d.title) + '</h3>' +
      '<p>' + esc(d.text) + '</p>' +
    '</div>';
  }).join('');

  // ---------- Clients ----------
  function group(title, list) {
    return '<div class="client-group" data-anim="up"><h3>' + esc(title) + '</h3><ul>' +
      list.map(function (c) { return '<li>' + esc(c) + '</li>'; }).join('') + '</ul></div>';
  }
  $('clientGroups').innerHTML =
    group('Hotels & Resorts', V.clients.hotels) +
    group('Hospitals & Clinics', V.clients.hospitals) +
    group('And more', V.clients.others);

  $('aboutWa').href = V.wa(V.waText.assessment);

  if (window.VistexMotion) window.VistexMotion.refresh(document);
})();
