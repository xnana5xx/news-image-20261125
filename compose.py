#!/usr/bin/env python3
"""Compose the 25 November 2026 front page from the hero illustration.

Reads assets/<hero webp>, crops it into a banner, and lays out a newspaper
front page with PIL: masthead, date, four dated stories. Writes
assets/entry.png (1024x1024, under 1 MiB). Re-run to rebuild identically.
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
HERO = os.path.join(
    ASSETS,
    "media-generation-news-20261125-hero-0-12874363-5885-4201-9a5e-28565933c9a0.webp",
)
OUT = os.path.join(ASSETS, "entry.png")

W, H = 1024, 1024
PAPER = (244, 239, 228)
INK = (24, 24, 26)
RED = (178, 34, 34)
TEAL = (18, 90, 96)
MUTED = (96, 92, 84)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width_px):
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for word in words:
            trial = (cur + " " + word).strip()
            if draw.textlength(trial, font=fnt) <= width_px or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def draw_block(draw, x, y, w, kicker, headline, body, hfont, bfont):
    draw.text((x, y), kicker, font=font(SANS, 20), fill=RED)
    y += 30
    for line in wrap(draw, headline, hfont, w):
        draw.text((x, y), line, font=hfont, fill=INK)
        y += 36
    y += 4
    for line in wrap(draw, body, bfont, w):
        draw.text((x, y), line, font=bfont, fill=(52, 50, 46))
        y += 25
    return y


def main():
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)

    # Masthead
    draw.text((512, 28), "THE WORLD IN ONE PAGE",
              font=font(SERIF, 64), fill=INK, anchor="ma")
    draw.text((512, 104), "WEDNESDAY 25 NOVEMBER 2026",
              font=font(SANS, 30), fill=RED, anchor="ma")
    draw.line([(48, 152), (976, 152)], fill=INK, width=4)
    draw.line([(48, 160), (976, 160)], fill=INK, width=1)

    # Hero banner
    hero = Image.open(HERO).convert("RGB")
    hw, hh = hero.size
    target_ratio = 928 / 300
    if hw / hh > target_ratio:
        nw = int(hh * target_ratio)
        hero = hero.crop(((hw - nw) // 2, 0, (hw + nw) // 2, hh))
    else:
        nh = int(hw / target_ratio)
        hero = hero.crop((0, (hh - nh) // 2, hw, (hh + nh) // 2))
    hero = hero.resize((928, 300), Image.LANCZOS)
    page.paste(hero, (48, 176))
    draw.rectangle([48, 176, 976, 476], outline=INK, width=3)
    draw.text((512, 490), "Ships struck, a tower hit, a climate summit fails",
              font=font(SERIF_REG, 26), fill=MUTED, anchor="ma")

    # Four stories, 2 x 2
    hfont = font(SERIF, 30)
    bfont = font(SANS_REG, 21)
    col_w = 436
    draw.line([(48, 540), (976, 540)], fill=INK, width=2)
    y1 = 556
    draw_block(draw, 48, y1, col_w, "UKRAINE  •  RUSSIA",
               "Ukraine hits Russian ships in two seas",
               "Zelenskiy confirms drone strikes on a Russian cargo ship "
               "in the Gulf of Finland and a warship off Libya. Moscow "
               "calls the attacks \u201cterrorism\u201d.",
               hfont, bfont)
    draw_block(draw, 536, y1, col_w, "MIDDLE EAST",
               "Houthis hit Riyadh tower again",
               "A strike on the PIF Tower, the capital\u2019s tallest, "
               "wounds 11 \u2014 the second attack on the skyscraper in "
               "a week. Riyadh condemns it as terrorism.",
               hfont, bfont)
    draw.line([(512, 556), (512, 772)], fill=MUTED, width=1)
    draw.line([(48, 786), (976, 786)], fill=MUTED, width=1)
    y2 = 800
    draw_block(draw, 48, y2, col_w, "CLIMATE",
               "COP31 collapses with no deal",
               "The UN climate summit in Antalya ends without an "
               "agreement as oil and gas producers block language on "
               "phasing out fossil fuels.",
               hfont, bfont)
    draw_block(draw, 536, y2, col_w, "CHINA",
               "Top official probed; Huawei convicted",
               "Beijing opens a corruption inquiry into Politburo member "
               "Chen Jining. A US jury convicts Huawei of conspiring to "
               "steal trade secrets.",
               hfont, bfont)

    page.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT} ({W}x{H}, {size} bytes)")
    assert size <= 1_048_576, "entry.png over 1 MiB"


if __name__ == "__main__":
    main()
