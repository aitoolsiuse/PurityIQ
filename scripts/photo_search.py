"""Multi-source photo search + candidate download.

Core API sources, searched for every slide, in parallel, one query each --
"first good fit" (see reference/purityiq-rules.md "Photo rules"): pick the
first candidate that fits, has no readable brand label, and isn't a repeat,
no runner-up comparisons.
  - Pexels (key required) -- Pexels License, no attribution required
  - Pixabay (key required) -- Pixabay Content License, no attribution required
  - Openverse (no key; restricted server-side to cc0/pdm only via the
    `license` param -- CC BY and every other license that needs credit is
    excluded, since captions never carry credit lines)
  - Wikimedia Commons (no key; restricted to CC0 / public domain only, same
    reason -- CC BY is excluded here too)
Envato Elements (via Claude in Chrome) is also core but isn't code in this
file -- it's searched by the agent. Situational sources (USDA Flickr direct
browse, Unsplash, Foodiesfeed) are hand-searched via Chrome too, only when a
slide's subject fits.

get_candidates() runs the 4 API sources concurrently (concurrent.futures) and
returns the combined candidate list -- no per-source logging happens here;
build_post.py logs the single winning pick per slide once one is chosen.

API keys are read with get_api_key(), which checks os.environ first, then
falls back to parsing the matching "export NAME=..." line out of ~/.zshrc.
The key value itself is never printed, logged, or put in a shell command --
only "<NAME> not set" is ever surfaced when a key is missing from both
places. Network/HTTP errors are reported without echoing the request URL,
since Pixabay's URL scheme carries the key in the query string.
"""
import os
import re
import json
import ssl
import certifi
import urllib.request
import urllib.parse
import urllib.error
import concurrent.futures

try:
    import pytesseract
    from PIL import Image, ImageOps
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

CTX = ssl.create_default_context(cafile=certifi.where())
UA = {"User-Agent": "Mozilla/5.0"}

# Licenses acceptable for the Wikimedia Commons source (lowercased prefixes).
# CC0/public domain only -- no CC BY, no CC BY-SA, no other license that
# would need a credit line (captions never carry one -- see
# reference/purityiq-rules.md "Photo rules").
_WIKIMEDIA_ALLOWED_LICENSES = ("cc0", "public domain", "pd")


def get_api_key(name):
    """os.environ first; else parse the "export NAME=..." line from ~/.zshrc.
    Never prints or logs the value. Returns None if not found in either place."""
    val = os.environ.get(name)
    if val:
        return val
    zshrc = os.path.expanduser("~/.zshrc")
    try:
        with open(zshrc) as f:
            content = f.read()
    except OSError:
        return None
    pattern = re.compile(r"^export\s+" + re.escape(name) + r"\s*=\s*(.+)$")
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        m = pattern.match(stripped)
        if m:
            v = m.group(1).strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
                v = v[1:-1]
            return v
    return None


def _get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        return json.load(r)


def _safe_error(e):
    """Render an exception without ever including a request URL (which may
    carry an API key in its query string, e.g. Pixabay)."""
    if isinstance(e, urllib.error.HTTPError):
        return f"HTTP {e.code} {e.reason}"
    if isinstance(e, urllib.error.URLError):
        return f"URLError: {e.reason}"
    return f"{type(e).__name__}: {e}"


# ---------------------------------------------------------------- Pexels ---

def pexels_search(query, per_page=6, orientation="portrait", api_key=None):
    key = api_key or get_api_key("PEXELS_API_KEY")
    if not key:
        raise RuntimeError("PEXELS_API_KEY not set")
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": per_page, "orientation": orientation}
    )
    data = _get(url, {"Authorization": key})
    out = []
    for p in data.get("photos", []):
        out.append({
            "source": "pexels",
            "id": p["id"],
            "page_url": p["url"],
            "photographer": p["photographer"],
            "download_url": p["src"]["original"],
            "width": p["width"],
            "height": p["height"],
            "license": "Pexels License (free to use, attribution not required)",
        })
    return out


def pexels_get(photo_id, api_key=None):
    key = api_key or get_api_key("PEXELS_API_KEY")
    if not key:
        raise RuntimeError("PEXELS_API_KEY not set")
    data = _get(f"https://api.pexels.com/v1/photos/{photo_id}", {"Authorization": key})
    return {
        "source": "pexels",
        "id": data["id"],
        "page_url": data["url"],
        "photographer": data["photographer"],
        "download_url": data["src"]["original"],
        "width": data["width"],
        "height": data["height"],
        "license": "Pexels License (free to use, attribution not required)",
    }


# --------------------------------------------------------------- Pixabay ---

