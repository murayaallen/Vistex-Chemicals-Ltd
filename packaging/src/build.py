"""Swift Toilet Blocks — 4 x 50 g folding carton artwork.

Builds a print-ready flat carton at true size (mm) as HTML that Chrome renders
to vector PDF. Everything is vector except the Vistex wordmark (755 px PNG,
~600 dpi at its printed size); the Swift oval is stamped in afterwards from the
supplied vector PDF by stamp.py, because Chrome cannot carry its gradients
through an <img> without rasterising them.

Writes two files:
  carton.html        artwork only, 261 x 216 mm  -> goes to plate
  carton-proof.html  artwork + dieline + legend  -> for checking and approval

Geometry: straight tuck end (STE) carton, 68 (w) x 118 (h) x 52 (d) mm.
"""
import json, math, pathlib

HERE = pathlib.Path(__file__).parent
A = json.loads((HERE / "assets.json").read_text(encoding="utf8"))

# ---------------------------------------------------------------- geometry
W_PANEL, H_PANEL, D_PANEL = 68.0, 118.0, 52.0
GLUE, TUCK, BLEED = 15.0, 46.0, 3.0
LEGEND = 19.0                                   # proof-only annotation band

FLAT_W = GLUE + W_PANEL + D_PANEL + W_PANEL + D_PANEL   # 255
FLAT_H = TUCK + H_PANEL + TUCK                          # 210
PAGE_W = FLAT_W + BLEED * 2                             # 261
PAGE_H = FLAT_H + BLEED * 2                             # 216

X_GLUE  = BLEED
X_BACK  = X_GLUE + GLUE
X_SIDEL = X_BACK + W_PANEL
X_FRONT = X_SIDEL + D_PANEL
X_SIDER = X_FRONT + W_PANEL
Y_TOP   = BLEED
Y_BODY  = Y_TOP + TUCK
Y_BOT   = Y_BODY + H_PANEL

NAVY, BLUE, BRAND = "#061A4A", "#123A9E", "#2E3995"
AQUA, PALE, RED   = "#00A6E6", "#BFE6FA", "#ED1E26"
INK, MUTED        = "#1B2440", "#55608A"


def mm(v):
    return f"{v:.3f}mm"


# ---------------------------------------------------------------- product art
def block_svg(uid, ridges=26):
    cx, cy, rx, ry, depth = 100.0, 66.0, 88.0, 48.0, 23.0
    o = ['<svg viewBox="0 0 200 150" xmlns="http://www.w3.org/2000/svg" '
         'preserveAspectRatio="xMidYMid meet">']
    o.append(f'''<defs>
      <linearGradient id="sd{uid}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#1B50C8"/><stop offset=".55" stop-color="#0E2E86"/>
        <stop offset="1" stop-color="#071E5C"/></linearGradient>
      <radialGradient id="tp{uid}" cx=".38" cy=".30" r=".85">
        <stop offset="0" stop-color="#4E8BEE"/><stop offset=".55" stop-color="#1E52C4"/>
        <stop offset="1" stop-color="#0B2E88"/></radialGradient>
      <linearGradient id="gl{uid}" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#FFF" stop-opacity=".55"/>
        <stop offset=".45" stop-color="#FFF" stop-opacity=".06"/>
        <stop offset="1" stop-color="#FFF" stop-opacity="0"/></linearGradient></defs>''')
    o.append(f'<path d="M{cx-rx:.2f},{cy:.2f} v{depth:.2f} '
             f'a{rx:.2f},{ry:.2f} 0 0 0 {rx*2:.2f},0 v-{depth:.2f} '
             f'a{rx:.2f},{ry:.2f} 0 0 1 -{rx*2:.2f},0 z" fill="url(#sd{uid})"/>')
    for i in range(ridges):
        a = math.pi * (i + .5) / ridges
        x, y = cx - rx * math.cos(a), cy + ry * math.sin(a)
        o.append(f'<path d="M{x:.2f},{y:.2f} v{depth:.2f}" stroke="#061A4A" '
                 f'stroke-opacity="{.30 if i % 2 else .10}" stroke-width="2.6"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#tp{uid})"/>')
    for i in range(ridges):
        a = 2 * math.pi * i / ridges
        o.append(f'<path d="M{cx+rx*.30*math.cos(a):.2f},{cy+ry*.30*math.sin(a):.2f} '
                 f'L{cx+rx*.95*math.cos(a):.2f},{cy+ry*.95*math.sin(a):.2f}" '
                 f'stroke="#9CC6FF" stroke-opacity=".40" stroke-width="2.2" stroke-linecap="round"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*.30:.2f}" ry="{ry*.30:.2f}" '
             f'fill="#0A2C84" fill-opacity=".55"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#gl{uid})"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" '
             f'stroke="#A9D4FF" stroke-opacity=".5" stroke-width="1.6"/></svg>')
    return "".join(o)


