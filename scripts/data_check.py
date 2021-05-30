# %%
import glob
import json
import pathlib
import pathlib

from tqdm import tqdm
# %%
nl_dirs = glob.glob("../data/newsletters/*/")
# %%
# Are there as many directories as we expect? (2751)
len(nl_dirs)

# %%
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# %%
# Where does the data not match up?
#   - Missing/empty index files
#   - Missiong/empty post files
#   - Post file length < index file length
missing = []
for i in tqdm(nl_dirs):
    nl_id = i.split("\\")[-2]
    index_path = i + "index.json"
    posts_path = i + "posts.json"
    index = load_json(index_path)
    posts = load_json(posts_path)
    if len(index)!=len(posts) or len(index)==0 or len(posts)==0:
        missing.append(nl_id)

# %%
missing
# %%
def get_newsletters(dir: pathlib.Path) -> list:
    """Load and concat newsletter files from a directory
    """
    nl_files = glob.glob(f"{dir}/*.json")
    nls = []
    for i in nl_files:
        with open(i, "r", encoding="utf-8") as f:
            data = json.load(f)
            nls.extend(data)

    return nls
# %%
nl_path = pathlib.Path("../data/newsletters")
cat_path = pathlib.Path("../data/categories")
# %%
newsletters = get_newsletters(cat_path)
# %%
[i for i in newsletters if str(i['id']) in missing][18]
# %%
nid = "3910"
index_path = "../data/newsletters/" + nid + "/index.json"
posts_path = "../data/newsletters/" + nid + "/posts.json"
index = load_json(index_path)
posts = load_json(posts_path)
# %%
index_ids = [i['id'] for i in index]
post_ids = [i['id'] for i in posts]
# %%
# %%
[i for i in index if type(i)!=dict]
# %%
len(index)
# %%
len(posts)
# %%
# Spot checks
obj = [i for i in newsletters if i['id']==23057][0]
# %%
nid = "23057"
index_path = "../data/newsletters/" + nid + "/index.json"
posts_path = "../data/newsletters/" + nid + "/posts.json"
index = load_json(index_path)
posts = load_json(posts_path)
# %%
len(index)
# %%
[i['title'] for i in index]
# %%

# %%
from ..newsletter_collect import Newsletter
# %%
obj
# %%
ep = "https://richardfreepress.substack.com/api/v1/archive"
# %%
import requests
# %%
url = ep + "?sort=new"
# %%
call = requests.get(url)
# %%
r = call.json()
# %%
len(r)
# %%
r[-1]
# %%
with open("../data/newsletters/100228/index.json", "r", encoding="utf-8") as f:
    index = json.load(f)
with open("../data/newsletters/100228/posts.json", "r", encoding="utf-8") as f:
    posts = json.load(f)
# %%
len(index)
# %%
len(posts)
# %%
index
# %%