def pixabay_search(query, per_page=6, orientation="vertical", api_key=None):
    key = api_key or get_api_key("PIXABAY_API_KEY")
    if not key:
        raise RuntimeError("PIXABAY_API_KEY not set")
    url = "https://pixabay.com/api/?" + urllib.parse.urlencode({
        "key": key, "q": query, "image_type": "photo",
        "orientation": orientation, "per_page": per_page, "safesearch": "true",
    })
    data = _get(url)
    out = []
    for h in data.get("hits", []):
        out.append({
            "source": "pixabay",
            "id": h["id"],
            "page_url": h["pageURL"],
            "photographer": h["user"],
            "download_url": h["largeImageURL"],
            "width": h.get("imageWidth"),
            "height": h.get("imageHeight"),
            "license": "Pixabay License (free to use, attribution not required)",
        })
    return out


def pixabay_get(photo_id, api_key=None):
    key = api_key or get_api_key("PIXABAY_API_KEY")
    if not key:
        raise RuntimeError("PIXABAY_API_KEY not set")
    data = _get(f"https://pixabay.com/api/?key={key}&id={photo_id}")
    hits = data.get("hits", [])
    if not hits:
        raise ValueError(f"pixabay id {photo_id} not found")
    h = hits[0]
    return {
        "source": "pixabay",
        "id": h["id"],
        "page_url": h["pageURL"],
        "photographer": h["user"],
        "download_url": h["largeImageURL"],
        "width": h.get("imageWidth"),
        "height": h.get("imageHeight"),
        "license": "Pixabay License (free to use, attribution not required)",
    }


# -------------------------------------------------------------- Openverse --

# Openverse's license_type=commercial is NOT sufficient on its own -- it still
# lets by-sa and by-nd through (verified against the live API), and "by" on
# its own needs a credit line, which captions never carry (see
# reference/purityiq-rules.md "Photo rules"). The `license` parameter
# restricts to an explicit list: cc0 and pdm (public domain mark) only, both
# no-credit-required. _OPENVERSE_ALLOWED_LICENSES is also enforced as a
# Python-side filter in case the API ever returns something outside that list.
_OPENVERSE_ALLOWED_LICENSES = ("cc0", "pdm")
_OPENVERSE_NO_CREDIT_LICENSES = ("cc0", "pdm")


def _openverse_record(r):
    lic = (r.get("license") or "").lower()
    if lic not in _OPENVERSE_ALLOWED_LICENSES:
        return None
    return {
        "source": "openverse",
        "id": r.get("id"),
        "page_url": r.get("foreign_landing_url") or r.get("url"),
        "photographer": r.get("creator") or "unknown",
        "download_url": r.get("url"),
        "width": r.get("width"),
        "height": r.get("height"),
        "license": f"{lic.upper()} {r.get('license_version') or ''}".strip(),
        "credit_required": lic not in _OPENVERSE_NO_CREDIT_LICENSES,
    }


def openverse_search(query, per_page=6, license_type=None, source=None, license=None):
    """No key required. Restricted server-side to cc0/pdm/by via the
    `license` param (not license_type, which also admits by-sa/by-nd); the
    same allow-list is re-checked in Python. Pass source='flickr' for the
    USDA-Flickr pass. `license_type` is accepted for backwards compatibility
    but ignored if `license` isn't also given -- callers should not rely on
    license_type alone."""
    params = {
        "q": query, "page_size": per_page,
        "license": license or ",".join(_OPENVERSE_ALLOWED_LICENSES),
        "mature": "false",
    }
    if source:
        params["source"] = source
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params)
    data = _get(url)
    out = []
    for r in data.get("results", []):
        rec = _openverse_record(r)
        if rec:
            out.append(rec)
    return out


def openverse_get(item_id):
    data = _get(f"https://api.openverse.org/v1/images/{item_id}/")
    rec = _openverse_record(data)
    if not rec:
        lic = (data.get("license") or "unknown").upper()
        raise ValueError(
            f"openverse item {item_id} has license '{lic}', which is not in "
            f"the allowed list {_OPENVERSE_ALLOWED_LICENSES} (no by/by-sa/by-nd/by-nc -- "
            "captions never carry a credit line)"
        )
    return rec


# ------------------------------------------------------------- Wikimedia ---

