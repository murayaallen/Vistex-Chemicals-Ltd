"""Swift Toilet Blocks — 4 x 50 g folding carton.

Follows the client's Swift_Toilet_Blocks_4PCS_Printable_Dieline as the template:
the same flat carton, the same panel order and the same content on each panel —

    glue | side A (why it works) | FRONT | side B (how to use) | BACK

That file could not be used as artwork (one 1536 x 1024 image stretched over
432 mm, about 90 dpi, no vector, no live text, no real dieline), so the layout
is rebuilt here at true size with a real die.

Everything is vector except the Vistex wordmark (755 px PNG, ~600 dpi at its
printed size); the Swift oval is stamped afterwards from the supplied vector PDF
by stamp.py, because Chrome rasterises its gradients through an <img>.

Writes carton.html (artwork) and carton-proof.html (artwork + dieline + legend).
"""
import json, math, pathlib

HERE = pathlib.Path(__file__).parent
A = json.loads((HERE / "assets.json").read_text(encoding="utf8"))

# ---------------------------------------------------------------- geometry
# Sized to the product: four blocks about 50 mm across and 28 mm thick, stacked
# in a column (4 x 28 = 112 mm inside a 118 mm height).
W_PANEL, H_PANEL, D_PANEL = 68.0, 118.0, 52.0
GLUE, TUCK, BLEED = 15.0, 46.0, 3.0
LEGEND = 19.0

FLAT_W = GLUE + D_PANEL + W_PANEL + D_PANEL + W_PANEL      # 255
FLAT_H = TUCK + H_PANEL + TUCK                             # 210
PAGE_W, PAGE_H = FLAT_W + BLEED * 2, FLAT_H + BLEED * 2    # 261 x 216

X_GLUE  = BLEED
X_SIDEA = X_GLUE + GLUE
X_FRONT = X_SIDEA + D_PANEL
X_SIDEB = X_FRONT + W_PANEL
X_BACK  = X_SIDEB + D_PANEL
Y_TOP   = BLEED
Y_BODY  = Y_TOP + TUCK
Y_BOT   = Y_BODY + H_PANEL

NAVY, DEEP, BLUE = "#04123A", "#071E5C", "#1340A8"
BRAND, AQUA, PALE = "#2E3995", "#00A6E6", "#BFE6FA"
RED, INK, MUTED, IVORY = "#ED1E26", "#17203C", "#55608A", "#FBFCFE"
PLAT = ["#FFFFFF", "#C6D2E4", "#8FA2BE", "#EAF1FA", "#7F93B2"]

FR = 3.5     # keyline frame inset inside each panel
PAD = 4.0    # content padding inside the frame


def mm(v):
    return f"{v:.3f}mm"


# ---------------------------------------------------------------- metal
_uid = [0]


def _nid():
    _uid[0] += 1
    return f"g{_uid[0]}"


def rule_plat(w, h=0.5, dark=False):
    i = _nid()
    stops = ('<stop offset="0" stop-color="#9FB0C8" stop-opacity="0"/>'
             '<stop offset=".2" stop-color="#7E90AE"/><stop offset=".5" stop-color="#C9D6E8"/>'
             '<stop offset=".8" stop-color="#7E90AE"/>'
             '<stop offset="1" stop-color="#9FB0C8" stop-opacity="0"/>') if dark else (
             f'<stop offset="0" stop-color="{PLAT[2]}" stop-opacity="0"/>'
             f'<stop offset=".18" stop-color="{PLAT[1]}"/><stop offset=".5" stop-color="{PLAT[0]}"/>'
             f'<stop offset=".82" stop-color="{PLAT[1]}"/>'
             f'<stop offset="1" stop-color="{PLAT[2]}" stop-opacity="0"/>')
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" '
            f'style="width:{mm(w)};height:{mm(h)};display:block">'
            f'<defs><linearGradient id="{i}" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#{i})"/></svg>')


def diamond(size=2.2, dark=False):
    a, b = ("#7E90AE", "#C9D6E8") if dark else ("#DCE6F3", "#9FB0C8")
    return (f'<svg viewBox="0 0 10 10" style="width:{mm(size)};height:{mm(size)};display:block">'
            f'<path d="M5 0 L10 5 L5 10 L0 5 Z" fill="{a}"/>'
            f'<path d="M5 2.2 L7.8 5 L5 7.8 L2.2 5 Z" fill="{b}"/></svg>')


def ornament_rule(total_w, dark=False, dsize=2.2):
    side = (total_w - dsize - 2.6) / 2
    return (f'<div style="display:flex;align-items:center;justify-content:center;gap:{mm(1.3)};'
            f'width:{mm(total_w)}">{rule_plat(side, dark=dark)}{diamond(dsize, dark)}'
            f'{rule_plat(side, dark=dark)}</div>')


