#!/usr/bin/env python3
"""
Google Sheet -> Classement SOLO

Colonnes :
Pseudo | Games | Win | Loose | Kill | Dead | Assist | KDA
"""

import os
from pathlib import Path
from typing import Tuple, Optional, List

import gspread
from PIL import Image, ImageDraw, ImageFont, ImageColor

# =================== CONFIG ===================

WORKSHEET_NAME = os.environ.get("WORKSHEET_NAME", "Classement")
BASE_IMAGE_PATH = os.environ.get("BASE_IMAGE_PATH", "bloc-solo.png")
OUTPUT_PATH     = os.environ.get("OUTPUT_PATH", "../bloc-solo.png")

FONT_PATH  = os.environ.get("FONT_PATH", "Oswald-Medium.ttf")
TEXT_COLOR = os.environ.get("TEXT_COLOR", "#ffffff")
SHADOW     = os.environ.get("SHADOW", "1") == "1"

SHEET_URL_DEFAULT = "https://docs.google.com/spreadsheets/d/1yp8fKsWip750zB2DWw0af0MfLSTEOYa_uQPZfsqyWEY"

ROW_COUNT = int(os.environ.get("ROW_COUNT", "30"))

# ----- Colonnes en % largeur image -----

PSEUDO_L  = 0.07
PSEUDO_R  = 0.35

GAMES_L = 0.30
GAMES_R = 0.53

WIN_L   = 0.365
WIN_R   = 0.58

LOOSE_L = 0.43
LOOSE_R = 0.63

KILL_L  = 0.625
KILL_R  = 0.72

DEAD_L  = 0.705
DEAD_R  = 0.80

ASSIST_L = 0.805
ASSIST_R = 0.88

KDA_L = 0.905
KDA_R = 0.97

# ----- Vertical -----

PRE_MARGIN_TOP_PX = 118
LINE_THICKNESS_PX = 3
BAND_HEIGHT_PX    = 85.2
MARGIN_TOP_PX     = 26
MARGIN_BOTTOM_PX  = 26
START_Y_PX        = PRE_MARGIN_TOP_PX + LINE_THICKNESS_PX

FONT_SIZE_MAX = 42
FONT_SIZE_MIN = 30

SERVICE_ACCOUNT_FILE = (
    os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    or str(Path(__file__).with_name("service-account.json"))
)

# =================================================


def parse_color(v):
    try:
        return ImageColor.getrgb(v)
    except:
        return (255,255,255)


def load_font(size):
    if Path(FONT_PATH).exists():
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.truetype("arial.ttf", size)


def fit_text(draw, text, box):
    x0,y0,x1,y1 = box
    max_w = x1-x0-4
    max_h = y1-y0-4
    size = FONT_SIZE_MAX
    while size >= FONT_SIZE_MIN:
        font = load_font(size)
        w,h = draw.textbbox((0,0), text, font=font)[2:]
        if w <= max_w and h <= max_h:
            return font
        size -= 1
    return load_font(FONT_SIZE_MIN)


def draw_in_box_center(draw, text, box, fill):
    x0,y0,x1,y1 = box
    font = fit_text(draw, text, box)
    w,h = draw.textbbox((0,0), text, font=font)[2:]
    x = (x0+x1)/2 - w/2
    y = (y0+y1)/2 - h/2
    draw.text((x,y), text, font=font, fill=fill)


def draw_in_box_left(draw, text, box, fill):
    x0,y0,x1,y1 = box
    font = fit_text(draw, text, box)
    w,h = draw.textbbox((0,0), text, font=font)[2:]
    x = x0
    y = (y0+y1)/2 - h/2
    draw.text((x,y), text, font=font, fill=fill)


def pct_to_px(p, total):
    return int(round(p * total))


def open_worksheet(sheet_url):
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open_by_url(sheet_url)
    return sh.worksheet(WORKSHEET_NAME)


def get_rows(sheet_url, row_count):
    ws = open_worksheet(sheet_url)
    rows = ws.get_all_records(
        head=1, expected_headers=["Classement Solo", "Pseudo", "Nombre Games", "Nombre Win", "Nombre Loose", "Nombre Kill", "Nombre Mort","Nombre Assist"],
    )
    rows = [r for r in rows if str(r.get("Classement Solo", "")).strip() != ""]
    try:
        rows.sort(key=lambda r: int(r.get("Classement Solo", 999999)))
    except Exception:
        pass
    return rows[:row_count]


def calculate_kda(kill, dead, assist):
    try:
        kill = float(kill)
        dead = float(dead)
        assist = float(assist)
        if dead == 0:
            return round(kill + assist, 2)
        return round((kill + assist) / dead, 2)
    except:
        return "0"


def main():

    sheet_url = os.environ.get("SHEET_URL") or SHEET_URL_DEFAULT

    im = Image.open(BASE_IMAGE_PATH).convert("RGBA")
    W,H = im.size
    draw = ImageDraw.Draw(im)
    color = parse_color(TEXT_COLOR)

    rows = get_rows(sheet_url, ROW_COUNT)

    for i,row in enumerate(rows):

        band_top = START_Y_PX + i * (BAND_HEIGHT_PX + LINE_THICKNESS_PX)

        y0 = band_top + MARGIN_TOP_PX
        y1 = band_top + BAND_HEIGHT_PX - MARGIN_BOTTOM_PX

        def col_box(l, r):
            return (
                pct_to_px(l, W),
                y0,
                pct_to_px(r, W),
                y1
            )

        pseudo = str(row.get("Pseudo",""))
        games  = str(row.get("Nombre Games",""))
        win    = str(row.get("Nombre Win",""))
        loose  = str(row.get("Nombre Loose",""))
        kill   = str(row.get("Nombre Kill",""))
        dead   = str(row.get("Nombre Mort",""))
        assist = str(row.get("Nombre Assist",""))
        kda    = str(calculate_kda(kill,dead,assist))

        draw_in_box_left(draw, pseudo, col_box(PSEUDO_L,PSEUDO_R), color)
        draw_in_box_center(draw, games,  col_box(GAMES_L,GAMES_R), color)
        draw_in_box_center(draw, win,    col_box(WIN_L,WIN_R), color)
        draw_in_box_center(draw, loose,  col_box(LOOSE_L,LOOSE_R), color)
        draw_in_box_center(draw, kill,   col_box(KILL_L,KILL_R), color)
        draw_in_box_center(draw, dead,   col_box(DEAD_L,DEAD_R), color)
        draw_in_box_center(draw, assist, col_box(ASSIST_L,ASSIST_R), color)
        draw_in_box_center(draw, kda,    col_box(KDA_L,KDA_R), color)

    im.convert("RGB").save(OUTPUT_PATH)
    print("✅ Classement SOLO généré :", OUTPUT_PATH)


if __name__ == "__main__":
    main()
