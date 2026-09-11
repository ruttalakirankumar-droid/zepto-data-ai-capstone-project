import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("books.db")

# -----------------------------------
# 1. Read SQL Query Result into Pandas
# -----------------------------------

query1 = """
SELECT title, rating, price_gbp
FROM books
WHERE rating >= 4;
"""

df_query1 = pd.read_sql(query1, conn)

print("\nQUERY 1 RESULT:")
print(df_query1.head())


# -----------------------------------
# 2. Read another SQL Query into Pandas
# -----------------------------------

query2 = """
SELECT DISTINCT rating
FROM books
ORDER BY rating;
"""

df_query2 = pd.read_sql(query2, conn)

print("\nQUERY 2 RESULT:")
print(df_query2)


# -----------------------------------
# 3. JOIN using SQL
# -----------------------------------

join_query = """
SELECT
    categories.category_name,
    books.title,
    books.rating,
    books.price_gbp
FROM books
JOIN categories
ON books.category_id = categories.category_id
ORDER BY categories.category_name, books.rating DESC;
"""

df_sql_join = pd.read_sql(join_query, conn)

print("\nSQL JOIN RESULT:")
print(df_sql_join.head(10))


# -----------------------------------
# 4. Read tables into Pandas DataFrames
# -----------------------------------

books_df = pd.read_sql("SELECT * FROM books", conn)
categories_df = pd.read_sql("SELECT * FROM categories", conn)


# -----------------------------------
# 5. JOIN using pd.merge() - No SQL JOIN
# -----------------------------------

df_pandas_join = pd.merge(
    books_df,
    categories_df,
    on="category_id"
)

# Select same columns as SQL JOIN
df_pandas_join = df_pandas_join[
    ["category_name", "title", "rating", "price_gbp"]
]

# Sort same way as SQL JOIN
df_pandas_join = df_pandas_join.sort_values(
    by=["category_name", "rating"],
    ascending=[True, False]
).reset_index(drop=True)

print("\nPANDAS MERGE RESULT:")
print(df_pandas_join.head(10))


# -----------------------------------
# 6. Check whether both results match
# -----------------------------------

df_sql_join = df_sql_join.reset_index(drop=True)

print("\nAre SQL JOIN and Pandas MERGE equivalent?")

if df_sql_join.equals(df_pandas_join):
    print("YES - Both outputs are equivalent!")
else:
    print("NO - Outputs are different!")


# Close database connection
conn.close()