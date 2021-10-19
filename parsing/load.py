import pandas as pd

def clean(cat):
    c = cat.lower()
    c = c.split("(")[0].strip().replace(" ", "")
    return c

def load_clf(path):
    clf = pd.read_csv(path)
    clf = clf[clf['id'].notna()]
    clf.loc[:, "cat"] = clf['Category 1'].apply(clean)

    return clf


def load_posts(path, cols, filters):
    df = pd.read_parquet(path, 
                     columns=cols,
                     filters=filters)
    
    return df