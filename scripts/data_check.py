# %%
import glob
import json
# %%
nl_dirs = glob.glob("../data/newsletters/*/")
# %%
# Are there as many directories as we expect? (2751)
len(nl_dirs)
# %%
# Where does the data not match up?
#   - Missing/empty index files
#   - Missiong/empty post files
#   - Post file length < index file length
