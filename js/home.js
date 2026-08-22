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
  // HERO PRODUCT STAGE
  //   Stage 1 "Cascade Shelf" — the ten products rise one after another
  //                             and settle onto a shared shelf line.
  //   Stage 2 "Hero Lift"     — the line-up clears and each product takes
  //                             centre stage in turn, floating in place.
  // Starts on vx:intro-done so it plays after the loader lifts, never behind it.
  // ==========================================================
  (function () {
    var stage = $('productStage');
    if (!stage) return;
    var itemsEl = $('pstageItems');
    var capEl   = $('pstageCap');
    var reduce  = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Two tiers, so each product is big enough to read at hero size.
    //   back  = the 4 jerricans, raised and slightly smaller for depth
    //   front = the 6 buckets, on the shelf line
    var all = V.products.filter(function (p) { return p.cutout; });
    var back  = all.filter(function (p) { return p.vessel === 'jerrican'; });
    var front = all.filter(function (p) { return p.vessel === 'bucket'; });
    if (!front.length && !back.length) return;

    // Spread each tier across its own span. The inset MUST be derived from the
    // live item width — it changes with the container queries (15.5% desktop,
    // up to 30% on a phone), and a hard-coded inset pushed the end products
    // past the stage edge on small screens.
    function pw(name, fallback) {
      var v = parseFloat(getComputedStyle(stage).getPropertyValue(name));
      return isNaN(v) ? fallback : v;
    }
    function spread(n, i, inset) {
      if (n === 1) return 50;
      return inset + i * ((100 - inset * 2) / (n - 1));
    }

    // Cascade order: back tier first (builds depth), then front.
    var items = [];
    // Front tier first, then slot the jerricans into the actual GAP MIDPOINTS
    // between buckets — evenly spreading them put two almost exactly behind a
    // bucket, which is the one arrangement to avoid.
    // half the item width + 1% breathing room keeps every product inside the box
    var frontInset = pw('--pw-front', 21.5) / 2 + 1;
    var frontPos = front.map(function (_, i) { return spread(front.length, i, frontInset); });
    var gaps = [];
    for (var g = 0; g < frontPos.length - 1; g++) gaps.push((frontPos[g] + frontPos[g + 1]) / 2);
    // choose a symmetric subset of gaps for however many jerricans there are
    var pick = [];
    if (back.length >= gaps.length) pick = gaps.slice(0, back.length);
    else {
      var drop = gaps.length - back.length;          // drop from the middle outwards
      var mid = Math.floor(gaps.length / 2);
      var skip = {};
      for (var k = 0; k < drop; k++) skip[mid + (k % 2 ? Math.ceil(k / 2) : -Math.ceil(k / 2))] = 1;
      gaps.forEach(function (v, gi) { if (!skip[gi]) pick.push(v); });
    }
    var backInset = pw('--pw-back', 19) / 2 + 1;
    back.forEach(function (p, i) {
      items.push({ p: p, tier: 'back', left: pick[i] != null ? pick[i] : spread(back.length, i, backInset) });
    });
    front.forEach(function (p, i) {
      items.push({ p: p, tier: 'front', left: frontPos[i] });
    });

    // ---------- build ----------
    var dots = document.createElement('div');
    dots.className = 'pstage-dots';
    var nodes = items.map(function (it, i) {
      var p = it.p;
      var d = document.createElement('div');
      d.className = 'pitem tier-' + it.tier;
      d.style.left = it.left.toFixed(2) + '%';
      // front tier always above back; within a tier, centre-forward
      var mid = (it.tier === 'front' ? front.length : back.length - 1) / 2;
      d.style.zIndex = String((it.tier === 'front' ? 20 : 5) + Math.round(3 - Math.abs(i - mid)));
      d.style.opacity = '0';
      d.innerHTML = '<picture><source srcset="' + p.cutout.replace('.png', '.webp') +
        '" type="image/webp"><img src="' + p.cutout + '" alt="' + esc(p.name) +
        (p.code ? ' ' + esc(p.code) : '') + '" width="406" height="466" ' +
        (i < 5 ? 'loading="eager"' : 'loading="lazy"') + ' decoding="async"></picture>';
      itemsEl.appendChild(d);
      dots.appendChild(document.createElement('i'));
      return d;
    });
    ($('pstageMeta') || stage).appendChild(dots);

    var dotEls = Array.prototype.slice.call(dots.children);
    function anim(el, frames, opts) {
      if (!el.animate) { el.style.opacity = '1'; return null; }
      return el.animate(frames, opts);
    }

    // ---------- Stage 1: Cascade Shelf ----------
    var groupAnims = [];
    function cascade(done) {
      stage.classList.add('lined');
      var STEP = reduce ? 40 : 85, DUR = reduce ? 320 : 760;
      groupAnims.length = 0;
      nodes.forEach(function (d, i) {
        // Commit the settled state inline; fill:'both' still holds the first
        // keyframe through the stagger delay, so the cascade reads the same
        // while the element always ends up in a known state.
        d.style.opacity = '1';
        d.style.transform = '';
        groupAnims.push(anim(d,
          reduce
            ? [{ opacity: 0 }, { opacity: 1 }]
            : [{ opacity: 0, transform: 'translateY(70px) scale(.9)' },
               { opacity: 1, transform: 'translateY(-10px) scale(1.02)', offset: .75 },
               { opacity: 1, transform: 'translateY(0) scale(1)' }],
          { duration: DUR, delay: i * STEP, easing: 'cubic-bezier(.2,1.3,.35,1)', fill: 'both' }));
      });
      setTimeout(done, (nodes.length - 1) * STEP + DUR + (reduce ? 500 : 1300));
    }

    // ---------- Stage 2: Hero Lift ----------
    var idx = 0, timer = null, bob = null;

    function feature(first) {
      var p = items[idx].p;
      stage.classList.add('featuring');
      stage.classList.remove('lined');

      // The cascade ran with fill:'both', so those animations keep asserting
      // opacity:1 forever — and a filling animation outranks inline style.
      // They must be retired or the hidden products spring straight back.
      if (groupAnims.length) {
        groupAnims.forEach(function (a) { if (a) { try { a.cancel(); } catch (e) {} } });
        groupAnims.length = 0;
      }

      nodes.forEach(function (d, i) {
        var isHero = i === idx;
        d.classList.toggle('is-hero', isHero);

        var fromT = d.style.transform || 'none';
        var fromO = d.style.opacity || getComputedStyle(d).opacity;

        if (isHero) {
          // Move only PART of the way to centre. Fully centring it would cover
          // the group; this keeps the product in context while still stepping
          // it clearly forward, and stops edge items overflowing the stage.
          var dx = 50 - items[i].left;               // full centre — stage is clear
          // A featured jerrican drops to the bucket baseline, so every product
          // steps out to the same place regardless of which tier it lives in.
          var dy = items[i].tier === 'back' ? (0.44 - 0.15) * stage.clientHeight : 0;

          var scale = parseFloat(getComputedStyle(stage).getPropertyValue('--hero-scale')) || 1.62;
          if (items[i].tier === 'back') scale *= 21.5 / 19;
          if (reduce) scale *= 0.94;

          var target = 'translateX(' + dx + 'cqw) translateY(' + dy + 'px) scale(' + scale + ')';

          d.style.zIndex = '40';
          d.style.opacity = '1';
          d.style.filter = 'none';
          d.style.transform = target;

          // park the light pool under wherever the product actually lands
          stage.style.setProperty('--pool-x', '50%');

          if (bob) { try { bob.cancel(); } catch (e) {} bob = null; }
          anim(d, [{ opacity: fromO, transform: fromT }, { opacity: 1, transform: target }],
            { duration: reduce ? 260 : (first ? 780 : 620),
              easing: 'cubic-bezier(.2,1.22,.35,1)', fill: 'none' });

          if (!reduce) {
            (function (el, t, y) {
              setTimeout(function () {
                if (!el.classList.contains('is-hero')) return;
                bob = anim(el,
                  [{ transform: t },
                   { transform: t.replace('translateY(' + y + 'px)', 'translateY(' + (y - 10) + 'px)') },
                   { transform: t }],
                  { duration: 3400, iterations: Infinity, easing: 'ease-in-out' });
              }, first ? 800 : 640);
            })(d, target, dy);
          }
        } else {
          // Clear the stage: after the group presentation only the featured
          // product remains, so nothing competes with it.
          var out = 'translateY(26px) scale(.88)';
          d.style.zIndex = '10';
          d.style.opacity = '0';
          d.style.filter = 'none';
          d.style.transform = out;
          anim(d, [{ opacity: fromO, transform: fromT }, { opacity: 0, transform: out }],
            { duration: reduce ? 200 : 400, easing: 'ease-in', fill: 'none' });
        }
      });

      capEl.innerHTML = '<b>' + esc(p.name) + '</b><span>' + esc(p.code || 'Swift') + '</span>';
      capEl.href = 'product.html?id=' + encodeURIComponent(p.id);
      capEl.setAttribute('tabindex', '0');
      anim(capEl, [{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'none' }],
        { duration: 400, easing: 'cubic-bezier(.22,1,.36,1)', fill: 'both' });
      dotEls.forEach(function (n, i) { n.classList.toggle('on', i === idx); });
    }

    function loop() {
      idx = (idx + 1) % items.length;
      feature(false);
    }

    function start() {
      cascade(function () {
        feature(true);
        timer = setInterval(loop, reduce ? 4200 : 2900);
      });
    }

    // Pause while the tab is hidden — no point animating into the void.
    document.addEventListener('visibilitychange', function () {
      if (document.hidden && timer) { clearInterval(timer); timer = null; }
      else if (!document.hidden && !timer && stage.classList.contains('featuring')) {
        timer = setInterval(loop, reduce ? 4200 : 2900);
      }
    });

    // Re-lay-out when the stage changes width: the container queries swap --pw
    // at breakpoints, so the positions computed from it must follow.
    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () {
        var fi = pw('--pw-front', 21.5) / 2 + 1, bi = pw('--pw-back', 19) / 2 + 1;
        var fp = front.map(function (_, i) { return spread(front.length, i, fi); });
        var gp = [];
        for (var g = 0; g < fp.length - 1; g++) gp.push((fp[g] + fp[g + 1]) / 2);
        var pk = [];
        if (back.length >= gp.length) pk = gp.slice(0, back.length);
        else {
          var dr = gp.length - back.length, md = Math.floor(gp.length / 2), sk = {};
          for (var k = 0; k < dr; k++) sk[md + (k % 2 ? Math.ceil(k / 2) : -Math.ceil(k / 2))] = 1;
          gp.forEach(function (v, gi) { if (!sk[gi]) pk.push(v); });
        }
        var bn = 0, fn = 0;
        items.forEach(function (it, i) {
          it.left = it.tier === 'back'
            ? (pk[bn] != null ? pk[bn++] : spread(back.length, bn++, bi))
            : fp[fn++];
          if (!nodes[i].classList.contains('is-hero')) nodes[i].style.left = it.left.toFixed(2) + '%';
        });
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
