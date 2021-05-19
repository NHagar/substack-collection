#!/usr/bin/env python
"""
Usage: data_collect.py

Runs data collection steps
"""
import time

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

class CatList:
    def __init__(self, cat):
        self.cat_name, self.cat_num = cat
        # Starting category-level URL
        self.base_url = f"https://substack.com/api/v1/category/public/{self.cat_num}/all?page="

    def __process_result(r):
        if r.ok:
            r_json = r.json()
            publications = r_json['publications']
            more = r_json['more']
        
        return publications, more

    def iter_list(self):
        it = 0
        first_call = requests.get(f"{self.base_url}{it}")
        publications, more = self.__process_result(first_call)
        while more:
            it += 1
            call = requests.get(f"{self.base_url}{it}")
            add_publications, more = self.__process_result(call)
            publications.extend(add_publications)
            time.sleep(2)
        
        return publications