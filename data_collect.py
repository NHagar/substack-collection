#!/usr/bin/env python
"""
Usage: data_collect.py

Runs data collection steps
"""

import requests



# Substack's categories correspond to hard-coded numbers
CATEGORIES = [
    ('culture', 96),
    ('politics', 14),
    ('technology', 4),
    ('business', 62),
    ('finance', 153),
    ('food_drink', 13645),
    ('sports', 94),
    ('faith', 223),
    ('news', 103),
    ('music', 11),
    ('literature', 339),
    ('art_illustration', 15417),
    ('climate', 15414),
    ('science', 134),
    ('health', 355),
    ('philosophy', 114),
    ('history', 18),
    ('travel', 109),
    ('education', 34)
]


for cat in CATEGORIES:
    json_results = iter_all(cat)
    ""