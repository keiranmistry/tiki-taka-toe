import pandas as pd

df = pd.read_csv("cleaned_players.csv")
countries = sorted(df["country"].unique())
print("🌍 Countries in cleaned_players.csv:\n")
for country in countries:
    print(country)