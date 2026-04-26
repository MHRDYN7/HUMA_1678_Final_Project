# --- 02_spatial_analysis.R ---
# Purpose: Analyze migration patterns and identify literary hubs.

library(tidyverse)

# Load the data
df <- read_csv("literature_laureates.csv")

# 1. Migration Analysis
# We compare birth_countryNow with the country of residence or affiliation.
# Since 'residence_1' or 'affiliation_1' might be used, we'll check for migration.
# Note: In the literature dataset, many laureates don't have 'orgName' but have 'residence_1'.

migration_df <- df |>
  mutate(
    # A simple migration flag: Is the birth country different from the residence/affiliation country?
    # We'll use birth_countryNow as the origin.
    origin = birth_countryNow,
    # For destination, we'll check residence_1 first, then affiliation_1
    destination = coalesce(residence_1, affiliation_1),
    is_migrant = !is.na(origin) & !is.na(destination) & (origin != destination)
  ) |>
  select(id, name, awardYear, origin, destination, is_migrant)

# 2. Hub Identification
# Identify cities that appear most frequently as birth cities vs. death/residence cities.
hubs_birth <- df |>
  count(birth_cityNow, sort = TRUE) |>
  rename(city = birth_cityNow, birth_count = n)

hubs_death <- df |>
  count(death_cityNow, sort = TRUE) |>
  rename(city = death_cityNow, death_count = n)

hubs_combined <- full_join(hubs_birth, hubs_death, by = "city") |>
  filter(!is.na(city)) |>
  mutate(
    birth_count = replace_na(birth_count, 0),
    death_count = replace_na(death_count, 0),
    total_activity = birth_count + death_count
  ) |>
  arrange(desc(total_activity))

# Save the results
write_csv(migration_df, "migration_analysis.csv")
write_csv(hubs_combined, "literary_hubs.csv")

print("Spatial analysis complete. Files saved: migration_analysis.csv, literary_hubs.csv")
