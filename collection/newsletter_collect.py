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
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}


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
        r = {"previous_post_slug": None}
        with open(ERROR_PATH, "a") as f:
            f.write(f"{endpoint}\n")
        
        return r

    def __post_loop(self, slug: str) -> requests.models.Response:
        """Helper function for looping post requests
        """
        endpoint = f"{self.post_endpoint}{slug}"
        call = requests.get(endpoint, headers=HEADERS)
        time.sleep(1)
        try:
            r = call.json()
            if "previous_post_slug" not in r:
                r = self.__post_error(endpoint)
        except json.JSONDecodeError:
            r = self.__post_error(endpoint)
        
        return r

    def get_index(self):
        """Grab the first post
        """
        endpoint = f"{self.index_endpoint}?sort=new&offset=0&limit=1"
        call = requests.get(endpoint, headers=HEADERS)
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
            while r['previous_post_slug']:
                slug = r['previous_post_slug']
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
    # Reset files that produced errors
    if ERROR_PATH.is_file():
        with open(ERROR_PATH, "r") as f:
            errors = f.read().splitlines()
        errors = [i.split("/api")[0] for i in errors]
        errors = ["".join(x for x in url if x.isalnum()) for url in errors]
        for e in errors:
            error_path = nl_path / f"{e}.json"
            error_path.unlink()
        open(ERROR_PATH, 'w').close()
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