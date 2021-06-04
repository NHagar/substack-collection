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


class Newsletter:
    """Individual Substack newsletter, with methods to handle IO and collection
    """
    def __init__(self, url: str):
        self.host = url
        self.index_endpoint = f"{self.host}/api/v1/archive"
        self.post_endpoint = f"{self.host}/api/v1/posts/"

    def __index_loop(self, start: int, chunk: int) -> requests.models.Response:
        """Helper function for looping index file requests
        """
        url = f"{self.index_endpoint}?sort=new&offset={start}&limit={chunk}"
        call = requests.get(url)
        time.sleep(1)
        try:
            r = call.json()
        except json.JSONDecodeError:
            print("JSON error - newsletter posts unavailable")
            r = []
        
        return r

    def get_index(self):
        """Grab the post index
        """
        start = 0
        chunk = 12
        posts = []
        r = self.__index_loop(start, chunk)
        posts.extend(r)
        while len(r)>0:
            start += chunk
            r = self.__index_loop(start, chunk)
            posts.extend(r)
        
        self.index = posts

    def get_posts(self):
        """Grab individual post bodies
        """
        slugs = [i['slug'] for i in self.index if type(i)==dict]
        posts = []
        for s in slugs:
            endpoint = f"{self.post_endpoint}{s}"
            call = requests.get(endpoint)
            time.sleep(1)
            try:
                r = call.json()
                posts.append(r)
            except json.JSONDecodeError as e:
                print(e)
                print("JSON error retrieving post")
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
    urls = newsletters.read(columns=['base_url']).column('base_url').topylist()
    all_posts = []
    for url in tqdm(urls):
        nl_object = Newsletter(url)
        nl_object.get_index()
        nl_object.get_posts()
        all_posts.extend(nl_object.posts)
    pdf = pd.DataFrame(all_posts)
    pdf.loc[:, 'post_date'] = pdf.post_date.apply(pd.to_datetime)
    pdf.loc[:, 'year'] = pdf.post_date.apply(lambda x: x.year)
    table = pa.Table.from_pandas(pdf)
    pq.write_to_dataset(table, root_path="./data/newsletters", partition_cols=['year', 'hidden'])