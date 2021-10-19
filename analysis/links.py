import pandas as pd

class DescriptiveStats:
    def __init__(self, df):
        self.posts_per_nl = df.groupby("publication_id").count().post_id
        self.raw_freq = self.count_domains_raw(df.domains)
        self.unique_freq = self.count_domains_unique(df)

    def count_domains_raw(self, hosts: pd.Series) -> pd.Series:
        """return raw domain frequencies across all posts
        """
        hosts_flat = hosts.explode()
        host_counts = hosts_flat.value_counts()
        host_counts = host_counts / host_counts.sum()

        return host_counts

    def count_domains_unique(self, df: pd.DataFrame) -> pd.DataFrame:
        """Count unique newsletters per domain
        """
        exploded = df[['publication_id', 'domains']].explode('domains')
        counts = exploded.groupby('domains').nunique()
        counts = counts.sort_values(by="publication_id", ascending=False)
        counts = counts.publication_id

        return counts

def get_str_rep(url):
    if type(url)==float:
        str_rep = None
    else:
        str_rep = url.geturl()
    
    return str_rep

def get_domain(url):
    if type(url)==float:
        domain = None
    else:
        domain = url.netloc
    
    return domain

def mark_link_classes(df: pd.DataFrame, 
                      nl_counts: pd.DataFrame,
                      mark_internal: bool = True, 
                      mark_repeat: bool = True,
                      repeat_threshold: float = 0.5) -> pd.DataFrame:
    """Mark whether URLs come from the same domain as the newsletter
    (i.e., are self-promotion/linkbacks), as well as those that appear in a large
    number of posts (e.g., recurring links to a particular Twitter profile)
    """
    cols = ['publication_id', 'post_id', 'canonical_url', 'links_expanded']
    # Expand link column and remove NAs
    exploded = df[cols].explode('links_expanded').reset_index(drop=True).drop_duplicates()
    exploded = exploded[exploded.links_expanded.notna()]
    # Get domain and URL string
    exploded.loc[:, 'domains'] = exploded.links_expanded.apply(lambda x: x.netloc)
    exploded.loc[:, "str_rep"] = exploded.links_expanded.apply(lambda x: x.geturl())
    if mark_internal:
        # Check if a link is from the same domain as the post it appears in
        exploded.loc[:, 'is_self'] = exploded \
            .apply(lambda x: x.links_expanded.netloc in x.canonical_url, axis=1)
    if mark_repeat:
        # Count the number of posts a link appears in per newsletter
        # Convert to percentage of total posts
        # Check whether pct frequency crosses a threshold
        url_freq = exploded.groupby(['publication_id', 'str_rep']) \
            .nunique().post_id.reset_index().set_index("publication_id")
        url_freq = url_freq.join(nl_counts, rsuffix="_counts")
        url_freq.loc[:, "is_repeat"] = (url_freq.post_id / url_freq.post_id_counts) >= repeat_threshold
        url_freq = url_freq.reset_index()
        exploded = exploded.merge(url_freq[["publication_id", "str_rep", "is_repeat"]],
                    on=["publication_id", "str_rep"],
                    how="left")

    return exploded