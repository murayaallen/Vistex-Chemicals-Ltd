"""Swift Toilet Blocks — 4 x 50 g euro-slot hang card.

Die matches the Blue-Drop sample supplied by the client: 130 x 180 mm rounded
rectangle with a sombrero euro hanger, so one cutting die can serve both SKUs.

Builds at true size (mm) as HTML that Chrome renders to vector PDF. Everything
is vector except the Vistex wordmark (755 px PNG, ~600 dpi at printed size);
the Swift oval is stamped afterwards from the supplied vector PDF by stamp.py,
because Chrome rasterises its gradients through an <img>.

Writes:
  card-front.html / card-back.html   artwork, 136 x 186 mm each (3 mm bleed)
  card-proof.html                    both side by side, dieline + legend
"""
import json, math, pathlib

HERE = pathlib.Path(__file__).parent
A = json.loads((HERE / "assets.json").read_text(encoding="utf8"))

# ---------------------------------------------------------------- geometry
CARD_W, CARD_H = 130.0, 180.0
BLEED = 3.0
PAGE_W, PAGE_H = CARD_W + BLEED * 2, CARD_H + BLEED * 2     # 136 x 186
CORNER = 6.0                 # die corner radius, measured off the sample
# sombrero euro hanger
HANG_SLOT_W, HANG_SLOT_H, HANG_SLOT_Y = 34.0, 6.2, 11.0     # slot centre line
HANG_BUMP_R, HANG_BUMP_CY = 6.4, 10.2
FRAME_TOP, FRAME_IN = 19.5, 6.5    # punch ends at 16.6 mm, so 2.9 mm clear    # keyline frame: below the hanger, inset
PAD = 6.5                          # content padding inside the frame

PROOF_GAP = 14.0
PROOF_W = PAGE_W * 2 + PROOF_GAP
PROOF_LEGEND = 22.0
PROOF_H = PAGE_H + PROOF_LEGEND

NAVY, DEEP, BLUE = "#04123A", "#071E5C", "#1340A8"
BRAND, AQUA, PALE = "#2E3995", "#00A6E6", "#BFE6FA"
RED, INK, MUTED = "#ED1E26", "#17203C", "#55608A"
IVORY = "#FBFCFE"

# platinum, echoing the chrome rim on the Swift oval
PLAT = ["#FFFFFF", "#C6D2E4", "#8FA2BE", "#EAF1FA", "#7F93B2"]


def mm(v):
    return f"{v:.3f}mm"


# ---------------------------------------------------------------- die path
def die_path(ox=0.0, oy=0.0):
    """Outline of the card: rounded rect minus the sombrero hanger."""
    x, y, w, h, r = ox, oy, CARD_W, CARD_H, CORNER
    cx = x + w / 2
    sw, sh = HANG_SLOT_W / 2, HANG_SLOT_H / 2
    sy = y + HANG_SLOT_Y
    br, bcy = HANG_BUMP_R, y + HANG_BUMP_CY
    # outer rounded rectangle, clockwise from the top-left arc
    outer = (f"M{x+r:.2f},{y:.2f} H{x+w-r:.2f} A{r},{r} 0 0 1 {x+w:.2f},{y+r:.2f} "
             f"V{y+h-r:.2f} A{r},{r} 0 0 1 {x+w-r:.2f},{y+h:.2f} H{x+r:.2f} "
             f"A{r},{r} 0 0 1 {x:.2f},{y+h-r:.2f} V{y+r:.2f} A{r},{r} 0 0 1 {x+r:.2f},{y:.2f} Z")
    # hanger: horizontal slot with fully rounded ends, plus a circle on top.
    # Drawn as two subpaths; even-odd fill makes them a hole in the card.
    slot = (f"M{cx-sw+sh:.2f},{sy-sh:.2f} H{cx+sw-sh:.2f} "
            f"A{sh},{sh} 0 0 1 {cx+sw-sh:.2f},{sy+sh:.2f} H{cx-sw+sh:.2f} "
            f"A{sh},{sh} 0 0 1 {cx-sw+sh:.2f},{sy-sh:.2f} Z")
    bump = (f"M{cx-br:.2f},{bcy:.2f} A{br},{br} 0 1 1 {cx+br:.2f},{bcy:.2f} "
            f"A{br},{br} 0 1 1 {cx-br:.2f},{bcy:.2f} Z")
    return outer, slot, bump


