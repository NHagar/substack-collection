library(tidyverse)

df <- read_csv("./data/posts_parsed.csv")

# params
repeat_threshold <- 0.5

# per-newsletter post counts
post_count <- df %>% 
  group_by(publication_id) %>% 
  summarize(post_count=n_distinct(post_id))

# ID internal links
df$is_internal <- mapply(grepl, pattern=df$domain, x=df$canonical_url, fixed=T)

# ID repeat links
link_count <- df %>% 
  distinct(post_id, str_rep, .keep_all=T) %>% 
  group_by(str_rep, publication_id) %>% 
  summarize(posts=n())

repeat_measure <- left_join(link_count, post_count, by="publication_id") %>% 
  mutate(pct = posts/post_count,
         is_repeat = pct>repeat_threshold)

df <- left_join(df,
          repeat_measure %>% select(str_rep, 
                                    publication_id,
                                    is_repeat),
          by=c("str_rep", "publication_id")
)

df %>% 
  filter(!is_repeat, !is_internal)
