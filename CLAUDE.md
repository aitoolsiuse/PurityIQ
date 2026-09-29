# PurityIQ Social — standing rules

This repo is a repeatable pipeline for building PurityIQ TikTok/Instagram slideshow
posts. `scripts/build_post.py` builds one post from one brief. Read this file before
touching any post.

## Format

Follow the "PurityIQ Slideshows" section of the `tiktok-slideshow-strategist` skill
for every post: 7 slides max (8 only if the story truly needs it), full-bleed photo
on every slide, bold white line in the lower third over a dark bottom gradient, the
PurityIQ logo badge + wordmark top-left, the required benefit slide (second to
last), and a final CTA slide. No text-only cards. No separate sources slide —
sources go in the caption.

## Mandatory reading

Before touching any post, read `reference/purityiq-rules.md` (what PurityIQ is, story
fit test, verification standard, banned words, slide 6 rule) and
`reference/story-bank.md` (candidate stories and their status). Both are binding.

## Copy

- Briefs written by the user are theirs: never rewrite, shorten or "improve" a slide's
  copy or claims. If a line doesn't fit or a claim looks unsupported, report it.
- Briefs produced by `/next-post` (`.claude/commands/next-post.md`) are written by
  Claude under `reference/purityiq-rules.md`: every claim verified against a primary
  source, source table in `briefs/PIQ-NNN-slug.sources.md`. Once written, the same
  rule applies: don't quietly edit copy to make it fit; flag it in `review.md`.

## Brand vocabulary

Never use: toxic, poison, dangerous, risk, safe, safer, unsafe, hazardous.
No emoji. No em dashes.
`build_post.py` scans each slide's text for these and prints a warning; it does not
block the build or silently fix the copy.

## Copy rules (full detail in `reference/purityiq-rules.md`)

- Word caps: slide 1 max 12 words, slides 2-5 max 14 words each, slide 6 max 18
  words, slide 7 is the fixed CTA.
- Story order: 1 hook (why a parent cares) → 2 what/where → 3 the divergence →
  4 strongest attributed fact → 5 what to check on the label → 6 benefit → 7 CTA.
- Plain words only: name the body ("California"), not the acronym ("OEHHA");
  drop units like "parts per million" from slide text. One idea per slide.
  Shortening never changes a claim's meaning — every line still traces to its
  source in the post's `.sources.md`.

## Sourcing photos and video

Target: under 10 minutes per post, end to end. Photo sourcing is "first good
fit" — pick the first candidate that fits, has no readable brand label (or a
blurrable one), and isn't a repeat, and move on. No runner-up comparisons, no
written justifications, no situational sources unless nothing else works.
Skip AI-generated images from any source.

