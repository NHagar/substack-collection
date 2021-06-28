import pandas as pd

def count_domains_raw(hosts: pd.Series) -> pd.Series:
    """return raw domain frequencies across all posts
    """
    hosts_flat = [i for l in hosts for i in l]
    hosts_flat = pd.Series(hosts_flat)
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