def frame(w, h, dark=True, r=2.6):
    """Double platinum keyline with corner diamonds — the premium device."""
    i = _nid()
    x = y = FR
    stops = (f'<stop offset="0" stop-color="{PLAT[0]}"/><stop offset=".25" stop-color="{PLAT[1]}"/>'
             f'<stop offset=".5" stop-color="{PLAT[2]}"/><stop offset=".75" stop-color="{PLAT[3]}"/>'
             f'<stop offset="1" stop-color="{PLAT[4]}"/>') if dark else (
             '<stop offset="0" stop-color="#B9C7DC"/><stop offset=".3" stop-color="#8295B4"/>'
             '<stop offset=".55" stop-color="#C9D6E8"/><stop offset="1" stop-color="#8295B4"/>')
    op = ".88" if dark else ".92"
    s = [f'<svg class="abs" style="left:0;top:0;width:{mm(w)};height:{mm(h)}" viewBox="0 0 {w} {h}">',
         f'<defs><linearGradient id="{i}" x1="0" y1="0" x2="1" y2="1">{stops}</linearGradient></defs>',
         f'<rect x="{x}" y="{y}" width="{w-2*x}" height="{h-2*y}" rx="{r}" fill="none" '
         f'stroke="url(#{i})" stroke-width=".5" opacity="{op}"/>',
         f'<rect x="{x+1.3}" y="{y+1.3}" width="{w-2*x-2.6}" height="{h-2*y-2.6}" '
         f'rx="{max(0,r-1.0)}" fill="none" stroke="url(#{i})" stroke-width=".28" opacity=".6"/>']
    for cx, cy in ((x, y), (w - x, y), (x, h - y), (w - x, h - y)):
        s.append(f'<path d="M{cx},{cy-1.4} L{cx+1.4},{cy} L{cx},{cy+1.4} L{cx-1.4},{cy} Z" '
                 f'fill="url(#{i})" opacity="{op}"/>')
    s.append("</svg>")
    return "".join(s)


def seal(size=16.0):
    i = _nid()
    return (f'<svg viewBox="0 0 100 100" style="width:{mm(size)};height:{mm(size)};display:block">'
            f'<defs><linearGradient id="{i}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{PLAT[0]}"/><stop offset=".3" stop-color="{PLAT[1]}"/>'
            f'<stop offset=".6" stop-color="{PLAT[2]}"/><stop offset="1" stop-color="{PLAT[3]}"/>'
            f'</linearGradient></defs>'
            f'<circle cx="50" cy="50" r="47" fill="#05163C"/>'
            f'<circle cx="50" cy="50" r="47" fill="none" stroke="url(#{i})" stroke-width="3.4"/>'
            f'<circle cx="50" cy="50" r="40" fill="none" stroke="url(#{i})" stroke-width="1" opacity=".75"/>'
            f'<text x="50" y="42" text-anchor="middle" font-family="Outfit" font-weight="900" '
            f'font-size="28" fill="#FFFFFF" letter-spacing="-1.5">50g</text>'
            f'<path d="M27 50 H73" stroke="url(#{i})" stroke-width="1.5"/>'
            f'<text x="50" y="78" text-anchor="middle" font-family="Outfit" font-weight="900" '
            f'font-size="28" fill="#FFFFFF">&#215;4</text></svg>')


