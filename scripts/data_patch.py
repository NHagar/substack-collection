# Fixing data collection error
# %%
import glob
import json

import pandas as pd
import requests
from tqdm import tqdm

# %%
nl_dirs = glob.glob("../data/newsletters/*/")
# %%
topatch = []
for i in nl_dirs:
    with open(i + "index.json", "r", encoding="utf-8") as f:
        index = json.load(f)
    if len(index)>11:
        topatch.append(i.split("\\")[-2])
# %%
def get_newsletters(dir) -> list:
    """Load and concat newsletter files from a directory
    """
    nl_files = glob.glob(f"{dir}/*.json")
    nls = []
    for i in nl_files:
        with open(i, "r", encoding="utf-8") as f:
            data = json.load(f)
            nls.extend(data)

    return nls

cat_path = "../data/categories"
# %%
newsletters = get_newsletters(cat_path)

# %%
for i in tqdm(topatch):
    # Get nl object, set up variables
    obj = [n for n in newsletters if str(n['id'])==i][0]
    index_url = f"{obj['base_url']}/api/v1/archive"
    post_url = f"{obj['base_url']}/api/v1/posts/"
    index_path = f"../data/newsletters/{i}/index.json"
    post_path = f"../data/newsletters/{i}/posts.json"
    # Get current index and posts
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    with open(post_path, "r", encoding="utf-8") as f:
        posts = json.load(f)
    # Get post IDs and dt of latest post
    post_ids = [p['id'] for p in posts]
    latest = pd.to_datetime(index[0]['post_date'])
    # Collecting index
    offset = 0
    limit = 12
    needed_index = []
    # Only get the first two pages
    while offset<limit * 2:
        url = f"{index_url}?sort=new&offset={offset}&limit={limit}"
        r = requests.get(url)
        try:
            rjs = r.json()
            new = [p for p in rjs if p['id'] not in post_ids and pd.to_datetime(p['post_date'])<=latest]
            needed_index.extend(new)
        except json.JSONDecodeError:
            pass
        offset += limit
    print(f"Found new posts: {len(needed_index)}")
    # Collecting posts
    needed_posts = []
    for post in needed_index:
        url = f"{post_url}{post['slug']}"
        r = requests.get(url)
        try:
            rjs = r.json()
            needed_posts.append(rjs)
        except json.JSONDecodeError:
            pass
    # This is a silly check to make sure we're not
    # destroying data on write. It also saves a little
    # time by not writing if there aren't new posts.
    indlen = len(index)
    # Extend and save index
    index.extend(needed_index)
    if len(index)>indlen:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f)
    else:
        pass
    # Extend and save posts
    postlen = len(posts)
    posts.extend(needed_posts)
    if len(posts)>postlen:
        with open(post_path, "w", encoding="utf-8") as f:
            json.dump(index, f)
    else:
        pass