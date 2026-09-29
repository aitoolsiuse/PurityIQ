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
| 14 | slide6-14.jpg | pexels:8532940 | Pexels | https://www.pexels.com/photo/hands-of-a-person-holding-a-smartphone-8532940/ | Hanna Pad | used | PIQ-034-raw-milk |
| 15 | slide6-15.jpg | pexels:17772714 | Pexels | https://www.pexels.com/photo/man-holding-a-phone-17772714/ | Kelemen Boldizsár | used | PIQ-035-juice-warning |
| 16 | slide6-16.jpg | pexels:5875077 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-using-a-mobile-phone-5875077/ | RDNE Stock project | used | PIQ-036-egg-labels |
| 17 | slide6-17.jpg | pexels:11613479 | Pexels | https://www.pexels.com/photo/hands-holding-smartphone-11613479/ | chen pincheng | used | PIQ-037-tenderized-beef |
| 18 | slide6-18.jpg | pexels:7787287 | Pexels | https://www.pexels.com/photo/close-up-photo-of-person-holding-a-cellphone-7787287/ | Ravi Roshan | retired | at the 9:16 crop the phone runs off the right edge (found in 2026-09-28 crop audit) |
| 19 | slide6-19.jpg | pexels:9898392 | Pexels | https://www.pexels.com/photo/a-person-holding-a-cellphone-9898392/ | Ron Lach | used | PIQ-038-stuffed-chicken |
| 20 | slide6-20.jpg | pexels:8274735 | Pexels | https://www.pexels.com/photo/a-person-holding-a-smartphone-8274735/ | Ron Lach | used | PIQ-039-cinnamon-lead |
| 21 | slide6-21.jpg | pexels:5592313 | Pexels | https://www.pexels.com/photo/a-person-texting-on-a-cell-phone-5592313/ | Thirdman | used | PIQ-040-raw-flour |
| 22 | slide6-22.jpg | pexels:3850266 | Pexels | https://www.pexels.com/photo/crop-unrecognizable-person-with-smartphone-using-social-media-application-3850266/ | ready made | retired | at the 9:16 crop the phone runs off the right edge (found in 2026-09-28 crop audit) |
| 23 | slide6-23.jpg | pexels:6612358 | Pexels | https://www.pexels.com/photo/person-holding-white-black-mobile-phone-6612358/ | Tima Miroshnichenko | used | PIQ-041-toddler-added-sugar |
| 24 | slide6-24.jpg | pexels:8217310 | Pexels | https://www.pexels.com/photo/person-holding-white-mobile-phone-and-touching-the-screen-8217310/ | MART PRODUCTION | used | PIQ-042-percent-juice |
| 25 | slide6-25.jpg | pexels:6612346 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-holding-a-cellphone-6612346/ | Tima Miroshnichenko | used | PIQ-043-date-labels |
| 26 | slide6-26.jpg | pexels:9432425 | Pexels | https://www.pexels.com/photo/man-using-black-smartphone-9432425/ | Monstera Production | used | PIQ-044-gluten-barley |
| 27 | slide6-27.jpg | pexels:6611960 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-holding-a-smartphone-6611960/ | Tima Miroshnichenko | used | PIQ-045-honey-infants |
| 28 | slide6-28.jpg | pexels:4724372 | Pexels | https://www.pexels.com/photo/hand-holding-cellphone-with-white-screen-4724372/ | Rulo Davila | used | PIQ-046-wv-school-dyes |
| 29 | slide6-29.jpg | pexels:6373082 | Pexels | https://www.pexels.com/photo/a-person-holding-a-smartphone-6373082/ | KATRIN BOLOVTSOVA | used | PIQ-047-louisiana-qr |
| 30 | slide6-30.jpg | pexels:6612356 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-holding-a-smartphone-6612356/ | Tima Miroshnichenko | used | PIQ-048-arizona-upf |
| 31 | slide6-31.jpg | pexels:6612376 | Pexels | https://www.pexels.com/photo/close-up-shot-of-a-person-holding-a-smartphone-6612376/ | Tima Miroshnichenko | used | PIQ-049-texas-school-additives |
| 32 | slide6-32.jpg | pexels:36781606 | Pexels | https://www.pexels.com/photo/hand-holding-smartphone-with-greenery-in-office-36781606/ | Jakub Zerdzicki | used | PIQ-050-cyclospora-lettuce |
| 33 | slide6-33.jpg | pexels:6584757 | Pexels | https://www.pexels.com/photo/a-person-holding-a-smartphone-6584757/ | Artem Podrez | used | PIQ-051-argentine-beef |
| 34 | slide6-34.jpg | pexels:8946984 | Pexels | https://www.pexels.com/photo/person-holding-smartphone-with-red-case-8946984/ | https://kaboompics.com/ | used | PIQ-052-raw-milk-cheese-ecoli |
| 35 | slide6-35.jpg | envato:hand-holding-phone-with-blank-white-screen | Envato | https://app.envato.com (search: hand holding smartphone white blank screen) | Hand Holding Phone with Blank White Screen (black background) | used | PIQ-053-sprout-outbreaks |
| 36 | slide6-36.jpg | envato:hands-holding-smartphone-with-white-mockup-screen | Envato | https://app.envato.com (search: hand holding smartphone white blank screen) | Hands Holding Smartphone With White Mockup Screen Over Green Background | used | PIQ-054-frozen-berries |
| 37 | slide6-37.jpg | envato:hand-holding-smartphone-with-blank-screen-on-blue | Envato | https://app.envato.com (search: hand holding smartphone white blank screen) | Hand Holding Smartphone with Blank Screen on Blue | used | PIQ-055-applesauce-patulin |
| 38 | slide6-38.jpg | envato:hand-holding-a-phone-in-restaurant-with-lights | Envato | https://app.envato.com (search: hand holding smartphone white blank screen) | Hand Holding a Phone in Restaurant with Lights (item 3ab2ab42-d659-42a7-9d2a-f177ff7c760b) | used | PIQ-056-egg-salmonella-us-uk |
| 39 | slide6-39.jpg | envato:65cb5caf-878a-44bc-b3a1-b70d8b31cadb | Envato | https://app.envato.com (auto-licensed) | Holding Phone in Grocery Store in Front of Produce | retired | duplicate of envato 65cb5caf already used on PIQ-014 slide 6 |
| 40 | slide6-40.jpg | envato:63548743-e87b-4c06-93b0-9067fabfe3ac | Envato | https://app.envato.com (auto-licensed) | Shopping List on Smartphone in Grocery Store (cart) | used | PIQ-058-uninspected-meat |
| 41 | slide6-41.jpg | envato:hand-holding-phone-with-blank-screen-in-store-a | Envato | https://app.envato.com (auto-licensed) | Hand Holding Phone with Blank Screen in Store (4ff439fe or 0557ebfa) | used | PIQ-059-jalapeno-salmonella |
| 42 | slide6-42.jpg | envato:hand-holding-phone-with-blank-screen-in-store-b | Envato | https://app.envato.com (auto-licensed) | Hand Holding Phone with Blank Screen in Store (4ff439fe or 0557ebfa) | used | PIQ-060-texas-snap |
| 43 | slide6-43.jpg | envato:5f87785c-f876-4fad-ad19-6f1d4e21d0f8 | Envato | https://app.envato.com (auto-licensed) | Hand Holding Yellow Smartphone in Bright Kitchen | used | PIQ-061-idaho-lab-grown |
| 44 | slide6-44.jpg | envato:woman-holding-phone-with-blank-screen-indoors | Envato | https://app.envato.com (auto-licensed) | Woman Holding Phone with Blank Screen Indoors | used | PIQ-062-animal-free-dairy |
| 45 | slide6-45.jpg | envato:person-holding-smartphone-with-blank-white-screen-over-lap | Envato | https://app.envato.com (auto-licensed) | Person Holding Smartphone With Blank White Screen Over Lap | used | PIQ-063-formula-testing |
| 46 | slide6-46.jpg | envato:adult-using-mobile-phone-at-home-with-lights | Envato | https://app.envato.com (auto-licensed) | Adult Using Mobile Phone at Home With Lights | used | PIQ-064-no-sugar-added |
| 47 | slide6-47.jpg | higgsfield:aba1740a | higgsfield-generated | Higgsfield job aba1740a | Generated from a text composition note (hand holding phone, blank screen, cereal aisle); Pinterest look only | used | PIQ-065-moringa-salmonella |
| 48 | slide6-48.jpg | higgsfield:af062778 | higgsfield-generated | Higgsfield job af062778 | Generated from a text composition note (hand holding phone, blank screen, dairy aisle); Pinterest look only | used | PIQ-066-pouch-plastic-recall |
| 49 | slide6-49.jpg | higgsfield:44744267 | higgsfield-generated | Higgsfield job 44744267 | Generated from a text composition note (hand holding phone, blank screen, farmers market); Pinterest look only | used | PIQ-067-allulose-sugar |
| 50 | slide6-50.jpg | higgsfield:d3c801fb | higgsfield-generated | Higgsfield job d3c801fb | Generated from a text composition note (hand holding phone, blank screen, meat counter); Pinterest look only | used | PIQ-068-requeson-listeria |
| 51 | slide6-51.jpg | higgsfield:1085fdcf | higgsfield-generated | Higgsfield job 1085fdcf | Generated from a text composition note (hand holding phone, blank screen, bakery); Pinterest look only | used | PIQ-069-eu-bpa-ban |
| 52 | slide6-52.jpg | higgsfield:5c825865 | higgsfield-generated | Higgsfield job 5c825865 | Generated from a text composition note (hand holding phone, blank screen, freezer aisle); Pinterest look only | used | PIQ-070-frozen-pasta-listeria |
| 53 | slide6-53.jpg | higgsfield:4d51ae28 | higgsfield-generated | Higgsfield job 4d51ae28 | Generated from a text composition note (hand holding phone, blank screen, baby food aisle); Pinterest look only | used | PIQ-071-pistachio-salmonella |
| 54 | slide6-54.jpg | higgsfield:813de8cb | higgsfield-generated | Higgsfield job 813de8cb | Generated from a text composition note (hand holding phone, blank screen, home pantry); Pinterest look only | used | PIQ-072-mango-sampling |
| 55 | slide6-55.jpg | higgsfield:1e0861b7 | higgsfield-generated | Higgsfield job 1e0861b7 | Generated from a text composition note (hand holding phone, blank screen, evening grocery aisle); Pinterest look only | used | PIQ-073-neonic-tolerances |
| 56 | slide6-56.jpg | higgsfield:ee8812e6 | higgsfield-generated | Higgsfield job ee8812e6 | Generated from a text composition note (hand holding phone, blank screen, spice aisle); Pinterest look only | used | PIQ-074-eu-pfas-packaging |
| 57 | slide6-57.jpg | higgsfield:d010eb87 | higgsfield-generated | Higgsfield job d010eb87 | Generated from a text composition note (hand holding phone, blank screen, kitchen table with vegetables); Pinterest look only | used | PIQ-075-sicily-tomatoes |
| 58 | slide6-58.jpg | higgsfield:3c72437f | higgsfield-generated | Higgsfield job 3c72437f | Generated from a text composition note (hand holding phone, blank screen, kids lunchbox table); Pinterest look only | used | PIQ-076-strawberry-flavored |
| 59 | slide6-59.jpg | higgsfield:4fd02829 | higgsfield-generated | Higgsfield job 4fd02829 | Generated from a text composition note (hand holding phone, blank screen, seafood counter); Pinterest look only | used | PIQ-077-ground-beef-lean |
| 60 | slide6-60.jpg | higgsfield:1684de44 | higgsfield-generated | Higgsfield job 1684de44 | Generated from a text composition note (hand holding phone, blank screen, produce bins); Pinterest look only | used | PIQ-078-wheat-flour |
| 61 | slide6-61.jpg | higgsfield:565c30bd | higgsfield-generated | Higgsfield job 565c30bd | Generated from a text composition note (hand holding phone, blank screen, refrigerator shelves); Pinterest look only | used | PIQ-079-caffeine-labels |
| 62 | slide6-62.jpg | higgsfield:6e684532 | higgsfield-generated | Higgsfield job 6e684532 | Generated from a text composition note (hand holding phone, blank screen, bulk bins); Pinterest look only | unused |  |
| 63 | slide6-63.jpg | higgsfield:b748cebc | higgsfield-generated | Higgsfield job b748cebc | Generated from a text composition note (hand holding phone, blank screen, shopping cart with child seat); Pinterest look only | unused |  |
| 64 | slide6-64.jpg | higgsfield:ec10e944 | higgsfield-generated | Higgsfield job ec10e944 | Generated from a text composition note (hand holding phone, blank screen, cheese and deli case); Pinterest look only | unused |  |
| 65 | slide6-65.jpg | higgsfield:24837be3 | higgsfield-generated | Higgsfield job 24837be3 | Generated from a text composition note (hand holding phone, blank screen, drink cooler); Pinterest look only | unused |  |
| 66 | slide6-66.jpg | higgsfield:298cc3f8 | higgsfield-generated | Higgsfield job 298cc3f8 | Generated from a text composition note (hand holding phone, blank screen, egg and dairy shelf); Pinterest look only | unused |  |

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

Refill (2026-09-29): #31-38 added before this batch of 15 posts (14 unused left, 15 needed). Every candidate was checked at the 9:16 slide crop, per the crop-audit note. #31-34 are from the API sources (4 kept out of 59 candidates that passed the filters); #35-38 are Envato (auto-licensed). Two more Envato downloads were landscape and were rejected.

Refill (2026-09-29, second): #39-46 from Envato, each checked at the 9:16 crop. 9 other downloads rejected (landscape crop cut the phone, or the screen quad was misdetected).

Refill (2026-09-29, third): #47-54 generated with Higgsfield (gpt_image_2_5) from text-only composition notes, per the user's instruction. Each has a .quad.json sidecar with screen corners validated at the 9:16 crop; build_post.py uses it when present.
#55-66 generated the same way (darker backgrounds; detect at the default threshold). Pool back to 20 unused.
