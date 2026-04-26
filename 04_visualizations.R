# --- 04_visualizations.R ---
# Purpose: Generate plots for migration trends, hubs, and networks.

library(tidyverse)

# Load processed data
migration_df <- read_csv("migration_analysis.csv")
hubs_df <- read_csv("literary_hubs.csv")

# 1. Migration Trend Over Time
migration_trend <- migration_df |>
  group_by(decade = 10 * (awardYear %/% 10)) |>
  summarise(
    total = n(),
    migrants = sum(is_migrant, na.rm = TRUE),
    percent_migrant = (migrants / total) * 100
  )

p1 <- ggplot(migration_trend, aes(x = decade, y = percent_migrant)) +
  geom_line(color = "steelblue", size = 1) +
  geom_point(color = "darkblue", size = 2) +
  labs(
    title = "Percentage of Migrant Literature Laureates by Decade",
    subtitle = "Comparing birth country vs. professional residence",
    x = "Decade",
    y = "Percentage (%)"
  ) +
  theme_minimal()

ggsave("migration_trend.png", p1, width = 8, height = 5)

# 2. Top Literary Hubs (Professional Bases)
top_hubs <- hubs_df |>
  arrange(desc(death_count)) |>
  head(10)

p2 <- ggplot(top_hubs, aes(x = reorder(city, death_count), y = death_count)) +
  geom_col(fill = "darkorange") +
  coord_flip() +
  labs(
    title = "Top 10 Literary Hubs (by Laureate Professional Base/Death City)",
    x = "City",
    y = "Number of Laureates"
  ) +
  theme_minimal()

ggsave("top_hubs.png", p2, width = 8, height = 5)

# 3. Origin vs. Destination (Top Countries)
top_origins <- migration_df |>
  count(origin, sort = TRUE) |>
  head(10)

p3 <- ggplot(top_origins, aes(x = reorder(origin, n), y = n)) +
  geom_col(fill = "seagreen") +
  coord_flip() +
  labs(
    title = "Top 10 Countries of Origin (Birth Country)",
    x = "Country",
    y = "Number of Laureates"
  ) +
  theme_minimal()

ggsave("top_origins.png", p3, width = 8, height = 5)

print("Visualizations complete. Files saved: migration_trend.png, top_hubs.png, top_origins.png")