# ---------------------------------------------------------------- product art
def block_svg(uid, ridges=30):
    cx, cy, rx, ry, depth = 100.0, 64.0, 90.0, 49.0, 24.0
    o = ['<svg viewBox="0 0 200 150" preserveAspectRatio="xMidYMid meet">']
    o.append(f'''<defs>
      <linearGradient id="sd{uid}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#2A62D8"/><stop offset=".5" stop-color="#11359C"/>
        <stop offset="1" stop-color="#06195A"/></linearGradient>
      <radialGradient id="tp{uid}" cx=".36" cy=".26" r=".88">
        <stop offset="0" stop-color="#7FB2F7"/><stop offset=".4" stop-color="#2E66DD"/>
        <stop offset=".78" stop-color="#1340A8"/><stop offset="1" stop-color="#0B2A74"/></radialGradient>
      <linearGradient id="gl{uid}" x1=".1" y1="0" x2=".8" y2="1">
        <stop offset="0" stop-color="#FFF" stop-opacity=".62"/>
        <stop offset=".38" stop-color="#FFF" stop-opacity=".08"/>
        <stop offset="1" stop-color="#FFF" stop-opacity="0"/></linearGradient></defs>''')
    o.append(f'<ellipse cx="{cx}" cy="{cy+depth+6}" rx="{rx*.92:.1f}" ry="{ry*.26:.1f}" '
             f'fill="#020A22" fill-opacity=".38"/>')
    o.append(f'<path d="M{cx-rx:.2f},{cy:.2f} v{depth:.2f} '
             f'a{rx:.2f},{ry:.2f} 0 0 0 {rx*2:.2f},0 v-{depth:.2f} '
             f'a{rx:.2f},{ry:.2f} 0 0 1 -{rx*2:.2f},0 z" fill="url(#sd{uid})"/>')
    for i in range(ridges):
        a = math.pi * (i + .5) / ridges
        x, y = cx - rx * math.cos(a), cy + ry * math.sin(a)
        o.append(f'<path d="M{x:.2f},{y:.2f} v{depth:.2f}" stroke="#03103A" '
                 f'stroke-opacity="{.34 if i % 2 else .12}" stroke-width="2.4"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#tp{uid})"/>')
    for i in range(ridges):
        a = 2 * math.pi * i / ridges
        o.append(f'<path d="M{cx+rx*.26*math.cos(a):.2f},{cy+ry*.26*math.sin(a):.2f} '
                 f'L{cx+rx*.94*math.cos(a):.2f},{cy+ry*.94*math.sin(a):.2f}" '
                 f'stroke="#BBD8FF" stroke-opacity=".42" stroke-width="2.0" stroke-linecap="round"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*.26:.2f}" ry="{ry*.26:.2f}" fill="#0A2770"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*.26:.2f}" ry="{ry*.26:.2f}" fill="none" '
             f'stroke="#9BC4FF" stroke-opacity=".5" stroke-width="1.4"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#gl{uid})"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" '
             f'stroke="#CFE4FF" stroke-opacity=".55" stroke-width="1.5"/></svg>')
    return "".join(o)


def icon(name, col="#FFFFFF", sw=1.85):
    p = {
      "flush":   '<path d="M5 4h14v5a7 7 0 0 1-14 0z"/><path d="M9 4V2h6v2"/><path d="M12 16v6"/>',
      "germ":    '<circle cx="12" cy="12" r="5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
      "scale":   '<path d="M3 20l5-9 4 5 3-4 6 8z"/><circle cx="8" cy="6" r="2.5"/>',
      "fresh":   '<path d="M12 3c3 4 5 6 5 9a5 5 0 0 1-10 0c0-3 2-5 5-9z"/>',
      "tank":    '<rect x="4" y="5" width="16" height="9" rx="1.5"/><path d="M8 14v5h8v-5M12 8v3"/>',
      "sparkle": '<path d="M12 4l1.8 4.7L18.5 10l-4.7 1.8L12 16l-1.8-4.2L5.5 10l4.7-1.3z"/><path d="M18 16l.9 2.1L21 19l-2.1.9L18 22l-.9-2.1L15 19l2.1-.9z"/>',
      "shield":  '<path d="M12 3l8 3v6c0 5-3.4 8.2-8 9-4.6-.8-8-4-8-9V6z"/>',
    }[name]
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="{col}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{p}</svg>')


# ---------------------------------------------------------------- copy
DESC = ("Cleans, freshens and protects the toilet bowl with every flush. Each block "
        "dissolves gradually, preventing limescale and leaving a fresh fragrance.")
STEPS = [("tank", "Drop one block into the cistern, clear of the inlet and float."),
         ("flush", "The block dissolves gradually, releasing cleaner with every flush."),
         ("sparkle", "Replace when fully dissolved — about one block per month.")]
BENEFITS = [("flush", "Cleans with every flush"), ("germ", "Fights germs"),
            ("scale", "Prevents limescale & stains"), ("fresh", "Long-lasting freshness")]
IDEAL = ["Homes", "Hotels", "Restaurants", "Schools", "Hospitals", "Offices", "Washrooms"]
CAUTION = ["Keep out of reach of children.", "Do not ingest.",
           "Avoid contact with skin and eyes.", "Wash hands after handling.",
           "Use only as directed."]

