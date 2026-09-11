# Data Pipeline

## Project Overview

This module builds a complete data pipeline using book data.

The project performs the following tasks:

- Scrapes book data
- Cleans the collected data
- Converts prices from GBP to INR
- Saves cleaned data into a CSV file
- Creates an SQLite database
- Stores data in two related tables
- Executes SQL queries
- Reads SQL results into pandas DataFrames
- Reproduces a SQL JOIN using pandas merge

## Files

- `scrape_books.py` - Scrapes book data
- `raw_books.csv` - Stores the raw scraped data
- `clean_data.py` - Cleans and processes the data
- `cleaned_books.csv` - Stores the cleaned data
- `database.py` - Creates the SQLite database and tables
- `load_to_database.py` - Loads cleaned data into the database
- `sql_queries.py` - Executes SQL queries
- `pandas_merge.py` - Compares SQL JOIN and pandas merge results

## Installation

Install the required packages using:

```bash
pip install -r requirements.txt

```

## How to Run

Run the scripts in the following order:

```bash
python scrape_books.py
python clean_data.py
python database.py
python load_to_database.py
python sql_queries.py
python pandas_merge.py
```

## Design Decisions

- Python was used for web scraping and data processing.
- Pandas was used for cleaning and analyzing the data.
- SQLite was used as the database because it is lightweight and easy to use.
- The data was stored in two related tables using primary and foreign keys.
- SQL queries were used to analyze the database.
- pandas `merge()` was used to reproduce and compare the SQL JOIN result.
- Book prices were converted from GBP to INR using the project-defined conversion rate.

## Requirements

The project demonstrates:

- Web scraping
- Data cleaning
- CSV file creation
- Price conversion from GBP to INR
- SQLite database creation
- Two related database tables
- SQL queries using SELECT, WHERE, ORDER BY, LIMIT, DISTINCT and IN/BETWEEN
- SQL JOIN between two tables
- Reading SQL results using pandas
- Comparing SQL JOIN and pandas merge results