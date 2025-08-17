import pandas as pd
from team_map import TEAM_NAME_MAP

# Load the cleaned players file
df = pd.read_csv("cleaned_players.csv")

# Apply the mapping to the 'team' column
df["team"] = df["team"].apply(lambda t: TEAM_NAME_MAP.get(t, t))  # fallback to original if not in map

# Save it back (or to a new file if you want a backup)
df.to_csv("cleaned_players.csv", index=False)

print("✅ Team names updated using TEAM_NAME_MAP in cleaned_players.csv")
