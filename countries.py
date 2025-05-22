import pandas as pd

# Load the cleaned players file
df = pd.read_csv("cleaned_players.csv")

# Replace "Korea, South" with "South Korea"
df["country"] = df["country"].replace("Bosnia-Herzegovina", "Bosnia and Herzegovina")

# Save it back to the same file (or change filename if you want to keep the original)
df.to_csv("cleaned_players.csv", index=False)


df = pd.read_csv("cleaned_players.csv")
countries = sorted(df["country"].unique())
print("🌍 Countries in cleaned_players.csv:\n")
for country in countries:
    print(country)