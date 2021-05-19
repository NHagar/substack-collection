# Check search method - how many newsletters, overlap w/categories, activity level
# %%
import pickle
import time

import requests

from tqdm import tqdm
# %%
url = "https://substack.com/api/v1/publication/search"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
keywords = ['featured', 'culture', 'politics', 'technology', 'climate', 'business', 'food', 'drink', 'sports', 'faith', 'news', 'literary', 'art', 'illustration', 'health']
todo = [i for i in keywords if i not in [*all_results]]

# %%
# all_results = {}
for k in tqdm(todo):
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
with open("data/search.pkl", "wb") as f:
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
