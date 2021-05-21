import glob
import json
import pathlib
import time

import requests
from tqdm import tqdm

DATA_PATH = pathlib.Path("./data/")


class Newsletter:
    def __init__(self, nlobj):
        self.id = nlobj['id']
        self.host = nlobj['base_url']
        self.index_endpoint = f"{self.host}/api/v1/archive"
        self.post_endpoint = f"{self.host}/api/v1/posts/"

    def __index_loop(self, start, chunk):
        url = f"{self.index_endpoint}?sort=new&offset={start}&limit={chunk}"
        call = requests.get(url)
        time.sleep(2)
        try:
            r = call.json()
        except json.JSONDecodeError:
            print("JSON error - newsletter posts unavailable")
            r = []
        
        return r
    
    def create_and_check_dir(self, nl_path):
        obj_path = nl_path / self.id
        if not obj_path.is_dir():
            obj_path.mkdir()
        else:
            self.index_path = obj_path / "index.json"
            self.has_index = self.index_path.is_file()
            self.posts_path = obj_path / "posts.json"
            self.has_posts = self.posts_path.is_file()

    def get_index(self):
        start = 0
        chunk = 14
        posts = []
        r = __index_loop(start, chunk)
        posts.extend(r)
        while len(r)>0:
            start += chunk
            r = __index_loop(start, chunk)
            posts.extend(r)
        
        self.index = posts

    def get_posts(self):
        slugs = [i['slug'] for i in self.index]
        posts = []
        for s in slugs:
            endpoint = f"{self.post_endpoint}/{s}"
            call = requests.get(endpoint)
            time.sleep(2)
            try:
                r = call.json()
            except json.JSONDecodeError:
                print("JSON error retrieving post")
                r = {}
            posts.append(r)

        self.posts = posts


def get_newsletters(dir):
    nl_files = glob.glob(f"{dir}/*.json")
    nls = []
    for i in nl_files:
        with open(i, "r", encoding="utf-8") as f:
            data = json.load(f)
            nls.extend(data)

    return nls


if __name__ == "__main__":
    # Check for directory structure
    nl_path = DATA_PATH / "newsletters"
    if not nl_path.is_dir():
        nl_path.mkdir(parents=True)
    # Get newsletters
    cat_path = DATA_PATH / "categories"
    newsletters = get_newsletters(cat_path)
    for nl in tqdm(newsletters):
        nl_object = Newsletter(nl)
        # Create directory if missing
        nl_object.create_and_check_dir(nl_path)
        # Build index file if missing
        if not nl_object.has_index:
            nl_object.get_index()
            with open(nl_object.index_path, "r", encoding="utf-8") as f:
                json.dump(nl_object.index, f)
        # Build post file if missing
        if not nl_object.has_posts:
            nl_object.get_posts()
            with open(nl_object.posts_path, "r", encoding="utf-8") as f:
                json.dump(nl_object.posts, f)
