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
      mutate(has_link=!is.na(str_rep)) %>% 
      mark_internal_links(.) %>% 
      mark_repeat_links(., repeat_threshold)
  ),
  tar_target(
    journalists,
    data %>% filter(cat=="journalist")
  ),
  tar_target(
    other,
    data %>% filter(cat!="journalist")
  ),
  tar_target(
    links_journalists,
    count_links(journalists)
  ),
  tar_target(
    links_other,
    count_links(other)
  ),
  tar_target(
    link_diff_overall,
    run_wilcox_test(links_journalists, links_other)
  ),
  tar_target(
    link_diff_external,
    run_wilcox_test(journalists %>% 
                      filter((!is_repeat) & (!is_internal)) %>% 
                      count_links(.) %>% 
                      .[.>0],
                    other %>% 
                      filter((!is_repeat) & (!is_internal)) %>% 
                      count_links(.) %>% 
                      .[.>0])
  ),
  tar_target(
    cum_pct_overall,
    cum_pct(journalists)
  ),
  tar_target(
    cum_pct_external,
    cum_pct(journalists %>% filter((!is_repeat) & (!is_internal)))
  )
)