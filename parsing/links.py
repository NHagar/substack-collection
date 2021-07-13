import pandas as pd

def count_domains_raw(hosts: pd.Series) -> pd.Series:
    """return raw domain frequencies across all posts
    """
    hosts_flat = hosts.explode()
    host_counts = hosts_flat.value_counts()

    return host_counts

def count_domains_unique(df: pd.DataFrame) -> pd.DataFrame:
    """Count unique newsletters per domain
    """
    exploded = df[['publication_id', 'domains']].explode('domains')
    counts = exploded.groupby('domains').nunique()
    counts = counts.sort_values(by="publication_id", ascending=False)
    counts = counts.publication_id

    return counts

def count_per_domain(df: pd.DataFrame, normalize: bool = True) -> pd.DataFrame:
    ""

def mark_link_classes(df: pd.DataFrame, 
                      mark_internal: bool = True, 
                      mark_repeat: bool = True,
                      repeat_threshold: float = 0.5) -> pd.DataFrame:
    """Mark whether URLs come from the same domain as the newsletter
    (i.e., are self-promotion/linkbacks), as well as those that appear in a large
    number of posts (e.g., recurring links to a particular Twitter profile)
    """
    cols = ['publication_id', 'id', 'canonical_url', 'links_expanded']
    exploded = df[cols].explode('links_expanded').reset_index(drop=True)
    exploded = exploded[exploded.links_expanded.notna()]
    exploded.loc[:, "str_rep"] = exploded.links_expanded.apply(lambda x: x.geturl())
    if mark_internal:
        exploded.loc[:, 'is_self'] = exploded.apply(lambda x: x.links_expanded.netloc in x.canonical_url, axis=1)
    if mark_repeat:
        link_frequency = exploded.groupby(["publication_id", "str_rep"]) \
            .count().reset_index().drop(columns="links_expanded")
        link_frequency = link_frequency.rename(columns={"id": "issues"})
        nl_counts = df.groupby("publication_id").count().id
        link_frequency = link_frequency.set_index("publication_id").join(nl_counts)
        link_frequency.loc[:, "pct"] = link_frequency.issues / link_frequency.id
        link_frequency.loc[:, "is_promo"] = link_frequency.pct >= repeat_threshold
        exploded = exploded.set_index("str_rep") \
            .join(link_frequency[['str_rep', 'is_promo']] \
                .set_index('str_rep')).reset_index()

    return exploded