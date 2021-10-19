library(targets)
source("R/functions.R")
tar_option_set(packages = c("tidyverse",
                            "Rtsne",
                            "dbscan"))

set.seed(20211019)

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
  ),
  tar_target(
    unique_domain_dist,
    journalists %>% 
      group_by(publication_id) %>% 
      summarize(domains=n_distinct(domain)) %>%
      ggplot(aes(domains)) + 
      geom_density() + 
      xlab("Domains") + 
      ylab("Newsletters")
  ),
  tar_target(
    tsne_data,
    tsne_prepro(journalists, 0.01)
  ),
  tar_target(
    opt_pc,
    get_opt_pc(tsne_data)
  ),
  tar_target(
    tsne,
    Rtsne(log1p(tsne_data), 
          perplexity=sqrt(nrow(tsne_data)), 
          initial_dims=opt_pc, 
          max_iter=10000, 
          num_threads=10)
  ),
  tar_target(
    clusters,
    hdbscan(tsne$Y, minPts = 15)
  ),
  tar_target(
    tsne_results,
    tsne$Y %>% 
      as_tibble() %>%
      mutate(cluster = clusters$cluster,
             publication_id = tsne_data$publication_id)
  ),
  tar_target(
    tsne_plot,
    tsne_results %>% 
      ggplot(aes(V1, V2, color=as.factor(cluster))) + 
      geom_point()
  )
)