def wikimedia_search(query, per_page=6):
    """No key required. Filtered to CC0 / public domain / CC BY only --
    CC BY-SA and other share-alike/non-commercial licenses are excluded."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrnamespace": 6,
        "gsrlimit": per_page * 4,  # overfetch, then filter by license below
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "format": "json",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    data = _get(url)
    pages = (data.get("query") or {}).get("pages") or {}
    out = []
    for page in pages.values():
        infos = page.get("imageinfo") or []
        if not infos:
            continue
        info = infos[0]
        meta = info.get("extmetadata") or {}
        lic_raw = (meta.get("LicenseShortName", {}).get("value") or "").strip()
        lic = lic_raw.lower()
        if lic.startswith("cc by-sa") or "sa" in lic.replace("cc by", ""):
            continue
        if not any(lic.startswith(a) for a in _WIKIMEDIA_ALLOWED_LICENSES):
            continue
        artist = re.sub("<[^>]+>", "", meta.get("Artist", {}).get("value") or "unknown").strip()
        out.append({
            "source": "wikimedia",
            "id": page.get("pageid"),
            "page_url": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(page.get('title', ''))}",
            "photographer": artist or "unknown",
            "download_url": info.get("url"),
            "width": info.get("width"),
            "height": info.get("height"),
            "license": lic_raw,
            "credit_required": not lic.startswith(("cc0", "public domain", "pd")),
        })
        if len(out) >= per_page:
            break
    return out


def wikimedia_get(pageid):
    params = {
        "action": "query", "pageids": pageid, "prop": "imageinfo",
        "iiprop": "url|extmetadata", "format": "json",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    data = _get(url)
    pages = (data.get("query") or {}).get("pages") or {}
    page = next(iter(pages.values()), None)
    if not page or not page.get("imageinfo"):
        raise ValueError(f"wikimedia pageid {pageid} not found")
    info = page["imageinfo"][0]
    meta = info.get("extmetadata") or {}
    lic_raw = (meta.get("LicenseShortName", {}).get("value") or "").strip()
    artist = re.sub("<[^>]+>", "", meta.get("Artist", {}).get("value") or "unknown").strip()
    return {
        "source": "wikimedia",
        "id": pageid,
        "page_url": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(page.get('title', ''))}",
        "photographer": artist or "unknown",
        "download_url": info.get("url"),
        "width": info.get("width"),
        "height": info.get("height"),
        "license": lic_raw,
        "credit_required": not lic_raw.lower().startswith(("cc0", "public domain", "pd")),
    }


# ------------------------------------------------------------------- OCR ---

def has_readable_text(image_path, min_word_len=4):
    """Best-effort brand/label filter: True if OCR finds a legible word of
    min_word_len+ letters anywhere in the frame -- the signal used to skip a
    candidate that likely shows a readable brand name or label text (see
    reference/purityiq-rules.md "Photo rules"). Grayscale conversion catches
    meaningfully more real label text than OCR-ing the raw photo (verified:
    a Coca-Cola bottle photo's stylized script logo itself isn't read, but
    "ORIGINAL TASTE" and "DELICIOUS AND REFRESHING" on the same label are,
    which is enough to correctly skip it).

    If OCR isn't available (pytesseract/tesseract not installed) this always
    returns False -- no filtering, not a build failure; callers fall back to
    picking the first candidate as before."""
    if not OCR_AVAILABLE:
        return False
    try:
        im = Image.open(image_path)
        im.thumbnail((1600, 1600))  # OCR doesn't need full resolution; faster
        gray = ImageOps.grayscale(im)
        text = pytesseract.image_to_string(gray)
    except Exception:
        return False
    return bool(re.search(r"[A-Za-z]{%d,}" % min_word_len, text))


# ------------------------------------------------------------- aggregate ---

def _msg(e):
    """Safe-to-print message for a source failure: a missing-key RuntimeError
    reads as-is ("<NAME> not set", never the key value); anything else goes
    through _safe_error so no request URL/key leaks into the output."""
    s = str(e)
    if isinstance(e, RuntimeError) and s.endswith("not set"):
        return s
    return _safe_error(e)


def get_candidates(query, count=6, timeout=20):
    """Searches the 4 core API sources CONCURRENTLY (one query each, no
    per-source runner-up passes) and returns the combined candidate list.
    Each source's failure (including a missing key) is caught and reported
    individually; the rest still run. `timeout` bounds the whole parallel
    search in seconds -- a source still running past it is abandoned and
    reported as timed out, and whatever the other sources returned is used.

    No logging happens here -- build_post.py records the single winning pick
    per slide once one is chosen (see reference/purityiq-rules.md "Photo
    rules": "first good fit", no written justification per source)."""
    tasks = {
        "pexels": lambda: pexels_search(query, per_page=count),
        "pixabay": lambda: pixabay_search(query, per_page=max(3, count)),
        "openverse": lambda: openverse_search(query, per_page=count),
        "wikimedia": lambda: wikimedia_search(query, per_page=count),
    }
    candidates = []
    ex = concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks))
    try:
        futures = {ex.submit(fn): name for name, fn in tasks.items()}
        done, not_done = concurrent.futures.wait(futures, timeout=timeout)
        for fut in done:
            try:
                candidates.extend(fut.result())
            except Exception as e:
                print(f"  [source {futures[fut]}] {_msg(e)}")
        for fut in not_done:
            print(f"  [source {futures[fut]}] timed out after {timeout}s")
    finally:
        ex.shutdown(wait=False, cancel_futures=True)
    return candidates


def resolve_pin(pin):
    """pin like 'pexels:10886018', 'pixabay:5953802', 'openverse:<uuid>',
    or 'wikimedia:<pageid>'."""
    source, _, pid = pin.partition(":")
    if source == "pexels":
        return pexels_get(pid)
    elif source == "pixabay":
        return pixabay_get(pid)
    elif source == "openverse":
        return openverse_get(pid)
    elif source == "wikimedia":
        return wikimedia_get(pid)
    raise ValueError(f"unrecognized photo_pin source: {pin}")


def download(url, dest_path):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r, open(dest_path, "wb") as f:
        f.write(r.read())
    return dest_path
