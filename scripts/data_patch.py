# Fixing data collection error
# %%
import glob
import json

import requests

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
topatch[0]
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
test_obj = [i for i in newsletters if str(i['id'])==topatch[0]][0]
# %%
with open("../data/newsletters/" + topatch[0] + "/index.json", "r", encoding="utf-8") as f:
    test = json.load(f)
# %%
offset = 0
limit = 12
needed = []
while offset<limit *2:
    url = test_obj['base_url'] + f"/api/v1/archive?sort=new&offset={offset}&limit={limit}"
    r = requests.get(url)
    rjs = r.json()
    offset += limit
# %%
test[0]['post_date']
# %%
