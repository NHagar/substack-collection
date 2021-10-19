# %%
import pathlib

from tqdm import tqdm

from parsing import load, filters

tqdm.pandas()
# %%
# params
clf_path = pathlib.Path("./data/newsletters_classified.csv")
post_path = pathlib.Path("./data/newsletters_pq")
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
