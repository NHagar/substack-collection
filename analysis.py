# %%
from bs4 import BeautifulSoup
import pandas as pd
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
df.body_html.apply(BeautifulSoup)
# %%
df[df.body_html.str.contains("<a")]
# %%
