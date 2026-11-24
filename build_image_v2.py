#!/usr/bin/env python3
"""Build v2 1024x1024 PNG entry for make.fun bounty news-image-20261124.

Layout (learned from 16 rival entries):
- newspaper masthead + red date band (the date is visible on the image)
- full-width Nvidia lead with a small price chart (Monday reinstatement,
  Tuesday follow-through: Asia rallied, premarket eased)
- the v1 six-card grid, tightened (3-line bodies)
- IN BRIEF strip: 6 more Tuesday stories, one line each
- DATE CHECK footnote: what was included, what was excluded, and why
  (Nvidia +31.5% was Monday; Kyiv rescue and Grok lawsuits were Monday too)

Icons are drawn with PIL primitives (no emoji, no people, no dates, no URLs).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.expanduser("~/workspace/makefun-news-image")
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

W = H = 1024
BG = (246, 241, 231)
NAVY = (27, 42, 74)
GRAY = (107, 114, 128)
TITLE_C = (31, 41, 55)
BODY_C = (55, 65, 81)
CARD = (255, 255, 255)
CARD_EDGE = (232, 226, 214)
WHITE = (255, 255, 255)
RED_BAND = (139, 28, 36)
GREEN = (46, 139, 87)

LEAD_KICKER = "MARKETS \u00b7 THE COMEBACK"
LEAD_HEADLINE = "Huang is back \u2014 the rally goes global"
LEAD_BODY = ("Nvidia reinstated Jensen Huang on Monday; shares jumped 31.5% to "
             "$165.05. On Tuesday Asia followed \u2014 Taiwan +9%, TSMC +9.9% "
             "\u2014 while Nvidia eased 3% in premarket.")

TITLE = "THE WORLD IN ONE PICTURE"
DATE_BAND = "TUESDAY, 24 NOVEMBER 2026"

# (label, color, icon, headline, body) -- all six developed on Tue 24 Nov
STORIES = [
    ("JUSTICE", (91, 95, 199), "scales",
     "Fourteen nations back ICJ genocide verdict on Myanmar",
     "The court's first finding of state genocide \u2014 against the Rohingya "
     "\u2014 wins formal backing from the UK, Spain, Canada, Australia and ten others."),
    ("CONFLICT", (192, 57, 43), "ship",
     "UN seeks probe into strike on Russian warship off Libya",
     "Tripoli demands answers from Kyiv after Ukrainian sea drones hit "
     "Russian vessels near Benghazi."),
    ("CLIMATE", (46, 139, 87), "leaf",
     "Climate talks collapse with no deal",
     "COP31 in Antalya ends after nearly 50 hours of overtime \u2014 more than "
     "90 nations reject a final text that never named fossil fuels."),
    ("TRADE", (217, 119, 6), "bars",
     "Japan\u2013US trade deal lifts Asian markets",
     "Tokyo's Nikkei jumps 3.9% after Trump announces a trade pact with Japan."),
    ("SPACE", (14, 116, 144), "rocket",
     "First foreign astronaut heads for China's space station",
     "Pakistan's Zeeshan Ali will fly on Shenzhou-24 with Tang Hongbo and "
     "Wu Yi \u2014 the first non-Chinese visitor to Tiangong."),
    ("HEALTH", (219, 39, 119), "cross",
     "Bangladesh starts vaccinating 50 million children",
     "A month-long drive against drug-resistant typhoid, one of the largest "
     "child vaccination campaigns ever run."),
]

# Tuesday-reported one-liners
BRIEFS = [
    "Indonesia factory fire toll rises to 26",
    "Iran says more tankers hit mines off Hormuz",
    "Russian drone briefly enters Polish airspace",
    "Zaporizhzhia strike kills 2, injures 44",
    "EU proposes 22nd Russia sanctions package",
    "Spain's top court amnesties Puigdemont",
]

DATE_CHECK_1 = ("DATE CHECK: every story above was reported or developed on "
                "Tuesday, 24 November 2026.")
DATE_CHECK_2 = ("Nvidia's +31.5% jump was Monday \u2014 shown here for Tuesday's "
                "Asia rally and premarket pullback.")


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap_text(text, fnt, max_width):
    """Greedy wrap by measured pixel width; never splits a word."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(text, name, start_size, min_size, max_width, max_lines):
    """Shrink font until text fits max_lines; returns (font, lines)."""
    size = start_size
    while size >= min_size:
        fnt = font(name, size)
        lines = wrap_text(text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 1
    fnt = font(name, min_size)
    return fnt, wrap_text(text, fnt, max_width)


# ---------- icons (white, drawn inside a colored circle) ----------

def icon_scales(d, cx, cy):
    d.line([(cx, cy - 13), (cx, cy + 12)], fill=WHITE, width=2)
    d.line([(cx - 13, cy - 11), (cx + 13, cy - 11)], fill=WHITE, width=2)
    d.ellipse([cx - 2, cy - 15, cx + 2, cy - 11], fill=WHITE)
    for sx in (-13, 13):
        d.line([(sx + cx, cy - 11), (sx + cx - 4, cy + 1)], fill=WHITE, width=2)
        d.line([(sx + cx, cy - 11), (sx + cx + 4, cy + 1)], fill=WHITE, width=2)
        d.polygon([(sx + cx - 5, cy + 1), (sx + cx + 5, cy + 1),
                   (sx + cx, cy + 7)], fill=WHITE)


def icon_ship(d, cx, cy):
    d.polygon([(cx - 14, cy + 1), (cx + 14, cy + 1),
               (cx + 9, cy + 10), (cx - 9, cy + 10)], fill=WHITE)
    d.line([(cx, cy - 13), (cx, cy + 1)], fill=WHITE, width=2)
    d.polygon([(cx, cy - 13), (cx + 9, cy - 10), (cx, cy - 7)], fill=WHITE)
    d.line([(cx - 14, cy + 14), (cx + 14, cy + 14)], fill=WHITE, width=2)
    d.line([(cx - 8, cy + 17), (cx + 8, cy + 17)], fill=WHITE, width=2)


def icon_leaf(d, cx, cy):
    pts = []
    for i in range(11):
        t = i / 10.0
        pts.append((cx - 12 + 24 * t, cy + 10 - 22 * t - 7 * math.sin(math.pi * t)))
    for i in range(11):
        t = i / 10.0
        pts.append((cx + 12 - 24 * t, cy - 12 + 22 * t + 7 * math.sin(math.pi * t)))
    d.polygon(pts, fill=WHITE)
    d.line([(cx - 12, cy + 10), (cx - 17, cy + 15)], fill=WHITE, width=2)
    d.line([(cx - 12, cy + 10), (cx + 12, cy - 12)], fill=WHITE, width=1)


def icon_bars(d, cx, cy):
    d.rectangle([cx - 13, cy + 2, cx - 8, cy + 11], fill=WHITE)
    d.rectangle([cx - 4, cy - 4, cx + 1, cy + 11], fill=WHITE)
    d.rectangle([cx + 5, cy - 10, cx + 10, cy + 11], fill=WHITE)
    d.line([(cx - 15, cy + 13), (cx + 15, cy + 13)], fill=WHITE, width=2)


def icon_rocket(d, cx, cy, circle_color):
    d.polygon([(cx, cy - 14), (cx + 6, cy - 5), (cx + 5, cy + 7),
               (cx - 5, cy + 7), (cx - 6, cy - 5)], fill=WHITE)
    d.polygon([(cx - 5, cy + 2), (cx - 5, cy + 7), (cx - 11, cy + 10)], fill=WHITE)
    d.polygon([(cx + 5, cy + 2), (cx + 5, cy + 7), (cx + 11, cy + 10)], fill=WHITE)
    d.polygon([(cx - 3, cy + 8), (cx + 3, cy + 8), (cx, cy + 15)], fill=WHITE)
    d.ellipse([cx - 3, cy - 6, cx + 3, cy], fill=circle_color)


def icon_cross(d, cx, cy):
    d.rectangle([cx - 3, cy - 12, cx + 3, cy + 12], fill=WHITE)
    d.rectangle([cx - 12, cy - 3, cx + 12, cy + 3], fill=WHITE)


ICONS = {
    "scales": lambda d, cx, cy, c: icon_scales(d, cx, cy),
    "ship": lambda d, cx, cy, c: icon_ship(d, cx, cy),
    "leaf": lambda d, cx, cy, c: icon_leaf(d, cx, cy),
    "bars": lambda d, cx, cy, c: icon_bars(d, cx, cy),
    "rocket": lambda d, cx, cy, c: icon_rocket(d, cx, cy, c),
    "cross": lambda d, cx, cy, c: icon_cross(d, cx, cy),
}


def draw_chart(d, x0, y0, x1, y1):
    """NVDA mini chart: Fri close 125.53, Mon close 165.05, Tue premarket ~160."""
    # panel
    d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=(238, 242, 247),
                        outline=(213, 220, 229), width=1)
    # value -> y (120 at bottom, 170 at top of plot area)
    px0, px1 = x0 + 16, x1 - 16
    py_top, py_bot = y0 + 14, y1 - 24
    def vy(v):
        return py_bot - (v - 120) / 50.0 * (py_bot - py_top)
    pts = [(px0 + 10, vy(125.53)), ((px0 + px1) // 2, vy(165.05)),
           (px1 - 10, vy(160.1))]
    for gy in (125, 150, 165):
        d.line([(px0, vy(gy)), (px1, vy(gy))], fill=(213, 220, 229), width=1)
    d.line(pts, fill=GREEN, width=3)
    for (x, y) in pts:
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=GREEN)
    tag_fnt = font("DejaVuSans-Bold.ttf", 12)
    d.text((pts[0][0] - 8, pts[0][1] + 8), "$125 Fri", font=tag_fnt, fill=TITLE_C)
    d.text((pts[1][0] - 22, pts[1][1] - 20), "$165 Mon", font=tag_fnt, fill=GREEN)
    d.text((pts[2][0] - 108, pts[2][1] + 10), "\u22123% premarket", font=tag_fnt,
           fill=(192, 57, 43))


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    title_fnt = font("DejaVuSans-Bold.ttf", 40)
    tw = title_fnt.getlength(TITLE)
    d.text(((W - tw) / 2, 16), TITLE, font=title_fnt, fill=NAVY)

    # ---- date band ----
    d.rectangle([0, 64, W, 92], fill=RED_BAND)
    date_fnt = font("DejaVuSans-Bold.ttf", 19)
    dw = date_fnt.getlength(DATE_BAND)
    d.text(((W - dw) / 2, 68), DATE_BAND, font=date_fnt, fill=WHITE)

    # ---- lead card: Nvidia ----
    lx0, ly0, lx1, ly1 = 28, 100, 996, 240
    d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=14, fill=CARD,
                        outline=CARD_EDGE, width=1)
    k_fnt = font("DejaVuSans-Bold.ttf", 16)
    d.text((lx0 + 20, ly0 + 12), LEAD_KICKER, font=k_fnt, fill=(192, 57, 43))
    h_fnt = font("DejaVuSans-Bold.ttf", 30)
    d.text((lx0 + 20, ly0 + 38), LEAD_HEADLINE, font=h_fnt, fill=TITLE_C)
    b_fnt, b_lines = fit_text(LEAD_BODY, "DejaVuSans.ttf", 16, 15, 640, 3)
    y = ly0 + 74
    for line in b_lines:
        d.text((lx0 + 20, y), line, font=b_fnt, fill=BODY_C)
        y += b_fnt.size + 5
    print(f"lead: body {len(b_lines)} lines @ {b_fnt.size}px, bottom y={y}")
    draw_chart(d, 712, ly0 + 12, lx1 - 16, ly1 - 12)

    # ---- six cards: 2 cols x 3 rows ----
    margin, gap = 28, 14
    cw = (W - 2 * margin - gap) // 2          # 477
    ch = 196
    top0 = 252
    pad = 20
    text_w = cw - 2 * pad                       # 437

    for i, (label, color, icon, headline, body) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = margin + col * (cw + gap)
        y0 = top0 + row * (ch + gap)
        x1, y1 = x0 + cw, y0 + ch
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=CARD,
                            outline=CARD_EDGE, width=1)

        lab_fnt = font("DejaVuSans-Bold.ttf", 18)
        d.text((x0 + pad, y0 + 14), label, font=lab_fnt, fill=color)
        icx, icy = x1 - pad - 19, y0 + 14 + 19
        d.ellipse([icx - 19, icy - 19, icx + 19, icy + 19], fill=color)
        ICONS[icon](d, icx, icy, color)

        h_fnt = font("DejaVuSans-Bold.ttf", 23)
        h_lines = wrap_text(headline, h_fnt, text_w)
        assert len(h_lines) <= 2, f"{label}: headline needs {len(h_lines)} lines"
        y = y0 + 50
        for line in h_lines:
            d.text((x0 + pad, y), line, font=h_fnt, fill=TITLE_C)
            y += h_fnt.size + 5

        b_fnt, b_lines = fit_text(body, "DejaVuSans.ttf", 17, 15, text_w, 3)
        assert len(b_lines) <= 3, f"{label}: body needs {len(b_lines)} lines"
        y = y0 + 116
        for line in b_lines:
            d.text((x0 + pad, y), line, font=b_fnt, fill=BODY_C)
            y += b_fnt.size + 4
        print(f"{label}: headline {len(h_lines)} lines, body {len(b_lines)} "
              f"lines @ {b_fnt.size}px, body bottom y={y} (card bottom {y1})")

    # ---- IN BRIEF strip ----
    by = 882
    brief_lab = font("DejaVuSans-Bold.ttf", 16)
    d.text((margin, by), "IN BRIEF", font=brief_lab, fill=(192, 57, 43))
    br_fnt = font("DejaVuSans.ttf", 15)
    for i, text in enumerate(BRIEFS):
        col, row = i % 2, i // 2
        x = margin + col * (cw + gap)
        yy = by + 24 + row * 22
        line = "\u25aa " + text
        assert br_fnt.getlength(line) <= cw, f"brief too long: {text}"
        d.text((x, yy), line, font=br_fnt, fill=BODY_C)
    print(f"briefs bottom y={by + 24 + 2 * 22 + 15}")

    # ---- DATE CHECK footnote ----
    dc_fnt = font("DejaVuSans.ttf", 13)
    for j, line in enumerate((DATE_CHECK_1, DATE_CHECK_2)):
        lw = dc_fnt.getlength(line)
        d.text(((W - lw) / 2, 968 + j * 18), line, font=dc_fnt, fill=GRAY)

    out = os.path.join(OUT_DIR, "entry-v2.png")
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"saved {out}: {img.size[0]}x{img.size[1]}, {size} bytes "
          f"({'OK <=1MiB' if size <= 1048576 else 'TOO BIG'})")


if __name__ == "__main__":
    main()