CSS = f"""
@font-face {{ font-family: Outfit; src: url(data:font/woff2;base64,{A['font_outfit']}) format('woff2');
  font-weight: 100 900; font-display: block; }}
@font-face {{ font-family: Outfit; src: url(data:font/woff2;base64,{A['font_outfit_ext']}) format('woff2');
  font-weight: 100 900; unicode-range: U+0100-024F; font-display: block; }}
@font-face {{ font-family: Jakarta; src: url(data:font/woff2;base64,{A['font_jakarta']}) format('woff2');
  font-weight: 200 800; font-display: block; }}
* {{ margin:0; padding:0; box-sizing:border-box;
     -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
body {{ font-family: Jakarta, sans-serif; background:#fff; position:relative; overflow:hidden; }}
.panel {{ position:absolute; overflow:hidden; }}
.abs {{ position:absolute; }}
.ctr {{ position:absolute; width:100%; text-align:center; }}

.deep {{ background:
   radial-gradient(92% 48% at 50% 26%, #2F6FE0 0%, #16429F 40%, {DEEP} 74%, {NAVY} 100%); }}
.sheen {{ position:absolute; inset:0; background:
   radial-gradient(48% 26% at 50% 62%, rgba(150,205,255,.26), transparent 72%),
   linear-gradient(180deg, rgba(255,255,255,.09), transparent 22%, transparent 74%, rgba(0,0,0,.24)); }}

.h-prod {{ font-family:Outfit; font-weight:900; letter-spacing:-.028em; line-height:.9;
           text-transform:uppercase; color:#fff; white-space:nowrap; }}
.sc {{ font-family:Outfit; font-weight:600; text-transform:uppercase; }}
.hdr {{ display:inline-block; background:{BRAND}; color:#fff; font-family:Outfit; font-weight:700;
        letter-spacing:.10em; text-transform:uppercase; border-radius:1.1mm;
        white-space:nowrap; line-height:1; }}
.hdr.red {{ background:{RED}; }}
.li {{ display:flex; gap:{mm(1.5)}; align-items:flex-start; }}
.li i {{ flex:none; border-radius:50%; background:{AQUA}; }}
.qrbox {{ background:#fff; border-radius:.8mm; }}
.qrbox svg {{ width:100%; height:100%; display:block; }}
.qrbox svg path {{ fill:#0A1430; }}

.cut {{ fill:none; stroke:#E6007E; stroke-width:.35; }}
.crease {{ fill:none; stroke:#00AEEF; stroke-width:.35; stroke-dasharray:2.2 1.4; }}
.bleedl {{ fill:none; stroke:#9A9A9A; stroke-width:.3; stroke-dasharray:1.2 1.2; }}
.dlabel {{ font-family:Jakarta; fill:#E6007E; font-weight:700; }}
.dnote {{ font-family:Jakarta; fill:#2B3350; }}
"""


# ---------------------------------------------------------------- FRONT
def front():
    x, y, w, h = X_FRONT, Y_BODY, W_PANEL, H_PANEL
    IX, IW = FR + PAD, w - (FR + PAD) * 2
    o = [f'<div class="panel deep" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)}">',
         '<div class="sheen"></div>']
    o.append(f'<svg class="abs" style="left:0;top:0;width:{mm(w)};height:{mm(h)}" viewBox="0 0 {w} {h}">' +
             "".join(f'<circle cx="{w/2}" cy="76" r="{10+i*5.5}" fill="none" stroke="#9FD0FF" '
                     f'stroke-opacity=".07" stroke-width=".35"/>' for i in range(7)) + "</svg>")
    o.append(frame(w, h, dark=True))

    o.append(f'<div class="abs" id="swift-front" style="left:{mm((w-31)/2)};top:{mm(8.0)};'
             f'width:{mm(31)};height:{mm(15.5)}"></div>')
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(26.0)}">{ornament_rule(IW)}</div>')
    o.append(f'<div class="ctr h-prod" style="top:{mm(29.5)};font-size:{mm(9.6)};'
             f'text-shadow:0 {mm(.4)} {mm(1.2)} rgba(0,0,0,.35)">TOILET</div>')
    o.append(f'<div class="ctr h-prod" style="top:{mm(38.2)};font-size:{mm(9.6)};'
             f'text-shadow:0 {mm(.4)} {mm(1.2)} rgba(0,0,0,.35)">BLOCKS</div>')
    o.append(f'<div class="ctr sc" style="top:{mm(49.0)};font-size:{mm(2.45)};letter-spacing:.14em;'
             f'color:{PALE}">Automatic Toilet Bowl Cleaner</div>')
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(54.0)}">{ornament_rule(IW)}</div>')

    # three blocks; each SVG is 4:3, so a block w mm wide stands 0.75 w tall
    lay = [(1.0, 1.0, 23.0, ".80"), (32.0, 0.0, 23.0, ".80"), (14.0, 8.0, 28.0, "1")]
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(57.5)};width:{mm(IW)};height:{mm(29)}">')
    for i, (bx, by, bw, op) in enumerate(lay):
        o.append(f'<div class="abs" style="left:{mm(bx)};top:{mm(by)};width:{mm(bw)};'
                 f'opacity:{op}">{block_svg("f%d" % i)}</div>')
    o.append("</div>")

    chips = "".join(
        f'<div style="display:flex;flex-direction:column;align-items:center;width:{mm(16)}">'
        f'<div style="width:{mm(4.4)};height:{mm(4.4)};margin-bottom:{mm(1.0)}">{icon(k, PALE)}</div>'
        f'<span class="sc" style="font-size:{mm(2.15)};letter-spacing:.09em;color:#fff">{t}</span></div>'
        for k, t in [("flush", "Cleans"), ("fresh", "Freshens"), ("shield", "Protects")])
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(90.0)};width:{mm(IW)};'
             f'display:flex;justify-content:center;gap:{mm(1.5)}">{chips}</div>')

    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(101.0)}">{ornament_rule(IW)}</div>')
    o.append(f'<div class="ctr" style="top:{mm(104.0)};font-family:Outfit;font-weight:800;'
             f'font-size:{mm(4.4)};color:#fff;white-space:nowrap">50 g &times; 4</div>')
    o.append(f'<div class="ctr" style="top:{mm(109.8)};font-family:Outfit;font-weight:600;'
             f'font-size:{mm(2.2)};letter-spacing:.12em;color:{PALE}">NET WT. 200 g</div>')
    o.append("</div>")
    return "".join(o)


