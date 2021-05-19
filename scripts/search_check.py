# Check search method - how many newsletters, overlap w/categories, activity level
# %%
import glob
import json
from json.decoder import JSONDecodeError
import pickle
import random
import statistics
import time

import pandas as pd
import requests

from tqdm import tqdm
# %%
url = "https://substack.com/api/v1/publication/search"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
keywords = ['featured', 'culture', 'politics', 'technology', 'climate', 'business', 'food', 'drink', 'sports', 'faith', 'news', 'literary', 'art', 'illustration', 'health']

# %%
all_results = {}
for k in tqdm(all_results):
    it = 0
    query = url + f"?query={k}&page={it}"
    r = requests.get(query, headers=HEADERS)
    r_json = r.json()
    try:
        results, more = r_json['results'], r_json['more']
        time.sleep(30)
        while more:
            it += 1
            new_query = url + f"?query={k}&page={it}"
            extra_r = requests.get(new_query, headers=HEADERS)
            extra_json = extra_r.json()
            extra_results, more = extra_json['results'], extra_json['more']
            results.extend(extra_results)
            time.sleep(30)
        all_results[k] = results
    except KeyError:
        pass

# %%
with open("../data/search.pkl", "wb") as f:
    pickle.dump(all_results, f)

# %%
for k,v in all_results.items():
    ids = [i['id'] for i in v]
    print(k)
    print(len(set(ids)))
# %%
all_ids = []
for k,v in all_results.items():
    ids = [i['id'] for i in v]
    all_ids.extend(ids)
# %%
len(set(all_ids))
# %%
with open("../data/search.pkl", "rb") as f:
    search = pickle.load(f)
# %%
# Comparing search versus category methods
search_ids = [[i['id'] for i in v] for k,v in search.items()]
search_ids = [i for l in search_ids for i in l]
search_ids = set(search_ids)
# %%
cat_files = glob.glob("../data/*.json")
cat = []
for i in cat_files:
    with open(i, "r", encoding="utf-8") as f:
        data = json.load(f)
    cat.extend(data)

# %%
cat_ids = [i['id'] for i in cat]
cat_ids = set(cat_ids)
# %%
len(search_ids.intersection(cat_ids))
# %%
cat_only = cat_ids.difference(search_ids)
search_only = search_ids.difference(cat_ids)
both = search_ids.intersection(cat_ids)
# %%
# Random sample from each
search_sample = random.sample(search_only, 50)
cat_sample = random.sample(cat_only, 50)
both_sample = random.sample(both, 50)
# %%
search_nl = {}
for _,v in search.items():
    for i in v:
        if i['id'] in search_sample:
            search_nl[i['id']] = i
search_nl = [v for _,v in search_nl.items()]
# %%
cat_nl = [i for i in cat if i['id'] in cat_sample]
# %%
both_nl = [i for i in cat if i['id'] in both_sample]

# %%
def post_loop(host, start, chunk):
    base_url = f"{host}/api/v1/archive?sort=new&offset={start}&limit={chunk}"
    call = requests.get(base_url)
    try:
        r = call.json()
    except json.JSONDecodeError:
        print("json error")
        r = []    
    return r

def get_posts(host, start, chunk):
    results = []
    r = post_loop(host, start, chunk)
    results.extend(r)
    while len(r)>0:
        start += chunk
        r = post_loop(host, start, chunk)
        results.extend(r)
        time.sleep(2)
    
    return results

def get_nl_stats(nl_list):
    nl_stats = []
    for i in tqdm(nl_list):
        it = 0
        limit = 14
        host = i['base_url']
        posts = get_posts(host, it, limit)
        post_num = len(posts)
        if post_num>0:
            most_recent = posts[0]['post_date']
        else:
            most_recent = ""
        stats = {'newsletter': i['name'], 'posts': post_num, 'most_recent': most_recent}
        nl_stats.append(stats)
    
    return nl_stats

# %%
search_stats = get_nl_stats(search_nl)
cat_stats = get_nl_stats(cat_nl)
both_stats = get_nl_stats(both_nl)
# %%
def pmedian(posts):
    pcounts = [i['posts'] for i in posts]
    return statistics.median(pcounts)
# %%
pmedian(cat_stats)
# %%
pmedian(search_stats)
# %%
pmedian(both_stats)

# %%
def pdelta(posts):
    today = pd.to_datetime('today', utc=True)
    pdates = [pd.to_datetime(i['most_recent']) for i in posts]
    deltas = [(today - i).days for i in pdates]

    return statistics.median(deltas)

# %%
pdelta(cat_stats)
# %%
pdelta(both_stats)
# %%
pdelta(search_stats)
# %%