def die_svg(ox, oy, cls_out="cut", cls_hole="cut"):
    o, s, b = die_path(ox, oy)
    return (f'<path class="{cls_out}" d="{o}"/>'
            f'<path class="{cls_hole}" d="{s}"/><path class="{cls_hole}" d="{b}"/>')


# ---------------------------------------------------------------- ornament
def defs(uid=""):
    return f'''<defs>
  <linearGradient id="plat{uid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{PLAT[0]}"/><stop offset=".22" stop-color="{PLAT[1]}"/>
    <stop offset=".46" stop-color="{PLAT[2]}"/><stop offset=".62" stop-color="{PLAT[3]}"/>
    <stop offset="1" stop-color="{PLAT[4]}"/></linearGradient>
  <linearGradient id="platH{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{PLAT[2]}" stop-opacity="0"/>
    <stop offset=".18" stop-color="{PLAT[1]}"/><stop offset=".5" stop-color="{PLAT[0]}"/>
    <stop offset=".82" stop-color="{PLAT[1]}"/>
    <stop offset="1" stop-color="{PLAT[2]}" stop-opacity="0"/></linearGradient>
  <linearGradient id="platD{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#9FB0C8" stop-opacity="0"/>
    <stop offset=".2" stop-color="#7E90AE"/><stop offset=".5" stop-color="#C9D6E8"/>
    <stop offset=".8" stop-color="#7E90AE"/>
    <stop offset="1" stop-color="#9FB0C8" stop-opacity="0"/></linearGradient>
</defs>'''


def rule_plat(w, h=0.5, dark=False):
    """A hairline that reads as brushed metal."""
    g = "platD" if dark else "platH"
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" '
            f'style="width:{mm(w)};height:{mm(h)};display:block">{defs("r%d" % (w*10))}'
            f'<rect width="{w}" height="{h}" fill="url(#{g}r{int(w*10)})"/></svg>')


def diamond(size=2.6, dark=False):
    c = "#7E90AE" if dark else "#DCE6F3"
    return (f'<svg viewBox="0 0 10 10" style="width:{mm(size)};height:{mm(size)};display:block">'
            f'<path d="M5 0 L10 5 L5 10 L0 5 Z" fill="{c}"/>'
            f'<path d="M5 2.2 L7.8 5 L5 7.8 L2.2 5 Z" fill="{"#C9D6E8" if dark else "#9FB0C8"}"/></svg>')


def ornament_rule(total_w, dark=False):
    """hairline — diamond — hairline, centred."""
    side = (total_w - 6.0) / 2
    return (f'<div style="display:flex;align-items:center;justify-content:center;gap:{mm(1.6)};'
            f'width:{mm(total_w)}">{rule_plat(side, dark=dark)}{diamond(2.6, dark)}'
            f'{rule_plat(side, dark=dark)}</div>')


# ---------------------------------------------------------------- product art
def block_svg(uid, ridges=30):
    cx, cy, rx, ry, depth = 100.0, 64.0, 90.0, 49.0, 24.0
    o = [f'<svg viewBox="0 0 200 150" preserveAspectRatio="xMidYMid meet">']
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


def icon(name, col="#FFFFFF", sw=1.8):
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
IDEAL = ["Homes", "Hotels", "Restaurants", "Schools",
         "Hospitals", "Offices", "Washrooms"]
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
.card {{ position:absolute; overflow:hidden; }}
.abs  {{ position:absolute; }}
.ctr  {{ position:absolute; width:100%; text-align:center; }}

