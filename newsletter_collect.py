#!/usr/bin/env python
"""
Usage: newsletter_collect.py

Runs data collection steps
"""

import json
import pathlib
import time

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
    
    def __post_error(self, endpoint: str) -> dict:
        """error handling block for post requests
        """
        print("JSON error - post unavailable")
        r = {"prev_slug": None}
        with open(ERROR_PATH, "a") as f:
            f.write(f"{endpoint}\n")
        
        return r

    def __post_loop(self, slug: str) -> requests.models.Response:
        """Helper function for looping post requests
        """
        endpoint = f"{self.post_endpoint}{slug}"
        call = requests.get(endpoint)
        time.sleep(1)
        try:
            r = call.json()
            if "prev_slug" not in r:
                r = self.__post_error(endpoint)
        except json.JSONDecodeError:
            r = self.__post_error(endpoint)
        
        return r

    def get_index(self):
        """Grab the first post
        """
        endpoint = f"{self.index_endpoint}?sort=new&offset=0&limit=1"
        call = requests.get(endpoint)
        time.sleep(1)
        try:
            r = call.json()[0]
            if "slug" not in r:
                r = self.__post_error(endpoint)
        except json.JSONDecodeError:
            r = self.__post_error(endpoint)

        self.index = r

    def get_posts(self):
        """Grab individual post bodies
        """
        posts = []
        if "slug" in self.index:
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
    for url in tqdm(urls):
        url_safe = "".join(x for x in url if x.isalnum())
        url_path = nl_path / f"{url_safe}.json"
        if not url_path.is_file():
            nl_object = Newsletter(url)
            nl_object.get_index()
            nl_object.get_posts()
            with open(url_path, "w", encoding="utf-8") as f:
                json.dump(nl_object.posts, f)
        else:
            pass