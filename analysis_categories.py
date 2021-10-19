# %%
import pandas as pd

# %%
clf = pd.read_csv("./data/newsletters_classified.csv")
# %%
clf = clf[clf['id'].notna()]

# %%
def clean(cat):
    c = cat.lower()
    c = c.split("(")[0].strip().replace(" ", "")
    return c


# %%
clf.loc[:, "cat"] = clf['Category 1'].apply(clean)
# %%
clf.groupby("cat").count()
# %%
