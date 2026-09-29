"""PurityIQ slideshow slide compositing: full-bleed photo, gradient, logo badge, bold text.

Settings here are the approved PIQ-001 look: fixed 64px/54px ExtraBold Inter text,
strong bottom gradient (85% black by 50% down the frame) + soft top gradient, a
blurred drop shadow behind the text, and a rounded-badge logo + wordmark top-left.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO, "assets")
FONT_PATH = os.path.join(ASSETS, "Inter.ttf")
LOGO_PATH = os.path.join(ASSETS, "purityiq-icon.png")

WHITE = (255, 255, 255, 255)

# Approved look, locked in from PIQ-001
FORMATS = {
    "tiktok": dict(w=1080, h=1920, badge=72, margin_x=48, margin_top=48,
                   right_exclusion=0.15, bottom_exclusion=0.20, font_size=64),
    "instagram": dict(w=1080, h=1350, badge=60, margin_x=48, margin_top=44,
                       right_exclusion=0.0, bottom_exclusion=0.055, font_size=54),
}


def load_font(size, weight="ExtraBold"):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def cover_crop(im, target_w, target_h, focus_y=0.5):
    src_w, src_h = im.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        new_h = target_h
        new_w = int(round(src_ratio * new_h))
    else:
        new_w = target_w
        new_h = int(round(new_w / src_ratio))
    im_resized = im.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) / 2
    top_max = new_h - target_h
    top = max(0, min(top_max, top_max * focus_y))
    box = (int(left), int(top), int(left) + target_w, int(top) + target_h)
    return im_resized.crop(box)


def rounded_mask(size, radius_frac=0.26):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    r = int(size * radius_frac)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    return m


def make_badge(size):
    icon = Image.open(LOGO_PATH).convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = rounded_mask(size, 0.26)
    icon.putalpha(mask)
    return icon


def gradient_overlay(w, h, top_h_frac=0.16, top_alpha=140,
                      bottom_start_frac=0.50, bottom_alpha=217):
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    top_h = int(h * top_h_frac)
    bottom_start = int(h * bottom_start_frac)
    ys = np.arange(h)
    alpha = np.zeros(h, dtype=np.float32)
    if top_h > 0:
        top_frac = np.clip(1 - (ys / top_h), 0, 1) ** 1.4
        alpha = np.maximum(alpha, top_frac * top_alpha)
    bottom_span = max(1, h - bottom_start)
    bottom_frac = np.clip((ys - bottom_start) / bottom_span, 0, 1) ** 1.5
    alpha = np.maximum(alpha, bottom_frac * bottom_alpha)
    arr[:, :, 3] = alpha.astype(np.uint8)[:, None]
    return Image.fromarray(arr, "RGBA")


def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(canvas, lines, font, line_h, x, bottom_y, stroke_width=2):
    total_h = line_h * len(lines)
    top_y = bottom_y - total_h

    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    dx, dy = max(2, int(font.size * 0.05)), max(3, int(font.size * 0.09))
    y = top_y
    for line in lines:
        sdraw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 210))
        y += line_h
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(max(3, int(font.size * 0.10))))
    canvas.alpha_composite(shadow_layer)

    draw = ImageDraw.Draw(canvas)
    y = top_y
    for line in lines:
        draw.text((x, y), line, font=font, fill=WHITE,
                   stroke_width=stroke_width, stroke_fill=(0, 0, 0, 170))
        y += line_h


def render_slide(photo_path, text, focus_y, fmt_key):
    fmt = FORMATS[fmt_key]
    target_w, target_h = fmt["w"], fmt["h"]

    photo = Image.open(photo_path).convert("RGB")
    cropped = cover_crop(photo, target_w, target_h, focus_y).convert("RGBA")

    grad = gradient_overlay(target_w, target_h)
    canvas = Image.alpha_composite(cropped, grad)

    badge = make_badge(fmt["badge"])
    canvas.alpha_composite(badge, (fmt["margin_x"], fmt["margin_top"]))
    draw = ImageDraw.Draw(canvas)
    word_font = load_font(int(fmt["badge"] * 0.56))
    wx = fmt["margin_x"] + fmt["badge"] + int(fmt["badge"] * 0.28)
    bbox = word_font.getbbox("PurityIQ")
    text_h = bbox[3] - bbox[1]
    wy = fmt["margin_top"] + (fmt["badge"] - text_h) // 2 - bbox[1]
    draw.text((wx, wy), "PurityIQ", font=word_font, fill=WHITE,
              stroke_width=2, stroke_fill=(0, 0, 0, 160))

    max_width = int(target_w * (1 - fmt["right_exclusion"])) - fmt["margin_x"]
    safe_bottom = int(target_h * (1 - fmt["bottom_exclusion"])) - int(target_h * 0.02)

    font = load_font(fmt["font_size"])
    lines = wrap_text(text, font, max_width, draw)
    line_h = int(fmt["font_size"] * 1.28)
    draw_text_block(canvas, lines, font, line_h, fmt["margin_x"], safe_bottom)

    return canvas.convert("RGB")
