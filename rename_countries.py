import pandas as pd

# Load cleaned players file
df = pd.read_csv("cleaned_players.csv")

# Replace country with replacement
df["country"] = df["country"].replace("old", "new")

# Save it back to the same file
df.to_csv("cleaned_players.csv", index=False)

# Print out list of countries
df = pd.read_csv("cleaned_players.csv")
countries = sorted(df["country"].unique())
print("🌍 Countries in cleaned_players.csv:\n")
for country in countries:
    print(country)