def icon(name, col="#FFFFFF"):
    p = {
      "flush":   '<path d="M5 4h14v5a7 7 0 0 1-14 0z"/><path d="M9 4V2h6v2"/><path d="M12 16v6"/>',
      "germ":    '<circle cx="12" cy="12" r="5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
      "scale":   '<path d="M3 20l5-9 4 5 3-4 6 8z"/><circle cx="8" cy="6" r="2.5"/>',
      "fresh":   '<path d="M12 3c3 4 5 6 5 9a5 5 0 0 1-10 0c0-3 2-5 5-9z"/>',
      "tank":    '<rect x="4" y="5" width="16" height="9" rx="1.5"/><path d="M8 14v5h8v-5M12 8v3"/>',
      "sparkle": '<path d="M12 4l1.8 4.7L18.5 10l-4.7 1.8L12 16l-1.8-4.2L5.5 10l4.7-1.3z"/><path d="M18 16l.9 2.1L21 19l-2.1.9L18 22l-.9-2.1L15 19l2.1-.9z"/>',
    }[name]
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="{col}" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round">{p}</svg>')


# ---------------------------------------------------------------- copy
DESC = ("Swift Toilet Blocks clean, freshen and protect the toilet bowl with every "
        "flush. Each block dissolves gradually, helping prevent limescale and stains "
        "while leaving a long-lasting fresh fragrance.")
STEPS = [("tank",    "Lift the cistern lid and drop one block into the tank, clear of the inlet and float."),
         ("flush",   "The block dissolves gradually, releasing cleaner with every flush."),
         ("sparkle", "Replace when fully dissolved — about one block per month.")]
BENEFITS = [("flush", "Cleans with every flush"), ("germ", "Fights germs"),
            ("scale", "Prevents limescale & stains"), ("fresh", "Long-lasting freshness")]
IDEAL = ["Homes", "Hotels & lodges", "Restaurants", "Schools",
         "Hospitals", "Offices", "Public washrooms"]
CAUTION = ["Keep out of reach of children.", "Do not ingest.",
           "Avoid contact with skin and eyes.", "Wash hands after handling.",
           "Use only as directed."]