.deep {{ background:
   radial-gradient(86% 46% at 50% 30%, #2F6FE0 0%, #16429F 38%, {DEEP} 72%, {NAVY} 100%); }}
.sheen {{ position:absolute; inset:0; background:
   radial-gradient(44% 24% at 50% 62%, rgba(150,205,255,.30), transparent 72%),
   linear-gradient(180deg, rgba(255,255,255,.10), transparent 24%, transparent 72%, rgba(0,0,0,.26)); }}

.h-prod {{ font-family:Outfit; font-weight:900; letter-spacing:-.028em; line-height:.9;
           text-transform:uppercase; color:#fff; white-space:nowrap; }}
.sc {{ font-family:Outfit; font-weight:600; text-transform:uppercase; }}

.hdr {{ display:inline-flex; align-items:center; gap:{mm(1.8)}; background:{BRAND}; color:#fff;
        font-family:Outfit; font-weight:700; letter-spacing:.11em; text-transform:uppercase;
        border-radius:1.2mm; white-space:nowrap; line-height:1; }}
.hdr.red {{ background:{RED}; }}
.li {{ display:flex; gap:{mm(1.7)}; align-items:flex-start; }}
.li i {{ flex:none; border-radius:50%; background:{AQUA}; }}
.qrbox {{ background:#fff; border-radius:1mm; }}
.qrbox svg {{ width:100%; height:100%; display:block; }}
.qrbox svg path {{ fill:#0A1430; }}

.cut    {{ fill:none; stroke:#E6007E; stroke-width:.35; }}
.crease {{ fill:none; stroke:#00AEEF; stroke-width:.35; stroke-dasharray:2.2 1.4; }}
.bleedl {{ fill:none; stroke:#9A9A9A; stroke-width:.3; stroke-dasharray:1.2 1.2; }}
.dlabel {{ font-family:Jakarta; fill:#E6007E; font-weight:700; }}
.dnote  {{ font-family:Jakarta; fill:#2B3350; }}
"""


# ---------------------------------------------------------------- frame
def frame(dark=True):
    """Double platinum keyline with corner diamonds — the premium device."""
    x0, y0 = FRAME_IN, FRAME_TOP
    x1, y1 = CARD_W - FRAME_IN, CARD_H - FRAME_IN
    w, h, r = x1 - x0, y1 - y0, 3.2
    op = ".85" if dark else ".9"
    g = "plat" if dark else "platDk"
    stops = (f'<stop offset="0" stop-color="{PLAT[0]}"/><stop offset=".25" stop-color="{PLAT[1]}"/>'
             f'<stop offset=".5" stop-color="{PLAT[2]}"/><stop offset=".75" stop-color="{PLAT[3]}"/>'
             f'<stop offset="1" stop-color="{PLAT[4]}"/>') if dark else (
             f'<stop offset="0" stop-color="#B9C7DC"/><stop offset=".3" stop-color="#8295B4"/>'
             f'<stop offset=".55" stop-color="#C9D6E8"/><stop offset="1" stop-color="#8295B4"/>')
    s = [f'<svg class="abs" style="left:0;top:0;width:{mm(CARD_W)};height:{mm(CARD_H)}" '
         f'viewBox="0 0 {CARD_W} {CARD_H}">',
         f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="1" y2="1">{stops}</linearGradient></defs>',
         f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{r}" fill="none" '
         f'stroke="url(#{g})" stroke-width=".55" opacity="{op}"/>',
         f'<rect x="{x0+1.5}" y="{y0+1.5}" width="{w-3}" height="{h-3}" rx="{max(0,r-1.2)}" '
         f'fill="none" stroke="url(#{g})" stroke-width=".3" opacity="{float(op)*0.65:.2f}"/>']
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        s.append(f'<path d="M{cx},{cy-1.7} L{cx+1.7},{cy} L{cx},{cy+1.7} L{cx-1.7},{cy} Z" '
                 f'fill="url(#{g})" opacity="{op}"/>')
    s.append("</svg>")
    return "".join(s)


def seal(size=21.0):
    """Roundel: platinum ring, 50 g x 4 inside. Sits on the hero, premium cue."""
    return (f'<svg viewBox="0 0 100 100" style="width:{mm(size)};height:{mm(size)};display:block">'
            f'{defs("s")}'
            f'<circle cx="50" cy="50" r="48" fill="#06173F"/>'
            f'<circle cx="50" cy="50" r="48" fill="none" stroke="url(#plats)" stroke-width="3.2"/>'
            f'<circle cx="50" cy="50" r="41" fill="none" stroke="url(#plats)" stroke-width="1.0" opacity=".8"/>'
            f'<text x="50" y="40" text-anchor="middle" font-family="Outfit" font-weight="900" '
            f'font-size="27" fill="#FFFFFF" letter-spacing="-1">50g</text>'
            f'<path d="M26 50 H74" stroke="url(#plats)" stroke-width="1.4"/>'
            f'<text x="50" y="75" text-anchor="middle" font-family="Outfit" font-weight="900" '
            f'font-size="27" fill="#FFFFFF">&#215;4</text></svg>')


# ---------------------------------------------------------------- front
def front_card(ox=0.0, oy=0.0):
    IX, IW = FRAME_IN + PAD, CARD_W - (FRAME_IN + PAD) * 2
    o = [f'<div class="card deep" style="left:{mm(ox)};top:{mm(oy)};'
         f'width:{mm(CARD_W)};height:{mm(CARD_H)}">', '<div class="sheen"></div>']

    # faint concentric arcs behind the product — texture, not pattern
    o.append(f'<svg class="abs" style="left:0;top:0;width:{mm(CARD_W)};height:{mm(CARD_H)}" '
             f'viewBox="0 0 {CARD_W} {CARD_H}">' +
             "".join(f'<circle cx="{CARD_W/2}" cy="124" r="{18+i*7.5}" fill="none" '
                     f'stroke="#9FD0FF" stroke-opacity=".07" stroke-width=".4"/>' for i in range(7)) +
             "</svg>")
    o.append(frame(dark=True))

    o.append(f'<div class="abs" id="swift-front" style="left:{mm((CARD_W-50)/2)};top:{mm(29)};'
             f'width:{mm(50)};height:{mm(24)}"></div>')
    # corner seal, level with the logo and clear of it
    o.append(f'<div class="abs" style="left:{mm(CARD_W-FRAME_IN-PAD-21)};top:{mm(29.5)}">{seal(21)}</div>')

    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(57.0)};">{ornament_rule(IW)}</div>')
    o.append(f'<div class="ctr h-prod" style="top:{mm(61.0)};font-size:{mm(15.6)};'
             f'text-shadow:0 {mm(.5)} {mm(1.6)} rgba(0,0,0,.35)">TOILET</div>')
    o.append(f'<div class="ctr h-prod" style="top:{mm(75.0)};font-size:{mm(15.6)};'
             f'text-shadow:0 {mm(.5)} {mm(1.6)} rgba(0,0,0,.35)">BLOCKS</div>')
    o.append(f'<div class="ctr sc" style="top:{mm(92.0)};font-size:{mm(3.4)};letter-spacing:.20em;'
             f'color:{PALE}">Automatic Toilet Bowl Cleaner</div>')
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(99.0)};">{ornament_rule(IW)}</div>')

    # Four blocks: two set back, two in front. Each SVG is 4:3, so a block w mm
    # wide stands 0.75 w tall — the heights below are what keep them inside the
    # 38 mm band and off the benefit icons underneath.
    lay = [(6.0, 0.0, 32.0, ".76"), (56.0, 1.0, 32.0, ".76"),
           (22.0, 11.0, 36.0, "1"), (48.0, 11.0, 36.0, "1")]
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(102.0)};width:{mm(IW)};height:{mm(38)}">')
    for i, (bx, by, bw, op) in enumerate(lay):
        o.append(f'<div class="abs" style="left:{mm(bx)};top:{mm(by)};width:{mm(bw)};'
                 f'opacity:{op}">{block_svg("f%d" % i)}</div>')
    o.append("</div>")

    chips = "".join(
        f'<div style="display:flex;flex-direction:column;align-items:center;width:{mm(26)}">'
        f'<div style="width:{mm(5.4)};height:{mm(5.4)};margin-bottom:{mm(1.3)}">{icon(k, PALE)}</div>'
        f'<span class="sc" style="font-size:{mm(2.65)};letter-spacing:.14em;color:#fff">{t}</span></div>'
        for k, t in [("flush", "Cleans"), ("fresh", "Freshens"), ("shield", "Protects")])
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(143.0)};width:{mm(IW)};'
             f'display:flex;justify-content:center;gap:{mm(5)}">{chips}</div>')

    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(155.5)};">{ornament_rule(IW)}</div>')
    o.append(f'<div class="ctr" style="top:{mm(159.0)};font-family:Outfit;font-weight:800;'
             f'font-size:{mm(5.0)};color:#fff;letter-spacing:.01em;white-space:nowrap">'
             f'50 g &times; 4 <span style="color:{PALE};font-weight:600;font-size:{mm(3.0)};'
             f'letter-spacing:.10em">&nbsp;&middot;&nbsp; NET WT. 200 g</span></div>')
    o.append("</div>")
    return "".join(o)

# ---------------------------------------------------------------- back
def back_card(ox=0.0, oy=0.0):
    """Laid out in normal document flow, not absolute positions: the carton
    version drifted into overlaps every time a line count changed."""
    IX, IW = FRAME_IN + PAD, CARD_W - (FRAME_IN + PAD) * 2
    o = [f'<div class="card" style="left:{mm(ox)};top:{mm(oy)};width:{mm(CARD_W)};'
         f'height:{mm(CARD_H)};background:{IVORY}">']
    o.append(f'<div class="abs" style="left:0;top:0;width:{mm(CARD_W)};height:{mm(CARD_H)};'
             f'background:radial-gradient(70% 40% at 50% 0%, #EEF4FD, transparent 70%)"></div>')
    o.append(frame(dark=False))

    hdr = (f'font-size:{mm(2.75)};padding:{mm(1.2)} {mm(2.6)}')
    steps = "".join(
        f'<div style="display:flex;gap:{mm(2.1)};align-items:flex-start;margin-top:{mm(2.9)}">'
        f'<div style="flex:none;width:{mm(5.6)};height:{mm(5.6)};border-radius:50%;background:{BRAND};'
        f'display:flex;align-items:center;justify-content:center">'
        f'<div style="width:{mm(3.2)};height:{mm(3.2)}">{icon(ic)}</div></div>'
        f'<div style="font-size:{mm(2.5)};line-height:1.38;color:{INK}">'
        f'<b style="color:{BRAND}">{i+1}.</b> {t}</div></div>'
        for i, (ic, t) in enumerate(STEPS))
    bens = "".join(
        f'<div style="display:flex;gap:{mm(2.0)};align-items:center;margin-top:{mm(2.8)}">'
        f'<div style="flex:none;width:{mm(4.4)};height:{mm(4.4)}">{icon(ic, AQUA)}</div>'
        f'<div style="font-size:{mm(2.6)};color:{INK};font-weight:600">{t}</div></div>'
        for ic, t in BENEFITS)
    cautions = "".join(
        f'<div class="li" style="break-inside:avoid;margin-top:{mm(1.8)}">'
        f'<i style="width:{mm(1.1)};height:{mm(1.1)};margin-top:{mm(1.0)};background:{RED}"></i>'
        f'<div style="font-size:{mm(2.45)};line-height:1.32;color:{INK}">{t}</div></div>'
        for t in CAUTION)

    o.append(f'''<div class="abs" id="backflow" style="left:{mm(IX)};top:{mm(23.5)};width:{mm(IW)}">
  <div style="text-align:center;font-family:Outfit;font-weight:800;font-size:{mm(7.0)};
       color:{BRAND};letter-spacing:-.015em;line-height:1.05">Swift Toilet Blocks</div>
  <div class="sc" style="text-align:center;font-size:{mm(2.85)};letter-spacing:.20em;
       color:{AQUA};margin-top:{mm(1.3)}">Automatic Toilet Bowl Cleaner</div>
  <div style="margin-top:{mm(2.6)}">{ornament_rule(IW, dark=True)}</div>
  <div style="margin-top:{mm(3.2)};font-size:{mm(2.75)};line-height:1.5;color:{INK};
       text-align:center">{DESC}</div>

  <div style="display:flex;gap:{mm(6.0)};margin-top:{mm(5.0)};align-items:flex-start">
    <div style="flex:1 1 0;min-width:0">
      <span class="hdr" style="{hdr}">How to use</span>{steps}
      <div style="margin-top:{mm(5.0)}"><span class="hdr red" style="{hdr}">Caution</span></div>
      <div style="margin-top:{mm(.4)}">{cautions}</div>
    </div>
    <div style="flex:1 1 0;min-width:0">
      <span class="hdr" style="{hdr}">Key benefits</span>{bens}
      <div style="margin-top:{mm(4.0)}"><span class="hdr" style="{hdr}">Ideal for</span></div>
      <div style="margin-top:{mm(2.4)};font-size:{mm(2.5)};line-height:1.55;color:{INK}">
        {" &middot; ".join(IDEAL)}</div>
    </div>
  </div>


  <div style="margin-top:{mm(5.0)};font-size:{mm(2.4)};line-height:1.42;color:{MUTED}">
    <b style="color:{BRAND}">Active ingredients:</b> sodium dichloroisocyanurate,
    anionic &amp; non-ionic surfactants, fragrance, colourant.</div>
</div>''')

    # footer pinned to the frame's bottom, so it never floats with copy length
    fy, qr = 147.5, 16.0
    o.append(f'<div class="abs" id="backfoot" style="left:{mm(IX)};top:{mm(fy-4.5)}">{ornament_rule(IW, dark=True)}</div>')
    o.append(f'<img src="data:image/png;base64,{A["vistex"]}" class="abs" '
             f'style="left:{mm(IX)};top:{mm(fy)};width:{mm(36)};height:auto">')
    o.append(f'<div class="abs" style="left:{mm(IX)};top:{mm(fy+13.4)};width:{mm(IW-qr-5)};'
             f'font-size:{mm(2.3)};line-height:1.46;color:{MUTED}">'
             f'P.O. Box 218 &ndash; 00606, Industrial Area, Nairobi, Kenya<br>'
             f'0739 446 655 &nbsp;&middot;&nbsp; info@vistexchemicals.co.ke<br>'
             f'www.vistexchemicals.co.ke</div>')
    o.append(f'<div class="qrbox abs" style="left:{mm(CARD_W-FRAME_IN-PAD-qr)};top:{mm(fy)};'
             f'width:{mm(qr)};height:{mm(qr)};padding:{mm(1.1)}">{A["qr_svg"]}</div>')
    o.append(f'<div class="abs sc" style="left:{mm(CARD_W-FRAME_IN-PAD-qr-4)};top:{mm(fy+qr+1.4)};'
             f'width:{mm(qr+4)};text-align:center;font-size:{mm(1.95)};letter-spacing:.06em;'
             f'color:{MUTED}">Scan for more</div>')
    o.append("</div>")
    return "".join(o)

# ---------------------------------------------------------------- bleed
def bleed_under(kind):
    """Colour behind the card so the die cut never reveals white paper."""
    if kind == "front":
        return (f'<div class="card deep" style="left:{mm(-BLEED)};top:{mm(-BLEED)};'
                f'width:{mm(CARD_W+BLEED*2)};height:{mm(CARD_H+BLEED*2)}"></div>')
    return (f'<div class="card" style="left:{mm(-BLEED)};top:{mm(-BLEED)};'
            f'width:{mm(CARD_W+BLEED*2)};height:{mm(CARD_H+BLEED*2)};background:{IVORY}"></div>')


def page(kind):
    inner = front_card() if kind == "front" else back_card()
    return (f'<div class="abs" style="left:{mm(BLEED)};top:{mm(BLEED)};'
            f'width:{mm(CARD_W)};height:{mm(CARD_H)}">{bleed_under(kind)}{inner}</div>')


def html(body, w, h, extra=""):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>'
            f'@page {{ size:{w}mm {h}mm; margin:0; }}'
            f'html,body {{ width:{w}mm; height:{h}mm; }}{CSS}{extra}</style></head>'
            f'<body>{body}</body></html>')


def proof():
    lx, rx = 0.0, PAGE_W + PROOF_GAP
    b = [f'<div class="abs" style="left:{mm(lx)};top:0;width:{mm(PAGE_W)};height:{mm(PAGE_H)}">{page("front")}</div>',
         f'<div class="abs" style="left:{mm(rx)};top:0;width:{mm(PAGE_W)};height:{mm(PAGE_H)}">{page("back")}</div>']
    s = [f'<svg class="abs" style="left:0;top:0;width:{mm(PROOF_W)};height:{mm(PROOF_H)}" '
         f'viewBox="0 0 {PROOF_W} {PROOF_H}">']
    for ox, lab in ((lx + BLEED, "FRONT"), (rx + BLEED, "BACK")):
        s.append(die_svg(ox, BLEED))
        s.append(f'<rect class="bleedl" x="{ox-BLEED+.15}" y="{.15}" '
                 f'width="{PAGE_W-.3}" height="{PAGE_H-.3}"/>')
        s.append(f'<text class="dlabel" font-size="3.0" x="{ox+CARD_W/2}" y="{PAGE_H+5.5}" '
                 f'text-anchor="middle">{lab}</text>')
    ly = PAGE_H + 11.0
    s.append(f'<text class="dnote" font-size="3.0" font-weight="700" fill="#2B3350" x="{lx}" y="{ly}">'
             f'Swift Toilet Blocks &#8212; 4 &#215; 50 g &#8212; euro-slot hang card, proof</text>')
    s.append(f'<text class="dnote" font-size="2.5" x="{lx}" y="{ly+4.4}">'
             f'Card {CARD_W:.0f} &#215; {CARD_H:.0f} mm, {CORNER:.0f} mm corner radius, '
             f'sombrero euro hanger &#183; {BLEED:.0f} mm bleed &#183; page {PAGE_W:.0f} &#215; {PAGE_H:.0f} mm each. '
             f'Die matches the Blue-Drop card, so one tool can cut both.</text>')
    s.append(f'<text class="dnote" font-size="2.5" x="{lx}" y="{ly+8.4}">'
             f'Magenta = cut (outline and hanger). For position only &#8212; absent from the artwork files. '
             f'Platinum rules and frame are printed CMYK; specify silver foil if a metallic finish is wanted.</text>')
    s.append("</svg>")
    return html("".join(b) + "".join(s), PROOF_W, PROOF_H)


for kind in ("front", "back"):
    (HERE / f"card-{kind}.html").write_text(html(page(kind), PAGE_W, PAGE_H), encoding="utf8")
(HERE / "card-proof.html").write_text(proof(), encoding="utf8")

meta = {"PAGE_W": PAGE_W, "PAGE_H": PAGE_H, "CARD_W": CARD_W, "CARD_H": CARD_H,
        "BLEED": BLEED, "CORNER": CORNER, "PROOF_W": PROOF_W, "PROOF_H": PROOF_H,
        "PROOF_GAP": PROOF_GAP,
        # x,y are relative to the card; pages add BLEED, the proof adds its offset
        "swift_slots": [{"id": "front", "x": (CARD_W - 50) / 2, "y": 30, "w": 50, "h": 25}],
        "die": {"slot_w": HANG_SLOT_W, "slot_h": HANG_SLOT_H, "slot_y": HANG_SLOT_Y,
                "bump_r": HANG_BUMP_R, "bump_cy": HANG_BUMP_CY}}
(HERE / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf8")
print(f"card {CARD_W:.0f} x {CARD_H:.0f} mm, page {PAGE_W:.0f} x {PAGE_H:.0f} mm, "
      f"proof {PROOF_W:.0f} x {PROOF_H:.0f} mm")
