#!/usr/bin/env python3
"""Build 1024x1024 PNG entry for make.fun bounty news-image-20261124.

Layout: warm paper background, header, 2x3 white rounded cards.
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

TITLE = "THE WORLD IN ONE PICTURE"
SUBTITLE = "Six stories that mattered most \u2014 from courtrooms to climate to orbit."
FOOTER = "Every story above happened on the same day."

# (label, color, icon, headline, body)
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


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- header ----
    title_fnt = font("DejaVuSans-Bold.ttf", 44)
    tw = title_fnt.getlength(TITLE)
    d.text(((W - tw) / 2, 26), TITLE, font=title_fnt, fill=NAVY)

    sub_fnt = font("DejaVuSans.ttf", 21)
    sw = sub_fnt.getlength(SUBTITLE)
    d.text(((W - sw) / 2, 88), SUBTITLE, font=sub_fnt, fill=GRAY)

    # ---- cards: 2 cols x 3 rows ----
    margin, gap = 28, 16
    cw = (W - 2 * margin - gap) // 2          # 476
    ch = 268
    top0 = 132
    pad = 20
    text_w = cw - 2 * pad                       # 436

    for i, (label, color, icon, headline, body) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = margin + col * (cw + gap)
        y0 = top0 + row * (ch + gap)
        x1, y1 = x0 + cw, y0 + ch
        d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=CARD,
                            outline=CARD_EDGE, width=1)

        # label (top-left) + icon circle (top-right)
        lab_fnt = font("DejaVuSans-Bold.ttf", 20)
        d.text((x0 + pad, y0 + 18), label, font=lab_fnt, fill=color)
        icx, icy = x1 - pad - 22, y0 + 18 + 22
        d.ellipse([icx - 22, icy - 22, icx + 22, icy + 22], fill=color)
        ICONS[icon](d, icx, icy, color)

        # headline, bold, uniform 25px so all six cards match, max 2 lines
        h_fnt = font("DejaVuSans-Bold.ttf", 25)
        h_lines = wrap_text(headline, h_fnt, text_w)
        assert len(h_lines) <= 2, f"{label}: headline needs {len(h_lines)} lines"
        y = y0 + 66
        for line in h_lines:
            d.text((x0 + pad, y), line, font=h_fnt, fill=TITLE_C)
            y += h_fnt.size + 6

        # body, max 4 lines (shrink 20 -> 18 if needed)
        b_fnt, b_lines = fit_text(body, "DejaVuSans.ttf", 20, 18, text_w, 4)
        y = y0 + 146
        for line in b_lines:
            d.text((x0 + pad, y), line, font=b_fnt, fill=BODY_C)
            y += b_fnt.size + 5

        print(f"{label}: headline {len(h_lines)} lines @ {h_fnt.size}px, "
              f"body {len(b_lines)} lines @ {b_fnt.size}px, "
              f"body bottom y={y - (b_fnt.size + 5) + b_fnt.size} (card bottom {y1})")

    # ---- footer ----
    foot_fnt = font("DejaVuSans.ttf", 18)
    fw = foot_fnt.getlength(FOOTER)
    d.text(((W - fw) / 2, 978), FOOTER, font=foot_fnt, fill=GRAY)

    out = os.path.join(OUT_DIR, "entry.png")
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"saved {out}: {img.size[0]}x{img.size[1]}, {size} bytes "
          f"({'OK <=1MiB' if size <= 1048576 else 'TOO BIG'})")


if __name__ == "__main__":
    main()
