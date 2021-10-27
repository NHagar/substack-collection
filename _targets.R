library(targets)
source("R/functions.R")
tar_option_set(packages = c("tidyverse",
                            "Rtsne",
                            "dbscan",
                            "igraph",
                            "widyr"))

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
  ),
  tar_target(
    top_by_cluster,
    left_join(
      tsne_results %>% select(-V1, -V2),
      journalists
    ) %>%
      filter(!is.na(domain)) %>% 
      group_by(cluster, domain) %>% 
      dplyr::summarize(posts=n_distinct(post_id)) %>% 
      mutate(posts_pct=posts/sum(posts)) %>% 
      filter(cluster!=0) %>% 
      top_n(5) %>% 
      arrange(cluster, desc(posts))
  ),
  tar_target(
    cross_pubs,
    journalists %>% 
      filter(!is.na(domain) &
               !is_internal &
               !is_repeat) %>% 
      filter(grepl("substack.com", str_rep)) %>% 
      select(base_url, domain) %>% 
      mutate(base_url=gsub("https://", "", base_url, fixed=T)) %>% 
      group_by(base_url, domain) %>% 
      summarize(weight=n()) %>% 
      rename(c("V1"=base_url, "V2"=domain))
  ),
  tar_target(
    cross_pubs_f,
    cross_pubs %>% 
      filter(V2 %in% cross_pubs$V1)
  ),
  tar_target(
    graph_cross,
    graph_from_data_frame(cross_pubs_f)
  ),
  tar_target(
    graph_powerlaw,
    fit_power_law(degree(graph_cross))
  ),
  tar_target(
    classifications_df,
    journalists %>% 
      mutate(base_url=gsub("https://", "", base_url),
             is_other_substack=grepl("substack.com", domain) & 
               !is_internal &
               !is_repeat &
               domain %in% base_url)    
  ),
  tar_target(
    clf_proportions,
    classifications_df %>% 
      group_by(is_internal, is_repeat, is_other_substack) %>% 
      summarize(links=n()) %>% 
      filter(!is.na(is_internal)) %>% 
      ungroup() %>%
      mutate(category = ifelse(
        is_internal,
        "internal",
        ifelse(
          (is_repeat & !is_internal),
          "promotional",
          ifelse(
            is_other_substack,
            "other_substack",
            "external"
          )
        )
      )) %>% 
      group_by(category) %>% 
      summarize(links=sum(links)) %>% 
      mutate(pct=links/sum(links),
             se=sqrt(pct * (1-pct) / sum(links)),
             upper = pct + 1.96 * se,
             lower = pct - 1.96 * se) %>% 
      ggplot(aes(category, pct)) + 
      geom_bar(stat="identity")
  ),
  tar_target(
    cdf,
    classifications_df %>% 
      filter(!is_internal &
               !is_repeat &
               !is_other_substack) %>% 
      group_by(domain) %>% 
      summarize(count=n()) %>% 
      arrange(desc(count)) %>% 
      mutate(cum=cumsum(count),
             cdf=cum/max(cum),
             row=row_number())
  ),
  tar_target(
    to_classify,
    cdf %>% 
      filter(cdf<=.75) %>% 
      df_out(., "./data/to_classify_raw.csv"),
    format="file"
  ),
  tar_target(
    classified_path,
    "./data/classified.csv"
  ),
  tar_target(
    classifications,
    read_csv(classified_path)
  ),
  tar_target(
    tagged_df,
    left_join(classifications_df %>% 
                filter(!is.na(domain) &
                         !is_internal &
                         !is_repeat &
                         !is_other_substack),
              classifications
    )
  ),
  tar_target(
    top_five,
    tagged_df %>% 
      filter(!is.na(class)) %>% 
      group_by(class, domain) %>% 
      summarize(count=n()) %>% 
      arrange(desc(count)) %>% 
      top_n(5)
  ),
  tar_target(
    external_prop,
    tagged_df %>% 
      filter(!is.na(class)) %>% 
      mutate(class=ifelse(
        class=="n", "News",
        ifelse(class=="p", "Platform", "Other")
      )) %>% 
      group_by(class) %>% 
      dplyr::summarize(count=n()) %>% 
      mutate(pct=count/sum(count),
             se=sqrt((1/1000)*pct*(1-pct)),
             lower = pct - 1.96*se,
             upper = pct + 1.96*se) %>% 
      ggplot(aes(class, pct)) + 
      geom_point() + 
      geom_errorbar(aes(ymin=lower, ymax=upper, width=0.1))
  ),
  tar_target(
    for_similarity,
    classifications_df %>% 
      group_by(domain) %>% 
      summarize(pubs=n_distinct(publication_id)) %>% 
      filter(pubs>=2)
  ),
  tar_target(
    domain_table,
    left_join(for_similarity,
              classifications_df
    ) %>% 
      group_by(publication_id, domain) %>% 
      summarize(links=n()) %>% 
      ungroup()
  ),
  tar_target(
    closest,
    domain_table %>% 
      pairwise_similarity(publication_id, domain, links) %>%
      arrange(desc(similarity))
  ),
  tar_target(
    similarity_observed,
    closest %>% 
      summarize(m=median(similarity)) %>% 
      pull()
  ),
  tar_target(
    similarity_plot,
    closest %>% 
      mutate(str_rep=ifelse(item1<item2,
                            str_c(as.character(item1), as.character(item2)),
                            str_c(as.character(item2), as.character(item1)))) %>%
      distinct(str_rep, .keep_all=T) %>% 
      ggplot(aes(similarity)) + 
      geom_density()
  ),
  tar_target(
    similarity_permuted,
    perm_cosine(domain_table, 10000)
  ),
  tar_target(
    perm_test,
    (sum(similarity_permuted > similarity_observed) / 10000) %>% 
      binom.test(., length(similarity_permuted)) %>% 
      .$conf.int
  )
)
