mark_internal_links <- function(df) {
  df$is_internal <- mapply(grepl, pattern=df$domain, x=df$canonical_url, fixed=T)
  return(df)
}

mark_repeat_links <- function(df, threshold) {
  post_count <- df %>% 
    group_by(publication_id) %>% 
    summarize(post_count=n_distinct(post_id))
  
  link_count <- df %>% 
    distinct(post_id, str_rep, .keep_all=T) %>% 
    group_by(str_rep, publication_id) %>% 
    summarize(posts=n())
  
  repeat_measure <- left_join(link_count, post_count, by="publication_id") %>% 
    mutate(pct = posts/post_count,
           is_repeat = pct>threshold)
  
  df <- left_join(df,
                  repeat_measure %>% select(str_rep, 
                                            publication_id,
                                            is_repeat),
                  by=c("str_rep", "publication_id")
  )
  
  return(df)
}
