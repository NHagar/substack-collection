mark_internal_links <- function(df) {
  # Check whether links point to the same domain as the newsletter
  df$is_internal <- mapply(grepl, pattern=df$domain, x=df$canonical_url, fixed=T)
  return(df)
}

mark_repeat_links <- function(df, threshold) {
  # Check whether links occur in more posts than a predetermined threshold
  
  # Count posts per newsletter
  post_count <- df %>% 
    group_by(publication_id) %>% 
    summarize(post_count=n_distinct(post_id))
  
  # Count posts per link
  link_count <- df %>% 
    distinct(post_id, str_rep, .keep_all=T) %>% 
    group_by(str_rep, publication_id) %>% 
    summarize(posts=n())
  # Get percentage of all posts for each link,
  # filter according to threshold
  repeat_measure <- left_join(link_count, post_count, by="publication_id") %>% 
    mutate(pct = posts/post_count,
           is_repeat = pct>threshold)
  # Join back to dataframe
  df <- left_join(df,
                  repeat_measure %>% select(str_rep, 
                                            publication_id,
                                            is_repeat),
                  by=c("str_rep", "publication_id")
  )
  
  return(df)
}

count_links <- function(df) {
  # Count and pull links per post
  link_count <- df %>% 
    group_by(post_id) %>% 
    summarize(links=sum(has_link)) %>% 
    pull(links)
  
  return(link_count)
}

run_wilcox_test <- function(a, b) {
  # Run Mann Whitney U test (and pull associated stats)
  w <- wilcox.test(a, b)
  result <- list(
    pval = w$p.value,
    a_median = median(a),
    b_median = median(b),
    a_hist = hist(a),
    b_hist = hist(b)
  )
  
  return(result)
}

cum_pct <- function(df) {
  # Get cumulative domain percentage distribution
  # Select only cases where a link is present
  links <- left_join(df %>% 
                       group_by(post_id) %>% 
                       summarize(links=sum(has_link)) %>% 
                       filter(links>0) %>% 
                       select(-links),
                     df
  )
  # Get cumulative percentage of all links, for each domain
  cdf <- links %>% 
    group_by(publication_id, domain) %>% 
    summarize(freq=n()) %>% 
    arrange(desc(freq)) %>% 
    mutate(csum=cumsum(freq),
           cdf=csum/max(csum),
           n=row_number())
  # Get mean value for filtering
  m_val <- cdf %>% 
    group_by(publication_id) %>% 
    summarize(n=max(n)) %>% 
    summarize(n=mean(n)) %>% 
    pull()
  # Build plot with confidence intervals
  p <- cdf %>% 
    filter(n<=m_val) %>% 
    group_by(n) %>% 
    summarize(mean=mean(cdf),
              left=mean(cdf) - (qnorm(0.975)*sd(cdf)/sqrt(n())),
              right=mean(cdf) + (qnorm(0.975)*sd(cdf)/sqrt(n()))) %>% 
    ggplot(aes(x=n, y=mean, ymin=left, ymax=right)) + 
    geom_line() + 
    geom_ribbon(alpha=0.5) + 
    xlab("Domain") + 
    ylab("Cumulative percentage")
  
  return(p)
}

tsne_prepro <- function(df, threshold_val) {
  # Filter and format data for TSNE analysis
  threshold <- df %>% 
    summarize(n_distinct(publication_id)) %>% 
    pull() * threshold_val
  threshold <- round(threshold)
  
  pub_counts <- df %>% 
    group_by(domain) %>% 
    summarize(pubs=n_distinct(publication_id)) %>% 
    filter(pubs>=threshold)
  
  tsne_data <- left_join(pub_counts %>% select(-pubs),
                         df) %>% 
    filter(has_link) %>% 
    mutate(domain=ifelse((is_internal) | (is_repeat),
                         "INT",
                         domain)) %>% 
    group_by(publication_id, domain) %>% 
    summarize(count=n()) %>% 
    pivot_wider(names_from=domain, values_from=count) %>% 
    ungroup() %>% 
    replace(is.na(.), 0)
  
  return(tsne_data)
}

get_opt_pc <- function(df) {
  df <- df %>% select(-publication_id)
  # https://towardsdatascience.com/how-to-tune-hyperparameters-of-tsne-7c0596a18868
  pc <- prcomp(log1p(df), center=T, scale=T)
  expl_var <- pc$sdev^2/sum(pc$sdev^2)
  
  N_perm <- 10
  expl_var_perm <- matrix(NA, ncol = length(pc$sdev), nrow = N_perm)
  for(k in 1:N_perm)
  {
    expr_perm <- apply(log1p(df),2,sample)
    PC_perm <- prcomp(expr_perm, center=TRUE, scale=TRUE)
    expl_var_perm[k,] <- PC_perm$sdev^2/sum(PC_perm$sdev^2)
  }
  
  pval <- apply(t(expl_var_perm) >= expl_var,1,sum) / N_perm
  optPC<-head(which(pval>=0.05),1)-1
  
  return(optPC)
}