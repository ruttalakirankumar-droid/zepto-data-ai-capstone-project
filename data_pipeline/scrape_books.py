import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin


BASE_URL = "https://books.toscrape.com/"

# 3 categories
CATEGORIES = [
    "Travel",
    "Mystery",
    "Historical Fiction"
]


def get_category_links():
    """Get category names and their URLs."""

    response = requests.get(BASE_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    category_links = {}

    for a in soup.select(".side_categories ul li ul li a"):
        category_name = a.text.strip()

        if category_name in CATEGORIES:
            category_links[category_name] = urljoin(
                BASE_URL,
                a["href"]
            )

    return category_links


def scrape_category(category_name, category_url):
    """Scrape all books from one category."""

    books_data = []
    current_url = category_url

    while current_url:

        response = requests.get(current_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        books = soup.find_all("article", class_="product_pod")

        for book in books:

            title = book.h3.a["title"]

            price = book.find(
                "p",
                class_="price_color"
            ).text

            availability = book.find(
                "p",
                class_="instock availability"
            ).text.strip()

            rating = book.find(
                "p",
                class_="star-rating"
            )["class"][1]

            books_data.append({
                "category": category_name,
                "title": title,
                "price": price,
                "rating": rating,
                "availability": availability
            })

        # Check for next page
        next_button = soup.select_one("li.next a")

        if next_button:
            current_url = urljoin(
                current_url,
                next_button["href"]
            )
        else:
            current_url = None

    return books_data


def main():

    all_books = []

    category_links = get_category_links()

    for category, url in category_links.items():

        print(f"Scraping {category}...")

        books = scrape_category(category, url)

        all_books.extend(books)

    df = pd.DataFrame(all_books)

    # Save raw scraped data
    df.to_csv(
        "data_pipeline/raw_books.csv",
        index=False
    )

    print("\nScraping completed!")
    print(f"Total books scraped: {len(df)}")

    print("\nBooks per category:")
    print(df["category"].value_counts())

    print("\nFirst 5 books:")
    print(df.head())


if __name__ == "__main__":
    main()