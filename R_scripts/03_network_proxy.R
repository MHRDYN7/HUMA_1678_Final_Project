# --- 03_network_proxy.R ---
# Purpose: Map the connections between laureates and their organizations/affiliations.

library(tidyverse)

# Load the data
df <- read_csv("literature_laureates.csv")

# 1. Create Edges (Laureate -> Organization)
# We'll look at orgName and affiliation_1
network_edges <- df |>
  select(name, orgName, affiliation_1) |>
  pivot_longer(cols = c(orgName, affiliation_1), names_to = "type", values_to = "organization") |>
  filter(!is.na(organization)) |>
  select(from = name, to = organization)

# 2. Create Nodes
laureate_nodes <- df |>
  select(name) |>
  distinct() |>
  mutate(type = "Laureate")

org_nodes <- network_edges |>
  select(organization) |>
  distinct() |>
  rename(name = organization) |>
  mutate(type = "Organization")

network_nodes <- bind_rows(laureate_nodes, org_nodes)

# Save the results for network visualization
write_csv(network_edges, "network_edges.csv")
write_csv(network_nodes, "network_nodes.csv")

print("Network proxy analysis complete. Files saved: network_edges.csv, network_nodes.csv")
