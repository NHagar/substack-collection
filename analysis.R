library(tidyverse)

df <- read_csv("./data/posts_parsed.csv")

# ID repeat / internal links
df %>% 
  mutate(is_internal)
