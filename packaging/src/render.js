// node render.js <input.html> <output.pdf>
// Renders at exactly the CSS page size — no scaling, no shrink-to-fit.
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');
const HERE = __dirname;
const [input, out] = process.argv.slice(2);
const meta = JSON.parse(fs.readFileSync(path.join(HERE, 'meta.json'), 'utf8'));
const pageH = input.includes('proof') ? meta.PAGE_H_PROOF : meta.PAGE_H;

(async () => {
  const b = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new', args: ['--no-sandbox', '--font-render-hinting=none'],
    protocolTimeout: 180000,
  });
  const p = await b.newPage();
  // Viewport exactly the page size in CSS px (96 px = 1 in). Any overflow makes
  // Chrome shrink-to-fit, which silently scaled the first build to 76%.
  const px = (v) => Math.round(v / 25.4 * 96);
  await p.setViewport({ width: px(meta.PAGE_W), height: px(pageH), deviceScaleFactor: 1 });
  await p.goto('file:///' + path.join(HERE, input).replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
  await p.evaluateHandle('document.fonts.ready');
  await new Promise(r => setTimeout(r, 500));
  const o = await p.evaluate(() => ({
    sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    sh: document.documentElement.scrollHeight, ch: document.documentElement.clientHeight }));
  if (o.sw > o.cw + 1 || o.sh > o.ch + 1) console.log('  WARNING page overflow', JSON.stringify(o));

  // Panels clip their contents, so anything past the edge is silently cut off —
  // that is how the back panel lost its web address. Report it instead.
  const clipped = await p.evaluate(() => {
    const PX = 96 / 25.4, out = [];
    for (const panel of document.querySelectorAll('.ink')) {
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
  await p.pdf({ path: out, printBackground: true, preferCSSPageSize: true,
                margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  console.log('  rendered', path.basename(out));
  await b.close();
})();
