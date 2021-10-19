library(targets)
source("R/functions.R")
tar_option_set(packages = c("tidyverse"))

list(
  tar_target(
    repeat_threshold,
    0.5
  ),
  tar_target(
    raw_data_file,
    "./data/posts_parsed.csv",
    format = "file"
  ),
  tar_target(
    data,
    read_csv(raw_data_file) %>% 
      mark_internal_links(.) %>% 
      mark_repeat_links(., repeat_threshold)
  )
)