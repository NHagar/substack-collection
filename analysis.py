# %%
import numpy as np
import pandas as pd
from tqdm import tqdm

from parsing import filters, links

tqdm.pandas()
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
# Newsletter-level filters
df = filters.filter_newsletters(df)

# %%
# Parse html bodies
df.loc[:, "parsed"] = df.body_html.progress_apply(filters.parse_docs)

# %%
# Parse and filter URLs
df.loc[:, "links"] = df.parsed.progress_apply(filters.get_and_parse_urls)

# %%
# Expand shortened links
shortened_domains = [
    "amzn.to",
    "youtu.be",
    "bit.ly",
    "t.co"
]

df.loc[:, "links_expanded"] = df.links.progress_apply(filters.expand_urls, 
                                             args=(shortened_domains,))

# %%
# Parse out domains
df.loc[:, "domains"] = df.links_expanded.progress_apply(lambda x: [i.netloc for i in x if i.netloc!=""])

# %%
# Link distribution
raw_count = links.count_domains_raw(df.domains)
nl_count = links.count_domains_unique(df)
# %%
np.log(raw_count).plot(kind="hist")
# %%
np.log(nl_count).plot(kind="hist")
# %%
links.count_domains_raw(df[df.publication_id==25649].domains)

# %%
import importlib
importlib.reload(links)

# %%
marked_links = links.mark_internal_external(df)
# %%
links.count_domains_raw(marked_links[~marked_links.is_self].domains)
# %%