CSS_T = """
@page {{ size: {pw}mm {ph}mm; margin: 0; }}
@font-face {{ font-family: Outfit; src: url(data:font/woff2;base64,{fo}) format('woff2');
  font-weight: 100 900; font-display: block; }}
@font-face {{ font-family: Outfit; src: url(data:font/woff2;base64,{foe}) format('woff2');
  font-weight: 100 900; unicode-range: U+0100-024F; font-display: block; }}
@font-face {{ font-family: Jakarta; src: url(data:font/woff2;base64,{fj}) format('woff2');
  font-weight: 200 800; font-display: block; }}
* {{ margin:0; padding:0; box-sizing:border-box;
     -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
html,body {{ width:{pw}mm; height:{ph}mm; }}
body {{ font-family: Jakarta, sans-serif; background:#fff; position:relative; overflow:hidden; }}
.panel {{ position:absolute; overflow:hidden; }}
.ink   {{ position:absolute; overflow:hidden; }}

.h-prod {{ font-family:Outfit; font-weight:900; letter-spacing:-.025em; line-height:.9;
           text-transform:uppercase; color:#fff; white-space:nowrap; }}
.kicker {{ font-family:Outfit; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }}

.blue {{ background: radial-gradient(118% 76% at 50% 15%, #2E6BD8 0%, #12399B 46%, {navy} 100%); }}
.blue::after {{ content:""; position:absolute; inset:0;
  background: radial-gradient(58% 32% at 50% 60%, rgba(140,200,255,.28), transparent 70%); }}

.f-c   {{ position:absolute; width:100%; text-align:center; }}
.f-rule{{ position:absolute; height:.45mm;
          background:linear-gradient(90deg,transparent,{aqua},transparent); }}
.chips {{ position:absolute; display:flex; justify-content:center; width:100%; }}
.chip  {{ display:flex; flex-direction:column; align-items:center; width:17mm; }}
.chip span {{ font-family:Outfit; font-weight:700; letter-spacing:.05em;
              text-transform:uppercase; color:#fff; text-align:center; line-height:1.1; }}
.badge {{ position:absolute; left:50%; transform:translateX(-50%); display:flex;
          align-items:baseline; white-space:nowrap; background:#fff;
          border-radius:1.8mm; box-shadow:0 .5mm 1.4mm rgba(0,0,0,.20); }}

.white {{ background:#fff; }}
.hdr {{ display:inline-block; background:{brand}; color:#fff; font-family:Outfit;
        font-weight:700; letter-spacing:.10em; text-transform:uppercase; border-radius:1.1mm;
        white-space:nowrap; line-height:1; }}
.hdr.red {{ background:{red}; }}
.li {{ display:flex; gap:1.6mm; align-items:flex-start; }}
.li i {{ flex:none; border-radius:50%; background:{aqua}; }}
.rule {{ height:.25mm; background:#D4DCEF; }}
.qrbox {{ background:#fff; }}
.qrbox svg {{ width:100%; height:100%; display:block; }}
.qrbox svg path {{ fill:#0A1430; }}

.s-row {{ display:flex; align-items:center; }}
.flap {{ background:{navy}; }}

.die {{ position:absolute; left:0; top:0; pointer-events:none; }}
.die line, .die rect, .die path {{ fill:none; }}
.cut    {{ stroke:#E6007E; stroke-width:.35; }}
.crease {{ stroke:#00AEEF; stroke-width:.35; stroke-dasharray:2.2 1.4; }}
.bleedl {{ stroke:#9A9A9A; stroke-width:.3; stroke-dasharray:1.2 1.2; }}
/* font-size is an SVG attribute in user units (1 unit = 1 mm); a CSS mm value
   inside a viewBox resolves inconsistently and rendered about 4x too large. */
.dlabel {{ font-family:Jakarta; fill:#E6007E; font-weight:700; }}
.dnote  {{ font-family:Jakarta; fill:#2B3350; }}
.dkey   {{ font-family:Jakarta; font-weight:700; }}
"""


# ---------------------------------------------------------------- panels
def front():
    x, y, w, h = X_FRONT, Y_BODY, W_PANEL, H_PANEL
    lay = [(0.0, 6.0, 25.0, ".92"), (17.0, 1.5, 31.0, "1"), (36.0, 6.5, 23.0, ".88")]
    blocks = f'<div style="position:absolute;left:{mm(5)};top:{mm(68.8)};width:{mm(w-10)};height:{mm(23)}">'
    for i, (bx, by, bw, op) in enumerate(lay):
        blocks += (f'<div style="position:absolute;left:{mm(bx)};top:{mm(by)};width:{mm(bw)};'
                   f'opacity:{op}">{block_svg("f%d" % i)}</div>')
    blocks += "</div>"
    chips = "".join(
        f'<div class="chip"><div style="width:{mm(5.0)};height:{mm(5.0)};margin-bottom:{mm(1.1)}">'
        f'{icon(k)}</div><span style="font-size:{mm(2.45)}">{t}</span></div>'
        for k, t in [("flush", "Cleans"), ("fresh", "Freshens"), ("germ", "Protects")])

    return f"""
<div class="panel blue" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)}"></div>
<div class="ink" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)}">
  <div id="swift-front" style="position:absolute;left:{mm((w-36)/2)};top:{mm(7)};
       width:{mm(36)};height:{mm(18)}"></div>
  <div class="f-c h-prod" style="top:{mm(30.0)};font-size:{mm(12.6)}">TOILET</div>
  <div class="f-c h-prod" style="top:{mm(41.2)};font-size:{mm(12.6)}">BLOCKS</div>
  <div class="f-rule" style="left:{mm(w/2-13)};top:{mm(55.7)};width:{mm(26)}"></div>
  <div class="f-c" style="top:{mm(58.5)};font-family:Outfit;font-weight:600;
       font-size:{mm(3.35)};letter-spacing:.05em;color:{PALE}">AUTOMATIC TOILET BOWL CLEANER</div>
  <div class="f-c" style="top:{mm(62.9)};font-size:{mm(2.75)};font-weight:500;
       letter-spacing:.02em;color:rgba(255,255,255,.74)">Cleans &middot; Freshens &middot; Prevents limescale</div>
  {blocks}
  <div class="chips" style="top:{mm(95.3)}">{chips}</div>
  <div class="badge" style="top:{mm(105.2)};padding:{mm(1.7)} {mm(4.0)};gap:{mm(2.6)}">
    <span style="font-family:Outfit;font-weight:900;font-size:{mm(6.4)};color:{BRAND};
          letter-spacing:-.01em">50 g &times; 4</span>
    <span style="font-family:Outfit;font-weight:700;font-size:{mm(2.5)};color:{BLUE};
          letter-spacing:.05em">NET WT. 200 g</span>
  </div>
</div>"""