# ---------------------------------------------------------------- SIDE A
def side_a():
    """Why it works — the benefits strip from the client's template."""
    x, y, w, h = X_SIDEA, Y_BODY, D_PANEL, H_PANEL
    IX, IW = FR + PAD, w - (FR + PAD) * 2
    o = [f'<div class="panel deep" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)}">',
         '<div class="sheen"></div>', frame(w, h, dark=True)]
    o.append(f'<div class="abs" id="swift-sidea" style="left:{mm((w-26)/2)};top:{mm(8.0)};'
             f'width:{mm(26)};height:{mm(13)}"></div>')
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(23.5)}">{ornament_rule(IW)}</div>')
    o.append(f'<div class="ctr sc" style="top:{mm(26.5)};font-size:{mm(2.4)};letter-spacing:.16em;'
             f'color:{PALE}">Why it works</div>')
    cy = 33.0
    for ic, t in BENEFITS:
        o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(cy)};width:{mm(IW)};'
                 f'display:flex;gap:{mm(2.0)};align-items:center">'
                 f'<div style="flex:none;width:{mm(5.6)};height:{mm(5.6)};border-radius:{mm(1.4)};'
                 f'background:rgba(255,255,255,.14);border:.2mm solid rgba(255,255,255,.22);'
                 f'display:flex;align-items:center;justify-content:center">'
                 f'<div style="width:{mm(3.4)};height:{mm(3.4)}">{icon(ic)}</div></div>'
                 f'<div style="font-family:Outfit;font-weight:600;font-size:{mm(2.45)};color:#fff;'
                 f'line-height:1.2">{t}</div></div>')
        cy += 11.5
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(83.0)}">{ornament_rule(IW)}</div>')
    o.append(f'<div class="abs" style="left:{mm((w-20)/2)};top:{mm(87.5)}">{seal(20)}</div>')
    o.append(f'<div class="ctr" style="top:{mm(110.0)};font-family:Outfit;font-weight:600;'
             f'font-size:{mm(2.2)};letter-spacing:.12em;color:{PALE}">NET WT. 200 g</div>')
    o.append("</div>")
    return "".join(o)


# ---------------------------------------------------------------- SIDE B
def side_b():
    """How to use — the directions strip from the client's template."""
    x, y, w, h = X_SIDEB, Y_BODY, D_PANEL, H_PANEL
    IX, IW = FR + PAD, w - (FR + PAD) * 2
    steps = "".join(
        f'<div style="display:flex;gap:{mm(1.9)};align-items:flex-start;margin-top:{mm(5.6)}">'
        f'<div style="flex:none;width:{mm(5.8)};height:{mm(5.8)};border-radius:50%;background:{BRAND};'
        f'display:flex;align-items:center;justify-content:center">'
        f'<div style="width:{mm(3.3)};height:{mm(3.3)}">{icon(ic)}</div></div>'
        f'<div style="font-size:{mm(2.3)};line-height:1.38;color:{INK}">'
        f'<b style="color:{BRAND}">{i+1}.</b> {t}</div></div>'
        for i, (ic, t) in enumerate(STEPS))
    o = [f'<div class="panel" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)};'
         f'background:{IVORY}">',
         f'<div class="abs" style="left:0;top:0;width:{mm(w)};height:{mm(h)};'
         f'background:radial-gradient(80% 36% at 50% 0%, #EDF3FD, transparent 72%)"></div>',
         frame(w, h, dark=False)]
    o.append(f'<div class="abs" id="sidebflow" style="left:{mm(IX)};top:{mm(9.0)};width:{mm(IW)}">'
             f'<div style="text-align:center"><span class="hdr" style="font-size:{mm(2.45)};'
             f'padding:{mm(1.1)} {mm(2.2)}">How to use</span></div>{steps}'
             f'<div style="margin-top:{mm(7.5)}">{ornament_rule(IW, dark=True)}</div>'
             f'<div style="margin-top:{mm(5.2)};text-align:center"><span class="hdr" '
             f'style="font-size:{mm(2.45)};padding:{mm(1.1)} {mm(2.2)}">Ideal for</span></div>'
             f'<div style="margin-top:{mm(2.4)};font-size:{mm(2.3)};line-height:1.55;color:{INK};'
             f'text-align:center">{" &middot; ".join(IDEAL)}</div></div>')
    o.append(f'<div class="abs" id="sidebfoot" style="left:{mm(IX)};top:{mm(h-13.0)}">'
             f'{ornament_rule(IW, dark=True)}</div>')
    o.append(f'<div class="ctr" style="top:{mm(h-9.6)};font-family:Outfit;font-weight:800;'
             f'font-size:{mm(3.6)};color:{BRAND};white-space:nowrap">50 g &times; 4</div>')
    o.append("</div>")
    return "".join(o)


