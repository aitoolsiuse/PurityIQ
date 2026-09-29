#!/usr/bin/env python3
"""
Build a PurityIQ slideshow post from a brief.

Usage:
    python3 scripts/build_post.py briefs/PIQ-NNN-slug.md [--status built]

For each slide this:
  1. resolves the slide's photo -- a cached Envato/browser file if present,
     else the brief's photo_pin, else the first fitting candidate from a
     parallel Pexels/Pixabay/Openverse/Wikimedia search ("first good fit",
     no runner-up comparisons -- see reference/purityiq-rules.md "Photo
     rules"). All slides resolve in parallel (network-bound).
  2. downloads it full-res, applies blur_regions and/or perspective-fits a
     screenshot if the brief asks for either
  3. composites both TikTok (1080x1920) and Instagram (1080x1350) sizes using the
     approved PIQ-001 look (fixed font size, gradient, drop shadow, logo badge)
Then writes caption.txt, stock-credits.txt, contact_sheet.jpg, copies the brief
into the post folder as brief.md, and updates queue.md.

Never rewrites slide copy: text comes verbatim from the brief. If a line doesn't
fit the frame at the fixed font size, this prints a warning rather than editing it.
"""
import os
import re
import sys
import time
import json
import shutil
import datetime
import argparse
import threading
import concurrent.futures

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brief_parser import parse_brief
import photo_search
import compose
import screenshot_fit
import blur_regions as blur_mod
import contact_sheet as cs_mod
import queue_utils

PROHIBITED_WORDS = [
    "toxic", "poison", "dangerous", "risk", "safe", "safer", "unsafe", "hazardous",
]

# Hard time budget for resolving one slide's photo (searching + picking).
# If it's exceeded, build_slide_photo takes the best candidate available and
# the caller flags it in review.md rather than hunting further.
SLIDE_PHOTO_BUDGET_SECONDS = 60

# Categories where free API sources (Pexels/Pixabay/Openverse/Wikimedia) are
# dominated by branded product photography -- notably cursive-script logos
# (Coca-Cola's Spencerian script confirmed as a real OCR blind spot: tesseract
# reads neither the "Coca-Cola" wordmark itself nor any other text on some of
# these labels). For these, go to Envato first rather than spending the API
# auto-pick's time -- see reference/purityiq-rules.md "Photo rules".
BRAND_HEAVY_KEYWORDS = (
    "soda", "cola", "drink", "beverage", "juice", "candy", "snack", "cookie",
    "cake", "cereal", "packaged", "wrapper", "bottle", "can", "chip",
    "chocolate", "gum", "cupcake",
)


def is_brand_heavy_category(photo_search_term):
    t = (photo_search_term or "").lower()
    return any(kw in t for kw in BRAND_HEAVY_KEYWORDS)


