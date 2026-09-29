# PurityIQ content rules
## What PurityIQ is
An iOS app that scores food from government and open-data records: USDA Pesticide Data Program residue tests, EPA tolerances, FDA regulations, EU/EFSA rulings, California Prop 65 (OEHHA). Every score shows its source. The benefit we sell: a score built on public records, not on opinion. The app is not yet in the App Store.
## Story fit test (a story must pass both)
(a) The core claim is backed by a government or open-data record that PurityIQ-style data would draw on.
(b) A parent can check or do something about it in a grocery aisle.
## Verification standard
- Every factual claim traces to a primary source: government sites (fda.gov, ecfr.gov, usda.gov, epa.gov, eur-lex.europa.eu, efsa.europa.eu, oehha.ca.gov, state legislature sites) or peer-reviewed journals. News and blogs may be used to find leads, never as the cited source.
- Confirm current status as of today; regulations change. If a claim can't be confirmed from a primary source, cut it.
- Quantify exactly as the source does. Distinguish "detected" (lab-tested) from "contains" (label). Never imply a food is harmful beyond what the named body said; name the body.
- Frame foreign rules as divergence ("the EU banned X; the US allows it"), never "stricter means better."
- Do not name or show brands in a negative context.

## Copy rules
- Word caps: slide 1 hook max 12 words. Slides 2 to 5 max 14 words each. Slide 6 max 18 words. Slide 7 is fixed: "PurityIQ is coming soon. Join the list for early access. Link in bio."
- Slide 1 must say why a parent should care (their food, their kids, their store), not report news. Test: would a parent in a grocery line swipe to slide 2?
- Story order: 1 hook. 2 what it is and where it's found. 3 the divergence (who allows it, who doesn't). 4 the single strongest attributed fact. 5 what to check on the label. 6 benefit. 7 CTA.
- Plain words only. "California" not "OEHHA". "a chemical known to cause cancer" or "California's cancer list" not "Prop 65". Drop "parts per million", "chemical review list" and breakdown-product names. Always keep attribution to the body that said it.
- One idea per slide. If a slide needs "and" to join two facts, split or cut.
- Shortening never changes a claim's meaning. Every line still traces to its source.
- Slide 6 names the data the story uses: residue stories say "test data", regulatory stories say "FDA, USDA, EPA and EU records". Always end with "Tap any score to see the source."
- Banned words (slides, captions, everywhere): toxic, poison, dangerous, risk, safe, safer, unsafe, hazardous. No emoji. No em dashes.
- When the banned-word check forces a change, rewrite the whole line so its meaning still matches the source -- never just delete the banned word and leave the rest. A word is banned because of what it implies, not because of its letters; deleting it while keeping the sentence's shape around it usually just relocates the same implication (or breaks the sentence) rather than fixing it. Re-derive the line from what the source actually says. Example: "California set the safe daily limit at 29 micrograms of 4-MEI" (wrong on both counts -- "safe" is banned, and "set...the...limit" overstates what an NSRL/safe-harbor threshold actually does) needed a real rewrite to what the source supports: "California requires a warning above 29 micrograms a day."

## Photo rules
Target: under 10 minutes per post, end to end. "First good fit," not
exhaustive comparison:
- **API, in parallel, one query each** (Pexels, Pixabay, Openverse, Wikimedia
  — `photo_search.get_candidates()` runs all four concurrently). Look at the
  top results and pick the first one that fits the slide, has no readable
  brand label (or a blurrable one), and isn't a repeat in
  `reference/used-photos.md`. Settle on it and move on — no runner-up
  comparisons, no written justifications. Openverse is restricted to
  `license=cc0,pdm`; Wikimedia to CC0/public domain only — no CC BY, no
  share-alike, nothing that would ever need a credit line.
  - **Automatic OCR text filter, not left to memory**: `build_post.py` runs
    OCR (`photo_search.has_readable_text()`, via `pytesseract`/tesseract) on
    each of the top 6 candidates before picking, and skips any with a
    readable word of 4+ letters anywhere in frame — the first one that
    passes is used. This is best-effort, not foolproof, with two confirmed
    blind spots: (1) stylized cursive script — tesseract reads neither the
    "Coca-Cola" wordmark itself nor other label text on some Coca-Cola
    photos; (2) label text photographed at a steep angle/perspective tilt —
    confirmed on a Heinz can where "HEINZ BEANS" was sharp and legible to
    the eye but tesseract returned nothing even after grayscale, inverted,
    autocontrast, and full-resolution passes. It reliably catches
    horizontal, front-facing printed/block-letter text (ingredient labels,
    "ORIGINAL TASTE"-style print, price tags) — just not tilted or cursive
    brand text. OCR also only checks for TEXT, not whether the photo
    actually matches the slide's subject (confirmed: an OCR-clean candidate
    for "toast" turned out to be a honey jar) — the mandatory post-build
    visual check in step f is still required for content fit, not optional
    just because OCR passed. If OCR isn't installed, `has_readable_text()`
    silently does nothing (falls back to the first candidate) rather than
    failing the build.
  - **Drink, candy, and packaged-goods slides go to Envato first, not API.**
    `build_post.py` checks the slide's `photo_search` term
    (`is_brand_heavy_category()`) and refuses to run the API auto-pick at
    all for these — free sources are dominated by branded shots there, and
    this is exactly the category where the OCR filter's blind spots bite
    hardest. Search Envato Elements for these from the start.
