"""Perspective-fit a pre-cropped app screenshot onto a blank-screen phone photo.

Auto-detects the phone screen as the largest bright, phone-aspect-ratio rotated
rectangle in the image (works for the common "hand holding phone with blank white
screen" stock/mockup photos). Falls back to raising if nothing plausible is found,
so a bad auto-detect never silently ships.
"""
import numpy as np
from PIL import Image, ImageDraw
import cv2


def find_screen_quad(photo_path, brightness_thresh=195, min_area_frac=0.03):
    im = Image.open(photo_path).convert("RGB")
    arr = np.array(im)
    gray = arr.mean(axis=2).astype(np.uint8)
    W, H = im.size

    mask = (gray > brightness_thresh).astype(np.uint8) * 255
    kernel = np.ones((15, 15), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError(f"no bright regions found in {photo_path}")

    img_area = W * H
    best = None
    for c in contours:
        area = cv2.contourArea(c)
        if area < img_area * min_area_frac:
            continue
        rect = cv2.minAreaRect(c)
        (rw, rh) = rect[1]
        if rw == 0 or rh == 0:
            continue
        aspect = max(rw, rh) / min(rw, rh)
        if not (1.5 <= aspect <= 2.6):
            continue
        if best is None or area > best[0]:
            best = (area, rect)

    if best is None:
        raise ValueError(
            f"no phone-shaped bright region found in {photo_path} "
            "(expected a blank/white phone screen)"
        )

    box = cv2.boxPoints(best[1])
    return order_points(box)


def order_points(pts):
    pts = sorted(pts.tolist(), key=lambda p: p[1])
    top2 = sorted(pts[:2], key=lambda p: p[0])
    bottom2 = sorted(pts[2:], key=lambda p: p[0])
    tl, tr = top2
    bl, br = bottom2
    return [tuple(tl), tuple(tr), tuple(br), tuple(bl)]


def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p2[0], p2[1], 1, 0, 0, 0, -p1[0] * p2[0], -p1[0] * p2[1]])
        matrix.append([0, 0, 0, p2[0], p2[1], 1, -p1[1] * p2[0], -p1[1] * p2[1]])
    A = np.array(matrix, dtype=float)
    B = np.array(pa).reshape(8)
    return np.linalg.solve(A, B)


def composite_screenshot(photo_path, screenshot_path, out_path, inset=0.018, quad=None):
    photo = Image.open(photo_path).convert("RGB")
    screenshot = Image.open(screenshot_path).convert("RGB")
    W, H = photo.size
    sw, sh = screenshot.size

    raw = quad if quad is not None else find_screen_quad(photo_path)
    cx = sum(p[0] for p in raw) / 4
    cy = sum(p[1] for p in raw) / 4
    dest = [(cx + (x - cx) * (1 - inset), cy + (y - cy) * (1 - inset)) for x, y in raw]

    src = [(0, 0), (sw, 0), (sw, sh), (0, sh)]
    coeffs = find_coeffs(src, dest)
    warped = screenshot.transform((W, H), Image.PERSPECTIVE, coeffs, Image.BICUBIC)

    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(dest, fill=255)

    result = photo.copy()
    result.paste(warped, (0, 0), mask)
    result.save(out_path, quality=95)
    return dest
