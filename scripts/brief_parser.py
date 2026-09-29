"""
Parser for briefs/PIQ-NNN-slug.md files.

Brief format (plain markdown, custom lightweight schema):

    id: PIQ-001
    slug: eu-chicken-ban
    title: EU Chicken Ban

    ## Caption

    <one or more lines of caption text>
    <hashtags line>

    ## Slides

    1. text: Europe banned American chicken in 1997. The reason isn't what you've heard.
       photo_search: raw chicken at a grocery store
       photo_pin: pexels:10886018
       focus_y: 0.28

    2. text: ...
       photo_search: ...
       ...

Recognized per-slide keys:
    text          - exact slide copy (required, verbatim from the brief, never rewritten)
    photo_search  - search query used against Pexels/Pixabay
    photo_pin     - optional "pexels:<id>" or "pixabay:<id>" to lock a specific photo
    focus_y       - optional vertical crop anchor (0=top, 1=bottom), default 0.5
    screenshot    - optional path (relative to repo root) to a pre-cropped app screenshot
                    to perspective-fit onto the chosen photo's phone screen
    blur_regions  - optional "x0,y0,x1,y1;x0,y0,x1,y1" pixel boxes (in the ORIGINAL
                    downloaded photo's coordinate space) to blur out brand marks
    photo_reference - optional one-line composition note (subject, angle, framing,
                    setting, lighting, color mood) written from a Pinterest look;
                    informational only, the build ignores it
"""
import re

SLIDE_KEYS = {"text", "photo_search", "photo_pin", "focus_y", "screenshot", "blur_regions",
              "photo_reference"}


def parse_brief(path):
    with open(path) as f:
        raw = f.read()

    meta = {}
    caption_lines = []
    slides = []

    # split top meta / ## Caption / ## Slides sections
    parts = re.split(r"^##\s+", raw, flags=re.MULTILINE)
    head = parts[0]
    for line in head.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()

    for part in parts[1:]:
        heading, _, body = part.partition("\n")
        heading = heading.strip().lower()
        if heading.startswith("caption"):
            caption_lines = [l for l in body.strip("\n").splitlines()]
        elif heading.startswith("slide"):
            slides = _parse_slides(body)

    if not meta.get("id") or not meta.get("slug"):
        raise ValueError(f"brief {path} missing id/slug in header")
    if not slides:
        raise ValueError(f"brief {path} has no slides")

    return {
        "id": meta["id"],
        "slug": meta["slug"],
        "title": meta.get("title", meta["slug"]),
        "caption": "\n".join(caption_lines).strip("\n"),
        "slides": slides,
    }


def _parse_slides(body):
    slides = []
    current = None
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = re.match(r"^(\d+)\.\s*(\w+):\s*(.*)$", line)
        if m:
            if current:
                slides.append(current)
            n, key, val = m.groups()
            current = {"n": int(n)}
            _assign(current, key, val)
            continue
        m2 = re.match(r"^(\w+):\s*(.*)$", line)
        if m2 and current is not None:
            key, val = m2.groups()
            _assign(current, key, val)
    if current:
        slides.append(current)
    slides.sort(key=lambda s: s["n"])
    return slides


def _assign(slide, key, val):
    if key not in SLIDE_KEYS:
        raise ValueError(f"unknown slide key '{key}' (slide {slide.get('n')})")
    if key == "focus_y":
        slide[key] = float(val)
    elif key == "blur_regions":
        regions = []
        for chunk in val.split(";"):
            chunk = chunk.strip()
            if not chunk:
                continue
            nums = [int(x.strip()) for x in chunk.split(",")]
            if len(nums) != 4:
                raise ValueError(f"blur_regions must be x0,y0,x1,y1 groups, got '{chunk}'")
            regions.append(tuple(nums))
        slide[key] = regions
    else:
        slide[key] = val


if __name__ == "__main__":
    import sys, json
    print(json.dumps(parse_brief(sys.argv[1]), indent=2))
