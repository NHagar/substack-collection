# Functions to collect lists of newsletters per category

# Starting category-level URL
BASE_URL = "https://substack.com/api/v1/category/public/{cat}/all?page=0"

def iter_all(cat):

    call_url = BASE_URL.format(cat=cat[1])

    ""