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

def mark_internal_external(df: pd.DataFrame) -> pd.DataFrame:
    """Mark whether URLs come from the same domain as the newsletter
    (i.e., are self-promotion/linkbacks)
    """
    exploded = df[['canonical_url', 'domains']].explode('domains')
    exploded = exploded[exploded.domains.notna()]
    exploded.loc[:, 'is_self'] = exploded.apply(lambda x: x.domains in x.canonical_url, axis=1)

    return exploded