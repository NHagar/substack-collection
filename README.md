This repository contains data collection code for a research project examining Substack newsletters. You can read a little about the research in this [Tow Center report](https://www.cjr.org/tow_center_reports/digital-platforms-and-journalistic-careers-a-case-study-of-substack-newsletters.php).

This code runs two types of data collection:

1) **Newsletter collection:** For every category in Substack's [internal taxonomy](https://substack.com/discover), collect all available newsletters. 

2) **Post collection:** For all available newsletters, collect every (non-paywalled) post. 

# Installation
`git clone https://github.com/NHagar/substack-collection.git`

`pip install -r requirements.txt`

# Usage
`python category_collect.py` runs data collection on all Substack categories

`python newsletter_collect.py` runs data collection for newsletters surfaced in category collection (this takes about a week to run)

`json_to_pq.py` translates raw json files into parquet dataset

`scripts/` contains one-off checks and analyses
