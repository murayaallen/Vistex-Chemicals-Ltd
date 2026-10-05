// node render.js <input.html> <output.pdf> <width_mm> <height_mm>
// Renders at exactly the CSS page size — no scaling, no shrink-to-fit.
const puppeteer = require('puppeteer-core');
const path = require('path');
const [input, out, wmm, hmm] = process.argv.slice(2);

(async () => {
  const b = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new', args: ['--no-sandbox', '--font-render-hinting=none'],
    protocolTimeout: 180000,
  });
  const p = await b.newPage();
  // Viewport exactly the page size in CSS px (96 px = 1 in). Any overflow makes
  // Chrome shrink-to-fit, which silently scaled an earlier build to 76%.
  const px = (v) => Math.round(v / 25.4 * 96);
  await p.setViewport({ width: px(+wmm), height: px(+hmm), deviceScaleFactor: 1 });
  await p.goto('file:///' + path.join(__dirname, input).replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
  await p.evaluateHandle('document.fonts.ready');
  await new Promise(r => setTimeout(r, 500));

  const o = await p.evaluate(() => ({
    sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    sh: document.documentElement.scrollHeight, ch: document.documentElement.clientHeight }));
  if (o.sw > o.cw + 1 || o.sh > o.ch + 1) console.log('  WARNING page overflow', JSON.stringify(o));

  // Panels clip their contents, so anything past the edge is silently cut off.
  const clipped = await p.evaluate(() => {
    const PX = 96 / 25.4, out = [];
    for (const panel of document.querySelectorAll('.panel')) {
      const pr = panel.getBoundingClientRect();
      for (const el of panel.querySelectorAll('*')) {
        if (!el.textContent.trim() && !el.querySelector('svg,img')) continue;
        if (el.children.length && !el.textContent.trim()) continue;
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) continue;
        const over = Math.max(pr.top - r.top, r.bottom - pr.bottom,
                              pr.left - r.left, r.right - pr.right);
        if (over > 0.4 * PX) out.push({ over: +(over / PX).toFixed(2),
          text: el.textContent.trim().slice(0, 44) || el.tagName });
      }
    }
    return out;
  });
  const worst = new Map();
  for (const c of clipped) if (!worst.has(c.text) || worst.get(c.text) < c.over) worst.set(c.text, c.over);
  if (worst.size) {
    console.log('  CLIPPED inside panel:');
    for (const [t, v] of worst) console.log(`    ${v} mm over — ${JSON.stringify(t)}`);
  }

  // Flowing copy above a pinned footer: clipping only catches overflow past the
  // panel edge, so copy could silently run into the footer instead.
  const gaps = await p.evaluate(() => {
    const PX = 96 / 25.4, out = [];
    for (const [flowId, footId] of [['backflow', 'backfoot'], ['sidebflow', 'sidebfoot']]) {
      const f = document.getElementById(flowId), g = document.getElementById(footId);
      if (!f || !g) continue;
      out.push([flowId, +((g.getBoundingClientRect().top - f.getBoundingClientRect().bottom) / PX).toFixed(2)]);
    }
    return out;
  });
  for (const [id, gap] of gaps) {
    if (gap < 1.5) console.log(`  COLLISION: ${id} ends ${(-gap).toFixed(2)} mm into its footer`);
    else console.log(`  ${id} clears its footer by ${gap.toFixed(1)} mm`);
  }

  await p.pdf({ path: out, printBackground: true, preferCSSPageSize: true,
                margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  console.log('  rendered', path.basename(out));
  await b.close();
})();
