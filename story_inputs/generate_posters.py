#!/usr/bin/env python3
"""Generate 10 book poster images for story types."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random
import os

FONTS_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
OUTPUT_DIR = "/home/claude/posters"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1200, 1800  # Poster dimensions

def load_font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS_DIR, name), size)
    except:
        return ImageFont.load_default()

def draw_gradient(draw, w, h, color_top, color_bottom):
    for y in range(h):
        t = y / h
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

def draw_radial_gradient(img, cx, cy, radius, color_center, color_edge):
    draw = ImageDraw.Draw(img)
    for r in range(int(radius), 0, -1):
        t = r / radius
        c = tuple(int(color_center[i] + (color_edge[i] - color_center[i]) * t) for i in range(3))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

def draw_stars(draw, n, w, h, color=(255, 255, 255)):
    random.seed(42)
    for _ in range(n):
        x, y = random.randint(0, w), random.randint(0, h)
        s = random.randint(1, 3)
        a = random.randint(100, 255)
        c = (color[0], color[1], color[2], a)
        draw.ellipse([x-s, y-s, x+s, y+s], fill=c[:3])

def draw_text_centered(draw, text, y, font, fill=(255,255,255), w=W):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, y), text, font=font, fill=fill)

def draw_text_centered_shadow(draw, text, y, font, fill=(255,255,255), shadow=(0,0,0), w=W):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (w - tw) // 2
    # Shadow
    draw.text((x+3, y+3), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

# =============================================================================
# POSTER 1: The Reluctant Hero - Fantasy
# =============================================================================
def poster_1():
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    # Deep forest green to dark background
    draw_gradient(draw, W, H, (10, 40, 25), (5, 10, 15))
    
    # Mystical forest trees in background
    random.seed(101)
    for i in range(30):
        x = random.randint(0, W)
        trunk_w = random.randint(8, 25)
        trunk_h = random.randint(400, 900)
        y_base = H - random.randint(0, 200)
        green = random.randint(15, 40)
        draw.rectangle([x, y_base - trunk_h, x + trunk_w, y_base], fill=(10, green, 10))
        # Canopy
        for j in range(3):
            cy = y_base - trunk_h - j * 30
            r = random.randint(30, 80)
            draw.ellipse([x + trunk_w//2 - r, cy - r, x + trunk_w//2 + r, cy + r], fill=(10, green + 10, 15))
    
    # Magical glow behind character
    for r in range(250, 0, -2):
        alpha = int(40 * (1 - r/250))
        c = (80 + alpha, 180 + min(alpha, 75), 80 + alpha)
        draw.ellipse([W//2 - r, 700 - r, W//2 + r, 700 + r], fill=c)
    
    # Character silhouette - hooded figure with staff
    cx, cy = W//2, 650
    # Body
    draw.polygon([(cx-80, cy+50), (cx+80, cy+50), (cx+120, cy+450), (cx-120, cy+450)], fill=(5, 5, 10))
    # Head/hood
    draw.ellipse([cx-55, cy-70, cx+55, cy+40], fill=(5, 5, 10))
    draw.polygon([(cx-60, cy-20), (cx, cy-90), (cx+60, cy-20)], fill=(5, 5, 10))
    # Staff
    draw.line([(cx+90, cy-100), (cx+70, cy+450)], fill=(60, 40, 20), width=8)
    # Staff glow
    for r in range(40, 0, -1):
        a = int(150 * (1 - r/40))
        draw.ellipse([cx+88-r, cy-102-r, cx+88+r, cy-102+r], fill=(100+a, 220, 100+a))
    
    # Floating magical particles
    random.seed(55)
    for _ in range(60):
        px = random.randint(100, W-100)
        py = random.randint(300, 1200)
        ps = random.randint(2, 6)
        draw.ellipse([px-ps, py-ps, px+ps, py+ps], fill=(100, 255, 150, 200))
    
    # Title
    title_font = load_font("Boldonse-Regular.ttf", 90)
    sub_font = load_font("CrimsonPro-Italic.ttf", 36)
    tag_font = load_font("CrimsonPro-Regular.ttf", 28)
    genre_font = load_font("InstrumentSans-Bold.ttf", 22)
    
    draw_text_centered_shadow(draw, "THE RELUCTANT", 80, title_font, fill=(180, 255, 180))
    draw_text_centered_shadow(draw, "HERO", 180, title_font, fill=(180, 255, 180))
    
    draw_text_centered(draw, "An ordinary soul. An extraordinary destiny.", 1300, sub_font, fill=(200, 255, 200))
    
    # Genre tag
    draw.rounded_rectangle([W//2 - 80, 1400, W//2 + 80, 1435], radius=12, fill=(30, 80, 40))
    draw_text_centered(draw, "FANTASY", 1405, genre_font, fill=(180, 255, 180))
    
    # Bottom text
    lines = wrap_text("A humble farmer discovers ancient magic and must journey across treacherous lands to save a kingdom from darkness.", tag_font, W - 200, draw)
    y = 1500
    for line in lines:
        draw_text_centered(draw, line, y, tag_font, fill=(150, 200, 160))
        y += 38
    
    # Theme
    draw_text_centered(draw, "GOOD TRIUMPHS OVER EVIL  ·  THIRD PERSON", 1700, genre_font, fill=(100, 160, 110))
    
    return img.convert("RGB")


# =============================================================================
# POSTER 2: The Anti-Hero - Dystopian
# =============================================================================
def poster_2():
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H, (40, 10, 10), (10, 5, 20))
    
    # Dystopian cityscape
    random.seed(202)
    for i in range(40):
        bx = random.randint(0, W)
        bw = random.randint(30, 120)
        bh = random.randint(200, 800)
        shade = random.randint(15, 45)
        draw.rectangle([bx, H - bh, bx + bw, H], fill=(shade, shade//2, shade//2))
        # Windows
        for wy in range(H - bh + 20, H - 20, 30):
            for wx in range(bx + 5, bx + bw - 5, 15):
                if random.random() > 0.5:
                    draw.rectangle([wx, wy, wx+6, wy+10], fill=(200, 150, 50, 100))
    
    # Red surveillance glow
    for r in range(300, 0, -3):
        a = int(25 * (1 - r/300))
        draw.ellipse([W//2-r, 400-r, W//2+r, 400+r], fill=(120+a, 20, 20))
    
    # Character - figure in long coat, turned sideways
    cx, cy = W//2, 600
    # Coat/body - angular, sharp
    draw.polygon([(cx-30, cy-40), (cx+30, cy-40), (cx+100, cy+400), (cx+80, cy+420),
                   (cx-20, cy+420), (cx-100, cy+400)], fill=(15, 10, 20))
    # Head
    draw.ellipse([cx-40, cy-120, cx+40, cy-30], fill=(15, 10, 20))
    # One red eye/visor
    draw.ellipse([cx+5, cy-85, cx+25, cy-70], fill=(255, 50, 50))
    # Weapon outline
    draw.line([(cx+60, cy+100), (cx+110, cy-50)], fill=(80, 80, 90), width=6)
    
    # Red scan lines
    for y in range(0, H, 6):
        draw.line([(0, y), (W, y)], fill=(255, 0, 0, 5), width=1)
    
    title_font = load_font("BigShoulders-Bold.ttf", 100)
    sub_font = load_font("CrimsonPro-Italic.ttf", 36)
    tag_font = load_font("CrimsonPro-Regular.ttf", 28)
    genre_font = load_font("InstrumentSans-Bold.ttf", 22)
    
    draw_text_centered_shadow(draw, "THE", 60, title_font, fill=(255, 80, 80))
    draw_text_centered_shadow(draw, "ANTI-HERO", 160, title_font, fill=(255, 80, 80))
    
    draw_text_centered(draw, "The wrong person. The only choice.", 1300, sub_font, fill=(255, 150, 150))
    
    draw.rounded_rectangle([W//2 - 100, 1400, W//2 + 100, 1435], radius=12, fill=(80, 20, 20))
    draw_text_centered(draw, "DYSTOPIAN", 1405, genre_font, fill=(255, 150, 150))
    
    lines = wrap_text("A smuggler in a totalitarian regime must transport a child who holds the key to revolution — choosing between self-preservation and sacrifice.", tag_font, W - 200, draw)
    y = 1500
    for line in lines:
        draw_text_centered(draw, line, y, tag_font, fill=(200, 140, 140))
        y += 38
    
    draw_text_centered(draw, "MORAL AMBIGUITY  ·  FIRST PERSON", 1700, genre_font, fill=(160, 80, 80))
    
    return img.convert("RGB")


# =============================================================================
# POSTER 3: The Tortured Genius - Victorian Historical
# =============================================================================
def poster_3():
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H, (50, 40, 30), (15, 10, 8))
    
    # Victorian fog / gas lamp glow
    for r in range(200, 0, -2):
        a = int(50 * (1 - r/200))
        draw.ellipse([200-r, 200-r, 200+r, 200+r], fill=(180+min(a,70), 140+min(a,50), 60+a))
    for r in range(200, 0, -2):
        a = int(50 * (1 - r/200))
        draw.ellipse([W-200-r, 250-r, W-200+r, 250+r], fill=(180+min(a,70), 140+min(a,50), 60+a))
    
    # Gears and clockwork background
    random.seed(303)
    for _ in range(15):
        gx, gy = random.randint(100, W-100), random.randint(200, 1200)
        gr = random.randint(40, 120)
        shade = random.randint(40, 70)
        draw.ellipse([gx-gr, gy-gr, gx+gr, gy+gr], outline=(shade, shade-10, shade-20), width=3)
        # Gear teeth
        for angle in range(0, 360, 30):
            ax = gx + int(gr * math.cos(math.radians(angle)))
            ay = gy + int(gr * math.sin(math.radians(angle)))
            draw.rectangle([ax-5, ay-5, ax+5, ay+5], fill=(shade, shade-10, shade-20))
    
    # Character - figure at desk with machine glow
    cx, cy = W//2, 700
    # Amber glow from machine
    for r in range(180, 0, -2):
        a = int(60 * (1 - r/180))
        draw.ellipse([cx-r, cy-50-r, cx+r, cy-50+r], fill=(100+a, 70+a, 20+a//2))
    
    # Seated figure
    draw.polygon([(cx-70, cy-20), (cx+70, cy-20), (cx+90, cy+300), (cx-90, cy+300)], fill=(10, 8, 5))
    draw.ellipse([cx-45, cy-100, cx+45, cy-10], fill=(10, 8, 5))
    # Top hat silhouette
    draw.rectangle([cx-35, cy-170, cx+35, cy-90], fill=(10, 8, 5))
    draw.rectangle([cx-50, cy-100, cx+50, cy-85], fill=(10, 8, 5))
    # Arms reaching to machine
    draw.line([(cx+50, cy+50), (cx+150, cy-20)], fill=(10, 8, 5), width=15)
    draw.line([(cx-50, cy+50), (cx-130, cy)], fill=(10, 8, 5), width=15)
    
    title_font = load_font("Gloock-Regular.ttf", 80)
    sub_font = load_font("CrimsonPro-Italic.ttf", 36)
    tag_font = load_font("CrimsonPro-Regular.ttf", 28)
    genre_font = load_font("InstrumentSans-Bold.ttf", 22)
    
    draw_text_centered_shadow(draw, "THE TORTURED", 60, title_font, fill=(220, 180, 100))
    draw_text_centered_shadow(draw, "GENIUS", 155, title_font, fill=(220, 180, 100))
    
    draw_text_centered(draw, "Brilliance is a beautiful prison.", 1300, sub_font, fill=(200, 170, 120))
    
    draw.rounded_rectangle([W//2 - 100, 1400, W//2 + 100, 1435], radius=12, fill=(70, 55, 30))
    draw_text_centered(draw, "HISTORICAL", 1405, genre_font, fill=(220, 180, 100))
    
    lines = wrap_text("A gifted inventor in 1880s London creates a crime-predicting machine — but its revelations threaten to unravel his own dark past.", tag_font, W - 200, draw)
    y = 1500
    for line in lines:
        draw_text_centered(draw, line, y, tag_font, fill=(180, 155, 110))
        y += 38
    
    draw_text_centered(draw, "THE COST OF KNOWLEDGE  ·  FIRST PERSON", 1700, genre_font, fill=(140, 110, 70))
    
    return img.convert("RGB")


# =============================================================================
# POSTER 4: The Chosen One - Sci-Fi Space Opera
# =============================================================================
def poster_4():
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H, (5, 5, 30), (2, 2, 10))
    
    # Stars
    draw_stars(draw, 400, W, H)
    
    # Nebula glow
    for r in range(350, 0, -3):
        a = int(30 * (1 - r/350))
        draw.ellipse([W//2-r-100, 500-r, W//2+r-100, 500+r], fill=(20+a, 10, 60+a))
    for r in range(250, 0, -3):
        a = int(20 * (1 - r/250))
        draw.ellipse([W//2+r+50, 600-r, W//2+r+350, 600+r], fill=(10, 20+a, 50+a))
    
    # Dying star
    for r in range(100, 0, -1):
        a = int(200 * (1 - r/100))
        draw.ellipse([900-r, 300-r, 900+r, 300+r], fill=(min(255,100+a), min(255,50+a), min(255,200+a)))
    
    # Character - figure looking up at star, space suit outline
    cx, cy = W//2, 800
    # Space suit body
    draw.polygon([(cx-70, cy), (cx+70, cy), (cx+100, cy+350), (cx-100, cy+350)], fill=(20, 25, 50))
    # Helmet
    draw.ellipse([cx-60, cy-130, cx+60, cy+10], fill=(20, 25, 50))
    # Visor glow
    draw.ellipse([cx-40, cy-100, cx+40, cy-30], fill=(60, 80, 180))
    draw.ellipse([cx-30, cy-90, cx+30, cy-40], fill=(80, 120, 220))
    # Signal beam from hand to star
    draw.line([(cx+80, cy+50), (900, 300)], fill=(100, 150, 255), width=3)
    for r in range(20, 0, -1):
        draw.ellipse([cx+78-r, cy+48-r, cx+78+r, cy+48+r], fill=(60+r*4, 80+r*4, 200))
    
    title_font = load_font("Tektur-Medium.ttf", 85)
    sub_font = load_font("CrimsonPro-Italic.ttf", 36)
    tag_font = load_font("CrimsonPro-Regular.ttf", 28)
    genre_font = load_font("InstrumentSans-Bold.ttf", 22)
    
    draw_text_centered_shadow(draw, "THE CHOSEN", 60, title_font, fill=(120, 160, 255))
    draw_text_centered_shadow(draw, "ONE", 155, title_font, fill=(120, 160, 255))
    
    draw_text_centered(draw, "The signal was meant only for them.", 1300, sub_font, fill=(150, 180, 255))
    
    draw.rounded_rectangle([W//2 - 80, 1400, W//2 + 80, 1435], radius=12, fill=(20, 30, 80))
    draw_text_centered(draw, "SCI-FI", 1405, genre_font, fill=(150, 180, 255))
    
    lines = wrap_text("A navigator decodes a signal from a dying star — a message that could mean first contact or galactic war.", tag_font, W - 200, draw)
    y = 1500
    for line in lines:
        draw_text_centered(draw, line, y, tag_font, fill=(130, 150, 220))
        y += 38
    
    draw_text_centered(draw, "UNITY ACROSS DIFFERENCES  ·  THIRD PERSON", 1700, genre_font, fill=(80, 100, 180))
    
    return img.convert("RGB")


# =============================================================================
# POSTER 5: The Survivor - Post-Apocalyptic / Zombie
# =============================================================================
def poster_5():
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H, (60, 50, 30), (15, 12, 8))
    
    # Toxic sky bands
    for y in range(0, 400, 2):
        t = y / 400
        r = int(60 + 40 * math.sin(t * 3))
        g = int(50 + 20 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, 15))
    
    # Ruined buildings
    random.seed(505)
    for i in range(20):
        bx = random.randint(0, W)
        bw = random.randint(40, 150)
        bh = random.randint(200, 600)
        shade = random.randint(20, 40)
        # Jagged top
        top_y = H - bh
        points = [(bx, H)]
        for x in range(bx, bx + bw, 10):
            jag = random.randint(-30, 30)
            points.append((x, top_y + jag))
        points.append((bx + bw, H))
        draw.polygon(points, fill=(shade, shade-5, shade-10))
    
    # Hazy sun
    for r in range(120, 0, -1):
        a = int(120 * (1 - r/120))
        draw.ellipse([W//2-r, 180-r, W//2+r, 180+r], fill=(min(255,150+a), min(255,100+a), 30))
    
    # Character - lone figure with backpack walking
    cx, cy = W//2, 750
    # Body
    draw.polygon([(cx-50, cy), (cx+50, cy), (cx+60, cy+350), (cx-60, cy+350)], fill=(12, 10, 8))
    # Head
    draw.ellipse([cx-35, cy-80, cx+35, cy+10], fill=(12, 10, 8))
    # Backpack
    draw.rectangle([cx+30, cy-20, cx+80, cy+120], fill=(15, 12, 10))
    # Walking stick
    draw.line([(cx-60, cy+30), (cx-100, cy+370)], fill=(50, 35, 20), width=6)
    
    # Dust particles
    random.seed(55)
    for _ in range(80):
        px = random.randint(0, W)
        py = random.randint(300, H)
        ps = random.randint(1, 4)
        shade = random.randint(80, 150)
        draw.ellipse([px-ps, py-ps, px+ps, py+ps], fill=(shade, shade-20, shade-40))
    
    title_font = load_font("BigShoulders-Bold.ttf", 100)
    sub_font = load_font("CrimsonPro-Italic.ttf", 36)
    tag_font = load_font("CrimsonPro-Regular.ttf", 28)
    genre_font = load_font("InstrumentSans-Bold.ttf", 22)
    
    draw_text_centered_shadow(draw, "THE", 60, title_font, fill=(220, 180, 80))
    draw_text_centered_shadow(draw, "SURVIVOR", 160, title_font, fill=(220, 180, 80))
    
    draw_text_centered(draw, "Hope is the last thing to die.", 1300, sub_font, fill=(200, 170, 100))
    
    draw.rounded_rectangle([W//2 - 130, 1400, W//2 + 130, 1435], radius=12, fill=(60, 45, 15))
    draw_text_centered(draw, "POST-APOCALYPTIC", 1405, genre_font, fill=(220, 180, 80))
    
    lines = wrap_text("Three years after a fungal outbreak, a lone survivor follows a radio signal to a supposed safe zone — but salvation may be a lie.", tag_font, W - 200, draw)
    y = 1490
    for line in lines:
        draw_text_centered(draw, line, y, tag_font, fill=(180, 150, 90))
        y += 38
    
    draw_text_centered(draw, "THE WILL TO SURVIVE  ·  FIRST PERSON", 1700, genre_font, fill=(140, 110, 60))
    
    return img.convert("RGB")


# =============================================================================
# POSTER 6: The Mentor - Fantasy
# =============================================================================
def poster_6():
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H, (20, 15, 45), (5, 3, 15))
    
    # Magical aurora / sky
    for y in range(0, 500):
        t = y / 500
        wave = math.sin(t * 8 + 0.5) * 30
        r = int(20 + 30 * t + wave)
        g = int(15 + 20 * t)
        b = int(60 + 40 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    
    # Ancient tower in background
    draw.rectangle([W//2 - 60, 200, W//2 + 60, 1100], fill=(25, 20, 40))
    draw.polygon([(W//2 - 80, 200), (W//2, 80), (W//2 + 80, 200)], fill=(30, 25, 45))
    # Tower windows
    for wy in range(250, 1050, 100):
        draw.ellipse([W//2-15, wy, W//2+15, wy+30], fill=(180, 140, 255))
    
    # Two characters - old wizard and young apprentice
    # Mentor (taller, left)
    mx, my = W//2 - 120, 700
    draw.polygon([(mx-70, my), (mx+70, my), (mx+100, my+450), (mx-100, my+450)], fill=(15, 12, 35))
    draw.ellipse([mx-45, my-90, mx+45, my+10], fill=(15, 12, 35))
    # Wizard hat
    draw.polygon([(mx-50, my-80), (mx, my-200), (mx+50, my-80)], fill=(15, 12, 35))
    # Staff
    draw.line([(mx+80, my-60), (mx+70, my+450)], fill=(60, 40, 30), width=7)
    
    # Apprentice (shorter, right)
    ax, ay = W//2 + 120, 800
    draw.polygon([(ax-50, ay), (ax+50, ay), (ax+70, ay+350), (ax-70, ay+350)], fill=(20, 15, 40))
    draw.ellipse([ax-35, ay-70, ax+35, ay+10], fill=(20, 15, 40))
    
    # Magic flow between them
    for t_val in range(50):
        t = t_val / 50
        bx = mx + 80 + (ax - mx - 80) * t
        by = my + 50 + math.sin(t * math.pi * 3) * 40 - 80 * t
        s = 3 + int(5 * math.sin(t * math.pi))
        draw.ellipse([bx-s, by-s, bx+s, by+s], fill=(150, 100, 255))
    
    # Apprentice's unstable glow
    for r in range(80, 0, -1):
        a = int(40 * (1 - r/80))
        draw.ellipse([ax-r, ay-40-r, ax+r, ay-40+r], fill=(min(255,120+a*2), 60+a, min(255,200+a)))
    
    title_font = load_font("Boldonse-Regular.ttf", 85)
    sub_font = load_font("CrimsonPro-Italic.ttf", 36)
    tag_font = load_font("CrimsonPro-Regular.ttf", 28)
    genre_font = load_font("InstrumentSans-Bold.ttf", 22)
    
    draw_text_centered_shadow(draw, "THE", 50, title_font, fill=(180, 140, 255))
    draw_text_centered_shadow(draw, "MENTOR", 140, title_font, fill=(180, 140, 255))
    
    draw_text_centered(draw, "Those who cannot do... must teach another to succeed.", 1300, sub_font, fill=(180, 160, 230))
    
    draw.rounded_rectangle([W//2 - 80, 1400, W//2 + 80, 1435], radius=12, fill=(30, 25, 60))
    draw_text_centered(draw, "FANTASY", 1405, genre_font, fill=(180, 140, 255))
    
    lines = wrap_text("An aging wizard who once failed to stop a great calamity must prepare a volatile apprentice to succeed where he couldn't.", tag_font, W - 200, draw)
    y = 1500
    for line in lines:
        draw_text_centered(draw, line, y, tag_font, fill=(160, 140, 200))
        y += 38
    
    draw_text_centered(draw, "REDEMPTION  ·  THIRD PERSON", 1700, genre_font, fill=(120, 100, 170))
    
    return img.convert("RGB")


# =============================================================================
# POSTER 7: The Outcast - Historical 1920s
# =============================================================================
def poster_7():
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H, (50, 30, 15), (10, 5, 15))
    
    # Art Deco geometric patterns
    gold = (220, 180, 80)
    dark_gold = (120, 95, 40)
    # Deco arch frame
    draw.arc([100, 100, W-100, 800], 180, 0, fill=gold, width=4)
    draw.arc([130, 130, W-130, 780], 180, 0, fill=dark_gold, width=2)
    # Vertical lines
    for x in [150, 180, W-150, W-180]:
        draw.line([(x, 400), (x, 1200)], fill=dark_gold, width=2)
    # Deco fan rays
    for angle in range(-80, 81, 20):
        ex = W//2 + int(400 * math.sin(math.radians(angle)))
        ey = 450 - int(400 * math.cos(math.radians(angle)))
        draw.line([(W//2, 450), (ex, ey)], fill=dark_gold, width=1)
    
    # Stage spotlight glow
    for r in range(250, 0, -2):
        a = int(40 * (1 - r/250))
        draw.ellipse([W//2-r, 600-r, W//2+r, 600+r], fill=(min(255,80+a*2), min(255,60+a), 20+a//2))
    
    # Character - jazz musician with saxophone silhouette
    cx, cy = W//2, 700
    # Body - suit
    draw.polygon([(cx-60, cy), (cx+60, cy), (cx+80, cy+380), (cx-80, cy+380)], fill=(10, 5, 15))
    # Head with hat
    draw.ellipse([cx-40, cy-90, cx+40, cy+5], fill=(10, 5, 15))
    # Fedora
    draw.rectangle([cx-30, cy-120, cx+30, cy-80], fill=(10, 5, 15))
    draw.rectangle([cx-55, cy-85, cx+55, cy-75], fill=(10, 5, 15))
    # Saxophone shape
    draw.arc([cx+20, cy+20, cx+120, cy+200], 0, 180, fill=(180, 150, 60), width=8)
    draw.line([(cx+70, cy+20), (cx+90, cy-40)], fill=(180, 150, 60), width=8)
    # Bell of saxophone
    draw.ellipse([cx+80, cy+160, cx+140, cy+220], outline=(180, 150, 60), width=6)
    
    # Music notes floating
    random.seed(77)
    note_font = load_font("CrimsonPro-Bold.ttf", 40)
    for _ in range(12):
        nx = random.randint(200, W-200)
        ny = random.randint(400, 1100)
        draw.text((nx, ny), "♪", font=note_font, fill=(220, 180, 80, 150))
    
    title_font = load_font("YoungSerif-Regular.ttf", 90)
    sub_font = load_font("CrimsonPro-Italic.ttf", 36)
    tag_font = load_font("CrimsonPro-Regular.ttf", 28)
    genre_font = load_font("InstrumentSans-Bold.ttf", 22)
    
    draw_text_centered_shadow(draw, "THE", 60, title_font, fill=gold)
    draw_text_centered_shadow(draw, "OUTCAST", 155, title_font, fill=gold)
    
    draw_text_centered(draw, "The music knows no color. The world does.", 1300, sub_font, fill=(220, 190, 120))
    
    draw.rounded_rectangle([W//2 - 100, 1400, W//2 + 100, 1435], radius=12, fill=(70, 55, 25))
    draw_text_centered(draw, "HISTORICAL", 1405, genre_font, fill=gold)
    
    lines = wrap_text("A mixed-race jazz musician in 1920s Harlem must choose between fame that erases their heritage and a truth that may destroy their career.", tag_font, W - 200, draw)
    y = 1490
    for line in lines:
        draw_text_centered(draw, line, y, tag_font, fill=(190, 160, 100))
        y += 38
    
    draw_text_centered(draw, "IDENTITY & BELONGING  ·  FIRST PERSON", 1700, genre_font, fill=(140, 115, 60))
    
    return img.convert("RGB")


# =============================================================================
# POSTER 8: Villain Turned Reluctant Ally - Dystopian
# =============================================================================
def poster_8():
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H, (25, 25, 35), (5, 5, 10))
    
    # Split composition - dark/light
    # Left side darker, right side slightly lighter (representing transformation)
    for x in range(W):
        t = x / W
        for y in range(H):
            yt = y / H
            base_r = int(25 - 15 * t + 10 * yt)
            base_g = int(25 - 10 * t + 15 * yt)
            base_b = int(35 + 10 * t + 5 * yt)
    
    # Shattered/cracked pattern
    random.seed(808)
    for _ in range(25):
        sx = random.randint(0, W)
        sy = random.randint(0, H)
        for seg in range(random.randint(2, 6)):
            ex = sx + random.randint(-100, 100)
            ey = sy + random.randint(-100, 100)
            draw.line([(sx, sy), (ex, ey)], fill=(50, 50, 60), width=1)
            sx, sy = ex, ey
    
    # Two-toned glow - red behind, blue emerging
    for r in range(200, 0, -2):
        a = int(30 * (1 - r/200))
        draw.ellipse([W//2-r-100, 600-r, W//2+r-100, 600+r], fill=(80+a, 10, 10))
    for r in range(150, 0, -2):
        a = int(30 * (1 - r/150))
        draw.ellipse([W//2-r+80, 650-r, W//2+r+80, 650+r], fill=(10, 30+a, 80+a))
    
    # Character - armored figure, half in shadow, half emerging
    cx, cy = W//2, 700
    # Body - heavy armor
    draw.polygon([(cx-90, cy-30), (cx+90, cy-30), (cx+110, cy+380), (cx-110, cy+380)], fill=(18, 18, 25))
    # Shoulder pads
    draw.ellipse([cx-120, cy-60, cx-40, cy+20], fill=(18, 18, 25))
    draw.ellipse([cx+40, cy-60, cx+120, cy+20], fill=(18, 18, 25))
    # Head/helmet
    draw.ellipse([cx-50, cy-130, cx+50, cy-20], fill=(18, 18, 25))
    # Split visor - one side red, one blue
    draw.ellipse([cx-30, cy-100, cx-5, cy-70], fill=(200, 40, 40))
    draw.ellipse([cx+5, cy-100, cx+30, cy-70], fill=(40, 80, 200))
    
    # Broken chains
    for i in range(5):
        draw.ellipse([cx-200+i*20, cy+300+i*10, cx-180+i*20, cy+320+i*10], outline=(80, 80, 90), width=3)
    for i in range(5):
        draw.ellipse([cx+100+i*20, cy+280+i*10, cx+120+i*20, cy+300+i*10], outline=(80, 80, 90), width=3)
    
    title_font = load_font("BigShoulders-Bold.ttf", 75)
    sub_font = load_font("CrimsonPro-Italic.ttf", 34)
    tag_font = load_font("CrimsonPro-Regular.ttf", 28)
    genre_font = load_font("InstrumentSans-Bold.ttf", 22)
    
    draw_text_centered_shadow(draw, "THE VILLAIN", 50, title_font, fill=(200, 80, 80))
    draw_text_centered_shadow(draw, "TURNED ALLY", 135, title_font, fill=(80, 120, 220))
    
    draw_text_centered(draw, "Redemption is earned in blood, not words.", 1300, sub_font, fill=(180, 150, 200))
    
    draw.rounded_rectangle([W//2 - 100, 1400, W//2 + 100, 1435], radius=12, fill=(40, 30, 60))
    draw_text_centered(draw, "DYSTOPIAN", 1405, genre_font, fill=(180, 150, 200))
    
    lines = wrap_text("A disgraced enforcer, abandoned by the regime, must earn the trust of the rebellion — while a greater threat forces both sides together.", tag_font, W - 200, draw)
    y = 1490
    for line in lines:
        draw_text_centered(draw, line, y, tag_font, fill=(160, 140, 180))
        y += 38
    
    draw_text_centered(draw, "REDEMPTION THROUGH ACTION  ·  THIRD PERSON", 1700, genre_font, fill=(110, 90, 140))
    
    return img.convert("RGB")


# =============================================================================
# POSTER 9: The Trickster - Sci-Fi
# =============================================================================
def poster_9():
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H, (10, 20, 40), (5, 8, 18))
    
    # Stars
    draw_stars(draw, 300, W, H)
    
    # Two alien ships/stations flanking
    # Left ship
    draw.polygon([(0, 500), (200, 400), (250, 600), (0, 700)], fill=(60, 20, 20))
    draw.polygon([(0, 520), (180, 420), (220, 580), (0, 680)], fill=(80, 30, 30))
    # Right ship
    draw.polygon([(W, 500), (W-200, 400), (W-250, 600), (W, 700)], fill=(20, 20, 60))
    draw.polygon([(W, 520), (W-180, 420), (W-220, 580), (W, 680)], fill=(30, 30, 80))
    
    # Character - suave figure between the two sides
    cx, cy = W//2, 700
    # Spotlight from above
    draw.polygon([(cx-20, 0), (cx+20, 0), (cx+200, cy+400), (cx-200, cy+400)], fill=(25, 30, 50))
    
    # Body - elegant suit/coat
    draw.polygon([(cx-60, cy), (cx+60, cy), (cx+90, cy+380), (cx-90, cy+380)], fill=(15, 18, 30))
    # Head
    draw.ellipse([cx-40, cy-90, cx+40, cy+5], fill=(15, 18, 30))
    # Charming hat tilt
    draw.polygon([(cx-55, cy-80), (cx+60, cy-95), (cx+50, cy-65), (cx-45, cy-55)], fill=(15, 18, 30))
    # Arms spread wide - welcoming gesture
    draw.line([(cx-60, cy+80), (cx-200, cy+20)], fill=(15, 18, 30), width=12)
    draw.line([(cx+60, cy+80), (cx+200, cy+20)], fill=(15, 18, 30), width=12)
    # Playing card or hologram in hand
    draw.rectangle([cx-210, cy, cx-180, cy+40], fill=(180, 180, 220))
    
    # Holographic treaty document floating
    for r in range(60, 0, -1):
        a = int(60 * (1 - r/60))
        draw.ellipse([cx-r, cy-200-r//2, cx+r, cy-200+r//2], fill=(40+a, 200+min(a,55), min(255,200+a)))
    
    # Sparkle/trick particles
    random.seed(99)
    for _ in range(40):
        px = random.randint(200, W-200)
        py = random.randint(400, 1100)
        ps = random.randint(1, 4)
        c = random.choice([(255, 215, 0), (0, 255, 200), (200, 100, 255)])
        draw.ellipse([px-ps, py-ps, px+ps, py+ps], fill=c)
    
    title_font = load_font("Boldonse-Regular.ttf", 90)
    sub_font = load_font("CrimsonPro-Italic.ttf", 36)
    tag_font = load_font("CrimsonPro-Regular.ttf", 28)
    genre_font = load_font("InstrumentSans-Bold.ttf", 22)
    
    draw_text_centered_shadow(draw, "THE", 50, title_font, fill=(0, 230, 180))
    draw_text_centered_shadow(draw, "TRICKSTER", 145, title_font, fill=(0, 230, 180))
    
    draw_text_centered(draw, "The greatest con? Telling the truth.", 1300, sub_font, fill=(100, 230, 200))
    
    draw.rounded_rectangle([W//2 - 80, 1400, W//2 + 80, 1435], radius=12, fill=(15, 50, 45))
    draw_text_centered(draw, "SCI-FI", 1405, genre_font, fill=(0, 230, 180))
    
    lines = wrap_text("A con artist posing as a diplomat accidentally brokers peace between warring aliens — and must keep the charade alive when both sides discover the truth.", tag_font, W - 200, draw)
    y = 1490
    for line in lines:
        draw_text_centered(draw, line, y, tag_font, fill=(100, 200, 180))
        y += 38
    
    draw_text_centered(draw, "AUTHENTICITY & MASKS  ·  FIRST PERSON", 1700, genre_font, fill=(60, 150, 130))
    
    return img.convert("RGB")


# =============================================================================
# POSTER 10: The Innocent - Post-Apocalyptic
# =============================================================================
def poster_10():
    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H, (70, 60, 50), (20, 15, 12))
    
    # Broken highway / ruins
    random.seed(1010)
    # Road vanishing to distance
    draw.polygon([(400, H), (W-400, H), (W//2 + 30, 500), (W//2 - 30, 500)], fill=(35, 30, 28))
    # Dashed line
    for y in range(500, H, 60):
        w_at_y = int(2 + 15 * ((y - 500) / (H - 500)))
        draw.rectangle([W//2 - w_at_y//2, y, W//2 + w_at_y//2, y+25], fill=(70, 65, 50))
    
    # Rusted cars
    for cx_car in [350, 750, 500]:
        cy_car = random.randint(900, 1100)
        shade = random.randint(40, 60)
        draw.rectangle([cx_car-30, cy_car, cx_car+30, cy_car+20], fill=(shade, shade-10, shade-15))
        draw.rectangle([cx_car-20, cy_car-15, cx_car+20, cy_car], fill=(shade-5, shade-15, shade-20))
    
    # Overcast sky with one break of warm light
    for r in range(200, 0, -2):
        a = int(40 * (1 - r/200))
        draw.ellipse([W//2-r, 200-r, W//2+r, 200+r], fill=(min(255,120+a*2), min(255,100+a), 50+a))
    
    # Small character - child figure with book
    cx, cy = W//2, 800
    # Small body
    draw.polygon([(cx-30, cy), (cx+30, cy), (cx+40, cy+200), (cx-40, cy+200)], fill=(15, 12, 10))
    # Head - slightly larger proportioned (child)
    draw.ellipse([cx-28, cy-65, cx+28, cy+5], fill=(15, 12, 10))
    # Picture book in hand (colorful contrast)
    draw.rectangle([cx+30, cy+40, cx+65, cy+80], fill=(180, 60, 60))
    draw.rectangle([cx+33, cy+43, cx+62, cy+77], fill=(220, 200, 150))
    
    # Butterflies / dandelion seeds (innocence)
    random.seed(42)
    for _ in range(15):
        bx = random.randint(200, W-200)
        by = random.randint(400, 1100)
        s = random.randint(3, 8)
        draw.ellipse([bx, by, bx+s, by+s*2], fill=(200, 180, 120, 150))
        draw.ellipse([bx+s, by, bx+s*2, by+s*2], fill=(200, 180, 120, 150))
    
    title_font = load_font("Lora-Bold.ttf", 90)
    sub_font = load_font("CrimsonPro-Italic.ttf", 36)
    tag_font = load_font("CrimsonPro-Regular.ttf", 28)
    genre_font = load_font("InstrumentSans-Bold.ttf", 22)
    
    draw_text_centered_shadow(draw, "THE", 60, title_font, fill=(230, 200, 140))
    draw_text_centered_shadow(draw, "INNOCENT", 155, title_font, fill=(230, 200, 140))
    
    draw_text_centered(draw, "The world they knew was only a story.", 1300, sub_font, fill=(210, 190, 140))
    
    draw.rounded_rectangle([W//2 - 130, 1400, W//2 + 130, 1435], radius=12, fill=(55, 45, 25))
    draw_text_centered(draw, "POST-APOCALYPTIC", 1405, genre_font, fill=(230, 200, 140))
    
    lines = wrap_text("A child born after the collapse journeys through ruins guided by a tattered picture book — discovering a world far more complex than the elders' stories.", tag_font, W - 200, draw)
    y = 1490
    for line in lines:
        draw_text_centered(draw, line, y, tag_font, fill=(190, 170, 120))
        y += 38
    
    draw_text_centered(draw, "LOSS OF INNOCENCE  ·  THIRD PERSON", 1700, genre_font, fill=(140, 125, 80))
    
    return img.convert("RGB")


# =============================================================================
# GENERATE ALL POSTERS
# =============================================================================
poster_funcs = [
    (poster_1, "01_The_Reluctant_Hero"),
    (poster_2, "02_The_Anti_Hero"),
    (poster_3, "03_The_Tortured_Genius"),
    (poster_4, "04_The_Chosen_One"),
    (poster_5, "05_The_Survivor"),
    (poster_6, "06_The_Mentor"),
    (poster_7, "07_The_Outcast"),
    (poster_8, "08_The_Villain_Turned_Ally"),
    (poster_9, "09_The_Trickster"),
    (poster_10, "10_The_Innocent"),
]

for func, name in poster_funcs:
    print(f"Generating {name}...")
    img = func()
    path = os.path.join(OUTPUT_DIR, f"{name}.jpg")
    img.save(path, "JPEG", quality=95)
    print(f"  Saved: {path}")

print("\nAll 10 posters generated!")
