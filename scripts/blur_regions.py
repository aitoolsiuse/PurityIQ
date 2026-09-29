"""Apply soft feathered blur boxes to a photo, e.g. to obscure a store/brand logo."""
from PIL import Image, ImageFilter, ImageDraw


def apply_blur_regions(photo_path, regions, out_path=None, blur_radius=35, feather=70):
    im = Image.open(photo_path).convert("RGB")
    for box in regions:
        region = im.crop(box)
        blurred = region.filter(ImageFilter.GaussianBlur(blur_radius))
        w, h = region.size
        mask = Image.new("L", region.size, 0)
        d = ImageDraw.Draw(mask)
        d.ellipse([w * 0.08, h * 0.08, w * 0.92, h * 0.92], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(feather))
        im.paste(blurred, box, mask)
    im.save(out_path or photo_path, quality=95)
    return out_path or photo_path