def back():
    x, y, w, h = X_BACK, Y_BODY, W_PANEL, H_PANEL
    pad, iw = 5.0, W_PANEL - 10.0
    o = [f'<div class="panel white" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)}"></div>',
         f'<div class="ink" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)}">']
    cy = 6.0

    def at(top, html):
        return f'<div style="position:absolute;left:{mm(pad)};top:{mm(top)};width:{mm(iw)}">{html}</div>'

    o.append(at(cy, f'<span style="font-family:Outfit;font-weight:800;font-size:{mm(4.4)};'
                    f'color:{BRAND};letter-spacing:-.012em">Swift Toilet Blocks</span>'))
    cy += 5.3
    o.append(at(cy, f'<span style="font-family:Outfit;font-weight:600;font-size:{mm(2.6)};'
                    f'color:{AQUA};letter-spacing:.075em;text-transform:uppercase;line-height:1.05">'
                    f'Automatic toilet bowl cleaner</span>'))
    cy += 5.2
    o.append(at(cy, '<div class="rule"></div>'))
    cy += 2.6
    o.append(at(cy, f'<div style="font-size:{mm(2.5)};line-height:1.44;color:{INK}">{DESC}</div>'))
    cy += 14.8

    o.append(at(cy, f'<span class="hdr" style="font-size:{mm(2.7)};padding:{mm(1.0)} {mm(2.3)}">How to use</span>'))
    cy += 6.4
    for i, (ic, t) in enumerate(STEPS):
        o.append(f'<div style="position:absolute;left:{mm(pad)};top:{mm(cy)};width:{mm(iw)};'
                 f'display:flex;gap:{mm(1.9)};align-items:flex-start">'
                 f'<div style="flex:none;width:{mm(5.2)};height:{mm(5.2)};border-radius:50%;'
                 f'background:{BRAND};display:flex;align-items:center;justify-content:center">'
                 f'<div style="width:{mm(3.0)};height:{mm(3.0)}">{icon(ic)}</div></div>'
                 f'<div style="font-size:{mm(2.45)};line-height:1.34;color:{INK};padding-top:{mm(.45)}">'
                 f'<b style="color:{BRAND}">{i+1}.</b> {t}</div></div>')
        cy += 7.0
    cy += 1.6

    o.append(at(cy, f'<span class="hdr red" style="font-size:{mm(2.7)};padding:{mm(1.0)} {mm(2.3)}">Caution</span>'))
    cy += 6.4
    for t in CAUTION:
        o.append(f'<div class="li" style="position:absolute;left:{mm(pad)};top:{mm(cy)};width:{mm(iw)}">'
                 f'<i style="width:{mm(1.0)};height:{mm(1.0)};margin-top:{mm(.9)};background:{RED}"></i>'
                 f'<div style="font-size:{mm(2.4)};line-height:1.3;color:{INK}">{t}</div></div>')
        cy += 3.4
    cy += 1.2
    o.append(at(cy, '<div class="rule"></div>'))
    cy += 2.0
    o.append(at(cy, f'<div style="font-size:{mm(2.2)};line-height:1.32;color:{MUTED}">'
                    f'<b style="color:{BRAND}">Active ingredients:</b> sodium dichloroisocyanurate, '
                    f'anionic &amp; non-ionic surfactants, fragrance, colourant.</div>'))

    # footer
    fy = h - 20.5
    qr = 15.5
    o.append(f'<img src="data:image/png;base64,{A["vistex"]}" style="position:absolute;'
             f'left:{mm(pad)};top:{mm(fy)};width:{mm(27)};height:auto">')
    o.append(f'<div style="position:absolute;left:{mm(pad)};top:{mm(fy+9.4)};width:{mm(w-pad*2-qr-1.0)};'
             f'font-size:{mm(1.9)};line-height:1.40;color:{MUTED}">'
             f'P.O. Box 218 &ndash; 00606, Industrial Area, Nairobi<br>'
             f'0739 446 655 &middot; info@vistexchemicals.co.ke<br>www.vistexchemicals.co.ke</div>')
    o.append(f'<div class="qrbox" style="position:absolute;left:{mm(w-pad-qr-1)};top:{mm(fy)};'
             f'width:{mm(qr)};height:{mm(qr)};padding:{mm(.9)}">{A["qr_svg"]}</div>')
    o.append(f'<div style="position:absolute;left:{mm(w-pad-qr-4)};top:{mm(fy+qr+1.2)};'
             f'width:{mm(qr+5)};text-align:center;font-size:{mm(1.85)};color:{MUTED};'
             f'letter-spacing:.01em;line-height:1.25">Scan for more info</div>')
    o.append("</div>")
    return "".join(o)


