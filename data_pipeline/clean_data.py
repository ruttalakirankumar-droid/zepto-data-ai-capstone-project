import pandas as pd


# Read the scraped data
df = pd.read_csv("raw_books.csv")
# Display basic information
print("Dataset Shape:", df.shape)

print("\nColumn Names:")
print(df.columns)

print("\nFirst 5 Rows:")
print(df.head())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

# Remove £ symbol and convert price to float
df["price_gbp"] = (
    df["price"]
    .str.replace(r"[^0-9.]", "", regex=True)
    .astype(float)
)

# Convert rating words to numbers
rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

df["rating"] = df["rating"].map(rating_map)

# Convert availability to Boolean
df["in_stock"] = df["availability"].str.contains(
    "In stock",
    case=False,
    na=False
)

# GBP to INR conversion
GBP_TO_INR = 105.50

df["price_inr"] = (
    df["price_gbp"] * GBP_TO_INR
).round(2)

# Keep only required columns
clean_df = df[
    [
        "category",
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock"
    ]
]

# Save cleaned data
clean_df.to_csv(
    "cleaned_books.csv",
    index=False
)

print("Data cleaning completed successfully!")
print(f"Total books: {len(clean_df)}")

print("\nFirst 5 rows:")
print(clean_df.head())

print("\nData types:")
print(clean_df.dtypes)
print("\nCategories:")
print(clean_df["category"].value_counts())