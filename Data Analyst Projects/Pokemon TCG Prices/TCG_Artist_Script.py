import pandas as pd

fileName = "C:\\Users\\Gabriel\\Desktop\\bi_dwh pivot\\pokemon_tcg_data\\pokemon-tcg-data-master 1999-2023.csv"
df = pd.read_csv(fileName)

artist_summary = (
    df.groupby("artist")
      .agg({
          "id": "count",
          "set": pd.Series.nunique,
          "rarity": lambda x: x.value_counts().to_dict()
      })
      .rename(columns={"id": "Card Count", "set": "Unique Sets", "rarity":"Rarity Distribution"})
      .reset_index()
)

artist_summary.to_csv("artist_summary.csv", index=False)