def side_left():
    x, y, w, h = X_SIDEL, Y_BODY, D_PANEL, H_PANEL
    pad = 5.5
    o = [f'<div class="panel blue" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)}"></div>',
         f'<div class="ink" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)}">']
    o.append(f'<div id="swift-sidel" style="position:absolute;left:{mm((w-30)/2)};top:{mm(8)};'
             f'width:{mm(30)};height:{mm(15)}"></div>')
    o.append(f'<div class="kicker" style="position:absolute;left:0;top:{mm(26.5)};width:100%;'
             f'text-align:center;font-size:{mm(2.5)};color:{PALE}">Why it works</div>')
    cy = 34.0
    for ic, t in BENEFITS:
        o.append(f'<div class="s-row" style="position:absolute;left:{mm(pad)};top:{mm(cy)};'
                 f'width:{mm(w-pad*2)};gap:{mm(2.2)}">'
                 f'<div style="flex:none;width:{mm(6.0)};height:{mm(6.0)};border-radius:{mm(1.5)};'
                 f'background:rgba(255,255,255,.15);display:flex;align-items:center;justify-content:center">'
                 f'<div style="width:{mm(3.6)};height:{mm(3.6)}">{icon(ic)}</div></div>'
                 f'<div style="font-family:Outfit;font-weight:600;font-size:{mm(2.7)};color:#fff;'
                 f'line-height:1.2">{t}</div></div>')
        cy += 12.8
    o.append(f'<div style="position:absolute;left:{mm(pad)};top:{mm(h-26)};width:{mm(w-pad*2)};'
             f'height:.4mm;background:rgba(255,255,255,.22)"></div>')
    o.append(f'<div style="position:absolute;left:0;top:{mm(h-21.5)};width:100%;text-align:center;'
             f'font-family:Outfit;font-weight:800;font-size:{mm(4.2)};color:#fff;white-space:nowrap">'
             f'50 g &times; 4</div>')
    o.append(f'<div style="position:absolute;left:0;top:{mm(h-15.6)};width:100%;text-align:center;'
             f'font-size:{mm(2.25)};color:{PALE};letter-spacing:.07em">NET WT. 200 g</div>')
    o.append("</div>")
    return "".join(o)


