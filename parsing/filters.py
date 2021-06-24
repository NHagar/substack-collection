from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd

def filter_newsletters(df: pd.DataFrame, 
                       remove_inactive: bool=True, 
                       remove_nolinks: bool=True) -> pd.DataFrame:
    """remove inactive newsletters and those without links
    """
    # Filter newsletters by activity
    if remove_inactive:
        most_recent = df.groupby("publication_id").post_date.max()
        active = most_recent[(most_recent.dt.year==2021) & (most_recent.dt.month>4)]
        df = df[df.publication_id.isin(active.index)]
    if remove_nolinks:
        # Filter to only posts that have links
        df = df[df.body_html.str.contains("<a")]
    
    return df


def parse_docs(doc: str) -> BeautifulSoup:
    """parse links from HTML document
    """
    html = BeautifulSoup(doc, "lxml", parse_only=SoupStrainer("a", {"class": None}))
    return html


def get_urls(html: BeautifulSoup) -> "list[str]":
    """filter extracted links
    """
    # Remove tweet embeds, images, buttons
    links = [i for i in html.find_all("a") if not i.findChild()]
    # Get remaining hrefs
    hrefs = [i['href'] for i in links]
    # Filter out Substack CDN
    hrefs = [i for i in hrefs if "cdn.substack.com" not in i]

    return hrefs



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