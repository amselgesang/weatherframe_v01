"""Two 800x480 e-paper screen designs (4 grey levels), rendered at 3x and downsampled.

  screen_forecast.png : time, date, 7-day forecast with icons
  screen_cartoon.png  : newspaper-style single-panel cartoon
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 3                      # supersampling
W, H = 800 * S, 480 * S
BLACK, DARK, LIGHT, WHITE = 0, 85, 170, 255
INTER = "/usr/share/fonts/opentype/inter/"


def font(name, size):
    return ImageFont.truetype(INTER + name, int(size * S))


def serif(size, italic=False, bold=False):
    f = "/usr/share/fonts/truetype/liberation/LiberationSerif-" + \
        ("BoldItalic" if bold and italic else "Bold" if bold else "Italic" if italic else "Regular") + ".ttf"
    return ImageFont.truetype(f, int(size * S))


# ------------------------------------------------------------------ icons
def sun(d, cx, cy, r, fill=BLACK, rays=True, lw=None):
    lw = lw or max(2, int(r * 0.14))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fill, width=lw)
    if rays:
        for k in range(8):
            a = k * math.pi / 4
            x0, y0 = cx + math.cos(a) * r * 1.45, cy + math.sin(a) * r * 1.45
            x1, y1 = cx + math.cos(a) * r * 1.95, cy + math.sin(a) * r * 1.95
            d.line([x0, y0, x1, y1], fill=fill, width=lw)
            d.ellipse([x0 - lw / 2, y0 - lw / 2, x0 + lw / 2, y0 + lw / 2], fill=fill)
            d.ellipse([x1 - lw / 2, y1 - lw / 2, x1 + lw / 2, y1 + lw / 2], fill=fill)


def cloud(d, cx, cy, s, fill=WHITE, outline=BLACK, lw=None):
    """Cloud centred at cx,cy, width ~ 2.2 s."""
    lw = lw or max(2, int(s * 0.13))
    parts = [(-0.55, 0.15, 0.48), (0.0, -0.18, 0.62), (0.55, 0.12, 0.5)]
    base = [cx - 1.03 * s, cy + 0.1 * s, cx + 1.05 * s, cy + 0.62 * s]
    # outline pass (fat), then fill pass
    for (dx, dy, r) in parts:
        d.ellipse([cx + (dx - r) * s - lw, cy + (dy - r) * s - lw, cx + (dx + r) * s + lw, cy + (dy + r) * s + lw], fill=outline)
    d.rounded_rectangle([base[0] - lw, base[1] - lw, base[2] + lw, base[3] + lw], radius=int(0.26 * s + lw), fill=outline)
    for (dx, dy, r) in parts:
        d.ellipse([cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s], fill=fill)
    d.rounded_rectangle(base, radius=int(0.26 * s), fill=fill)


def drops(d, cx, cy, s, n=3, lw=None, fill=BLACK):
    lw = lw or max(2, int(s * 0.13))
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * 0.55 * s
        d.line([x + 0.12 * s, cy, x - 0.12 * s, cy + 0.42 * s], fill=fill, width=lw)


def flakes(d, cx, cy, s, n=3, fill=BLACK):
    lw = max(2, int(s * 0.09))
    for i in range(n):
        x, y = cx + (i - (n - 1) / 2) * 0.6 * s, cy + (0.15 if i % 2 else 0.0) * s
        for k in range(3):
            a = k * math.pi / 3
            dx, dy = math.cos(a) * 0.17 * s, math.sin(a) * 0.17 * s
            d.line([x - dx, y - dy, x + dx, y + dy], fill=fill, width=lw)


def bolt(d, cx, cy, s, fill=BLACK):
    pts = [(0.1, -0.05), (-0.22, 0.42), (0.02, 0.42), (-0.12, 0.85), (0.3, 0.27), (0.06, 0.27), (0.22, -0.05)]
    d.polygon([(cx + x * s, cy + y * s) for x, y in pts], fill=fill)


def icon(d, kind, cx, cy, s):
    """s ~ half width of the icon."""
    if kind == "sun":
        sun(d, cx, cy, s * 0.48)
    elif kind == "partly":
        sun(d, cx + s * 0.28, cy - s * 0.3, s * 0.34)
        cloud(d, cx - s * 0.12, cy + s * 0.1, s * 0.62)
    elif kind == "cloud":
        cloud(d, cx + s * 0.25, cy - s * 0.28, s * 0.45, fill=LIGHT)
        cloud(d, cx - s * 0.08, cy + s * 0.05, s * 0.62)
    elif kind == "rain":
        cloud(d, cx, cy - s * 0.2, s * 0.62)
        drops(d, cx, cy + s * 0.32, s * 0.62)
    elif kind == "showers":
        sun(d, cx + s * 0.3, cy - s * 0.42, s * 0.3)
        cloud(d, cx - s * 0.08, cy - s * 0.14, s * 0.6)
        drops(d, cx - s * 0.08, cy + s * 0.36, s * 0.6, n=2)
    elif kind == "storm":
        cloud(d, cx, cy - s * 0.22, s * 0.62, fill=LIGHT)
        bolt(d, cx, cy + s * 0.12, s * 0.62)
    elif kind == "snow":
        cloud(d, cx, cy - s * 0.2, s * 0.62)
        flakes(d, cx, cy + s * 0.5, s * 0.62)


def text_c(d, x, y, s, f, fill=BLACK):
    w = d.textlength(s, font=f)
    d.text((x - w / 2, y), s, font=f, fill=fill)


def finish(img, path):
    out = img.resize((800 * 2, 480 * 2), Image.LANCZOS)    # 1600x960 texture
    # 4 grey levels with a soft edge: quantise mid-tones, keep a 1-step anti-alias
    lut = []
    for v in range(256):
        q = round(v / 85) * 85
        lut.append(int(0.8 * q + 0.2 * v))
    out = out.point(lut)
    out.save(path)
    print("wrote", path, out.size)


# ------------------------------------------------------------------ forecast screen
def forecast(path):
    img = Image.new("L", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    m = 34 * S
    # time + date
    d.text((m - 6 * S, 18 * S), "07:45", font=font("Inter-Bold.otf", 128), fill=BLACK)
    d.text((m, 178 * S), "Dienstag, 13. Oktober", font=font("Inter-SemiBold.otf", 30), fill=BLACK)
    d.text((m, 220 * S), "Budapest  ·  Sonnenaufgang 07:08  ·  Untergang 18:12", font=font("Inter-Medium.otf", 17), fill=DARK)
    # current conditions, right
    x0 = 488 * S
    d.line([x0, 40 * S, x0, 236 * S], fill=LIGHT, width=2 * S)
    icon(d, "partly", 576 * S, 104 * S, 70 * S)
    d.text((660 * S, 52 * S), "14°", font=font("Inter-Bold.otf", 64), fill=BLACK)
    d.text((664 * S, 134 * S), "Leicht bewölkt", font=font("Inter-Medium.otf", 17), fill=BLACK)
    d.text((520 * S, 182 * S), "Innen 21.4°  ·  47 %", font=font("Inter-Medium.otf", 17), fill=DARK)
    d.text((520 * S, 208 * S), "Wind 12 km/h  ·  Regen 10 %", font=font("Inter-Medium.otf", 17), fill=DARK)
    # 7-day strip
    top = 262 * S
    d.line([m, top, W - m, top], fill=BLACK, width=2 * S)
    days = [("Heute", "partly", 16, 7, 10), ("Mi", "rain", 13, 9, 90), ("Do", "showers", 14, 8, 60),
            ("Fr", "cloud", 12, 6, 20), ("Sa", "sun", 15, 4, 0), ("So", "sun", 17, 5, 0), ("Mo", "storm", 15, 9, 70)]
    colw = (W - 2 * m) / 7
    for i, (name, kind, hi, lo, pop) in enumerate(days):
        cx = m + colw * (i + 0.5)
        if i:
            d.line([m + colw * i, top + 22 * S, m + colw * i, H - 26 * S], fill=LIGHT, width=S)
        text_c(d, cx, top + 16 * S, name, font("Inter-SemiBold.otf", 20), BLACK)
        icon(d, kind, cx, top + 92 * S, 34 * S)
        text_c(d, cx, top + 136 * S, f"{hi}°", font("Inter-Bold.otf", 26), BLACK)
        text_c(d, cx, top + 166 * S, f"{lo}°", font("Inter-Medium.otf", 20), DARK)
    # tiny footer
    d.text((W - m - 170 * S, H - 22 * S), "aktualisiert 07:45", font=font("Inter-Medium.otf", 12), fill=DARK)
    finish(img, path)


# ------------------------------------------------------------------ cartoon screen
def hatch(d, box, step, fill=BLACK, width=None, mask=None):
    x0, y0, x1, y1 = box
    width = width or S
    k = -(y1 - y0)
    while k < (x1 - x0):
        d.line([x0 + k, y1, x0 + k + (y1 - y0), y0], fill=fill, width=width)
        k += step


def cartoon(path):
    img = Image.new("L", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    # masthead
    d.text((30 * S, 14 * S), "DER WETTERBOTE", font=serif(34, bold=True), fill=BLACK)
    d.text((560 * S, 20 * S), "Dienstag, 13. Oktober 2026", font=serif(16, italic=True), fill=BLACK)
    d.text((560 * S, 40 * S), "Ausgabe Nr. 287  ·  Preis: 1 Sonnenstrahl", font=serif(13), fill=BLACK)
    d.line([30 * S, 62 * S, W - 30 * S, 62 * S], fill=BLACK, width=3 * S)
    d.line([30 * S, 67 * S, W - 30 * S, 67 * S], fill=BLACK, width=S)

    # panel
    px0, py0, px1, py1 = 30 * S, 80 * S, W - 30 * S, 400 * S
    # Ben-Day dots sky, fading downward
    panel = Image.new("L", (px1 - px0, py1 - py0), WHITE)
    pd = ImageDraw.Draw(panel)
    step = 9 * S
    for yy in range(0, py1 - py0, step):
        r = max(0, 2.3 * S * (1 - yy / (py1 - py0) * 1.25))
        off = (yy // step % 2) * step / 2
        for xx in range(0, px1 - px0 + step, step):
            if r > 0.4 * S:
                pd.ellipse([xx + off - r, yy - r, xx + off + r, yy + r], fill=LIGHT)
    img.paste(panel, (px0, py0))
    d = ImageDraw.Draw(img)

    ground = 352 * S
    d.rectangle([px0, ground, px1, py1], fill=WHITE)
    d.line([px0, ground, px1, ground], fill=BLACK, width=3 * S)
    hatch(d, (px0, ground + 6 * S, px1, py1), 14 * S, fill=DARK, width=S)
    d.rectangle([0, ground, px0, py1 + 2 * S], fill=WHITE)
    d.rectangle([px1, ground, W, py1 + 2 * S], fill=WHITE)

    # --- the worried rain cloud holding an umbrella, raining on itself? no: raining UP onto its umbrella
    ccx, ccy, cs = 290 * S, 240 * S, 82 * S
    lw = 5 * S
    # rain falling from the cloud
    for i in range(9):
        x = ccx - 0.95 * cs + i * 0.24 * cs
        for j in range(3):
            y = ccy + 0.75 * cs + j * 34 * S + (i % 2) * 14 * S
            if y + 16 * S < ground - 8 * S:
                d.line([x + 4 * S, y, x - 2 * S, y + 16 * S], fill=BLACK, width=3 * S)
    cloud(d, ccx, ccy, cs, fill=WHITE, outline=BLACK, lw=lw)
    # shading hatch on cloud bottom
    for k in range(7):
        y = ccy + 0.42 * cs + k * 4 * S
        d.line([ccx - 0.8 * cs + k * 6 * S, y, ccx + 0.8 * cs - k * 6 * S, y], fill=DARK, width=S)
    # face: worried eyebrows, eyes looking up, little wavy mouth
    ex = [ccx - 0.32 * cs, ccx + 0.18 * cs]
    for x in ex:
        d.ellipse([x - 13 * S, ccy - 30 * S, x + 13 * S, ccy - 2 * S], fill=WHITE, outline=BLACK, width=3 * S)
        d.ellipse([x - 5 * S, ccy - 28 * S, x + 5 * S, ccy - 16 * S], fill=BLACK)
    d.line([ex[0] - 16 * S, ccy - 38 * S, ex[0] + 10 * S, ccy - 46 * S], fill=BLACK, width=4 * S)
    d.line([ex[1] - 10 * S, ccy - 46 * S, ex[1] + 16 * S, ccy - 38 * S], fill=BLACK, width=4 * S)
    mx = ccx - 0.07 * cs
    d.line([mx - 20 * S, ccy + 22 * S, mx - 10 * S, ccy + 16 * S, mx, ccy + 22 * S, mx + 10 * S, ccy + 16 * S, mx + 20 * S, ccy + 22 * S],
           fill=BLACK, width=4 * S, joint="curve")
    # sweat drop
    d.polygon([(ccx + 0.55 * cs, ccy - 34 * S), (ccx + 0.5 * cs, ccy - 18 * S), (ccx + 0.6 * cs, ccy - 18 * S)], fill=BLACK)
    d.ellipse([ccx + 0.5 * cs, ccy - 24 * S, ccx + 0.6 * cs, ccy - 12 * S], fill=BLACK)
    # little arm + umbrella held over itself
    hx, hy = ccx + 1.22 * cs, ccy + 0.05 * cs
    d.line([ccx + 0.98 * cs, ccy + 0.25 * cs, hx - 4 * S, hy], fill=BLACK, width=lw)          # little arm
    d.ellipse([hx - 9 * S, hy - 9 * S, hx + 9 * S, hy + 9 * S], fill=WHITE, outline=BLACK, width=4 * S)  # hand
    ux, uy, ur = hx - 0.35 * cs, ccy - 0.98 * cs, 1.05 * cs
    d.line([ux, uy, hx, hy + 22 * S], fill=BLACK, width=5 * S)                         # shaft
    d.arc([hx - 4 * S, hy + 10 * S, hx + 20 * S, hy + 34 * S], 0, 180, fill=BLACK, width=5 * S)  # J handle
    canopy = [ux - ur, uy - 0.75 * ur, ux + ur, uy + 0.75 * ur]
    d.pieslice(canopy, 180, 360, fill=WHITE, outline=BLACK, width=lw)
    # scalloped rim + panel ribs + hatching on alternate panels
    n = 5
    for k in range(n):
        a0 = ux - ur + k * 2 * ur / n
        d.chord([a0, uy - 0.09 * ur, a0 + 2 * ur / n, uy + 0.09 * ur], 0, 180, fill=WHITE, outline=BLACK, width=3 * S)
    for k in range(1, n):
        a = math.pi + k * math.pi / n
        d.line([ux, uy - 0.75 * ur, ux + math.cos(a) * ur, uy], fill=BLACK, width=3 * S)
    d.ellipse([ux - 6 * S, uy - 0.75 * ur - 10 * S, ux + 6 * S, uy - 0.75 * ur + 2 * S], fill=BLACK)

    # --- a smug sun in sunglasses on a deck chair, right
    sx, sy, sr = 610 * S, 270 * S, 46 * S
    # deck chair
    d.line([sx - 70 * S, ground, sx + 10 * S, sy + 12 * S], fill=BLACK, width=5 * S)
    d.line([sx + 60 * S, ground, sx - 10 * S, sy + 40 * S], fill=BLACK, width=5 * S)
    d.polygon([(sx - 60 * S, sy + 52 * S), (sx + 40 * S, sy + 34 * S), (sx + 75 * S, sy - 40 * S), (sx + 50 * S, sy - 46 * S),
               (sx + 18 * S, sy + 20 * S), (sx - 64 * S, sy + 38 * S)], fill=WHITE, outline=BLACK, width=4 * S)
    for k in range(4):
        d.line([sx - 50 * S + k * 24 * S, sy + 48 * S - k * 4 * S, sx - 48 * S + k * 24 * S, sy + 38 * S - k * 4 * S], fill=BLACK, width=2 * S)
    sun(d, sx, sy - 30 * S, sr, lw=5 * S)
    d.ellipse([sx - sr + 5 * S, sy - 30 * S - sr + 5 * S, sx + sr - 5 * S, sy - 30 * S + sr - 5 * S], fill=WHITE)
    # sunglasses
    gy = sy - 40 * S
    for gx in (sx - 20 * S, sx + 18 * S):
        d.rounded_rectangle([gx - 16 * S, gy - 9 * S, gx + 16 * S, gy + 11 * S], radius=6 * S, fill=BLACK)
    d.line([sx - 4 * S, gy - 2 * S, sx + 2 * S, gy - 2 * S], fill=BLACK, width=3 * S)
    d.arc([sx - 18 * S, gy + 6 * S, sx + 18 * S, gy + 36 * S], 20, 160, fill=BLACK, width=4 * S)   # grin
    # cocktail
    d.polygon([(sx + 70 * S, sy + 4 * S), (sx + 96 * S, sy + 4 * S), (sx + 83 * S, sy + 22 * S)], fill=WHITE, outline=BLACK, width=3 * S)
    d.line([sx + 83 * S, sy + 22 * S, sx + 83 * S, sy + 44 * S], fill=BLACK, width=3 * S)
    d.line([sx + 72 * S, sy + 44 * S, sx + 94 * S, sy + 44 * S], fill=BLACK, width=3 * S)
    d.line([sx + 88 * S, sy + 6 * S, sx + 100 * S, sy - 14 * S], fill=BLACK, width=2 * S)

    # puddle under the cloud
    d.ellipse([ccx - 120 * S, ground + 8 * S, ccx + 120 * S, ground + 30 * S], fill=WHITE, outline=BLACK, width=3 * S)
    d.arc([ccx - 60 * S, ground + 12 * S, ccx - 20 * S, ground + 24 * S], 200, 340, fill=BLACK, width=2 * S)

    # panel border + signature
    d.rectangle([px0, py0, px1, py1], outline=BLACK, width=4 * S)
    d.text((px1 - 64 * S, py1 - 22 * S), "~ wf", font=serif(15, italic=True), fill=BLACK)

    # caption
    cap = "„Der Wetterbericht sagt 90 % Regen. Ich geh lieber auf Nummer sicher.“"
    f = serif(20, italic=True)
    text_c(d, W / 2, 414 * S, cap, f, BLACK)
    text_c(d, W / 2, 446 * S, "Die Regenwolke vor ihrem großen Auftritt.", serif(15), BLACK)
    finish(img, path)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    forecast(out + "/screen_forecast.png")
    cartoon(out + "/screen_cartoon.png")
