# Slide 6 photo pool

Pre-validated pool of hand-holding-phone photos for slide 6 (screen facing
camera, no readable text, composites cleanly with
`assets/purityiq-scan-screen.png`). Files live in `assets/slide6-pool/` as
`slide6-NN.jpg` — the ORIGINAL blank-screen photo, not pre-composited;
`build_post.py` runs the perspective-fit composite fresh against the current
screenshot asset at build time.

Built 2026-09-28. Source: Pexels/Pixabay/Openverse via
`photo_search.get_candidates()`, auto-filtered by `has_readable_text()` (OCR)
and `screenshot_fit.find_screen_quad()`, then every survivor was visually
reviewed for composite fit, subject match, and screen-facing-camera framing
before being accepted. All licenses are no-attribution-required (Pexels
License, Pixabay Content License, or Openverse CC0/PDM).

`/next-post` takes the next row with `status: unused`, marks it `used` with
the post ID, and logs the same photo/post/slide in `reference/used-photos.md`
as usual. When fewer than 5 rows remain `unused`, add 10 more following the
same search + auto-filter + mandatory-visual-review process used to build
this pool, and append them below (continuing the index numbering).

| # | File | Photo ID | Source | URL | Creator | Status | Used by (post) |
|---|---|---|---|---|---|---|---|
| 1 | slide6-01.jpg | openverse:fd42351d-b4e2-4219-98ee-70e08370cf7a | Openverse | https://www.flickr.com/photos/157635012@N07/48846000382 | Artem Beliaikin | retired | landscape (1024x683): the 9:16 crop cuts the phone in half; tried and pulled from PIQ-023 |
| 2 | slide6-02.jpg | pexels:8947174 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-holding-a-mobile-phone-on-white-background-8947174/ | kaboompics.com | retired | tight close-up: at the 9:16 crop the screenshot fills the frame and no hand shows; pulled from PIQ-023 |
| 3 | slide6-03.jpg | pexels:6278755 | Pexels | https://www.pexels.com/photo/person-holding-iphone-with-blank-screen-6278755/ | Artem Podrez | used | PIQ-023-baby-food-metals |
| 4 | slide6-04.jpg | pexels:6203792 | Pexels | https://www.pexels.com/photo/mockup-with-woman-holding-phone-6203792/ | Hanna Pad | used | PIQ-024-sesame-allergen |
| 5 | slide6-05.jpg | pexels:8217475 | Pexels | https://www.pexels.com/photo/hand-holding-iphone-mockup-8217475/ | MART PRODUCTION | used | PIQ-025-healthy-claim |
| 6 | slide6-06.jpg | pexels:4792351 | Pexels | https://www.pexels.com/photo/faceless-person-demonstrating-empty-screen-on-smartphone-4792351/ | Anete Lusina | used | PIQ-026-product-of-usa |
| 7 | slide6-07.jpg | pexels:6373207 | Pexels | https://www.pexels.com/photo/a-person-holding-a-smartphone-with-a-blank-screen-6373207/ | KATRIN BOLOVTSOVA | used | PIQ-027-country-of-origin |
| 8 | slide6-08.jpg | pexels:6373084 | Pexels | https://www.pexels.com/photo/a-person-holding-a-smartphone-6373084/ | KATRIN BOLOVTSOVA | used | PIQ-028-apple-juice-arsenic |
| 9 | slide6-09.jpg | pexels:7412033 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-holding-a-smartphone-7412033/ | Monstera Production | used | PIQ-029-rice-cereal-arsenic |
| 10 | slide6-10.jpg | pexels:6278759 | Pexels | https://www.pexels.com/photo/person-holding-black-iphone-6278759/ | Artem Podrez | used | PIQ-030-fish-mercury |
| 11 | slide6-11.jpg | pexels:6612379 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-holding-a-smartphone-6612379/ | Tima Miroshnichenko | used | PIQ-031-irradiation-label |
| 12 | slide6-12.jpg | pexels:6279105 | Pexels | https://www.pexels.com/photo/food-person-woman-hand-6279105/ | Artem Podrez | used | PIQ-032-school-food-dyes |
| 13 | slide6-13.jpg | pexels:8490400 | Pexels | https://www.pexels.com/photo/person-holding-an-iphone-with-black-case-8490400/ | PNW Production | used | PIQ-033-organic-label-tiers |
| 14 | slide6-14.jpg | pexels:8532940 | Pexels | https://www.pexels.com/photo/hands-of-a-person-holding-a-smartphone-8532940/ | Hanna Pad | unused |  |
| 15 | slide6-15.jpg | pexels:17772714 | Pexels | https://www.pexels.com/photo/man-holding-a-phone-17772714/ | Kelemen Boldizsár | unused |  |
| 16 | slide6-16.jpg | pexels:5875077 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-using-a-mobile-phone-5875077/ | RDNE Stock project | unused |  |
| 17 | slide6-17.jpg | pexels:11613479 | Pexels | https://www.pexels.com/photo/hands-holding-smartphone-11613479/ | chen pincheng | unused |  |
| 18 | slide6-18.jpg | pexels:7787287 | Pexels | https://www.pexels.com/photo/close-up-photo-of-person-holding-a-cellphone-7787287/ | Ravi Roshan | retired | at the 9:16 crop the phone runs off the right edge (found in 2026-09-28 crop audit) |
| 19 | slide6-19.jpg | pexels:9898392 | Pexels | https://www.pexels.com/photo/a-person-holding-a-cellphone-9898392/ | Ron Lach | unused |  |
| 20 | slide6-20.jpg | pexels:8274735 | Pexels | https://www.pexels.com/photo/a-person-holding-a-smartphone-8274735/ | Ron Lach | unused |  |
| 21 | slide6-21.jpg | pexels:5592313 | Pexels | https://www.pexels.com/photo/a-person-texting-on-a-cell-phone-5592313/ | Thirdman | unused |  |
| 22 | slide6-22.jpg | pexels:3850266 | Pexels | https://www.pexels.com/photo/crop-unrecognizable-person-with-smartphone-using-social-media-application-3850266/ | ready made | retired | at the 9:16 crop the phone runs off the right edge (found in 2026-09-28 crop audit) |
| 23 | slide6-23.jpg | pexels:6612358 | Pexels | https://www.pexels.com/photo/person-holding-white-black-mobile-phone-6612358/ | Tima Miroshnichenko | unused |  |
| 24 | slide6-24.jpg | pexels:8217310 | Pexels | https://www.pexels.com/photo/person-holding-white-mobile-phone-and-touching-the-screen-8217310/ | MART PRODUCTION | unused |  |
| 25 | slide6-25.jpg | pexels:6612346 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-holding-a-cellphone-6612346/ | Tima Miroshnichenko | unused |  |
| 26 | slide6-26.jpg | pexels:9432425 | Pexels | https://www.pexels.com/photo/man-using-black-smartphone-9432425/ | Monstera Production | unused |  |
| 27 | slide6-27.jpg | pexels:6611960 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-holding-a-smartphone-6611960/ | Tima Miroshnichenko | unused |  |
| 28 | slide6-28.jpg | pexels:4724372 | Pexels | https://www.pexels.com/photo/hand-holding-cellphone-with-white-screen-4724372/ | Rulo Davila | unused |  |
| 29 | slide6-29.jpg | pexels:6373082 | Pexels | https://www.pexels.com/photo/a-person-holding-a-smartphone-6373082/ | KATRIN BOLOVTSOVA | unused |  |
| 30 | slide6-30.jpg | pexels:6612356 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-holding-a-smartphone-6612356/ | Tima Miroshnichenko | unused |  |

Note: #25 and #30 (and the original candidates #23, #27) are the same
photographer's studio series (same model/backdrop) but are distinct photo
IDs/poses — acceptable under the no-repeat rule, which is keyed on photo ID,
but avoid using two entries from this same series back-to-back in the queue
order if it can be helped.

Crop audit (2026-09-28): the original review checked composites at each
photo's native aspect ratio, not at the 9:16 slide crop. Rendering every row
through `compose.cover_crop(1080x1920, focus_y 0.18)` found 4 that fail there
(#1 landscape, #2 tight close-up with no hand visible, #18 and #22 phone off
the right edge); they are marked `retired`. When refilling the pool, check
each candidate at the 9:16 crop as well, not only the raw composite.