def load_photo_log(post_dir):
    """posts/<post>/photos/sources_log.json: a minimal per-slide record of
    the photo actually used -- {"<n>": {"source", "photo_id", "photo_url",
    "query"}}. No per-source search trail, no justification -- see
    reference/purityiq-rules.md "Photo rules" ("first good fit")."""
    path = os.path.join(post_dir, "photos", "sources_log.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


_PHOTO_LOG_LOCK = threading.Lock()


def write_photo_pick(post_dir, slide_n, source, raw_id, photo_url, query):
    """Records the one photo chosen for a slide. `raw_id` is the source's own
    id (e.g. a Pexels numeric id, or an Envato item UUID); this stores it in
    the same "source:id" convention reference/used-photos.md uses (Envato ids
    are already unique UUIDs and are stored bare, matching that ledger).

    Slides resolve in parallel (main()'s ThreadPoolExecutor), so every call
    here writes to the same sources_log.json -- the lock serializes the
    read-modify-write so concurrent slides never truncate/corrupt each
    other's write."""
    photo_id = str(raw_id) if source == "envato" else f"{source}:{raw_id}"
    path = os.path.join(post_dir, "photos", "sources_log.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _PHOTO_LOG_LOCK:
        log = load_photo_log(post_dir)
        log[str(slide_n)] = {
            "source": source, "photo_id": photo_id,
            "photo_url": photo_url or "", "query": query or "",
        }
        with open(path, "w") as f:
            json.dump(log, f, indent=2)
    return photo_id


def check_photo_pick(post_dir, brief):
    """Minimal gate (see reference/purityiq-rules.md "Photo rules"): fails a
    build only if a slide has no recorded photo, or its photo_id repeats an
    entry already in reference/used-photos.md for a different post or a
    different slide of this same post. Returns a list of problems; empty
    means the build may proceed."""
    post_slug = f"{brief['id']}-{brief['slug']}"
    log = load_photo_log(post_dir)
    ledger = load_used_photos_ledger()
    problems = []
    for slide in brief["slides"]:
        n = slide["n"]
        entry = log.get(str(n))
        if not entry or not entry.get("photo_id"):
            problems.append(f"slide {n}: no photo recorded in sources_log.json")
            continue
        pid = entry["photo_id"]
        for row in ledger:
            if row.get("Photo ID") == pid and not (
                row.get("Post") == post_slug and row.get("Slide") == str(n)
            ):
                problems.append(
                    f"slide {n}: photo {pid} already used in used-photos.md "
                    f"({row.get('Post')} slide {row.get('Slide')}) -- pick a "
                    "different photo"
                )
                break
    return problems


def check_brand_rules(text):
    """Word-boundary match (case-insensitive) so e.g. "safety" passes while
    "safe", "Safe.", "unsafe", "safer" fail. A plain substring match would
    also flag "safe" inside "safety" -- see reference/purityiq-rules.md."""
    problems = []
    for w in PROHIBITED_WORDS:
        if re.search(r"\b" + re.escape(w) + r"\b", text, re.IGNORECASE):
            problems.append(f"prohibited word '{w}'")
    if "—" in text:
        problems.append("em dash")
    for ch in text:
        if ord(ch) > 0x2600:  # rough emoji/symbol range
            problems.append(f"non-text character '{ch}'")
            break
    return problems


def post_dir_for(brief):
    return os.path.join(REPO, "posts", f"{brief['id']}-{brief['slug']}")


def load_used_photos_ledger():
    """Parses reference/used-photos.md's table into a list of dicts keyed by
    its column headers (Photo ID, Source, URL, Post, Slide, Creator, License,
    Credit Required, Sources Searched)."""
    path = os.path.join(REPO, "reference", "used-photos.md")
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path) as f:
        lines = f.readlines()
    header_idx = None
    for i, l in enumerate(lines):
        if l.strip().startswith("| Photo ID"):
            header_idx = i
            break
    if header_idx is None:
        return rows
    cols = [c.strip() for c in lines[header_idx].strip().strip("|").split("|")]
    for l in lines[header_idx + 2:]:
        l = l.rstrip("\n")
        if not l.strip().startswith("|"):
            continue
        vals = [v.strip() for v in l.strip().strip("|").split("|")]
        if len(vals) != len(cols):
            continue
        rows.append(dict(zip(cols, vals)))
    return rows


def save_candidates(candidates, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    manifest = []
    for i, c in enumerate(candidates, 1):
        ext = ".png" if c["download_url"].lower().endswith(".png") else ".jpg"
        thumb_path = os.path.join(out_dir, f"candidate{i}{ext}")
        try:
            photo_search.download(c["download_url"], thumb_path)
        except Exception as e:
            print(f"    [warn] failed to download candidate {i}: {e}")
            continue
        manifest.append({**c, "file": os.path.basename(thumb_path)})
    with open(os.path.join(out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    return manifest


def find_envato_file(post_dir, n):
    """posts/<post>/photos/envato/slideN.<ext>, licensed and downloaded via the
    Claude in Chrome + Envato Elements workflow. Takes priority over everything
    else when present."""
    envato_dir = os.path.join(post_dir, "photos", "envato")
    if not os.path.isdir(envato_dir):
        return None
    for ext in (".jpg", ".jpeg", ".png", ".mp4", ".mov"):
        path = os.path.join(envato_dir, f"slide{n}{ext}")
        if os.path.exists(path):
            meta_path = os.path.join(envato_dir, f"slide{n}.json")
            meta = {}
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    meta = json.load(f)
            return {
                "source": meta.get("source", "envato"),
                "id": meta.get("item_id", ""),
                "page_url": meta.get("item_url", "unknown - fill in slideN.json"),
                "photographer": meta.get("title", "unknown - fill in slideN.json"),
                "download_url": None,
                "width": None,
                "height": None,
                "_local_path": path,
                "_project": meta.get("project"),
            }
    return None


SLIDE6_POOL_DIR = os.path.join(REPO, "assets", "slide6-pool")
SLIDE6_POOL_LOG = os.path.join(REPO, "reference", "slide6-pool.md")
SLIDE6_POOL_LOCK = threading.Lock()
SLIDE6_POOL_LOW_WATERMARK = 5


def load_slide6_pool():
    """Parses reference/slide6-pool.md's table into a list of row dicts, in
    file order (matching the '#' column). See that file's header for the
    schema and reference/purityiq-rules.md "Photo rules" for how slide 6
    photos are picked."""
    rows = []
    if not os.path.exists(SLIDE6_POOL_LOG):
        return rows
    with open(SLIDE6_POOL_LOG) as f:
        lines = f.readlines()
    header_idx = None
    for i, l in enumerate(lines):
        if l.strip().startswith("| #"):
            header_idx = i
            break
    if header_idx is None:
        return rows
    cols = [c.strip() for c in lines[header_idx].strip().strip("|").split("|")]
    for l in lines[header_idx + 2:]:
        l = l.rstrip("\n")
        if not l.strip().startswith("|"):
            continue
        vals = [v.strip() for v in l.strip().strip("|").split("|")]
        if len(vals) != len(cols):
            continue
        rows.append(dict(zip(cols, vals)))
    return rows


def _rewrite_slide6_pool(rows):
    with open(SLIDE6_POOL_LOG) as f:
        lines = f.readlines()
    header_idx = None
    for i, l in enumerate(lines):
        if l.strip().startswith("| #"):
            header_idx = i
            break
    if header_idx is None:
        raise RuntimeError(f"{SLIDE6_POOL_LOG}: couldn't find the table header")
    cols = [c.strip() for c in lines[header_idx].strip().strip("|").split("|")]
    new_table_lines = []
    for r in rows:
        new_table_lines.append("| " + " | ".join(r.get(c, "") for c in cols) + " |\n")
    # Everything after the table (trailing notes) is preserved as-is.
    tail_idx = header_idx + 2
    while tail_idx < len(lines) and lines[tail_idx].strip().startswith("|"):
        tail_idx += 1
    new_lines = lines[:header_idx + 2] + new_table_lines + lines[tail_idx:]
    with open(SLIDE6_POOL_LOG, "w") as f:
        f.writelines(new_lines)


def pick_and_mark_slide6_pool_photo(post_slug, slide_n):
    """Takes the next `unused` row from reference/slide6-pool.md, marks it
    `used` (with this post), appends the matching row to
    reference/used-photos.md, and returns (chosen, local_path) in the same
    shape build_slide_photo()'s other branches produce. Returns None if the
    pool has no unused rows left (falls back to a normal search).

    Warns (via the returned `low` flag folded into the review.md note the
    caller writes) once fewer than SLIDE6_POOL_LOW_WATERMARK rows remain
    unused after this pick -- reference/purityiq-rules.md says to add 10 more
    at that point."""
    with SLIDE6_POOL_LOCK:
        rows = load_slide6_pool()
        if not rows:
            return None
        picked = None
        for r in rows:
            if r.get("Status") == "unused":
                picked = r
                break
        if picked is None:
            return None
        picked["Status"] = "used"
        picked["Used by (post)"] = post_slug
        _rewrite_slide6_pool(rows)
        remaining = sum(1 for r in rows if r.get("Status") == "unused")

    photo_id = picked["Photo ID"]
    source = photo_id.split(":", 1)[0] if ":" in photo_id else photo_id
    raw_id = photo_id.split(":", 1)[1] if ":" in photo_id else photo_id
    local_path = os.path.join(SLIDE6_POOL_DIR, picked["File"])
    if not os.path.exists(local_path):
        raise RuntimeError(
            f"slide6-pool.md row #{picked.get('#')} points at missing file "
            f"{local_path} -- fix the ledger or the pool directory"
        )

    # Append to the master ledger (reference/used-photos.md) the same way
    # every other picked photo is logged there -- enforced here rather than
    # left for the agent to remember, per the current instruction.
    used_photos_path = os.path.join(REPO, "reference", "used-photos.md")
    row_line = (
        f"| {photo_id} | {source} | {picked.get('URL', '')} | {post_slug} | "
        f"{slide_n} | {picked.get('Creator', '')} | no-attribution-required "
        f"(Pexels/Pixabay/Openverse, pre-restricted to no-credit licenses -- "
        f"see purityiq-rules.md) | No | slide6-pool.md #{picked.get('#')} |\n"
    )
    with open(used_photos_path, "a") as f:
        f.write(row_line)

    chosen = {
        "source": source, "id": raw_id,
        "page_url": picked.get("URL", ""), "photographer": picked.get("Creator", ""),
    }
    return chosen, local_path, remaining


def build_slide_photo(slide, post_dir, photos_dir, candidates_dir, keep_photos=False):
    """Resolves one slide's photo, fastest path first: a cached Envato file,
    then a locked photo_pin (no search needed), then --keep-photos reuse of
    an already-built photos/slideN.jpg, then a fresh parallel API search
    ("first good fit" -- see reference/purityiq-rules.md "Photo rules")."""
    n = slide["n"]
    final_path = os.path.join(photos_dir, f"slide{n}.jpg")
    reused = False  # True only for the --keep-photos branch below

    envato = find_envato_file(post_dir, n)
    if envato:
        print(f"  slide {n}: using Envato Elements file (photos/envato/slide{n}.*)")
        chosen = envato
        shutil.copy(envato["_local_path"], final_path)
    elif slide.get("photo_pin"):
        chosen = photo_search.resolve_pin(slide["photo_pin"])
        print(f"  slide {n}: using pinned photo {slide['photo_pin']}")
        raw_path = os.path.join(photos_dir, f"slide{n}_raw.jpg")
        photo_search.download(chosen["download_url"], raw_path)
        shutil.copy(raw_path, final_path)
        os.remove(raw_path)
    elif keep_photos and os.path.exists(final_path):
        # This file is already fully processed (blur/screenshot already
        # baked in) from whichever run originally produced it -- reused =
        # True below skips blur_regions/screenshot so they never run again
        # on top of themselves. Bug history: re-running composite_screenshot
        # on an already-composited photo makes find_screen_quad() detect a
        # *new* bright region inside the pasted screenshot itself and paste
        # a second, shifted copy over the first (confirmed by reproducing it
        # on posts/PIQ-022-acrylamide's original slide 6 photo,
        # pexels:7412033 -- see photos/candidates or git history for that
        # post's now-superseded first slide6.jpg).
        print(f"  slide {n}: --keep-photos, reusing existing photos/slide{n}.jpg")
        reused = True
        existing = load_photo_log(post_dir).get(str(n))
        if existing:
            raw_id = existing["photo_id"]
            if ":" in raw_id:
                raw_id = raw_id.split(":", 1)[1]
            chosen = {"source": existing["source"], "id": raw_id,
                      "page_url": existing.get("photo_url", ""), "photographer": "kept"}
        else:
            chosen = {"source": "kept", "id": "existing", "page_url": "",
                      "photographer": "kept-existing, no prior sources_log.json record"}
    elif n == 6:
        # Slide 6 always pulls from the pre-validated pool
        # (assets/slide6-pool/ + reference/slide6-pool.md) instead of
        # searching -- every photo in it is already confirmed to composite
        # cleanly with the current screenshot asset. Falls through to a
        # normal search only if the pool is empty (shouldn't happen once
        # it's kept topped up -- see the low-watermark warning below).
        post_slug = os.path.basename(post_dir)
        result = pick_and_mark_slide6_pool_photo(post_slug, n)
        if result is None:
            print(f"  slide {n}: slide6-pool.md has no unused rows left -- "
                  f"falling back to a normal search (add 10 more to the pool "
                  f"after this build)")
            chosen = None
        else:
            chosen, pool_path, remaining = result
            print(f"  slide {n}: using slide6-pool photo {chosen['source']}:{chosen['id']} "
                  f"({remaining} unused left in pool)")
            shutil.copy(pool_path, final_path)
            if remaining < SLIDE6_POOL_LOW_WATERMARK:
                log_low_slide6_pool(post_dir, remaining)
        if chosen is None:
            search_term = slide.get("photo_search", "")
            started = time.monotonic()
            print(f"  slide {n}: searching '{search_term}'")
            candidates = photo_search.get_candidates(
                search_term, count=6, timeout=SLIDE_PHOTO_BUDGET_SECONDS
            )
            slide_cand_dir = os.path.join(candidates_dir, f"slide{n}")
            manifest = save_candidates(candidates, slide_cand_dir)
            if not manifest:
                raise RuntimeError(f"slide {n}: no candidates found and no photo_pin set")
            top6 = manifest[:6]
            chosen = None
            for c in top6:
                thumb_path = os.path.join(slide_cand_dir, c["file"])
                if photo_search.has_readable_text(thumb_path):
                    continue
                chosen = c
                break
            if chosen is None:
                raise RuntimeError(
                    f"slide {n}: all {len(top6)} candidates checked have readable text "
                    "in frame (likely a brand name or label) -- source this slide via "
                    "Envato Elements instead (see reference/purityiq-rules.md "
                    "\"Photo rules\")"
                )
            elapsed = time.monotonic() - started
            if elapsed > SLIDE_PHOTO_BUDGET_SECONDS:
                log_slow_slide_pick(post_dir, n, elapsed)
            raw_path = os.path.join(photos_dir, f"slide{n}_raw.jpg")
            photo_search.download(chosen["download_url"], raw_path)
            shutil.copy(raw_path, final_path)
            os.remove(raw_path)
    else:
        search_term = slide.get("photo_search", "")
        if is_brand_heavy_category(search_term):
            raise RuntimeError(
                f"slide {n}: photo_search {search_term!r} is a drink/candy/"
                "packaged-goods category -- free API sources are dominated by "
                "branded shots there (and OCR won't reliably catch stylized "
                "script logos like Coca-Cola's). Search Envato Elements first "
                "instead (see reference/purityiq-rules.md \"Photo rules\")."
            )
        started = time.monotonic()
        print(f"  slide {n}: searching '{search_term}'")
        candidates = photo_search.get_candidates(
            search_term, count=6, timeout=SLIDE_PHOTO_BUDGET_SECONDS
        )
        slide_cand_dir = os.path.join(candidates_dir, f"slide{n}")
        manifest = save_candidates(candidates, slide_cand_dir)
        if not manifest:
            raise RuntimeError(f"slide {n}: no candidates found and no photo_pin set")

        # OCR text filter: skip any of the top 6 candidates with a readable
        # 4+ letter word anywhere in frame (brand name, label text) -- see
        # reference/purityiq-rules.md "Photo rules". Best-effort: if OCR
        # isn't installed, has_readable_text() always returns False and this
        # behaves exactly like the old blind "first candidate" pick.
        top6 = manifest[:6]
        chosen = None
        for c in top6:
            thumb_path = os.path.join(slide_cand_dir, c["file"])
            if photo_search.has_readable_text(thumb_path):
                continue
            chosen = c
            break
        if chosen is None:
            raise RuntimeError(
                f"slide {n}: all {len(top6)} candidates checked have readable text "
                "in frame (likely a brand name or label) -- source this slide via "
                "Envato Elements instead (see reference/purityiq-rules.md "
                "\"Photo rules\")"
            )
        print(f"    first OCR-clean candidate ({chosen['source']}:{chosen['id']}) - review before posting")

        elapsed = time.monotonic() - started
        if elapsed > SLIDE_PHOTO_BUDGET_SECONDS:
            log_slow_slide_pick(post_dir, n, elapsed)

        raw_path = os.path.join(photos_dir, f"slide{n}_raw.jpg")
        photo_search.download(chosen["download_url"], raw_path)
        shutil.copy(raw_path, final_path)
        os.remove(raw_path)

    write_photo_pick(
        post_dir, n, chosen["source"], chosen["id"], chosen["page_url"],
        slide.get("photo_search", ""),
    )

    if reused:
        # final_path already has blur_regions/screenshot baked in from the
        # run that actually resolved this photo -- redoing either here would
        # double them (see the reused=True comment above).
        return chosen, final_path

    if slide.get("blur_regions"):
        blur_mod.apply_blur_regions(final_path, slide["blur_regions"], out_path=final_path)
        print(f"    blurred {len(slide['blur_regions'])} region(s)")

    if slide.get("screenshot"):
        shot_path = os.path.join(REPO, slide["screenshot"])
        screenshot_fit.composite_screenshot(final_path, shot_path, final_path)
        print(f"    perspective-fit screenshot {slide['screenshot']}")

    return chosen, final_path


def slide_has_existing_photo(slide, post_dir, photos_dir):
    """True if this slide's photo is already resolved without a new search:
    a locked photo_pin, a cached Envato/browser file, or an already-built
    photos/slideN.jpg from a previous run."""
    n = slide["n"]
    if slide.get("photo_pin"):
        return True
    if find_envato_file(post_dir, n):
        return True
    if os.path.exists(os.path.join(photos_dir, f"slide{n}.jpg")):
        return True
    return False


def log_keep_photos_use(post_dir):
    """--keep-photos skipped the photo-pick gate for this build; note it in
    review.md so this isn't only in scrollback. Appends (creates the file if
    it doesn't exist yet)."""
    review_path = os.path.join(post_dir, "review.md")
    line = (
        f"\n- `--keep-photos` used on {datetime.date.today().isoformat()}: "
        "photo-pick gate skipped because every slide's photo was already "
        "pinned/cached/existing; no photo changes this build.\n"
    )
    with open(review_path, "a") as f:
        f.write(line)


def log_slow_slide_pick(post_dir, slide_n, elapsed):
    """A slide's photo search ran past the 60s budget; note it in review.md
    (the pick itself -- best available -- still stands, per the speed rule
    in reference/purityiq-rules.md "Photo rules")."""
    review_path = os.path.join(post_dir, "review.md")
    line = (
        f"\n- slide {slide_n}: photo search took {elapsed:.0f}s, over the "
        f"{SLIDE_PHOTO_BUDGET_SECONDS}s budget -- took the best candidate "
        "available rather than searching further.\n"
    )
    with open(review_path, "a") as f:
        f.write(line)


def log_low_slide6_pool(post_dir, remaining):
    """Warns in review.md when a slide-6 pool pick leaves fewer than
    SLIDE6_POOL_LOW_WATERMARK rows unused -- reference/purityiq-rules.md
    ("Photo rules") says to add 10 more at that point."""
    review_path = os.path.join(post_dir, "review.md")
    line = (
        f"\n- slide 6 pool (reference/slide6-pool.md) is down to {remaining} "
        f"unused photo(s), under the {SLIDE6_POOL_LOW_WATERMARK}-photo "
        "watermark -- add 10 more (search + auto-filter + mandatory visual "
        "review, same process as the original 30).\n"
    )
    with open(review_path, "a") as f:
        f.write(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief_path")
    ap.add_argument("--status", default="built")
    ap.add_argument(
        "--keep-photos", action="store_true",
        help="Skip the photo-pick gate and reuse already-built photos, but "
             "only if every slide's photo is already pinned, already cached "
             "in photos/envato/, or already built in photos/ from a "
             "previous run -- i.e. this run changes no photos. Any slide "
             "that would need a new photo pick still goes through the gate "
             "normally.",
    )
    args = ap.parse_args()

    brief = parse_brief(args.brief_path)
    post_dir = post_dir_for(brief)
    photos_dir = os.path.join(post_dir, "photos")
    candidates_dir = os.path.join(photos_dir, "candidates")
    envato_dir = os.path.join(photos_dir, "envato")
    tiktok_dir = os.path.join(post_dir, "tiktok")
    ig_dir = os.path.join(post_dir, "instagram")
    video_dir = os.path.join(post_dir, "video")
    for d in (photos_dir, candidates_dir, envato_dir, tiktok_dir, ig_dir, video_dir):
        os.makedirs(d, exist_ok=True)

    shutil.copy(args.brief_path, os.path.join(post_dir, "brief.md"))

    keep_photos_applies = args.keep_photos and all(
        slide_has_existing_photo(s, post_dir, photos_dir) for s in brief["slides"]
    )
    if args.keep_photos and not keep_photos_applies:
        print(
            "--keep-photos was passed, but at least one slide has no "
            "pinned/cached/existing photo -- that slide needs a new pick, "
            "so photos are still resolved (and gated) normally this run.\n"
        )

    print(f"Building {brief['id']} - {brief['title']}")

    # Phase 1: resolve every slide's photo in parallel (network-bound --
    # this is the biggest speed win). Each call is independent and safe to
    # run concurrently: distinct files, and write_photo_pick's read-modify
    # -write of sources_log.json only ever touches this post's own file.
    def _resolve(slide):
        return slide["n"], build_slide_photo(
            slide, post_dir, photos_dir, candidates_dir, keep_photos=keep_photos_applies
        )

    photo_results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(brief["slides"]))) as ex:
        for n, result in ex.map(_resolve, brief["slides"]):
            photo_results[n] = result

    if keep_photos_applies:
        print("--keep-photos: every slide's photo was already pinned/cached/existing.")
        log_keep_photos_use(post_dir)
    else:
        gate_problems = check_photo_pick(post_dir, brief)
        if gate_problems:
            print(f"\nBUILD FAILED: {brief['id']} - photo pick problem(s)\n")
            for p in gate_problems:
                print(f"  - {p}")
            sys.exit(1)

    # Phase 2: composite (sequential -- fast, CPU-bound, keeps output order
    # deterministic).
    warnings = []
    credits = []
    for slide in brief["slides"]:
        n = slide["n"]
        problems = check_brand_rules(slide["text"])
        if problems:
            warnings.append(f"slide {n} copy issue: {', '.join(problems)} (fix in the brief, not here)")

        chosen, photo_path = photo_results[n]
        credits.append({"n": n, "brief": slide.get("photo_search", ""), **chosen,
                         "screenshot": slide.get("screenshot")})

        for fmt_key, out_dir in (("tiktok", tiktok_dir), ("instagram", ig_dir)):
            img = compose.render_slide(photo_path, slide["text"], slide.get("focus_y", 0.5), fmt_key)
            img.save(os.path.join(out_dir, f"slide{n}.jpg"), quality=92)

            # rough fit check: warn if the fixed font size overflows the frame badly
            fmt = compose.FORMATS[fmt_key]
            from PIL import ImageDraw
            probe = ImageDraw.Draw(img)
            font = compose.load_font(fmt["font_size"])
            max_width = int(fmt["w"] * (1 - fmt["right_exclusion"])) - fmt["margin_x"]
            lines = compose.wrap_text(slide["text"], font, max_width, probe)
            line_h = int(fmt["font_size"] * 1.28)
            total_h = line_h * len(lines)
            if total_h > fmt["h"] * 0.75:
                warnings.append(
                    f"slide {n} ({fmt_key}): text runs {len(lines)} lines and may crowd the frame "
                    "- consider a shorter line in the brief"
                )
        print(f"  slide {n}: composited both sizes")

    with open(os.path.join(post_dir, "caption.txt"), "w") as f:
        f.write(brief["caption"] + "\n")

    with open(os.path.join(post_dir, "stock-credits.txt"), "w") as f:
        f.write(f"{brief['id']} - {brief['title']} - Stock Photo Credits\n\n")
        for c in credits:
            f.write(f"Slide {c['n']} ({c['brief']}):\n")
            f.write(f"  Source: {c['source'].title()}\n")
            f.write(f"  Photo URL: {c['page_url']}\n")
            f.write(f"  Photographer: {c['photographer']}\n")
            if c.get("_project"):
                f.write(f"  Envato project: {c['_project']}\n")
            if c.get("screenshot"):
                f.write(f"  Screen composited with: {c['screenshot']}\n")
            f.write("\n")

    cs_mod.build_contact_sheet(tiktok_dir, os.path.join(post_dir, "contact_sheet.jpg"), len(brief["slides"]))

    queue_utils.upsert(brief["id"], brief["slug"], args.status)

    print(f"\nDone: {post_dir}")
    if warnings:
        print("\nReview needed:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\nNo copy-fit or brand-rule warnings.")


if __name__ == "__main__":
    main()
