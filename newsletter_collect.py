import glob
import json
import pathlib
import time

import requests
from tqdm import tqdm

DATA_PATH = pathlib.Path("./data/")


# Check directory structure
# Make all missing newsletter dirs
# Build index queue
# Build post queue
# Collect indices
# Collect posts

class Newsletter:
    def __init__(self, nlobj):
        self.id = nlobj['id']
        self.host = nlobj['base_url']
        self.index_endpoint = f"{self.host}/api/v1/archive"
        self.post_endpoint = f"{self.host}/api/v1/posts/"
    
    def create_dir(self, nl_path):
        obj_path = nl_path / self.id
        if not obj_path.is_dir():
            obj_path.mkdir()
        else:
            pass

    

    
def get_newsletters(dir):
    nl_files = glob.glob(f"{dir}/*.json")
    nls = []
    for i in nl_files:
        with open(i, "r", encoding="utf-8") as f:
            data = json.load(f)
            nls.extend(data)

    return nls


if __name__ == "__main__":
    # Check for directory structure
    nl_path = DATA_PATH / "newsletters"
    if not nl_path.is_dir():
        nl_path.mkdir(parents=True)
    # Get newsletters
    cat_path = DATA_PATH / "categories"
    newsletters = get_newsletters(cat_path)
    for nl in tqdm(newsletters):
        nl_object = Newsletter(nl)
        # Create directory if missing
        nl_object.create_dir(nl_path)
        # Build index file if missing
        # Build post file if missing
    
