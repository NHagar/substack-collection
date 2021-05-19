# Check search method - how many newsletters, overlap w/categories, activity level
# %%
import glob
import json
import pickle
import random
import time

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
search_nl[0]['base_url']
# %%
