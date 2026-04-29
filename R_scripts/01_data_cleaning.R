library("tidyverse")

nobel_data <- read_csv("complete.csv")

literature_laureates <- nobel_data |>
  filter(category == "Literature") |>
  arrange(awardYear)


head(literature_laureates)

write_csv(literature_laureates, "literature_laureates.csv")
