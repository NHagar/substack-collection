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
# Newsletter slot variation
counts = true_links.groupby(["publication_id", "id"]).str_rep.count().reset_index()
counts.groupby("publication_id").str_rep.mean().hist()
counts.groupby("publication_id").str_rep.std().describe()

# %%
# Number of available slots, domain prominence
correlations = true_links.groupby(['publication_id', "id"]) \
    .agg({"domains_x": "count", "domains_y": "median"}) \
        .reset_index()[['publication_id', "domains_x", "domains_y"]] \
            .groupby("publication_id").corr().unstack().iloc[:,1]

correlations.hist()

# %%
# Entropy
# Link slot probabilities
pub_count = df.groupby("publication_id").count().id.rename("posts")

# %%
t = true_links.groupby(["publication_id", "id"]).apply(lambda x: x.sort_values(by="domains_y", ascending=False)) \
        .reset_index(drop=True)
t.loc[:, "slot"] = t.groupby(["publication_id", "id"]).cumcount()

# %%
slot_counts = t.groupby(["publication_id", "slot"]).count().id
slot_counts = pd.merge(slot_counts.reset_index(), pub_count.reset_index(), on="publication_id") \
    .set_index(["publication_id", "slot"])
slot_counts.loc[:, "pct"] = slot_counts.id / slot_counts.posts
# %%
# Domain slot probabilities
domain_counts = t.groupby(["publication_id", "slot", "domains_x"]).count().str_rep
domain_counts = pd.merge(slot_counts, domain_counts, left_index=True, right_index=True)
domain_counts = domain_counts.drop(columns=["posts", "pct"])
domain_counts.loc[:, "pct"] = domain_counts.str_rep / domain_counts.id

domain_counts = domain_counts.reset_index().drop(columns=["id", "str_rep"])
slot_counts = slot_counts.reset_index().drop(columns=["id", "posts"])
# %%
# Conversion to conditional probabilities
proba_table = pd.merge(domain_counts, slot_counts, on=["publication_id", "slot"])
proba_table = proba_table.rename(columns={"pct_x": "proba_domain", "pct_y": "proba_slot"})
proba_table.loc[:, "probability"] = proba_table.proba_domain * proba_table.proba_slot

# %%
# Entropy calculation
ent = proba_table.groupby(["publication_id", "slot"]).agg({"probability": entropy}).reset_index()
ent[ent.slot<10].groupby("slot").mean().probability
# %%
# Dissenting newsletters
true_links.groupby("publication_id").mean().domains_y.hist()
# %%
