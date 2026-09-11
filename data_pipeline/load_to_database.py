import sqlite3
import pandas as pd

# Read cleaned books data
df = pd.read_csv("data_pipeline/cleaned_books.csv")

# Connect to SQLite database
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

# Insert categories
categories = df["category"].unique()

for category in categories:
    cursor.execute(
        "INSERT OR IGNORE INTO categories (category_name) VALUES (?)",
        (category,)
    )

conn.commit()

# Get category IDs
cursor.execute("SELECT category_id, category_name FROM categories")

category_map = {
    name: category_id
    for category_id, name in cursor.fetchall()
}

# Insert books
for _, row in df.iterrows():

    cursor.execute("""
        INSERT INTO books (
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["title"],
        row["price_gbp"],
        row["price_inr"],
        row["rating"],
        bool(row["in_stock"]),
        category_map[row["category"]]
    ))

conn.commit()

# Check inserted data
cursor.execute("SELECT COUNT(*) FROM books")
book_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM categories")
category_count = cursor.fetchone()[0]

print("Data loaded successfully!")
print(f"Total categories: {category_count}")
print(f"Total books: {book_count}")

conn.close()