- **Envato Elements, via Claude in Chrome** — for drink/candy/packaged-goods
  slides (always), or when the API auto-pick had no good fit for another
  slide, or for the slide 6 hand-holding-phone shot if no API result has a
  front-facing screen. One search per slide max, pick from the first page.
  Licensed to a project named with the post ID, never use Envato AI tools.
- No situational sources (dropped: USDA Flickr direct browse, Unsplash,
  Foodiesfeed) — API-then-Envato covers every slide.
- **Enforced, not left to memory**: `build_post.py` resolves every slide's
  photo itself and writes a minimal record to
  `posts/<post>/photos/sources_log.json` (`{"<n>": {"source", "photo_id",
  "photo_url", "query"}}`) — no per-source search trail, no justification.
  The build fails only if a slide ends up with no recorded photo, or that
  photo's id already appears in `reference/used-photos.md` under a different
  post or a different slide of this one. Slides resolve in parallel
  (network-bound). Hard budget: 60 seconds of searching per slide; past that,
  `build_post.py` takes the best candidate available and flags it in
  `review.md` itself. `--keep-photos` skips this gate for a rebuild that
  changes no photos (every slide already pinned/cached/built) — logged
  automatically to that post's `review.md`.
- No photo repeats across posts. Keep `reference/used-photos.md` as the master
  list — photo ID, source, URL, creator, license, post, slide — and check it
  before every pick. Reuse is allowed only if the photo hasn't appeared in
  the last 5 posts and no unused option exists.
- **No credit lines in captions, ever.** Only use photos whose license needs
  no attribution: Pexels License, Pixabay Content License, Envato Elements
  license, CC0, or public domain (PDM). The sources above are pre-restricted
  to exactly this, so a correct pick never needs one.
- Show food, store aisles, labels, hands and parents. No gavels, courthouse columns, generic documents or lab glassware unless the slide is literally about that object.
- Slide 6: a different hand-holding-phone photo every post, screen facing camera, ideally in an aisle matching the topic, with the PurityIQ app screenshot fitted on the screen. Blur the "0 of 10 free scans used this month" line until the screenshot is recaptured with the new free tier.
- Slide 7: a topic-matched photo (a parent in the relevant aisle or with a relevant product), never a repeated generic portrait.
- No readable brand labels; blur them.

Story research and verification still get full care — the speed rule above
only applies to photos and the build.

## Working rules
- Scratch files go in `tmp/` at the repo root, never `/tmp`. `tmp/` is gitignored.
- No enforced daily cap on Envato downloads. Log each day's Envato download
  count in `reference/used-photos.md` for reference.
- Pexels/Pixabay keys: read from `PEXELS_API_KEY`/`PIXABAY_API_KEY` in the
  environment, or from the matching `export NAME=` line in `~/.zshrc` if not
  set there — read inside Python only, never echoed, printed, `cat`, sourced,
  or passed in a shell command. A missing key surfaces only as "`<NAME>` not
  set". Openverse and Wikimedia Commons need no key.
- Never post, publish or send anything. This pipeline only ever produces files under `posts/`.

## Banned words (slides, captions, everywhere)
toxic, poison, dangerous, risk, safe, safer, unsafe, hazardous. No emoji. No em dashes.
## Slide 6 benefit line
Must name the kind of data the story actually uses. Residue stories: "test data." Regulatory stories: "FDA, USDA, EPA and EU records." Always end with "Tap any score to see the source."
