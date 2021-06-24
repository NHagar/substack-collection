# %%
import collections
import urllib

from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd

# %%
def parse_docs(doc: str) -> BeautifulSoup:
    html = BeautifulSoup(doc, "lxml", parse_only=SoupStrainer("a", {"class": None}))
    return html

def get_urls(html: BeautifulSoup) -> "list[str]":
    # Remove tweet embeds, images, buttons
    links = [i for i in html.find_all("a") if not i.findChild()]
    # Get remaining hrefs
    hrefs = [i['href'] for i in links]
    # Filter out Substack CDN
    hrefs = [i for i in hrefs if "cdn.substack.com" not in i]

    return hrefs

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
# Filter newsletters by activity
most_recent = df.groupby("publication_id").post_date.max()
active = most_recent[(most_recent.dt.year==2021) & (most_recent.dt.month>4)]
df = df[df.publication_id.isin(active.index)]
# Filter to only posts that have links
df = df[df.body_html.str.contains("<a")]

# %%
# Parse html bodies
df.loc[:, "parsed"] = df.body_html.apply(parse_docs)

# %%
df.loc[:, "links"] = df.parsed.apply(get_urls)

# %%
# Shortened links
## amzn.to
## youtu.be
## bit.ly
## t.co
# Self-links
# Amazon - affiliate links?

links = set([i for l in df.links.tolist() for i in l])
# %%
hosts = [urllib.parse.urlparse(i).netloc for i in links]
hosts = [i for i in hosts if i!=""]
# %%
hostcount = collections.Counter(hosts)
# %%
hostcount.most_common(50)
# %%
len(links)
# %%
len(set(links))
# %%
