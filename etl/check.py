import pandas as pd

df = pd.read_csv("data/raw/olist_order_reviews_dataset.csv")

# Find duplicate review_id values
duplicates = df[df.duplicated(subset=["review_id"], keep=False)]

print("Duplicate review_id rows:", len(duplicates))

print(duplicates.sort_values("review_id").head(30))