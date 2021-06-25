# Second pass through shortened links that
# didn't expand, with more careful scraping params.
# %%
import json
from time import sleep

import requests
from tqdm import tqdm

# %%
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
}

# %%
with open("../data/shortened.json", "r", encoding="utf-8") as f:
    lookups = json.load(f)
# %%
failed = {k:v for k,v in lookups.items() if k==v}
# %%
for k,_ in tqdm(failed.items()):
    try:
        resp = requests.head(k, headers=headers, allow_redirects=True, timeout=30)
        expanded = resp.url
        sleep(3)
        lookups[k] = expanded
    except (requests.TooManyRedirects, 
                    requests.ConnectionError,
                    requests.Timeout) as e:
        pass
# %%
with open("../data/shortened.json", "w", encoding="utf-8") as f:
    json.dump(lookups, f)
# %%
