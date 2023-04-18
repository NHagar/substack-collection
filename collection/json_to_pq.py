# %%
import json
import pathlib

import pandas as pd
from tqdm import tqdm

# %%
nl_path = pathlib.Path("./data/newsletters")

# %%
# Load all newsletter files
newsletters = nl_path.glob("*.json")
all_newsletters = []
for i in newsletters:
    with open(i, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_newsletters.append(data)

all_newsletters = [i for l in all_newsletters for i in l]
# Cast to dataframe
df = pd.DataFrame(all_newsletters)
# Dump variable for memory
all_newsletters = None
# Remove NAs
df = df[(~df.id.isna()) & (~df.body_html.isna())]
# Column transformations
df.loc[:, 'post_date'] = df.post_date.apply(pd.to_datetime)
df.loc[:, 'year'] = df.post_date.apply(lambda x: x.year)
df.loc[:, 'hidden'] = df.hidden.fillna(False)
df.loc[:, "body_html"] = df.body_html.apply(lambda x: x.encode("utf-8", "replace").decode("utf-8"))
df.loc[:, "reactions"] = df.reactions.apply(lambda x: x['❤'])
# Memory-efficient typing
df.loc[:, "reactions"] = pd.to_numeric(df.reactions, downcast="unsigned")
df.loc[:, "id"] = pd.to_numeric(df.id, downcast="unsigned")
df.loc[:, "publication_id"] = pd.to_numeric(df.publication_id, downcast="unsigned")
df.loc[:, "audience"] = df.audience.astype("category")
df.loc[:, "comment_count"] = pd.to_numeric(df.comment_count, downcast="unsigned")
df.loc[:, "year"] = df.year.astype("category")
df.loc[:, "write_comment_permissions"] = df.write_comment_permissions.astype("category")
# Clean up unused/mostly null columns
df = df.drop(columns=["type", 
                      "section_id", 
                      "search_engine_title",
                      "search_engine_description",
                      "subtitle",
                      "reaction",
                      "podcast_url",
                      "podcast_duration",
                      "default_comment_sort",
                      "top_exclusions",
                      "pins",
                      "section_pins",
                      "publishedBylines",
                      "comments"])

# %%
# Break the write into chunks to manage memory
chunksize = 50_000
r = range(0, len(df)+chunksize, chunksize)
divs = list(zip(r, r[1:]))
for d in tqdm(divs):
    subset = df.iloc[d[0]:d[1]]
    subset.to_parquet("./data/newsletters_pq", index=False, partition_cols=["year", "hidden"])

# %%