def side_right():
    x, y, w, h = X_SIDER, Y_BODY, D_PANEL, H_PANEL
    pad, iw = 5.5, D_PANEL - 11.0
    o = [f'<div class="panel white" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)}"></div>',
         f'<div class="ink" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)}">']
    o.append(f'<div style="position:absolute;left:0;top:0;width:100%;height:{mm(8)};background:{BRAND}"></div>')
    o.append(f'<div class="kicker" style="position:absolute;left:0;top:{mm(2.6)};width:100%;'
             f'text-align:center;font-size:{mm(2.5)};color:#fff">Ideal for</div>')
    cy = 12.5
    for t in IDEAL:
        o.append(f'<div class="li" style="position:absolute;left:{mm(pad)};top:{mm(cy)};width:{mm(iw)}">'
                 f'<i style="width:{mm(1.2)};height:{mm(1.2)};margin-top:{mm(1.0)}"></i>'
                 f'<div style="font-size:{mm(2.55)};color:{INK};font-weight:500">{t}</div></div>')
        cy += 5.0
    cy += 2.2
    o.append(f'<div class="rule" style="position:absolute;left:{mm(pad)};top:{mm(cy)};width:{mm(iw)}"></div>')
    cy += 3.0
    o.append(f'<div style="position:absolute;left:{mm(pad)};top:{mm(cy)};width:{mm(iw)};'
             f'font-family:Outfit;font-weight:700;font-size:{mm(2.35)};color:{BRAND};'
             f'letter-spacing:.08em;text-transform:uppercase">Storage</div>')
    cy += 3.9
    o.append(f'<div style="position:absolute;left:{mm(pad)};top:{mm(cy)};width:{mm(iw)};'
             f'font-size:{mm(2.25)};line-height:1.38;color:{MUTED}">'
             f'Store in a cool, dry place away from direct sunlight.</div>')
    cy += 9.0
    o.append(f'<div style="position:absolute;left:{mm(pad)};top:{mm(cy)};width:{mm(iw)};'
             f'font-size:{mm(2.15)};line-height:1.5;color:{MUTED}">'
             f'Batch no. ___________<br>Mfg ______ &nbsp; Exp ______</div>')

    bw, bh = 37.29, 25.93          # EAN-13 at 100% magnification
    bx, by = (w - bw) / 2, h - bh - 5.5
    o.append(f'<div id="barcode-zone" style="position:absolute;left:{mm(bx)};top:{mm(by)};'
             f'width:{mm(bw)};height:{mm(bh)};border:.3mm dashed #B6BFD6;border-radius:.8mm;'
             f'display:flex;flex-direction:column;align-items:center;justify-content:center;'
             f'gap:{mm(1.0)};background:#fff">'
             f'<div style="font-family:Outfit;font-weight:700;font-size:{mm(2.3)};color:#8C97B4;'
             f'letter-spacing:.06em">EAN-13</div>'
             f'<div style="font-size:{mm(1.95)};color:#A3ACC6;text-align:center;line-height:1.3">'
             f'Barcode area 37.3 &times; 25.9 mm<br>client to supply GTIN</div></div>')
    o.append("</div>")
    return "".join(o)


def flaps():
    o = []
    o.append(f'<div class="panel flap" style="left:{mm(X_FRONT)};top:{mm(Y_TOP)};'
             f'width:{mm(W_PANEL)};height:{mm(TUCK)}"></div>')
    o.append(f'<div id="swift-top" style="position:absolute;left:{mm(X_FRONT+(W_PANEL-28)/2)};'
             f'top:{mm(Y_TOP+12)};width:{mm(28)};height:{mm(14)}"></div>')
    o.append(f'<div style="position:absolute;left:{mm(X_FRONT)};top:{mm(Y_TOP+28.5)};'
             f'width:{mm(W_PANEL)};text-align:center;font-family:Outfit;font-weight:800;'
             f'font-size:{mm(4.0)};color:#fff;letter-spacing:.03em;text-transform:uppercase;'
             f'white-space:nowrap">Toilet Blocks</div>')
    o.append(f'<div class="panel flap" style="left:{mm(X_FRONT)};top:{mm(Y_BOT)};'
             f'width:{mm(W_PANEL)};height:{mm(TUCK)}"></div>')
    o.append(f'<div style="position:absolute;left:{mm(X_FRONT)};top:{mm(Y_BOT+6.0)};'
             f'width:{mm(W_PANEL)};text-align:center;font-family:Outfit;font-weight:800;'
             f'font-size:{mm(4.8)};color:#fff;white-space:nowrap">50 g &times; 4</div>')
    o.append(f'<div style="position:absolute;left:{mm(X_FRONT)};top:{mm(Y_BOT+12.4)};'
             f'width:{mm(W_PANEL)};text-align:center;font-size:{mm(2.35)};color:{PALE};'
             f'letter-spacing:.08em">NET WT. 200 g</div>')
    for yy in (Y_TOP, Y_BOT):
        o.append(f'<div class="panel" style="left:{mm(X_BACK)};top:{mm(yy)};width:{mm(W_PANEL)};'
                 f'height:{mm(TUCK)};background:{BRAND}"></div>')
    for xx in (X_SIDEL, X_SIDER):
        for yy in (Y_TOP, Y_BOT):
            o.append(f'<div class="panel" style="left:{mm(xx)};top:{mm(yy)};width:{mm(D_PANEL)};'
                     f'height:{mm(TUCK)};background:{BRAND}"></div>')
    # glue flap left unprinted — ink there weakens the bond
    o.append(f'<div class="panel white" style="left:{mm(X_GLUE)};top:{mm(Y_BODY)};'
             f'width:{mm(GLUE)};height:{mm(H_PANEL)}"></div>')
    return "".join(o)


