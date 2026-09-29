"""Build a contact sheet from a folder of slideN.jpg TikTok-size images."""
import os
from PIL import Image


def build_contact_sheet(slides_dir, out_path, n_slides, cols=4, thumb_w=360):
    rows = (n_slides + cols - 1) // cols
    pad = 12
    thumb_h = int(thumb_w * 1920 / 1080)
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad

    sheet = Image.new("RGB", (sheet_w, sheet_h), (30, 30, 30))
    for i in range(1, n_slides + 1):
        path = os.path.join(slides_dir, f"slide{i}.jpg")
        im = Image.open(path).resize((thumb_w, thumb_h), Image.LANCZOS)
        col = (i - 1) % cols
        row = (i - 1) // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(im, (x, y))
    sheet.save(out_path, quality=90)
    return out_path
