#!/usr/bin/env python3
"""Tests for check_brand_rules() word-boundary matching.
Run: python3 scripts/test_brand_rules.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_post import check_brand_rules

CASES = [
    # (text, expect_a_problem)
    ("The food safety agency reviewed the label.", False),   # "safety" must pass
    ("This ingredient is generally safe for most people.", True),   # "safe"
    ("Is it safe?", True),
    ("Considered unsafe by some regulators.", True),
    ("A safer alternative exists.", True),
    ("Tap any score to see the source.", False),
    ("This dye is toxic in high doses.", True),
    ("Rat poison studies from the 1970s.", True),
    ("A hazardous chemical by another name.", True),
    ("This is dangerous for children.", True),
    ("There's some risk with repeated exposure.", True),
    ("Passenger safety film screening room.", False),  # "safety" again, different context
    ("Safe.", True),  # capitalized + trailing punctuation
    ("UNSAFE at any dose.", True),  # all caps
]

failures = []
for text, expect_problem in CASES:
    problems = check_brand_rules(text)
    got_problem = bool(problems)
    status = "PASS" if got_problem == expect_problem else "FAIL"
    if status == "FAIL":
        failures.append((text, expect_problem, problems))
    print(f"{status}: {text!r} -> problems={problems}")

if failures:
    print(f"\n{len(failures)} of {len(CASES)} cases FAILED")
    sys.exit(1)
else:
    print(f"\nAll {len(CASES)} cases passed.")
