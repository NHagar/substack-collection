#!/usr/bin/env python
"""
Usage: newsletter_collect.py

Runs data collection steps
"""

import glob
import json
import pathlib
import time

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
from tqdm import tqdm

DATA_PATH = pathlib.Path("./data/")
ERROR_PATH = DATA_PATH / "errors.txt"


class Newsletter:
    """Individual Substack newsletter, with methods to handle IO and collection
    """
    def __init__(self, url: str):
        self.host = url
        self.index_endpoint = f"{self.host}/api/v1/archive"
        self.post_endpoint = f"{self.host}/api/v1/posts/"

    def __post_loop(self, slug: str) -> requests.models.Response:
        """Helper function for looping post requests
        """
        endpoint = f"{self.post_endpoint}{slug}"
        call = requests.get(endpoint)
        time.sleep(1)
        try:
            r = call.json()
        except json.JSONDecodeError:
            print("JSON error - post unavailable")
            r = {}
            with open(ERROR_PATH, "a") as f:
                    f.write(f"{endpoint}\n")
        
        return r

    def get_index(self):
        """Grab the first post
        """
        endpoint = f"{self.index_endpoint}?sort=new&offset=0&limit=1"
        call = requests.get(endpoint)
        time.sleep(1)
        try:
            r = call.json()
        except json.JSONDecodeError:
            print("JSON error - post unavailable")
            r = [{}]
            with open(ERROR_PATH, "a") as f:
                    f.write(f"{endpoint}\n")

        self.index = r[0]

    def get_posts(self):
        """Grab individual post bodies
        """
        posts = []
        if len(self.index)>0:
            first_slug = self.index['slug']
            r = self.__post_loop(first_slug)
            posts.append(r)
            while r['prev_slug']:
                slug = r['prev_slug']
                r = self.__post_loop(slug)
                posts.append(r)
        else:
            pass

        self.posts = posts

if __name__ == "__main__":
    # Check for directory structure
    nl_path = DATA_PATH / "newsletters"
    if not nl_path.is_dir():
        nl_path.mkdir(parents=True)
    # Get newsletters
    cat_path = DATA_PATH / "categories"
    newsletters = pq.ParquetDataset(cat_path)
    urls = newsletters.read(columns=['base_url']).column('base_url').to_pylist()
    all_posts = []
    for url in tqdm(urls):
        nl_object = Newsletter(url)
        nl_object.get_index()
        nl_object.get_posts()
        all_posts.extend(nl_object.posts)
    pdf = pd.DataFrame(all_posts)
    pdf.loc[:, 'post_date'] = pdf.post_date.apply(pd.to_datetime)
    pdf.loc[:, 'year'] = pdf.post_date.apply(lambda x: x.year)
    pdf.loc[:, 'hidden'] = pdf.hidden.fillna(False)
    table = pa.Table.from_pandas(pdf)
    pq.write_to_dataset(table, root_path="./data/newsletters", partition_cols=['year', 'hidden'])