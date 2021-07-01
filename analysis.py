# %%
import pandas as pd
from tqdm import tqdm

from parsing import filters, links

tqdm.pandas()
# %%
# Load dataframe
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
# Parse html bodies
df.loc[:, "parsed"] = df.body_html.progress_apply(filters.parse_docs)
# Parse and filter URLs
df.loc[:, "links"] = df.parsed.progress_apply(filters.get_and_parse_urls)
# Expand shortened links
shortened_domains = [
    "amzn.to",
    "youtu.be",
    "bit.ly",
    "t.co"
]
df.loc[:, "links_expanded"] = df.links.progress_apply(filters.expand_urls, 
                                             args=(shortened_domains,))
# Parse out domains
df.loc[:, "domains"] = df.links_expanded.progress_apply(lambda x: [i.netloc for i in x if i.netloc!=""])

# %%
# Link distribution counts
raw_count = links.count_domains_raw(df.domains)
nl_count = links.count_domains_unique(df)
marked_links = links.mark_internal_external(df)
external_count = links.count_domains_raw(marked_links[~marked_links.is_self].domains)
# %%
# Cluster analysis
# Preprocessing
# Per-NL vector of domains
# Domains weighted to frequency (# of newsletters / total issues)
e = df[['domains', 'publication_id', 'id']].explode("domains")
e = e[e.domains.notna()].drop_duplicates()
# %%
counts = e.groupby(["publication_id", "domains"]).count()
# %%
counts_vectors = counts.reset_index().pivot(index="publication_id", 
                           columns="domains",
                           values="id")
# %%
nl_counts = df.groupby("publication_id").count().id
# %%
joined = counts_vectors.join(nl_counts)
# %%
joined.iloc[:, :-1].div(joined.id, axis=0)
# %%