# ---------------------------------------------------------------- BACK
def back():
    """Flowed, not absolutely positioned: hand-computed block heights were the
    single cause of every overlap in earlier drafts."""
    x, y, w, h = X_BACK, Y_BODY, W_PANEL, H_PANEL
    IX, IW = FR + PAD, w - (FR + PAD) * 2
    hdr = f'font-size:{mm(2.45)};padding:{mm(1.1)} {mm(2.2)}'

    cautions = "".join(
        f'<div class="li" style="margin-top:{mm(1.5)}">'
        f'<i style="width:{mm(1.0)};height:{mm(1.0)};margin-top:{mm(.9)};background:{RED}"></i>'
        f'<div style="font-size:{mm(2.25)};line-height:1.32;color:{INK}">{t}</div></div>'
        for t in CAUTION)
    o = [f'<div class="panel" style="left:{mm(x)};top:{mm(y)};width:{mm(w)};height:{mm(h)};'
         f'background:{IVORY}">',
         f'<div class="abs" style="left:0;top:0;width:{mm(w)};height:{mm(h)};'
         f'background:radial-gradient(80% 34% at 50% 0%, #EDF3FD, transparent 72%)"></div>',
         frame(w, h, dark=False)]
    o.append(f'''<div class="abs" id="backflow" style="left:{mm(IX)};top:{mm(8.0)};width:{mm(IW)}">
  <div style="text-align:center;font-family:Outfit;font-weight:800;font-size:{mm(4.4)};
       color:{BRAND};letter-spacing:-.015em;line-height:1.05">Swift Toilet Blocks</div>
  <div class="sc" style="text-align:center;font-size:{mm(2.2)};letter-spacing:.14em;
       color:{AQUA};margin-top:{mm(1.2)}">Automatic Toilet Bowl Cleaner</div>
  <div style="margin-top:{mm(2.4)}">{ornament_rule(IW, dark=True)}</div>
  <div style="margin-top:{mm(2.6)};font-size:{mm(2.4)};line-height:1.46;color:{INK};
       text-align:center">{DESC}</div>
  <div style="margin-top:{mm(4.4)}"><span class="hdr red" style="{hdr}">Caution</span></div>
  {cautions}
  <div style="margin-top:{mm(3.6)};font-size:{mm(2.15)};line-height:1.4;color:{MUTED}">
    <b style="color:{BRAND}">Active ingredients:</b> sodium dichloroisocyanurate,
    anionic &amp; non-ionic surfactants, fragrance, colourant.</div>
</div>''')

    fy, qr = h - 27.0, 14.0
    o.append(f'<div class="abs" id="backfoot" style="left:{mm(IX)};top:{mm(fy-3.4)}">'
             f'{ornament_rule(IW, dark=True)}</div>')
    o.append(f'<img src="data:image/png;base64,{A["vistex"]}" class="abs" '
             f'style="left:{mm(IX)};top:{mm(fy)};width:{mm(28)};height:auto">')
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(fy+10.0)};width:{mm(IW-qr-2)};'
             f'font-size:{mm(1.9)};line-height:1.44;color:{MUTED}">'
             f'P.O. Box 218 &ndash; 00606, Nairobi<br>0739 446 655<br>'
             f'info@vistexchemicals.co.ke</div>')
    o.append(f'<div class="qrbox abs" style="left:{mm(w-FR-PAD-qr)};top:{mm(fy)};'
             f'width:{mm(qr)};height:{mm(qr)};padding:{mm(.9)}">{A["qr_svg"]}</div>')
    o.append(f'<div class="abs sc" style="left:{mm(w-FR-PAD-qr-3)};top:{mm(fy+qr+1.0)};'
             f'width:{mm(qr+3)};text-align:center;font-size:{mm(1.8)};letter-spacing:.04em;'
             f'color:{MUTED}">Scan for more</div>')
    o.append("</div>")
    return "".join(o)