def bleed_fill():
    # Each strip must carry the colour of the panel it adjoins, not the front
    # panel's: above and below the front column sit the navy tuck flaps.
    o = []
    for yy in (0, PAGE_H - BLEED - .3):
        o.append(f'<div class="panel flap" style="left:{mm(X_FRONT)};top:{mm(yy)};'
                 f'width:{mm(W_PANEL)};height:{mm(BLEED+.3)}"></div>')
    for xx, ww in ((X_BACK, W_PANEL + D_PANEL), (X_SIDER, D_PANEL + BLEED)):
        o.append(f'<div class="panel" style="left:{mm(xx)};top:0;width:{mm(ww)};height:{mm(BLEED+.3)};background:{BRAND}"></div>')
        o.append(f'<div class="panel" style="left:{mm(xx)};top:{mm(PAGE_H-BLEED-.3)};width:{mm(ww)};height:{mm(BLEED+.3)};background:{BRAND}"></div>')
    o.append(f'<div class="panel white" style="left:{mm(PAGE_W-BLEED-.3)};top:{mm(Y_BODY)};width:{mm(BLEED+.3)};height:{mm(H_PANEL)}"></div>')
    for yy in (Y_TOP, Y_BOT):
        o.append(f'<div class="panel" style="left:{mm(PAGE_W-BLEED-.3)};top:{mm(yy)};'
                 f'width:{mm(BLEED+.3)};height:{mm(TUCK)};background:{BRAND}"></div>')
    return "".join(o)


