# %%
import collections
import urllib

from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd

# %%
df = pd.read_parquet("./data/newsletters_pq", 
                     columns=["id", 
                              "publication_id", 
                              "title", 
                              "post_date", 
                              "comment_count", 
                              "reactions",
                              "description",
                              "body_html",
                              "canonical_url"],
                     filters=[("year", "in", [2020, 2021]), ("hidden", "=", "False")])

# %%
# Parse html bodies
df.loc[:, "parsed"] = df.body_html.apply(parse_docs)

# %%
df.loc[:, "links"] = df.parsed.apply(get_urls)

