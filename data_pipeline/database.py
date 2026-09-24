import sqlite3
import pandas as pd

# Create/connect to SQLite database
conn = sqlite3.connect("books.db")

# Create cursor
cursor = conn.cursor()

# Create categories table
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE
)
""")

# Create books table
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,
    title TEXT,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock BOOLEAN,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
)
""")

# Save changes
conn.commit()

print("Database and tables created successfully!")
# Load cleaned data
df = pd.read_csv("cleaned_books.csv")

print("Cleaned data loaded successfully!")
print(f"Total books: {len(df)}")
# Insert unique categories
categories = df["category"].unique()

for category in categories:
    cursor.execute(
        "INSERT OR IGNORE INTO categories (category_name) VALUES (?)",
        (category,)
    )

conn.commit()

print("Categories inserted successfully!")
# Get category IDs
category_ids = {}

cursor.execute("SELECT category_id, category_name FROM categories")

for category_id, category_name in cursor.fetchall():
    category_ids[category_name] = category_id
    # Insert books into the books table
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO books
        (title, price_gbp, price_inr, rating, in_stock, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["title"],
        row["price_gbp"],
        row["price_inr"],
        row["rating"],
        row["in_stock"],
        category_ids[row["category"]]
    ))

conn.commit()

print("Books inserted successfully!")
# Close connection
conn.close()