def dieline(page_h):
    s = [f'<svg class="die" viewBox="0 0 {PAGE_W} {page_h}" width="{PAGE_W}mm" height="{page_h}mm">']
    s.append(f'<rect class="cut" x="{X_GLUE}" y="{Y_BODY}" width="{FLAT_W}" height="{H_PANEL}"/>')
    for xx, ww in ((X_BACK, W_PANEL), (X_SIDEL, D_PANEL), (X_FRONT, W_PANEL), (X_SIDER, D_PANEL)):
        s.append(f'<rect class="cut" x="{xx}" y="{Y_TOP}" width="{ww}" height="{TUCK}"/>')
        s.append(f'<rect class="cut" x="{xx}" y="{Y_BOT}" width="{ww}" height="{TUCK}"/>')
    for xx in (X_BACK, X_SIDEL, X_FRONT, X_SIDER):
        s.append(f'<line class="crease" x1="{xx}" y1="{Y_TOP}" x2="{xx}" y2="{Y_BOT+TUCK}"/>')
    for yy in (Y_BODY, Y_BOT):
        s.append(f'<line class="crease" x1="{X_GLUE}" y1="{yy}" x2="{X_SIDER+D_PANEL}" y2="{yy}"/>')
    s.append(f'<rect class="bleedl" x="0.15" y="0.15" width="{PAGE_W-.3}" height="{PAGE_H-.3}"/>')
    for cx, t in [(X_GLUE + GLUE/2, "GLUE"), (X_BACK + W_PANEL/2, "BACK"),
                  (X_SIDEL + D_PANEL/2, "SIDE"), (X_FRONT + W_PANEL/2, "FRONT"),
                  (X_SIDER + D_PANEL/2, "SIDE")]:
        s.append(f'<text class="dlabel" font-size="2.6" x="{cx}" y="{Y_BODY-2.0}" '
                 f'text-anchor="middle">{t}</text>')
    # legend band, below the artwork so nothing sits in the bleed
    ly = PAGE_H + 4.6
    s.append(f'<line class="bleedl" x1="0" y1="{PAGE_H}" x2="{PAGE_W}" y2="{PAGE_H}"/>')
    s.append(f'<text class="dkey" font-size="3.0" fill="#2B3350" x="{X_GLUE}" y="{ly}">'
             f'Swift Toilet Blocks &#8212; 4 &#215; 50 g &#8212; folding carton, proof</text>')
    s.append(f'<text class="dnote" font-size="2.5" x="{X_GLUE}" y="{ly+4.3}">'
             f'Straight tuck end carton {W_PANEL:.0f} &#215; {H_PANEL:.0f} &#215; {D_PANEL:.0f} mm '
             f'(w &#215; h &#215; d) &#183; flat {FLAT_W:.0f} &#215; {FLAT_H:.0f} mm '
             f'&#183; {BLEED:.0f} mm bleed all round &#183; page {PAGE_W:.0f} &#215; {PAGE_H:.0f} mm</text>')
    s.append(f'<text class="dnote" font-size="2.5" x="{X_GLUE}" y="{ly+8.2}">'
             f'Magenta = cut &#183; cyan dashed = crease &#183; grey dashed = bleed. '
             f'Dieline marks are for position only and must not print &#8212; '
             f'they are absent from the artwork file.</text>')
    s.append(f'<text class="dnote" font-size="2.5" x="{X_GLUE}" y="{ly+12.1}">'
             f'Glue flap is intentionally unprinted. Barcode area on the right side panel '
             f'awaits the client&#8217;s GTIN.</text>')
    s.append("</svg>")
    return "".join(s)


def build(proof):
    page_h = PAGE_H + (LEGEND if proof else 0)
    css = CSS_T.format(pw=PAGE_W, ph=page_h, fo=A["font_outfit"],
                       foe=A["font_outfit_ext"], fj=A["font_jakarta"],
                       navy=NAVY, aqua=AQUA, brand=BRAND, red=RED)
    body = bleed_fill() + flaps() + back() + side_left() + front() + side_right()
    if proof:
        body += dieline(page_h)
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>'
            f'<body>{body}</body></html>')
    name = "carton-proof.html" if proof else "carton.html"
    (HERE / name).write_text(html, encoding="utf8")
    return name, page_h


meta = {"PAGE_W": PAGE_W, "PAGE_H": PAGE_H, "PAGE_H_PROOF": PAGE_H + LEGEND,
        "FLAT_W": FLAT_W, "FLAT_H": FLAT_H, "W": W_PANEL, "H": H_PANEL,
        "D": D_PANEL, "BLEED": BLEED,
        "swift_slots": [
            {"id": "front", "x": X_FRONT + (W_PANEL - 36) / 2, "y": Y_BODY + 7, "w": 36, "h": 18},
            {"id": "side",  "x": X_SIDEL + (D_PANEL - 30) / 2, "y": Y_BODY + 8, "w": 30, "h": 15},
            # Must match the #swift-tuck placeholder in flaps() exactly — these
            # coordinates are where stamp.py places the vector logo, and the two
            # drifted apart once before, overlapping the flap's wordmark.
            {"id": "tuck",  "x": X_FRONT + (W_PANEL - 28) / 2, "y": Y_TOP + 12, "w": 28, "h": 14},
        ]}
(HERE / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf8")

for pf in (False, True):
    n, ph = build(pf)
    print(f"{n:20s} page {PAGE_W:.0f} x {ph:.0f} mm")
print(f"carton {W_PANEL:.0f}(w) x {H_PANEL:.0f}(h) x {D_PANEL:.0f}(d) mm, flat {FLAT_W:.0f} x {FLAT_H:.0f} mm")
