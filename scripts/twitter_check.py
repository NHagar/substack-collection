# How many newsletter authors have associated Twitter accounts?
# How many of those accounts mention Substack in bio?
# %%
import glob
import json

# %%
files = glob.glob("../data/*.json")
# %%
nl = []
for i in files:
    with open(i, "r", encoding="utf-8") as f:
        data = json.load(f)
    nl.extend(data)

# %%
twitter_names = [i['twitter_screen_name'] for i in nl if 'twitter_screen_name' in i]

# %%
len(set(twitter_names))
# %%
len(twitter_names)/len(nl)

# %%
