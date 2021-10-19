# %%
import pathlib

import pandas as pd
from tqdm import tqdm

from analysis import links
from parsing import load, filters

tqdm.pandas()
# %%
# params
clf_path = pathlib.Path("./data/newsletters_classified.csv")
post_path = pathlib.Path("./data/newsletters_pq")
out_path = pathlib.Path("./data/posts_parsed.csv")
columns = ["id", 
            "publication_id", 
            "title", 
            "post_date", 
            "comment_count", 
            "reactions",
            "description",
            "body_html",
            "canonical_url"]
pq_filters = [("year", "in", [2020, 2021]), ("hidden", "=", "False")]

# %%
# Load data
clf = load.load_clf(clf_path)
posts = load.load_posts(post_path,
                        columns,
                        pq_filters)
# %%
# Filter posts
# Newsletter-level filters
posts = filters.filter_newsletters(posts)
# Parse html bodies
posts.loc[:, "parsed"] = posts.body_html.progress_apply(filters.parse_docs)
# Parse and filter URLs
posts.loc[:, "links"] = posts.parsed.progress_apply(filters.get_and_parse_urls)
# Expand shortened links
shortened_domains = [
    "amzn.to",
    "youtu.be",
    "bit.ly",
    "t.co"
]
posts.loc[:, "links_expanded"] = posts.links.progress_apply(filters.expand_urls, 
                                             args=(shortened_domains,))
# Parse out domains
posts.loc[:, "links_expanded"] = posts.links_expanded.progress_apply(lambda x: [i for i in x if i.netloc!=""])
posts.loc[:, "domains"] = posts.links_expanded.progress_apply(lambda x: [i.netloc for i in x])

# %%
# Join posts to classifications
df = posts.merge(clf, left_on="publication_id", right_on="id")
df = df.drop(columns=["id_y"])
df = df.rename(columns={"id_x": "post_id"})
df = df.explode("links_expanded")
df.loc[:, "str_rep"] = df.links_expanded.apply(links.get_str_rep)
df.loc[:, "domain"] = df.links_expanded.apply(links.get_domain)
# Save processed dataframe
df = df.drop(columns=["body_html", 
                      "Unnamed: 0", 
                      "stripe_user_id", 
                      "stripe_country", 
                      "stripe_publishable_key",
                      "parsed",
                      "links",
                      "links_expanded",
                      "domains"])

# %%
df.to_csv(out_path, index=False)


# %%
# Calculate overall descriptive counts - 
# posts per newsletter, total domain link frequencies,
# and unique newsletter counts
desc_overall = links.DescriptiveStats(df)

# %%
# Flag internal and repeated links
marked_links = links.mark_link_classes(df, desc_overall.posts_per_nl)




# %%
true_links = marked_links[(~marked_links.is_repeat) & (~marked_links.is_self)]

# %%
# Calculate same counts for external links only
desc_external = links.DescriptiveStats(true_links)

# %%
# Link prevalence
true_links = pd.merge(true_links,
         desc_external.raw_freq,
         how="left",
         left_on="domains",
         right_index=True)

# %%
# How many links does a typical newsletter's post have?
counts = true_links.groupby(["publication_id", "post_id"]).str_rep.count().reset_index()
counts.groupby("publication_id").str_rep.mean().hist()
counts.groupby("publication_id").str_rep.std().describe()

# %%
g = true_links.groupby(["publication_id", "domains_x"]).count().sort_values(ascending=False, by="post_id")
g.loc[:, "cumsum"] = g.reset_index().groupby("publication_id")['post_id'].transform(pd.Series.cumsum)


# %%
import importlib
importlib.reload(links)
# %%
