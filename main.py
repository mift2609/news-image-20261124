#!/usr/bin/env python3
"""Render one 1024x1024 PNG summing up 24 November 2026's world news.

Deterministic: fixed layout, fixed fonts, no timestamps, no randomness.
Stdlib + Pillow only. Output: /output/entry.png (and entry.png next to main.py).
"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT_MAIN = "/output/entry.png"
OUT_LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# Palette
BG_TOP = (13, 17, 23)
BG_BOT = (24, 30, 40)
INK = (240, 238, 232)
MUTED = (168, 175, 186)
RULE = (62, 70, 84)
RED = (214, 48, 49)
CHIP_BG = (31, 38, 50)
CHIP_TEXT = (147, 197, 253)
NUM_TEXT = (214, 48, 49)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

STORIES = [
    {
        "tag": "CLIMATE",
        "headline": "COP31 ends with no fossil-fuel deal",
        "summary": "Climate talks collapse in Antalya: negotiators leave with no "
                   "agreement on stronger fossil-fuel phase-out language.",
    },
    {
        "tag": "INDONESIA",
        "headline": "Banten factory fire: death toll at least 24",
        "summary": "Rescue continues after the candy-factory fire in Cikande; "
                   "around 30 people are still missing.",
    },
    {
        "tag": "WAR IN UKRAINE",
        "headline": "Russian drone strike hits Kyiv region",
        "summary": "President Zelenskyy reports a Russian drone strike in the "
                   "Kyiv region leaving several people missing.",
    },
    {
        "tag": "PORTUGAL",
        "headline": "Thousands march in Lisbon against rising living costs",
        "summary": "Thousands take to the streets of Lisbon to protest the "
                   "cost of living.",
    },
    {
        "tag": "FORMULA 1",
        "headline": "Verstappen wins the Las Vegas Grand Prix",
        "summary": "Max Verstappen takes victory in the 2026 Las Vegas Grand Prix.",
    },
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap returning a list of lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main():
    img = Image.new("RGB", (W, H))
    # Vertical gradient background.
    top = Image.new("RGB", (W, H), BG_TOP)
    bot = Image.new("RGB", (W, H), BG_BOT)
    mask = Image.new("L", (1, H))
    mask.putdata([int(255 * y / (H - 1)) for y in range(H)])
    img = Image.composite(bot, top, mask.resize((W, H)))
    d = ImageDraw.Draw(img)

    margin = 56
    x0, x1 = margin, W - margin

    # ---- Header ----
    y = 36
    f_kicker = font(SANS_BOLD, 24)
    f_title = font(SERIF_BOLD, 54)
    f_sub = font(SANS, 24)

    d.text((x0, y), "THE WORLD IN ONE DAY", font=f_kicker, fill=RED)
    y += 36
    title_lines = wrap(d, "24 NOVEMBER 2026", f_title, x1 - x0)
    for line in title_lines:
        d.text((x0, y), line, font=f_title, fill=INK)
        y += 64
    y += 4
    d.text((x0, y), "Five stories that defined the day.",
           font=f_sub, fill=MUTED)
    y += 40
    d.rectangle([x0, y, x1, y + 3], fill=RED)
    y += 18

    # ---- Story blocks (height measured per block so nothing overlaps) ----
    f_num = font(SERIF_BOLD, 36)
    f_tag = font(SANS_BOLD, 20)
    f_head = font(SANS_BOLD, 30)
    f_sum = font(SANS, 23)
    HEAD_LH, SUM_LH = 36, 29
    CHIP_H, GAP = 32, 8

    def block_height(s):
        head = wrap(d, s["headline"], f_head, x1 - (x0 + 78))[:2]
        summ = wrap(d, s["summary"], f_sum, x1 - (x0 + 78))[:2]
        return 6 + CHIP_H + 6 + len(head) * HEAD_LH + 4 + len(summ) * SUM_LH + 6, head, summ

    by = y
    for i, s in enumerate(STORIES):
        bh, head_lines, sum_lines = block_height(s)
        if i:
            d.line([x0, by - GAP // 2, x1, by - GAP // 2], fill=RULE, width=1)
        # Big number
        d.text((x0, by + 4), f"{i + 1:02d}", font=f_num, fill=NUM_TEXT)
        tx = x0 + 78
        # Category chip
        tag = s["tag"]
        tw = d.textlength(tag, font=f_tag)
        chip_w = int(tw) + 26
        d.rounded_rectangle([tx, by + 6, tx + chip_w, by + 6 + CHIP_H],
                            radius=6, fill=CHIP_BG)
        d.text((tx + 13, by + 10), tag, font=f_tag, fill=CHIP_TEXT)
        # Headline
        hy = by + 6 + CHIP_H + 6
        for line in head_lines:
            d.text((tx, hy), line, font=f_head, fill=INK)
            hy += HEAD_LH
        # Summary
        hy += 4
        for line in sum_lines:
            d.text((tx, hy), line, font=f_sum, fill=MUTED)
            hy += SUM_LH
        by += bh + GAP

    # ---- Footer ----
    fy = H - 56
    d.line([x0, fy - 14, x1, fy - 14], fill=RULE, width=1)
    f_foot = font(SANS_BOLD, 22)
    d.text((x0, fy), "24 NOVEMBER 2026", font=f_foot, fill=MUTED)
    right = "FIVE STORIES \u00b7 ONE DAY"
    rw = d.textlength(right, font=f_foot)
    d.text((x1 - rw, fy), right, font=f_foot, fill=MUTED)

    os.makedirs("/output", exist_ok=True)
    img.save(OUT_MAIN, format="PNG")
    img.save(OUT_LOCAL, format="PNG")
    print(f"wrote {OUT_MAIN} and {OUT_LOCAL}")


if __name__ == "__main__":
    main()
