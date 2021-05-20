# How many newsletter authors have associated Twitter accounts?
# How many of those accounts mention Substack in bio?
# %%
import glob
import json
import os

from dotenv import load_dotenv
import twitter
from tqdm import tqdm

load_dotenv()
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
api = twitter.Api(consumer_key=os.environ["CONSUMER_KEY"],
                  consumer_secret=os.environ["CONSUMER_SECRET"],
                  access_token_key=os.environ["ACCESS_KEY"],
                  access_token_secret=os.environ["ACCESS_SECRET"],
                  sleep_on_rate_limit=True)
# %%
results = []
for i in tqdm(twitter_names):
    try:
        desc = api.GetUser(screen_name=i).description
        substack = "substack" in desc.lower()
        result = {"user": i, "description": desc, "mentions_substack": substack}
        results.append(result)
    except twitter.TwitterError as e:
        print(e)
        pass
# %%
sum([i['mentions_substack'] for i in results])/len(nl)