# ---------------------------------------------------------------- flaps
def flaps():
    # Flaps run into the bleed: a 3 mm strip of its own would sample a different
    # part of the radial gradient than the 46 mm flap beside it, and the join
    # would show after trimming.
    o = []
    for yy, hh in ((Y_TOP - BLEED, TUCK + BLEED), (Y_BOT, TUCK + BLEED)):
        o.append(f'<div class="panel deep" style="left:{mm(X_FRONT)};top:{mm(yy)};'
                 f'width:{mm(W_PANEL)};height:{mm(hh)}"></div>')
    o.append(f'<div class="abs" id="swift-tuck" style="left:{mm(X_FRONT+(W_PANEL-26)/2)};'
             f'top:{mm(Y_TOP+11.0)};width:{mm(26)};height:{mm(13)}"></div>')
    o.append(f'<div class="abs" style="left:{mm(X_FRONT+8)};top:{mm(Y_TOP+26.5)}">'
             f'{ornament_rule(W_PANEL-16)}</div>')
    o.append(f'<div class="abs" style="left:{mm(X_FRONT)};top:{mm(Y_TOP+29.5)};width:{mm(W_PANEL)};'
             f'text-align:center;font-family:Outfit;font-weight:800;font-size:{mm(3.8)};color:#fff;'
             f'letter-spacing:.03em;text-transform:uppercase;white-space:nowrap">Toilet Blocks</div>')
    o.append(f'<div class="abs" style="left:{mm(X_FRONT)};top:{mm(Y_BOT+9.0)};width:{mm(W_PANEL)};'
             f'text-align:center;font-family:Outfit;font-weight:800;font-size:{mm(4.6)};color:#fff;'
             f'white-space:nowrap">50 g &times; 4</div>')
    o.append(f'<div class="abs" style="left:{mm(X_FRONT)};top:{mm(Y_BOT+15.5)};width:{mm(W_PANEL)};'
             f'text-align:center;font-family:Outfit;font-weight:600;font-size:{mm(2.2)};'
             f'letter-spacing:.12em;color:{PALE}">NET WT. 200 g</div>')
    for xx, ww in ((X_SIDEA, D_PANEL), (X_SIDEB, D_PANEL), (X_BACK, W_PANEL + BLEED)):
        for yy, hh in ((Y_TOP - BLEED, TUCK + BLEED), (Y_BOT, TUCK + BLEED)):
            o.append(f'<div class="panel" style="left:{mm(xx)};top:{mm(yy)};width:{mm(ww)};'
                     f'height:{mm(hh)};background:{BRAND}"></div>')
    # glue flap stays unprinted — ink there weakens the bond
    o.append(f'<div class="panel" style="left:0;top:{mm(Y_BODY)};'
             f'width:{mm(GLUE+BLEED)};height:{mm(H_PANEL)};background:#fff"></div>')
    return "".join(o)


def bleed_fill():
    """Only the right edge needs a strip: the back panel is a flat ivory, so a
    separate strip matches it exactly. Every other edge is carried by the flap
    or glue panel itself."""
    return (f'<div class="panel" style="left:{mm(PAGE_W-BLEED-.3)};top:{mm(Y_BODY)};'
            f'width:{mm(BLEED+.3)};height:{mm(H_PANEL)};background:{IVORY}"></div>')

