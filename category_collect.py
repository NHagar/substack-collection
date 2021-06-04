#!/usr/bin/env python
"""
Usage: category_collect.py

Runs data collection steps
"""
import json
import pathlib
import time
from typing import Tuple

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
from tqdm import tqdm

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

DATA_PATH = pathlib.Path("./data/")


class CatList:
    """One category of newsletters, with methods for retrieval
    """

    def __init__(self, cat: tuple):
        self.cat_name, self.cat_num = cat
        # Starting category-level URL
        self.base_url = f"https://substack.com/api/v1/category/public/{self.cat_num}/all?page="

    def __process_result(self, r: requests.models.Response) -> Tuple[list,bool]:
        """Small function to grab results from JSON file
        """
        if r.ok:
            r_json = r.json()
            publications = r_json['publications']
            more = r_json['more']
        else:
            raise Exception(
                f"HTTP request returned status code {r.status_code}")

        return publications, more

    def iter_list(self) -> list:
        """Iterates through category list and collects all newsletters
        """
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


if __name__ == "__main__":
    # Check directory structure, instantiate if necessary
    cat_path = DATA_PATH / "categories"
    if not cat_path.is_dir():
        cat_path.mkdir(parents=True)
    # Iterate through categories
    newsletters = []
    for cat in tqdm(CATEGORIES):
        # Instatiate category
        cl = CatList(cat)
        # Get list of publication objects
        publications = cl.iter_list()
        publications = [{**pub, "category": cl.cat_name} for pub in publications]
        newsletters.extend(publications)
    pub_table = pd.DataFrame(newsletters)
    # Save publications to disk
    pub_table = pa.Table.from_pandas(pub_table)
    pq.write_to_dataset(pub_table, root_path="./data/categories", partition_cols=['category'])