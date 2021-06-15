# %%
import collections
import urllib

from bs4 import BeautifulSoup
import pandas as pd

# %%
def get_urls(html: BeautifulSoup) -> "list[str]":
    links = [i['href'] for i in html.find_all("a", href=True)]
    return links

# %%
df = pd.read_parquet("./data/newsletters_pq", 
                     columns=["id", 
                              "publication_id", 
                              "title", 
                              "post_date", 
                              "comment_count", 
                              "reactions",
                              "description",
                              "body_html"],
                     filters=[("year", "in", [2020, 2021]), ("hidden", "=", "False")])

# %%
df.groupby("publication_id").count().id.max()

# %%
df.loc[:, "parsed"] = df.body_html.apply(BeautifulSoup)
df.loc[:, "links"] = df.parsed.apply(get_urls)

# %%
df.links.apply(len).hist()

# %%
links = [i for l in df.links.tolist() for i in l if "cdn.substack.com" not in i]
# %%
hosts = [urllib.parse.urlparse(i).netloc for i in links]
hosts = [i for i in hosts if i!=""]
# %%
hostcount = collections.Counter(hosts)
# %%
hostcount.most_common(10)
# %%
[i for i in links if urllib.parse.urlparse(i).netloc==""]
# %%