def dieline(page_h):
    s = [f'<svg class="abs" style="left:0;top:0;width:{mm(PAGE_W)};height:{mm(page_h)}" '
         f'viewBox="0 0 {PAGE_W} {page_h}">']
    s.append(f'<rect class="cut" x="{X_GLUE}" y="{Y_BODY}" width="{FLAT_W}" height="{H_PANEL}"/>')
    for xx, ww in ((X_SIDEA, D_PANEL), (X_FRONT, W_PANEL), (X_SIDEB, D_PANEL), (X_BACK, W_PANEL)):
        s.append(f'<rect class="cut" x="{xx}" y="{Y_TOP}" width="{ww}" height="{TUCK}"/>')
        s.append(f'<rect class="cut" x="{xx}" y="{Y_BOT}" width="{ww}" height="{TUCK}"/>')
    for xx in (X_SIDEA, X_FRONT, X_SIDEB, X_BACK):
        s.append(f'<line class="crease" x1="{xx}" y1="{Y_TOP}" x2="{xx}" y2="{Y_BOT+TUCK}"/>')
    for yy in (Y_BODY, Y_BOT):
        s.append(f'<line class="crease" x1="{X_GLUE}" y1="{yy}" x2="{X_BACK+W_PANEL}" y2="{yy}"/>')
    s.append(f'<rect class="bleedl" x="0.15" y="0.15" width="{PAGE_W-.3}" height="{PAGE_H-.3}"/>')
    for cx, t in [(X_GLUE + GLUE / 2, "GLUE"), (X_SIDEA + D_PANEL / 2, "SIDE A"),
                  (X_FRONT + W_PANEL / 2, "FRONT"), (X_SIDEB + D_PANEL / 2, "SIDE B"),
                  (X_BACK + W_PANEL / 2, "BACK")]:
        s.append(f'<text class="dlabel" font-size="2.6" x="{cx}" y="{Y_BODY-2.0}" '
                 f'text-anchor="middle">{t}</text>')
    ly = PAGE_H + 4.6
    s.append(f'<line class="bleedl" x1="0" y1="{PAGE_H}" x2="{PAGE_W}" y2="{PAGE_H}"/>')
    s.append(f'<text class="dnote" font-size="3.0" font-weight="700" x="{X_GLUE}" y="{ly}">'
             f'Swift Toilet Blocks &#8212; 4 &#215; 50 g &#8212; folding carton, proof</text>')
    s.append(f'<text class="dnote" font-size="2.5" x="{X_GLUE}" y="{ly+4.3}">'
             f'Straight tuck end carton {W_PANEL:.0f} &#215; {H_PANEL:.0f} &#215; {D_PANEL:.0f} mm '
             f'(w &#215; h &#215; d) &#183; flat {FLAT_W:.0f} &#215; {FLAT_H:.0f} mm '
             f'&#183; {BLEED:.0f} mm bleed &#183; page {PAGE_W:.0f} &#215; {PAGE_H:.0f} mm. '
             f'Panel order follows the client&#8217;s template.</text>')
    s.append(f'<text class="dnote" font-size="2.5" x="{X_GLUE}" y="{ly+8.2}">'
             f'Magenta = cut &#183; cyan dashed = crease &#183; grey dashed = bleed. For position only '
             f'&#8212; absent from the artwork file. Glue flap is intentionally unprinted.</text>')
    s.append(f'<text class="dnote" font-size="2.5" x="{X_GLUE}" y="{ly+12.1}">'
             f'Platinum frame and rules print CMYK; specify silver foil for a metallic finish.</text>')
    s.append("</svg>")
    return "".join(s)


def build(proof):
    page_h = PAGE_H + (LEGEND if proof else 0)
    body = bleed_fill() + flaps() + side_a() + front() + side_b() + back()
    if proof:
        body += dieline(page_h)
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>'
            f'@page {{ size:{PAGE_W}mm {page_h}mm; margin:0; }}'
            f'html,body {{ width:{PAGE_W}mm; height:{page_h}mm; }}{CSS}</style></head>'
            f'<body>{body}</body></html>')
    name = "carton-proof.html" if proof else "carton.html"
    (HERE / name).write_text(html, encoding="utf8")
    return name, page_h


meta = {"PAGE_W": PAGE_W, "PAGE_H": PAGE_H, "PAGE_H_PROOF": PAGE_H + LEGEND,
        "FLAT_W": FLAT_W, "FLAT_H": FLAT_H, "W": W_PANEL, "H": H_PANEL,
        "D": D_PANEL, "BLEED": BLEED,
        # must match the #swift-* placeholders above; stamp.py reads these
        "swift_slots": [
            {"id": "front", "x": X_FRONT + (W_PANEL - 31) / 2, "y": Y_BODY + 8.0, "w": 31, "h": 15.5},
            {"id": "sidea", "x": X_SIDEA + (D_PANEL - 26) / 2, "y": Y_BODY + 8.0, "w": 26, "h": 13},
            {"id": "tuck",  "x": X_FRONT + (W_PANEL - 26) / 2, "y": Y_TOP + 11.0, "w": 26, "h": 13},
        ]}
(HERE / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf8")

for pf in (False, True):
    n, ph = build(pf)
    print(f"{n:20s} page {PAGE_W:.0f} x {ph:.0f} mm")
print(f"carton {W_PANEL:.0f}(w) x {H_PANEL:.0f}(h) x {D_PANEL:.0f}(d) mm, flat {FLAT_W:.0f} x {FLAT_H:.0f} mm")
print("panel order: glue | side A | FRONT | side B | BACK  (as the template)")
