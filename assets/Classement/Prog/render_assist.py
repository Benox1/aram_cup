#!/usr/bin/env python3
"""
Google Sheet -> Classement Assist 5 joueurs

Colonnes dans Google Sheet :
Assist Classement | Pseudo Assist | Nb Assist
"""

import os
from pathlib import Path
import gspread
from PIL import Image, ImageDraw, ImageFont, ImageColor

# =================== CONFIG ===================

WORKSHEET_NAME = os.environ.get("WORKSHEET_NAME", "Classement")
BASE_IMAGE_PATH = os.environ.get("BASE_IMAGE_PATH", "top-assist.png")
OUTPUT_PATH     = os.environ.get("OUTPUT_PATH", "../top-assist.png")

FONT_PATH  = os.environ.get("FONT_PATH", "Oswald-Medium.ttf")
TEXT_COLOR = os.environ.get("TEXT_COLOR", "#ffffff")

ROW_COUNT = 5  # 5 lignes seulement

# Colonnes en % largeur image
PP_L = 0.35
PP_R = 0.45

PSEUDO_L = 0.47
PSEUDO_R = 0.85

ASSIST_L = 0.82
ASSIST_R = 0.95

# Vertical
PRE_MARGIN_TOP_PX = 135
LINE_THICKNESS_PX = 1
BAND_HEIGHT_PX    = 80
MARGIN_TOP_PX     = 12
MARGIN_BOTTOM_PX  = 12
START_Y_PX        = PRE_MARGIN_TOP_PX + LINE_THICKNESS_PX
SPACE_BETWEEN_LINES = 0  # ajuste ici pour plus d'espace entre les lignes

FONT_SIZE_MAX = 20
FONT_SIZE_MIN = 20

SERVICE_ACCOUNT_FILE = (
    os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    or str(Path(__file__).with_name("service-account.json"))
)

# =================== MAPPING PP ===================
# Mapping pseudo -> fichier PP (.png)
PP_FILES = {
    "Aikyuuu": "pp/aikyuuu.png",
    "Akiraa": "pp/akiraa.png",
    "alexpotato1234": "pp/alex.png",
    "Alpha_Scr33m": "pp/alpha.png",
    "Celestial": "pp/celestial.png",
    "DanMartin": "pp/danmartin.png",
    "Dozemon": "pp/dozemon.png",
    "durity42": "pp/durity.png",
    "Genda": "pp/genda.png",
    "Gourmandise_": "pp/gourmandise.png",
    "Jerpheonix": "pp/jerpheonix.png",
    "k0p1": "pp/kop1.png",
    "Kanade": "pp/kanade.png",
    "Kira": "pp/kira.png",
    "Liloohart": "pp/liloo.png",
    "MatisM": "pp/matism.png",
    "NovaMat": "pp/nova.png",
    "OUZGOULOU": "pp/ouzgoulou.png",
    "PandArt": "pp/pandart.png",
    "Pigi": "pp/pigi.png",
    "PinkyLaTerreur": "pp/pinky.png",
    "Poums": "pp/poums.png",
    "SeeaX_Tw": "pp/seax.png",
    "Snoopi": "pp/snoopi.png",
    "Strange__": "pp/strange.png",
    "Sunrise": "pp/sunrise.png",
    "UnBout2Bois": "pp/b2b.png",
    "UneBiscotteMolle": "pp/biscotte.png",
    "Xiuren15N": "pp/xiuren.png",
    "y": "pp/y.png",
}

# =================== FONCTIONS ===================

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
        head=1, expected_headers=["Assist Classement", "Pseudo Assist", "Nb Assist"],
    )
    rows = [r for r in rows if str(r.get("Assist Classement", "")).strip() != ""]
    try:
        rows.sort(key=lambda r: int(r.get("Assist Classement", 999999)))
    except Exception:
        pass
    return rows[:row_count]

# =================== MAIN ===================

def main():
    sheet_url = os.environ.get("SHEET_URL") or "https://docs.google.com/spreadsheets/d/1yp8fKsWip750zB2DWw0af0MfLSTEOYa_uQPZfsqyWEY"

    im = Image.open(BASE_IMAGE_PATH).convert("RGBA")
    W,H = im.size
    draw = ImageDraw.Draw(im)
    color = parse_color(TEXT_COLOR)

    rows = get_rows(sheet_url, ROW_COUNT)

    for i,row in enumerate(rows):
        band_top = START_Y_PX + i * (BAND_HEIGHT_PX + SPACE_BETWEEN_LINES -2.8)
        y0 = band_top + MARGIN_TOP_PX
        y1 = band_top + BAND_HEIGHT_PX - MARGIN_BOTTOM_PX

        def col_box(l,r):
            return (pct_to_px(l,W), y0, pct_to_px(r,W), y1)

        pseudo = str(row.get("Pseudo Assist"))
        assists  = str(row.get("Nb Assist",""))

        # ---- PP rond ----
        box_left, box_top, box_right, box_bottom = col_box(PP_L,PP_R)
        circle_diameter = int(box_bottom - box_top + 3)
        circle_x0 = int(box_left - 13)
        circle_y0 = int(box_top + 2)  # ajuste si tu veux remonter
        circle_x1 = circle_x0 + circle_diameter
        circle_y1 = circle_y0 + circle_diameter

        pp_file = PP_FILES.get(pseudo)
        if pp_file and Path(pp_file).exists():
            pp_im = Image.open(pp_file).convert("RGBA")
            pp_im = pp_im.resize((circle_diameter, circle_diameter))
            mask = Image.new("L", (circle_diameter, circle_diameter), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0,0,circle_diameter,circle_diameter), fill=255)
            im.paste(pp_im, (circle_x0,circle_y0), mask)

        # ---- pseudo à droite du rond ----
        pseudo_box = (circle_x1 + 10, box_top, pct_to_px(PSEUDO_R,W), y1)
        draw_in_box_left(draw, pseudo, pseudo_box, color)

        # ---- assists ----
        draw_in_box_center(draw, assists, col_box(ASSIST_L,ASSIST_R), color)

    im.convert("RGB").save(OUTPUT_PATH)
    print("✅ Classement Assist généré :", OUTPUT_PATH)

if __name__ == "__main__":
    main()
