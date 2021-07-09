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
# Get unique domains per post, per newsletter
e = df[['domains', 'publication_id', 'id']].explode("domains")
e = e[e.domains.notna()].drop_duplicates()
# %%
# Count the number of posts each domain appears in per newsletter
counts = e.groupby(["publication_id", "domains"]).count()
# %%
# Pivot wide, one vector per newsletter
counts_vectors = counts.reset_index().pivot(index="publication_id", 
                           columns="domains",
                           values="id")

# %%
# Remove any extremely sparse domains
repeat_domains = nl_count[nl_count>1].index.tolist()
counts_vectors = counts_vectors[repeat_domains]

# %%
# Get number of posts per newsletter
nl_counts = df.groupby("publication_id").count().id
# %%
# Join vectors to counts
joined = counts_vectors.join(nl_counts)
# %%
# Divide every column by the total post count to generate percentage
vectors_normalized = joined.iloc[:, :-1].div(joined.id, axis=0)
# %%
# Replace NAs with 0s
vectors_normalized = vectors_normalized.fillna(0)
# %%
from collections import Counter

from sklearn.cluster import DBSCAN
# %%
clust = DBSCAN(eps=0.2, min_samples=2).fit(vectors_normalized)
# %%
Counter(clust.labels_)
# %%
