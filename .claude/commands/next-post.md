---
description: Build the next PurityIQ post end to end, from story selection to finished slides
argument-hint: "[count N, default 1]"
model: opus
---

Build $ARGUMENTS posts (default 1 if empty) autonomously, one after another. Do not ask the user anything mid-run. Never post, publish, upload or send anything anywhere.

Before starting, read in full: CLAUDE.md, reference/purityiq-rules.md, reference/story-bank.md, the "PurityIQ Slideshows" section of ~/.claude/skills/tiktok-slideshow-strategist/SKILL.md, and briefs/PIQ-001-eu-chicken-ban.md (the format model). Today's date is the "as of" date for every status check.

For each post:

## a. Pick the story
Take the first `verified` or `candidate` row in reference/story-bank.md. If the bank has fewer than 3 candidates, first research and add more (each must pass the fit test in purityiq-rules.md; use WebSearch to find leads, primary sources to confirm). Post ID is the next unused PIQ-NNN (check briefs/, posts/, queue.md). If the user's request or the bank names a specific ID (e.g. "use for PIQ-002"), use that ID.

## b. Verify every claim
Using WebSearch and WebFetch, confirm every factual claim against a primary source per the verification standard in purityiq-rules.md, including current status as of today, even for rows already marked `verified`. Fetch the actual page; do not rely on search snippets. If the story fails (claim unconfirmable, status changed, fails the fit test), set the row to `dropped` with the reason in story-bank.md and pick the next story. Cut any single claim that can't be confirmed rather than softening it.

## c. Write the brief
Write briefs/PIQ-NNN-slug.md in the PIQ-001 format (id/slug/title header, `## Caption`, `## Slides`), 7 slides, following the copy rules in `reference/purityiq-rules.md` exactly:
- Word caps: slide 1 max 12 words, slides 2-5 max 14 words each, slide 6 max 18 words, slide 7 is the fixed CTA.
- Story order: 1 hook (why a parent should care — their food, their kids, their store, not a news report). 2 what it is and where it's found. 3 the divergence (who allows it, who doesn't). 4 the single strongest attributed fact. 5 what to check on the label. 6 benefit. 7 CTA (exactly: PurityIQ is coming soon. Join the list for early access. Link in bio.)
- Plain words only: name the body ("California") not the acronym ("OEHHA"); drop units like "parts per million" and breakdown-product names from the slide text. Always keep attribution to the body that said it. One idea per slide — if a slide needs "and" to join two facts, split or cut. Shortening never changes a claim's meaning; every line still traces to its source.
- Slide 6 names the data the story uses (residue stories: "test data"; regulatory stories: "FDA, USDA, EPA and EU records"), always ending "Tap any score to see the source."
Caption lists the primary sources by name and ends with the hashtag line. Give each slide a `photo_search` and a `focus_y` (slides 1-5 and 7 also get a `photo_reference:` composition note in step e), and on slide 6 `screenshot: assets/purityiq-scan-screen.png`. Do not set a `photo_pin` on slide 6 — `build_post.py` pulls its photo automatically from the pre-validated pool (`assets/slide6-pool/` + `reference/slide6-pool.md`); slide 6's `photo_search` is kept only as the fallback query for the rare case the pool runs dry mid-build.
Do not put URLs or any `word:` lines inside the brief's Slides section (the parser treats them as keys). Put the source table (claim | source | URL | date checked) in the companion file briefs/PIQ-NNN-slug.sources.md, and copy it to posts/<post>/sources.md after the build.

## d. Self-check before sourcing photos
Confirm: no banned word (toxic, poison, dangerous, risk, safe, safer, unsafe, hazardous) in slides or caption, no emoji, no em dashes, no brand named in a negative context, every claim has a row in the source table, exactly 7 slides, every word cap respected (slide 1 ≤12, slides 2-5 ≤14 each, slide 6 ≤18), slide 6 matches the rule, slide 7 matches the CTA exactly, story order matches the 7-step structure above. Fix the brief and re-check until it passes.

## e. Source photos (fast, "first good fit")
Target: under 10 minutes for this whole post.

**Per slide, except 6 (pool), in this order:**
1. **Pinterest, look only.** Before the first run, check the Higgsfield MCP
   tools are in the session (`mcp__claude_ai_Higgsfield__generate_image`);
   if not, skip step 4 below and tell the user. Load the Chrome tools with
   one ToolSearch call. In Chrome, one Pinterest search for the slide's scene
   (e.g. "parent reading food label grocery aisle"), 30 seconds max. Pick
   the strongest pin, and write a one-line composition note: subject, camera
   angle, framing, setting, lighting, color mood (e.g. "close-up, woman's
   hands holding a cereal box, eye level, blurred grocery aisle behind, warm
   overhead light, muted tones"). Put it in the brief as `photo_reference:`
   on that slide. Never download, save, screenshot to disk, crop or upload a
   pin. Never log in; if Pinterest walls the results, write the note from
   the slide text and flag it in review.md.
2. **Envato**, via Chrome, one search written from the note (Envato rules
   below).
3. **API sources** (build_post.py's automatic search, or a pinned API
   photo), queries written from the note. Take the first licensed photo
   that matches the note and passes the OCR and visual checks.
4. **Higgsfield text-to-image, only if nothing licensed matches.** Prompt =
   the note's text only + "no text, no logos, no brand labels,
   photorealistic, 4:5 vertical". Never pass a Pinterest image, URL or
   screenshot to Higgsfield or any tool. Save the result to
   posts/<post>/photos/envato/slideN.jpg with a slideN.json sidecar
   (`source: higgsfield-generated`), log it in reference/used-photos.md with
   source `higgsfield-generated`, then do the normal visual check. `build_post.py` does the actual
resolving and logging itself (see below) — your job is just to get a decent
`photo_search` term on each slide and a `photo_pin` when you already know
which item you want; skip ahead to step f for most posts.

- **API sources run automatically, in parallel, one query each**: Pexels,
  Pixabay, Openverse (`license=cc0,pdm` only), Wikimedia Commons (CC0/public
  domain only) — all no-attribution-required. `build_post.py` OCR-checks the
  top 6 candidates itself (`photo_search.has_readable_text()`) and takes the
  first one with no readable 4+ letter word in frame; no runner-up
  comparisons, no manual review needed for this part. OCR is best-effort —
  it doesn't reliably read stylized cursive script (confirmed on Coca-Cola's
  wordmark specifically) — so it's not a guarantee, just a first pass.
