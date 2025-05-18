import pandas as pd

# Load the dataset
df = pd.read_csv("transfers.csv")

# Show the first 5 rows
print(df.head())

# Show all column names
print(df.columns)

# Load players and clubs
players_df = pd.read_csv("players.csv")
clubs_df = pd.read_csv("clubs.csv")

# Show their columns
print("Players Columns:", players_df.columns)
print("Clubs Columns:", clubs_df.columns)
