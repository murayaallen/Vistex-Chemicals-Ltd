// ==========================================================
// VISTEX — Home page render
// ==========================================================
(function () {
  'use strict';

  var V = window.VISTEX, co = V.company, icon = window.icon, esc = window.vxEsc;
  var $ = function (id) { return document.getElementById(id); };

  // ---------- Marquee: product names, doubled for a seamless loop ----------
  (function () {
    var names = V.products.map(function (p) { return p.name + (p.code ? ' ' + p.code : ''); });
    var uniq = names.filter(function (n, i) { return names.indexOf(n) === i; }).slice(0, 20);
    var run = uniq.map(function (n) { return '<span>' + esc(n) + '</span>'; }).join('');
    $('marquee').innerHTML = run + run;
  })();

  // ---------- Problem → solution ledger ----------
  $('ledger').innerHTML = V.problemSolutions.map(function (r, i) {
    return '<div class="ledger-row" data-anim="up">' +
      '<span class="ledger-n">' + String(i + 1).padStart(2, '0') + '</span>' +
      '<div class="ledger-p"><span class="ledger-tag">The problem</span>' + esc(r.problem) + '</div>' +
      '<div class="ledger-arrow">' + icon('arrow-right', 18) + '</div>' +
      '<div class="ledger-s"><span class="ledger-tag">What we do</span>' + esc(r.solution) + '</div>' +
    '</div>';
  }).join('');

  // ---------- Systems showcase ----------
  var WAVE =
    '<svg viewBox="0 0 1440 60" preserveAspectRatio="none" aria-hidden="true">' +
    '<path fill="currentColor" d="M0,40 C60,15 120,15 180,40 C240,65 300,65 360,40 C420,15 480,15 540,40 ' +
    'C600,65 660,65 720,40 C780,15 840,15 900,40 C960,65 1020,65 1080,40 C1140,15 1200,15 1260,40 ' +
    'C1320,65 1380,65 1440,40 L1440,60 L0,60 Z"/></svg>';

  $('sysGrid').innerHTML = V.systems.map(function (s) {
    var n = V.bySystem(s.key).length;
    return '<a class="sys-card" data-anim="up" href="systems.html?system=' + s.key + '">' +
      window.vxPicture(s.img, '', { cls: 'sys-card-img', w: 640, h: 480, extra: ' onerror="this.remove()"' }) +
      '<div class="sys-wave">' + WAVE + '</div>' +
      '<div class="sys-card-top">' +
        '<span class="sys-emblem">' + icon(s.icon, 24) + '</span>' +
        '<span class="sys-count">' + n + ' products</span>' +
      '</div>' +
      '<h3>' + esc(s.name) + '</h3>' +
      '<p>' + esc(s.description) + '</p>' +
      '<span class="sys-more">Explore ' + esc(s.short) + icon('arrow-right', 15) + '</span>' +
    '</a>';
  }).join('');

  // ---------- Process: photo stage + pips ----------
  $('pvShots').innerHTML = V.process.map(function (p, i) {
    return '<div class="pv-shot' + (i === 0 ? ' active' : '') + '" data-shot="' + i + '">' +
      window.vxPicture(p.img, p.alt, { w: 900, h: 1125, eager: i === 0 }) +
    '</div>';
  }).join('');
  $('pvPips').innerHTML = V.process.map(function (_, i) {
    return '<span class="' + (i === 0 ? 'on' : '') + '" data-pip="' + i + '"></span>';
  }).join('');

  // ---------- Process steps ----------
  $('processSteps').innerHTML = V.process.map(function (p, i) {
    return '<div class="pstep" data-label="' + esc(p.label) + '" data-anim="up">' +
      '<div class="pn">Step ' + String(i + 1).padStart(2, '0') + '</div>' +
      '<h4>' + esc(p.title) + '</h4>' +
      '<p>' + esc(p.text) + '</p>' +
    '</div>';
  }).join('');
  $('stepLabel').textContent = V.process[0].label;

  // ---------- Differentiators (bento) ----------
  $('diffGrid').innerHTML = V.differentiators.map(function (d) {
    return '<div class="card card-glow diff-card" data-anim="up">' +
      '<div class="ico">' + icon(d.icon, 24) + '</div>' +
      '<h3>' + esc(d.title) + '</h3>' +
      '<p>' + esc(d.text) + '</p>' +
    '</div>';
  }).join('');

  // ==========================================================
  // MOBILE SWIPE DECKS
  // Phones get one idea per screen instead of a sticky scrollytelling rig or a
  // six-card bento. Native horizontal scroll-snap: vertical page scrolling is
  // never intercepted, so reaching the last slide simply hands scrolling back.
  // ==========================================================
  function buildDeck(host, slides) {
    if (!host) return;
    host.innerHTML =
      '<div class="swipe-track">' + slides.map(function (sl, i) {
        return '<article class="swipe-slide">' +
          (sl.media ? '<figure class="swipe-media">' + sl.media + '</figure>' : '') +
          '<div class="swipe-body">' +
            '<span class="swipe-step">' + esc(sl.kicker) + '</span>' +
            '<h4>' + esc(sl.title) + '</h4>' +
            '<p>' + esc(sl.text) + '</p>' +
          '</div>' +
        '</article>';
      }).join('') + '</div>' +
      '<div class="swipe-dots" aria-hidden="true">' +
        slides.map(function (_, i) { return '<i class="' + (i === 0 ? 'on' : '') + '"></i>'; }).join('') +
      '</div>';

    var track = host.querySelector('.swipe-track');
    var dots = Array.prototype.slice.call(host.querySelectorAll('.swipe-dots i'));
    var cards = Array.prototype.slice.call(host.querySelectorAll('.swipe-slide'));

    function sync() {
      var mid = track.scrollLeft + track.clientWidth / 2;
      var best = 0, bestD = Infinity;
      cards.forEach(function (c, i) {
        var d = Math.abs(c.offsetLeft + c.offsetWidth / 2 - mid);
        if (d < bestD) { bestD = d; best = i; }
      });
      dots.forEach(function (d, i) { d.classList.toggle('on', i === best); });
      cards.forEach(function (c, i) { c.classList.toggle('is-active', i === best); });
    }
    track.addEventListener('scroll', function () {
      window.requestAnimationFrame(sync);
    }, { passive: true });
    sync();
  }

  buildDeck($('processSwipe'), V.process.map(function (p, i) {
    return {
      kicker: 'Step ' + String(i + 1).padStart(2, '0'),
      title: p.title,
      text: p.text,
      media: window.vxPicture(p.img, p.alt, { w: 800, h: 600 })
    };
  }));

  buildDeck($('diffSwipe'), V.differentiators.map(function (d, i) {
    return {
      kicker: String(i + 1).padStart(2, '0') + ' / ' + String(V.differentiators.length).padStart(2, '0'),
      title: d.title,
      text: d.text,
      media: '<span class="swipe-ico">' + icon(d.icon, 30) + '</span>'
    };
  }));

  // ---------- Clients ----------
  $('clientRow').innerHTML = V.clients.hotels.concat(V.clients.hospitals)
    .map(function (c) { return '<span class="chip">' + esc(c) + '</span>'; }).join('');

  // ---------- CTA links ----------
  $('ctaWa').href = V.wa(V.waText.assessment);
  $('ctaMail').href = V.mailto('Hygiene assessment request', V.waText.assessment);


  // ==========================================================
  // HERO PRODUCT STAGE — "Conveyor"
  //
  // Every product sits at an angle on a horizontal circle, and the whole
  // circle turns at a constant rate. Products sweep forward through the
  // spotlight at the front of the belt, then recede around the back and
  // converge on a single vanishing point before coming round again.
  //
  // The perspective is the real projection, not a fake:
  //
  //     Z    = cam - cos(phi)         depth from the camera, in circle radii
  //     proj = 1 / Z                  the perspective divisor
  //     x    = span * sin(phi) * proj
  //     y    = floor + rise * (1 - dn)      dn = proj normalised to 0..1
  //     s    = scale * proj / projNear
  //
  // Two things fall out of doing it properly. Because x and y are both linear
  // in proj, the path traced is exactly the perspective image of a circle — an
  // ellipse — which is why the belt under the products can be one CSS ellipse
  // and still land on every baseline. And because cam > 1 the whole circle
  // stays in front of the camera, so the loop is genuinely endless: no wrap,
  // no reset, no seam to hide.
  //
  // Starts on vx:intro-done so it plays after the loader lifts, never behind it.
  // ==========================================================
  (function () {
    var stage = $('productStage');
    if (!stage) return;
    var itemsEl = $('pstageItems');
    var capEl   = $('pstageCap');
    var reduce  = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var VESSELS = ['bucket', 'jerrican', 'bottle'];

    // Deal the vessel types out round-robin. In catalogue order the seven
    // buckets arrive as one indistinguishable block; alternating silhouettes
    // keeps each neighbour readable as its own product.
    var list = (function (all) {
      var groups = VESSELS.map(function (v) {
        return all.filter(function (p) { return p.vessel === v; });
      }).filter(function (g) { return g.length; });
      var out = [], more = true;
      while (more) {
        more = false;
        groups.forEach(function (g) { if (g.length) { out.push(g.shift()); more = true; } });
      }
      return out;
      // A cut-out alone is not enough to earn a place on the belt — it also needs
      // a vessel. The urinal mat has a cut-out for the scent picker, but a flat
      // disc cannot stand on a conveyor built for drums, buckets and bottles.
    })(V.products.filter(function (p) { return p.cutout && VESSELS.indexOf(p.vessel) >= 0; }));

    var N = list.length;
    if (!N) return;
    var STEP = Math.PI * 2 / N;

    // ---------- build ----------
    var dots = document.createElement('div');
    dots.className = 'pstage-dots';
    var nodes = list.map(function (p, i) {
      var d = document.createElement('div');
      d.className = 'pitem';
      d.innerHTML = '<picture><source srcset="' + p.cutout.replace('.png', '.webp') +
        '" type="image/webp"><img src="' + p.cutout + '" alt="' + esc(p.name) +
        (p.code ? ' ' + esc(p.code) : '') + '" width="406" height="466" ' +
        (i < 6 ? '' : 'loading="lazy" ') + 'decoding="async"></picture>';
      d.style.opacity = '0';
      d._o = -1; d._z = -1; d._d = -1;
      itemsEl.appendChild(d);
      dots.appendChild(document.createElement('i'));
      return d;
    });
    ($('pstageMeta') || stage).appendChild(dots);
    var dotEls = Array.prototype.slice.call(dots.children);

    // ---------- camera ----------
    // Read from CSS so the container queries can re-aim the shot per width.
    function num(name, fb) {
      var v = parseFloat(getComputedStyle(stage).getPropertyValue(name));
      return isNaN(v) ? fb : v;
    }
    var G = {};
    function measure() {
      var r = stage.getBoundingClientRect();
      G.w = r.width; G.h = r.height;
      G.cam   = Math.max(1.05, num('--cv-cam', 1.62));   // <= 1 would put the belt through the lens
      G.span  = num('--cv-span', 48);
      G.floor = num('--cv-floor', 12);
      G.rise  = num('--cv-rise', 30);
      G.scale = num('--cv-scale', 1.75);
      G.fade  = num('--cv-fade', 1.2);
      G.near  = 1 / (G.cam - 1);
      G.far   = 1 / (G.cam + 1);
      G.k     = 1 / (G.near - G.far);
    }
    measure();

    var DOF = 3;
    function place(d, phi, alpha) {
      var proj = 1 / (G.cam - Math.cos(phi));
      var dn   = (proj - G.far) * G.k;              // 0 at the vanishing point, 1 in the spotlight
      var x    = G.span * Math.sin(phi) * proj;     // % of stage width
      var y    = G.floor + G.rise * (1 - dn);       // % of stage height, up from the floor
      var s    = G.scale * proj / G.near;

      d.style.transform =
        'translate3d(' + (x * G.w / 100).toFixed(1) + 'px,' +
        (-y * G.h / 100).toFixed(1) + 'px,0) scale(' + s.toFixed(3) + ')';

      // Style writes are the expensive half of a 16-item rAF loop, so each
      // property is only written when its value has actually moved.
      var o = Math.round(Math.pow(dn, G.fade) * alpha * 100) / 100;
      if (o !== d._o) { d.style.opacity = o; d._o = o; }

      var z = Math.round(dn * 900) + 10;
      if (z !== d._z) { d.style.zIndex = z; d._z = z; }

      var b = Math.min(DOF - 1, Math.floor((1 - dn) * DOF));
      if (b !== d._d) {
        if (d._d >= 0) d.classList.remove('dof' + d._d);
        d.classList.add('dof' + b);
        d._d = b;
      }
    }

    // ---------- caption ----------
    var shown = -1;
    function caption(k) {
      if (k === shown) return;
      shown = k;
      var p = list[k];
      capEl.innerHTML = '<b>' + esc(p.name) + '</b><span>' + esc(p.code || p.pack || 'Swift') + '</span>';
      capEl.href = 'product.html?id=' + encodeURIComponent(p.id);
      capEl.setAttribute('tabindex', '0');
      dotEls.forEach(function (n, i) { n.classList.toggle('on', i === k); });
      nodes.forEach(function (n, i) { n.classList.toggle('is-hero', i === k); });
    }

    // ---------- the belt ----------
    var PERIOD = 2900;                 // ms between two products reaching the spotlight
    var phase = 0, last = 0, t0 = 0, raf = 0, speed = 1, want = 1;

    function render(now) {
      raf = requestAnimationFrame(render);
      if (!last) { last = now; t0 = now; }
      var dt = Math.min(64, now - last);   // a throttled tab must not jump the belt
      last = now;

      speed += (want - speed) * Math.min(1, dt / 260);
      phase += (STEP / PERIOD) * dt * speed;
      if (phase >= Math.PI * 2) phase -= Math.PI * 2;

      var since = now - t0;
      for (var i = 0; i < N; i++) {
        // the belt is already turning as the products arrive onto it
        var a = Math.max(0, Math.min(1, (since - i * 70) / 520));
        place(nodes[i], i * STEP - phase, a);      // phi decreasing => travel right to left
      }
      caption(Math.round(phase / STEP) % N);
    }

    // Slow rather than stop on hover: the caption below the stage is a link to
    // the product currently in the spotlight, so it has to be catchable.
    var host = stage.parentNode;
    host.addEventListener('pointerenter', function () { want = 0.16; });
    host.addEventListener('pointerleave', function () { want = 1; });

    function stepped() {
      // Reduced motion: hold each product in the spotlight instead of turning
      // the belt. Still shows the whole range, with no sustained movement.
      var k = 0;
      function once() {
        if (document.hidden) return;
        phase = k * STEP;
        for (var i = 0; i < N; i++) place(nodes[i], i * STEP - phase, 1);
        caption(k);
        k = (k + 1) % N;
      }
      once();
      setInterval(once, 4200);
    }

    function start() {
      stage.classList.add('lined', 'featuring');
      if (reduce) { stage.classList.add('stepped'); stepped(); return; }
      raf = requestAnimationFrame(render);
    }

    // Pause while the tab is hidden — no point animating into the void.
    document.addEventListener('visibilitychange', function () {
      if (reduce) return;
      if (document.hidden) { cancelAnimationFrame(raf); raf = 0; }
      else if (!raf && stage.classList.contains('featuring')) {
        last = 0;                       // resume from now, not from the last frame
        raf = requestAnimationFrame(render);
      }
    });

    // Re-aim on resize: the container queries swap the camera at breakpoints,
    // and every position is derived from the stage's own pixel size.
    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () {
        measure();
        if (reduce) for (var i = 0; i < N; i++) place(nodes[i], i * STEP - phase, 1);
      }, 200);
    }, { passive: true });

    // Start on the intro-done event, but never depend on it alone: if that
    // event is missed for any reason the products must still appear.
    var started = false;
    function kick() { if (started) return; started = true; setTimeout(start, 260); }
    if (window.__vxIntro && window.__vxIntro.done) kick();
    else document.addEventListener('vx:intro-done', kick, { once: true });
    setTimeout(kick, 4000);          // hard fallback
  })();

  // ---------- Hero sector rotator ----------
  // The rotator lives inside a [data-split] headline, so motion.js may rebuild
  // its DOM when fonts load or the window resizes. Everything below therefore
  // re-looks-up the host each tick and re-applies its sizing if it was lost.
  (function () {
    // Deliberately NOT gated on prefers-reduced-motion. The rotating sector is
    // content, not decoration — it names who Vistex serves. Under reduced motion
    // the CSS collapses the transition, so it becomes a plain instant swap
    // instead of a slide, which is the behaviour that setting actually asks for.
    var words = ['Hotels', 'Hospitals', 'Schools', 'Kitchens', 'Laundries', 'Pools', 'Institutions'];
    var i = 0, busy = false;

    // Reserve the width of the longest word so the headline never reflows mid-swap.
    function sizeHost(host) {
      if (host.dataset.sized) return;
      var probe = document.createElement('span');
      probe.className = 'w';
      probe.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap';
      host.appendChild(probe);
      var widest = 0;
      words.forEach(function (w) { probe.textContent = w; widest = Math.max(widest, probe.offsetWidth); });
      probe.remove();
      if (widest) host.style.minWidth = Math.ceil(widest) + 'px';
      host.dataset.sized = '1';
    }

    setInterval(function () {
      var host = $('heroRotator');
      if (!host || busy || document.hidden) return;
      sizeHost(host);

      // Sweep any stale words first. A re-split (fonts.ready / resize) restores
      // the rotator from a snapshot, and if that snapshot was taken mid-swap it
      // froze TWO words into the DOM — which then stacked behind every
      // subsequent one. Only ever keep the most recent.
      var all = host.querySelectorAll('.w');
      for (var k = 0; k < all.length - 1; k++) all[k].remove();

      var out = host.querySelector('.w');
      if (!out) return;
      out.classList.remove('in');

      busy = true;
      i = (i + 1) % words.length;
      var next = document.createElement('span');
      next.className = 'w text-grad in';
      next.textContent = words[i];
      host.appendChild(next);

      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          out.classList.add('out');
          next.classList.remove('in');
        });
      });
      setTimeout(function () { if (out.parentNode) out.remove(); busy = false; }, 560);
    }, 2600);
  })();
})();
