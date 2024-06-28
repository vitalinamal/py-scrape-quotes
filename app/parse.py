import csv
from dataclasses import dataclass, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tags_content = quote_soup.select_one(".keywords")["content"]
    tags = tags_content.split(",") if tags_content else []

    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tags,
    )


def get_next_page(current_url: BeautifulSoup) -> str | None:
    response = requests.get(current_url)
    soup = BeautifulSoup(response.content, "html.parser")
    next_link = soup.select_one("li.next a")
    if not next_link:
        return None

    next_page_url = next_link["href"]
    return f"{BASE_URL.rstrip('/')}{next_page_url}"  # noqa: Q000


def get_single_page_quotes(page_url: str) -> list[Quote]:
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    current_url = BASE_URL

    while True:
        quotes = get_single_page_quotes(current_url)
        all_quotes.extend(quotes)

        next_page = get_next_page(current_url)
        if not next_page:
            break

        current_url = next_page

    return all_quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in get_all_quotes()])


if __name__ == "__main__":
    main("quotes.csv")