- **API, in parallel, one query each** (`scripts/photo_search.py`'s
  `get_candidates()`, which `build_post.py` calls automatically — this runs
  Pexels, Pixabay, Openverse, and Wikimedia concurrently, not one after
  another): Pexels (Pexels License), Pixabay (Pixabay Content License),
  Openverse (restricted server-side to `license=cc0,pdm` — CC BY and
  anything else needing credit is excluded), Wikimedia Commons (CC0 / public
  domain only, same reason). All four are no-attribution-required licenses,
  so nothing here ever needs a caption credit line.
  - **OCR text filter, automatic**: `build_post.py` runs OCR
    (`photo_search.has_readable_text()`) on each of the top 6 candidates and
    skips any with a readable 4+ letter word in frame before taking the
    first one that passes — no manual review needed for this. It's
    best-effort: tesseract doesn't reliably read stylized cursive script
    (confirmed on Coca-Cola's wordmark specifically), so it catches most
    printed/block-letter text but not every cursive logo. If all 6 fail
    OCR, or if the slide is a drink/candy/packaged-goods category to begin
    with (next bullet), `build_post.py` raises instead of guessing — go to
    Envato for that slide.
- **Drink, candy, and packaged-goods slides go to Envato first, not API.**
  `build_post.py` detects this from the slide's `photo_search` term
  (`is_brand_heavy_category()`) and refuses the API auto-pick outright for
  these — free sources are dominated by branded shots there, exactly where
  the OCR filter's cursive-script blind spot matters most.
- **Envato Elements, via Claude in Chrome** — for drink/candy/packaged-goods
  slides (always, see above), or whenever the API auto-pick had no good fit
  for another slide (slide 6 does not use this — see the pool section
  below). One search, pick from the first
  page — no bulk downloads, no AI tools (Generate, Riff, AI credits). Tell
  the user to run `/chrome` if it isn't connected. On the first stock
  download of each session, read the sidebar credit count before and after;
  if a download reduced it, stop and tell the user. License it to a project
  named for the post ID (e.g. `PIQ-002`), creating it if needed. Move the
  downloaded file from `~/Downloads` to
  `posts/<post>/photos/envato/slideN.<ext>`, and write a
  `posts/<post>/photos/envato/slideN.json` sidecar with `item_url`, `title`,
  `project`, and `source`. `build_post.py` always checks
  `photos/envato/slideN.*` first and uses it without searching further —
  that folder name is a holdover; it holds the chosen file regardless of
  which source it came from.

No situational sources (USDA Flickr direct browse, Unsplash, Foodiesfeed) —
the API-then-Envato order above covers every slide.

Across all sources: no photo repeats across posts — check
`reference/used-photos.md` before every pick, and reuse an earlier item only
if it hasn't appeared in the last 5 posts and no unused option exists. Slide
6's photo comes from the pool (below), not a search. Slide 7 always gets a
topic-matched photo (a parent in the relevant aisle or with a relevant
product) — never the same slide 7 photo twice.

### Slide 6: pre-validated photo pool, not a search

`build_post.py` pulls slide 6's photo from `assets/slide6-pool/` +
`reference/slide6-pool.md` instead of searching or going to Envato: it takes
the next `unused` row, marks it `used` with the post ID, copies the file into
`posts/<post>/photos/slide6.jpg`, appends it to `reference/used-photos.md`,
and then runs the normal perspective-fit screenshot composite on it — nothing
manual needed for a normal build. Every pool photo (hand holding a phone,
screen facing camera, no readable text) was visually confirmed ahead of time
to composite cleanly against the current `assets/purityiq-scan-screen.png`,
so a per-post visual check of slide 6's photo *fit* is no longer required —
still glance at the built slide like any other. If the pool is empty,
`build_post.py` falls back to a normal search for that one slide and prints a
warning; flag this in `review.md`. When a pick leaves fewer than 5 rows
`unused`, `build_post.py` logs a warning to `review.md` itself — refill by
adding 10 more rows, following the same process the pool was built with
(search several diverse queries → `has_readable_text()` OCR filter →
`screenshot_fit.find_screen_quad()` geometry filter → composite each survivor
against the current screenshot asset → **visually review every one** for
clean full-screen coverage, correct perspective, no ghosting, a real hand
holding the phone, and screen facing camera — see `reference/slide6-pool.md`
for the exact table format to append to).

**No credit lines in captions, ever.** Only use photos whose license needs no
attribution — the sources above are all pre-restricted to that, so a correct
pick never needs one. Never put a "Photo: creator / license" line in a
caption.

Reject readable brand labels (or blur them with `blur_regions` in the brief), gore,
and anything that contradicts the slide's text. The build script cannot judge this
on its own — after any build that wasn't a pinned/approved rebuild, visually review
the chosen photo per slide and report which ones you're unsure about.

### Enforced: every slide needs a recorded, non-repeating photo

`build_post.py` resolves every slide's photo itself (cached Envato file,
photo_pin, or the first fitting API candidate) and writes a minimal record to
`posts/<post>/photos/sources_log.json` — `{"<n>": {"source", "photo_id",
"photo_url", "query"}}` — with no action needed from you. It refuses to
finish the build only if a slide ends up with no recorded photo, or that
photo's id already appears in `reference/used-photos.md` under a different
post or a different slide of this one. All slides resolve in parallel
(network-bound); the hard budget is 60 seconds of searching per slide — past
that, `build_post.py` takes the best candidate available and flags it in
`review.md` itself, rather than searching further.

**Rebuilding without new photos:** pass `--keep-photos` to skip this gate and
reuse already-built images, but it only applies if every slide's photo is
already pinned, already cached in `photos/envato/`, or already built in
`photos/` from a previous run — i.e. the rebuild changes no photos. Any slide
that would need a new pick still goes through the gate normally.
`build_post.py` logs every `--keep-photos` use to that post's `review.md`
itself.

Story research and verification still get full care — the speed rule above
only applies to photos and the build.

## Never publish

This pipeline only ever produces files under `posts/`. Never post, upload, or
publish anything to TikTok, Instagram, or anywhere else — that stays a manual,
human step outside this repo.

## Tracking

Update `queue.md`'s status for a post right after building it (`build_post.py`
does this automatically via `--status`, default `built`). Statuses: `brief` →
`built` → `approved` → `posted`.

## Credentials

Pexels and Pixabay keys come from the `PEXELS_API_KEY` and `PIXABAY_API_KEY`
environment variables, or (if not set there) from the matching `export NAME=`
line in `~/.zshrc` — `scripts/photo_search.get_api_key()` reads either
location inside Python. Never write either key to a file in this repo, and
never echo, print, cat, source, or pass a key value in a shell command or
tool output; a missing key surfaces only as "`<NAME>` not set", never a
value. Openverse and Wikimedia Commons need no key.

## Dependencies

The photo-pick OCR filter (`photo_search.has_readable_text()`) needs
`tesseract` (`brew install tesseract`) and the `pytesseract` Python package
(`pip3 install pytesseract`) — both already installed in this environment.
If either is missing, `photo_search.OCR_AVAILABLE` is `False` and the filter
silently no-ops (first candidate is used, same as before it existed) rather
than failing the build.

## Scratch files

Never read or write temp files under `/tmp`. Use `tmp/` at the repo root for all
scratch work (zoom crops for review, test renders, anything intermediate). It's
gitignored — nothing in it is ever committed.
