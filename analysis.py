# %%
import pandas as pd
from scipy.stats import entropy
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
df.loc[:, "links_expanded"] = df.links_expanded.progress_apply(lambda x: [i for i in x if i.netloc!=""])
df.loc[:, "domains"] = df.links_expanded.progress_apply(lambda x: [i.netloc for i in x])

# %%
# Get number of posts per newsletter
nl_counts = df.groupby("publication_id").count().id

# %%
# Flag internal and repeated links
marked_links = links.mark_link_classes(df, nl_counts)
true_links = marked_links[(~marked_links.is_repeat) & (~marked_links.is_self)]

# %%
import importlib
importlib.reload(links)


# %%
# Link distribution counts
raw_count = links.count_domains_raw(df.domains)
unique_count = links.count_domains_unique(df)
external_count = links.count_domains_raw(true_links.domains)
external_unique_count = links.count_domains_unique(true_links)

# %%
# Link prevalence
true_links = pd.merge(true_links,
         external_count,
         how="left",
         left_on="domains",
         right_index=True)

# %%
correlations = true_links.groupby(['publication_id', "id"]) \
    .agg({"domains_x": "count", "domains_y": "median"}) \
        .reset_index()[['publication_id', "domains_x", "domains_y"]] \
            .groupby("publication_id").corr().unstack().iloc[:,1]

# %%
correlations.hist()

# %%
# Link stability
test = true_links[true_links.publication_id==242615]
test_sorted = test.groupby("id").apply(lambda x: x.sort_values(by="domains_y", ascending=False))
test_sorted = test_sorted.reset_index(drop=True)
test_sorted.loc[:, "slot"] = test_sorted.groupby("id").cumcount()
test_sorted.groupby("slot").agg({"domains_y": [entropy, "count"]})

# %%
t = true_links.groupby(["publication_id", "id"]).apply(lambda x: x.sort_values(by="domains_y", ascending=False)) \
        .reset_index(drop=True)
t.loc[:, "slot"] = t.groupby(["publication_id", "id"]).cumcount()
t.groupby("slot").agg({"domains_y": [entropy, "count"]})

# %%
pub_count = true_links[['str_rep', 'publication_id']].groupby("str_rep").nunique()

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
repeat_domains = unique_count[unique_count > df.publication_id.nunique() * 0.01].index.tolist()
counts_vectors = counts_vectors[repeat_domains]

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
from sklearn.decomposition import PCA

# %%
pca = PCA()
# %%
pca.fit(vectors_normalized)
# %%
pca.explained_variance_ratio_
# %%
