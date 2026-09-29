#!/usr/bin/env python3
"""Checks reference/used-photos.md for duplicate rows.

Uniqueness is keyed on (Photo ID, Post, Slide) -- the same photo ID showing
up twice for the exact same post+slide is a data-entry bug (e.g. an edit that
appended instead of replacing) and is always an error.

A photo ID reused across *different* post/slide combos is a separate concern
(the no-repeat-across-posts rule in reference/purityiq-rules.md "Photo
rules") -- this script reports it informationally but does not treat it as a
hard error on its own, since the ledger's reuse-after-5-posts exception is a
judgment call made at pick time, not something this script can adjudicate.

Usage: python3 scripts/check_used_photos.py
Exit code 0 if no composite-key duplicates; 1 if any are found.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(REPO, "reference", "used-photos.md")


def load_rows(path=LEDGER):
    with open(path) as f:
        lines = f.readlines()
    header_idx = None
    for i, l in enumerate(lines):
        if l.strip().startswith("| Photo ID"):
            header_idx = i
            break
    if header_idx is None:
        raise ValueError(f"no '| Photo ID' header row found in {path}")
    rows = []
    for l in lines[header_idx + 2:]:
        l = l.rstrip("\n")
        if not l.strip().startswith("|"):
            continue
        parts = [p.strip() for p in l.strip().strip("|").split("|")]
        rows.append(parts)
    return rows


def main():
    rows = load_rows()
    print(f"total rows: {len(rows)}")

    seen = {}
    dupes = []
    for r in rows:
        key = (r[0], r[3], r[4])  # Photo ID, Post, Slide
        seen.setdefault(key, 0)
        seen[key] += 1
        if seen[key] == 2:
            dupes.append(key)

    if dupes:
        print(f"\nCOMPOSITE-KEY DUPLICATES (photo ID + post + slide), {len(dupes)}:")
        for key in dupes:
            print(f"  photo_id={key[0]!r} post={key[1]!r} slide={key[2]!r}")
    else:
        print("no composite-key duplicates (photo ID + post + slide all unique)")

    by_id = {}
    for r in rows:
        by_id.setdefault(r[0], []).append((r[3], r[4]))
    reused = {pid: combos for pid, combos in by_id.items() if len(combos) > 1}
    if reused:
        print(f"\nINFO: {len(reused)} photo ID(s) appear in more than one post/slide "
              "(check against the no-repeat-across-posts rule):")
        for pid, combos in reused.items():
            print(f"  {pid}: {combos}")

    sys.exit(1 if dupes else 0)


if __name__ == "__main__":
    main()
