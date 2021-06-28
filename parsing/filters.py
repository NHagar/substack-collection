import json
import pathlib
import urllib

from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd
import requests

SHORTENED_LOOKUP = pathlib.Path("./data/shortened.json")
# Check for URL lookup file,
# set to empty dict if none found
if SHORTENED_LOOKUP.is_file():
    with open(SHORTENED_LOOKUP, "r", encoding="utf-8") as f:
        lookups = json.load(f)
else:
    lookups = dict()

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


def get_and_parse_urls(html: BeautifulSoup) -> "list[str]":
    """filter and parse extracted links
    """
    # Remove tweet embeds, images, buttons
    links = [i for i in html.find_all("a") if not i.findChild()]
    # Get remaining hrefs
    hrefs = [i['href'] for i in links]
    # Filter out Substack CDN
    hrefs = [i for i in hrefs if "cdn.substack.com" not in i]
    hrefs = [urllib.parse.urlparse(i) for i in hrefs]

    return hrefs


def expand_urls(urls: list[urllib.parse.ParseResult],
                domains: list[str]) -> list[urllib.parse.ParseResult]:
    """Attempts to expand shortened urls from selected domains
    """
    # Instantiate requests session
    session = requests.Session()
    len_init = len(lookups)
    expanded_urls = []
    for url in urls:
        # Get URL string representation
        rep = url.geturl()
        # If URL host not in shortened domain, represent as itself
        if url.netloc not in domains:
            expanded = url
        # If URL in lookup dict, get corresponding value
        elif rep in lookups:
            expanded = lookups[rep]
        # Otherwise, request the expanded version
        else:
            try:
                resp = session.head(rep, allow_redirects=True, timeout=10)
                expanded = resp.url
            except (requests.TooManyRedirects, 
                    requests.ConnectionError,
                    requests.Timeout) as e:
                print(f"Problem with url: {rep}")
                expanded = rep
            # Add new key-value pair to lookup
            lookups[rep] = expanded
        if type(expanded)==str:
            parsed = urllib.parse.urlparse(expanded)
        else:
            parsed = expanded
        expanded_urls.append(parsed)
    
    # Save new lookup dict if it has grown
    if len(lookups)>len_init:
        with open(SHORTENED_LOOKUP, "w", encoding="utf-8") as f:
            json.dump(lookups, f)
    
    return expanded_urls
