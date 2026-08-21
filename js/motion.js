// ==========================================================
// VISTEX — Motion engine
//
//  1. reveal      [data-anim]        IntersectionObserver + stagger
//  2. splitText   [data-split]       line-masked word/char cascade
//  3. parallax    [data-parallax]    rAF scroll translate
//  4. steps       .process-steps     sticky scrollytelling
//  5. counters    [data-count]       eased count-up
//  6. marquee     .marquee           velocity-reactive ticker
//  7. tilt/glow   [data-tilt]        pointer micro-interaction
//  8. chrome      scroll progress, header state
//  9. decor       aurora + bubble spawning
//
// Every module no-ops under prefers-reduced-motion: reduce.
// One shared rAF loop drives everything scroll-related.
// ==========================================================
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var scrollTasks = [];            // fns run once per animation frame
  var lastScroll = window.scrollY;
  var velocity = 0;
  var ticking = false;

  function onFrame() {
    var y = window.scrollY;
    var delta = y - lastScroll;
    lastScroll = y;
    velocity = velocity * 0.88 + delta * 0.12;

    for (var i = 0; i < scrollTasks.length; i++) scrollTasks[i](y, velocity);

    ticking = false;
    if (Math.abs(velocity) > 0.05 || alwaysRun) requestAnimationFrame(schedule);
  }
  var alwaysRun = false;
  function schedule() { if (!ticking) { ticking = true; requestAnimationFrame(onFrame); } }

  function startLoop(always) {
    if (always) alwaysRun = true;
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule, { passive: true });
    schedule();
  }

  // ==========================================================
  // 1. REVEAL
  // ==========================================================
  function initReveal() {
    var els = document.querySelectorAll('[data-anim]');
    if (reduce || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    document.querySelectorAll('.reveal-parent').forEach(function (parent) {
      var kids = parent.querySelectorAll('[data-anim]');
      kids.forEach(function (el, i) { el.style.setProperty('--i', i); });
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in');
        io.unobserve(e.target);
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -7% 0px' });
    els.forEach(function (el) { io.observe(el); });
  }

  // ==========================================================
  // 2. SPLIT TEXT — words wrapped in per-line overflow masks
  // ==========================================================
  function splitOne(el) {
    var mode = el.dataset.split || 'lines';

    if (!el._splitSource) el._splitSource = el.innerHTML;
    // A re-split rebuilds from source, which would reset any element that is
    // being driven at runtime (the hero word rotator). Snapshot and restore it.
    var live = {};
    el.querySelectorAll('[data-live][id]').forEach(function (n) { live[n.id] = n.innerHTML; });
    el.innerHTML = el._splitSource;
    Object.keys(live).forEach(function (id) {
      var n = el.querySelector('[data-live][id="' + id + '"]');
      if (n) n.innerHTML = live[id];
    });

    // -- Pass 1: replace text nodes with word spans, leave element children intact.
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
    var textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);

    textNodes.forEach(function (node) {
      var words = node.nodeValue.split(/(\s+)/);
      if (!node.nodeValue.trim()) return;
      var frag = document.createDocumentFragment();
      words.forEach(function (w) {
        if (!w) return;
        if (/^\s+$/.test(w)) {
          frag.appendChild(document.createTextNode(' '));
          return;
        }
        var span = document.createElement('span');
        span.className = 'split-unit';
        if (mode === 'chars') {
          span.style.whiteSpace = 'nowrap';
          w.split('').forEach(function (ch) {
            var c = document.createElement('span');
            c.className = 'split-unit';
            c.textContent = ch;
            span.appendChild(c);
          });
          span.classList.remove('split-unit');
          span.className = 'split-word';
          span.style.display = 'inline-block';
        } else {
          span.textContent = w;
        }
        frag.appendChild(span);
      });
      node.parentNode.replaceChild(frag, node);
    });

    // Element children that weren't text (e.g. the hero rotator) become units too.
    Array.prototype.forEach.call(el.children, function (child) {
      if (!child.classList.contains('split-unit') &&
          !child.classList.contains('split-word') &&
          !child.classList.contains('split-line')) {
        child.classList.add('split-unit');
        // Only force inline-block when the child would otherwise be inline —
        // elements with their own display (e.g. the hero rotator) keep it.
        if (getComputedStyle(child).display === 'inline') child.style.display = 'inline-block';
      }
    });

    // -- Pass 2: group units into visual lines by their offsetTop, wrap each in a mask.
    var units = Array.prototype.slice.call(el.querySelectorAll(':scope > .split-unit, :scope > .split-word'));
    if (!units.length) { el.classList.add('split-ready'); return; }

    var lines = [];
    var currentTop = null;
    units.forEach(function (u) {
      var top = u.offsetTop;
      if (currentTop === null || Math.abs(top - currentTop) > 4) {
        lines.push([]);
        currentTop = top;
      }
      lines[lines.length - 1].push(u);
    });

    lines.forEach(function (line, li) {
      var wrap = document.createElement('span');
      wrap.className = 'split-line';
      line[0].parentNode.insertBefore(wrap, line[0]);
      line.forEach(function (u, wi) {
        // pull the whitespace text node that follows the word along with it
        var next = u.nextSibling;
        wrap.appendChild(u);
        if (next && next.nodeType === 3 && !next.nodeValue.trim() && wi < line.length - 1) {
          wrap.appendChild(next);
        }
        var d = li * 110 + wi * 30;
        if (u.classList.contains('split-word')) {
          Array.prototype.forEach.call(u.children, function (c, ci) {
            c.style.setProperty('--d', (d + ci * 18) + 'ms');
          });
        } else {
          u.style.setProperty('--d', d + 'ms');
        }
      });
    });

    el.classList.add('split-ready');
  }

  function initSplit() {
    var els = document.querySelectorAll('[data-split]');
    if (!els.length) return;
    if (reduce) { els.forEach(function (el) { el.classList.add('is-in', 'split-ready'); }); return; }

    function run() { els.forEach(splitOne); }

    // Split immediately, then again once webfonts land — their metrics change
    // where the lines break, and the masks have to match the real line boxes.
    run();
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () {
        els.forEach(function (el) {
          var wasIn = el.classList.contains('is-in');
          splitOne(el);
          if (wasIn) el.classList.add('is-in');
        });
      });
    }

    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () {
        els.forEach(function (el) {
          var wasIn = el.classList.contains('is-in');
          splitOne(el);
          if (wasIn) el.classList.add('is-in');
        });
      }, 220);
    }, { passive: true });
  }

  // ==========================================================
  // 3. PARALLAX
  // ==========================================================
  function initParallax() {
    if (reduce) return;
    var els = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
    if (!els.length) return;

    scrollTasks.push(function () {
      var vh = window.innerHeight;
      els.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        var speed = parseFloat(el.dataset.parallax) || 0.1;
        var progress = (r.top + r.height / 2 - vh / 2) / vh;
        el.style.transform = 'translate3d(0,' + (-progress * speed * 100).toFixed(2) + 'px,0)';
      });
    });
    alwaysRun = true;
  }

  // ==========================================================
  // 4. PROCESS STEPS — sticky scrollytelling
  // ==========================================================
  function initSteps() {
    var wrap = document.querySelector('[data-steps]');
    if (!wrap) return;
    var steps = Array.prototype.slice.call(wrap.querySelectorAll('.pstep'));
    var num = document.querySelector('[data-step-num]');
    var lab = document.querySelector('[data-step-label]');
    if (!steps.length) return;

    var current = -1;
    function update() {
      var focal = window.innerHeight * 0.45;
      var best = 0, bestDist = Infinity;
      steps.forEach(function (s, i) {
        var r = s.getBoundingClientRect();
        var d = Math.abs(r.top + r.height / 2 - focal);
        if (d < bestDist) { bestDist = d; best = i; }
      });
      if (best === current) return;
      current = best;
      steps.forEach(function (s, i) { s.classList.toggle('active', i === best); });

      // cross-fade the photo stage and move the progress pips
      document.querySelectorAll('[data-shot]').forEach(function (el, i) {
        el.classList.toggle('active', i === best);
      });
      document.querySelectorAll('[data-pip]').forEach(function (el, i) {
        el.classList.toggle('on', i === best);
      });

      if (num) {
        num.style.opacity = '0';
        num.style.transform = 'translateY(10px)';
        setTimeout(function () {
          num.textContent = String(best + 1).padStart(2, '0');
          if (lab) lab.textContent = steps[best].dataset.label || '';
          num.style.opacity = '1';
          num.style.transform = 'none';
        }, 170);
      }
    }
    scrollTasks.push(update);
    update();
  }

  // ==========================================================
  // 5. COUNTERS
  // ==========================================================
  function initCounters() {
    // MUST be scoped to .count — `.bubbles` also uses data-count (for how many
    // bubbles to spawn), and an unscoped selector printed "14" / "16" as text
    // into the bubble containers.
    var els = document.querySelectorAll('.count[data-count]');
    if (!els.length) return;
    if (reduce || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.textContent = el.dataset.count + (el.dataset.suffix || ''); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        var el = e.target;
        var target = parseFloat(el.dataset.count) || 0;
        var suffix = el.dataset.suffix || '';
        var dur = 1500, t0 = performance.now();
        (function step(now) {
          var p = Math.min((now - t0) / dur, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(target * eased) + (p === 1 ? suffix : '');
          if (p < 1) requestAnimationFrame(step);
        })(t0);
      });
    }, { threshold: 0.4 });
    els.forEach(function (el) { io.observe(el); });
  }

  // ==========================================================
  // 6. MARQUEE — base drift + scroll-velocity boost
  // ==========================================================
  function initMarquee() {
    var track = document.querySelector('.marquee-track');
    if (!track) return;
    // Not gated on reduced motion — this ticker is content. It simply pans
    // slower, and stops reacting to scroll velocity, when that setting is on.
    var baseSpeed = reduce ? 0.20 : 0.42;

    var pos = 0, half = 0, last = performance.now();
    function measure() { half = track.scrollWidth / 2; }
    measure();
    window.addEventListener('resize', measure, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);

    (function loop(now) {
      var dt = Math.min((now - last) / 16.67, 3);
      last = now;
      pos -= (baseSpeed + (reduce ? 0 : velocity * 0.09)) * dt;
      if (half) {
        if (pos <= -half) pos += half;
        if (pos > 0) pos -= half;
      }
      track.style.transform = 'translate3d(' + pos.toFixed(2) + 'px,0,0)';
      requestAnimationFrame(loop);
    })(last);
  }

  // ==========================================================
  // 7. TILT + POINTER GLOW
  // ==========================================================
  function initPointer() {
    if (reduce || window.matchMedia('(hover: none)').matches) return;

    document.querySelectorAll('.card-glow').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        el.style.setProperty('--my', (e.clientY - r.top) + 'px');
      });
    });

    document.querySelectorAll('[data-tilt]').forEach(function (el) {
      var max = parseFloat(el.dataset.tilt) || 5;
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform =
          'perspective(900px) rotateX(' + (-py * max).toFixed(2) + 'deg) rotateY(' +
          (px * max).toFixed(2) + 'deg) translateY(-4px)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  }

  // ==========================================================
  // 8. CHROME — scroll progress + header state
  // ==========================================================
  function initChrome() {
    var header = document.querySelector('.site-header');
    var bar = document.querySelector('.scroll-progress');
    if (!header && !bar) return;

    scrollTasks.push(function (y) {
      if (header) header.classList.toggle('scrolled', y > 24);
      if (bar) {
        var max = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.setProperty('--sp', max > 0 ? (y / max).toFixed(4) : 0);
      }
    });
  }

  // ==========================================================
  // 9b. BACKGROUND VIDEO — armed early, played only when ready
  // Starts downloading ~1200px before it scrolls into view, so by the time the
  // band is on screen the clip is buffered. It is never played on a guess:
  // canplaythrough is the browser's own promise it can run without stalling.
  // Falls back silently to the poster if that never arrives.
  // ==========================================================
  function initBgVideo() {
    var vids = document.querySelectorAll('video[data-src]');
    if (!vids.length) return;
    if (reduce || !('IntersectionObserver' in window)) return;   // poster only

    // Respect a metered connection — never pull a background video on save-data.
    var conn = navigator.connection || {};
    if (conn.saveData || /(^|-)2g$/.test(conn.effectiveType || '')) return;

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var v = e.target;
        io.unobserve(v);
        v.src = v.dataset.src;
        v.preload = 'auto';
        v.load();
        v.addEventListener('canplaythrough', function () {
          var band = v.closest('.stats-band');
          var p = v.play();
          if (p && p.catch) p.catch(function () {});
          if (band) band.classList.add('video-live');
        }, { once: true });
      });
    }, { rootMargin: '1200px 0px' });

    vids.forEach(function (v) { io.observe(v); });

    // Pause when off screen or the tab is hidden — no point decoding frames
    // nobody is looking at.
    var vis = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        if (!v.src) return;
        if (e.isIntersecting) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
        else v.pause();
      });
    }, { threshold: 0.05 });
    vids.forEach(function (v) { vis.observe(v); });

    document.addEventListener('visibilitychange', function () {
      vids.forEach(function (v) {
        if (!v.src) return;
        if (document.hidden) v.pause();
      });
    });
  }

  // ==========================================================
  // 9. DECOR — aurora layers + drifting bubbles
  // ==========================================================
  function initDecor() {
    if (reduce) return;

    document.querySelectorAll('.aurora:empty').forEach(function (host) {
      host.innerHTML = '<span class="a1"></span><span class="a2"></span><span class="a3"></span>';
    });

    document.querySelectorAll('.bubbles:empty').forEach(function (box) {
      var n = parseInt(box.dataset.count || '12', 10);
      var frag = document.createDocumentFragment();
      for (var i = 0; i < n; i++) {
        var b = document.createElement('span');
        b.className = 'bubble';
        var size = 6 + Math.random() * 30;
        b.style.width = size + 'px';
        b.style.height = size + 'px';
        b.style.left = (Math.random() * 100).toFixed(2) + '%';
        b.style.animationDuration = (9 + Math.random() * 12).toFixed(1) + 's';
        b.style.animationDelay = (-Math.random() * 14).toFixed(1) + 's';
        frag.appendChild(b);
      }
      box.appendChild(frag);
    });
  }

  // ==========================================================
  // BOOT
  // ==========================================================
  // Split elements are rebuilt once webfonts land (their metrics move the line
  // breaks). If the reveal fired before that rebuild, the freshly-created units
  // would inherit the finished state and the animation would simply not play.
  // So: hold the reveal until the split has settled.
  function whenSplitSettled(cb) {
    if (reduce || !document.querySelector('[data-split]')) return cb();
    var done = false;
    function go() { if (done) return; done = true; cb(); }
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { requestAnimationFrame(go); });
      setTimeout(go, 1200);            // fonts blocked or never resolve
    } else {
      go();
    }
  }

  // The loader covers the viewport for ~1.15s. Revealing on fonts.ready alone
  // meant the whole hero animation played behind an opaque veil and was already
  // finished by the time it lifted. Wait for the intro to start clearing.
  function whenIntroDone(cb) {
    if (reduce || !window.__vxIntro || window.__vxIntro.done) return cb();
    var fired = false;
    function go() { if (fired) return; fired = true; cb(); }
    document.addEventListener('vx:intro-done', go, { once: true });
    setTimeout(go, 3000);              // never strand the page on a missed event
  }

  function init() {
    window.__vxMotionPending = false;   // stand down the reveal failsafe in partials.js
    initDecor();
    initSplit();
    whenSplitSettled(function () { whenIntroDone(initReveal); });
    initCounters();
    initMarquee();
    initPointer();
    initChrome();
    initBgVideo();
    initParallax();
    initSteps();
    startLoop(false);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  // Re-run reveal/split/icons over content injected later (e.g. catalog filtering).
  window.VistexMotion = {
    refresh: function (root) {
      root = root || document;
      if (window.hydrateIcons) window.hydrateIcons(root);
      if (reduce || !('IntersectionObserver' in window)) {
        root.querySelectorAll('[data-anim]').forEach(function (el) { el.classList.add('is-in'); });
        return;
      }
      root.querySelectorAll('.reveal-parent').forEach(function (parent) {
        parent.querySelectorAll('[data-anim]').forEach(function (el, i) { el.style.setProperty('--i', i); });
      });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add('is-in');
          io.unobserve(e.target);
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -7% 0px' });
      root.querySelectorAll('[data-anim]:not(.is-in)').forEach(function (el) { io.observe(el); });
    }
  };
})();
