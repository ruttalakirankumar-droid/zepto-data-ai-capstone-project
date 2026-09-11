import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("books.db")

# All SQL queries
queries = {

    # Query 1: SELECT + WHERE
    "Query 1 - SELECT + WHERE": """
        SELECT title, rating, price_gbp
        FROM books
        WHERE rating >= 4;
    """,

    # Query 2: ORDER BY
    "Query 2 - ORDER BY": """
        SELECT title, rating, price_gbp
        FROM books
        ORDER BY price_gbp DESC;
    """,

    # Query 3: LIMIT
    "Query 3 - LIMIT": """
        SELECT title, rating, price_gbp
        FROM books
        LIMIT 10;
    """,

    # Query 4: DISTINCT
    "Query 4 - DISTINCT": """
        SELECT DISTINCT rating
        FROM books
        ORDER BY rating;
    """,

    # Query 5: BETWEEN
    "Query 5 - BETWEEN": """
        SELECT title, rating, price_gbp
        FROM books
        WHERE price_gbp BETWEEN 20 AND 40;
    """,

    # Query 6: JOIN
    "Query 6 - JOIN": """
        SELECT
            categories.category_name,
            books.title,
            books.rating,
            books.price_gbp
        FROM books
        JOIN categories
            ON books.category_id = categories.category_id
        ORDER BY categories.category_name, books.rating DESC
        LIMIT 10;
    """
}

# Execute and display each query
for name, query in queries.items():

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    print("\nSQL Query:")
    print(query)

    result = pd.read_sql_query(query, conn)

    print("\nOutput:")
    print(result)

# Close connection
conn.close()

print("\nAll SQL queries executed successfully!")s