- **Drink, candy, and packaged-goods slides skip the API auto-pick
  entirely.** `build_post.py` detects this from the slide's `photo_search`
  term and raises instead of guessing — go straight to Envato for these
  (see below). Free sources are dominated by branded shots in this
  category, exactly where the OCR filter's cursive-script blind spot bites
  hardest.
- **Envato Elements, via Claude in Chrome** — searched first for every
  slide except 6 (step 2 above), using the composition note. Load the Chrome tools with one ToolSearch call
  (tell the user to run `/chrome` if it isn't connected). One search, pick
  from the first page — no bulk downloads, never Envato's AI tools (Generate,
  Riff, AI credits — they spend credits). On the first stock download of
  each session, read the sidebar "Credits remaining" count before and after;
  if it dropped, STOP the whole run and tell the user. License to a project
  named for the post ID, move the file to
  posts/<post>/photos/envato/slideN.<ext>, write slideN.json sidecar
  (item_url, title, project, source).
- No situational sources (USDA Flickr direct browse, Unsplash, Foodiesfeed
  are dropped) — API-then-Envato covers every slide.
- **No credit lines in captions, ever.** Every source above is
  no-attribution-required, so a correct pick never needs one — don't add a
  "Photo: creator / license" line.
- Reject readable brand labels (or blur with blur_regions), gore, and
  anything contradicting the slide text. Reject gavels, courthouse columns,
  generic documents and lab glassware unless the slide is literally about
  that object — prefer food, store aisles, labels, hands and parents.
- **Slide 6 photos come from the pool, not a search.** `build_post.py`
  automatically takes the next `unused` row from `reference/slide6-pool.md`
  (backed by `assets/slide6-pool/`), marks it `used` with this post's ID, and
  appends it to `reference/used-photos.md` itself — nothing to do here.
  Every pool photo was already visually confirmed to composite cleanly with
  the current screenshot asset, so no per-post review of slide 6's photo
  fit is needed (still glance at the built slide in step f like any other).
  If `build_post.py` prints that the pool is empty, it falls back to a
  normal search for that one slide — flag this in review.md and refill the
  pool per the note at the top of `reference/slide6-pool.md` (add 10 more,
  same search + auto-filter + mandatory-visual-review process used to build
  it, once fewer than 5 rows remain `unused` — a warning is auto-logged to
  review.md at that point too). Slide 7 always gets a topic-matched photo (a
  parent in the relevant aisle or with a relevant product) — never a
  repeated generic portrait, and never the same photo as any earlier post's
  slide 7.
- **Enforced, not left to memory**: `build_post.py` writes
  `photos/sources_log.json` itself — a minimal `{source, photo_id,
  photo_url, query}` per slide, no per-source trail from you — and refuses
  to finish only if a slide ends up with no photo or its photo repeats
  `reference/used-photos.md` under a different post/slide. If it fails,
  fix that one slide (a different pin, or an Envato swap) and rerun.

## f. Build and inspect
Run `python3 scripts/build_post.py briefs/PIQ-NNN-slug.md`. It resolves every slide's photo itself (parallel API search, 60s budget per slide) and fails only on a missing or repeated photo — see step e. If this is a rebuild that changes no photos (every slide already pinned/cached/built from a previous run), add `--keep-photos` to skip that gate and reuse the existing images — it's logged automatically to review.md; any slide that would need a new photo pick still goes through the gate regardless. Then view EVERY slide image (posts/<post>/tiktok/slideN.jpg, and spot check instagram) and check for: readable brand labels, text legibility over the photo, text clipped or overflowing, a photo that contradicts its slide, blur or screenshot fit problems. Fix (pin a different photo, adjust focus_y, add blur_regions, swap the Envato item) and rebuild, up to 2 rebuilds. Never edit slide copy to fix a fit problem in a way that changes meaning; if a line does not fit, note it in review.md.

## g. Record
- queue.md status: build_post.py sets `built`. Never set `approved` or `posted`.
- reference/story-bank.md: set the row to `built` and note the post ID.
- posts/<post>/review.md: list everything the user should look at: unsure photos, slides with fallback sourcing, Envato items used with their licenses, any claim softened or cut, any warning from the build, any rule the run could not satisfy.

When all posts are done, give a short summary and open each post's contact_sheet.jpg (`open posts/<post>/contact_sheet.jpg`).
