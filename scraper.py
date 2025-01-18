import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "http://quotes.toscrape.com"

def scrape_quotes_and_authors():
    quotes = []
    authors = {}
    next_page = "/page/1"

    while next_page:
        response = requests.get(BASE_URL + next_page)
        soup = BeautifulSoup(response.text, "html.parser")

        
        for quote_block in soup.find_all("div", class_="quote"):
            text = quote_block.find("span", class_="text").text
            author = quote_block.find("small", class_="author").text
            tags = [tag.text for tag in quote_block.find_all("a", class_="tag")]

            
            quotes.append({
                "quote": text,
                "author": author,
                "tags": tags,
            })

            
            if author not in authors:
                author_link = quote_block.find("a")["href"]
                author_details = scrape_author_details(BASE_URL + author_link)
                authors[author] = author_details

        
        next_btn = soup.find("li", class_="next")
        next_page = next_btn.find("a")["href"] if next_btn else None

    
    with open("quotes.json", "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=4)

    with open("authors.json", "w", encoding="utf-8") as f:
        json.dump(list(authors.values()), f, ensure_ascii=False, indent=4)

def scrape_author_details(url):
    """Збирає інформацію про автора."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    fullname = soup.find("h3", class_="author-title").text.strip()
    born_date = soup.find("span", class_="author-born-date").text.strip()
    born_location = soup.find("span", class_="author-born-location").text.strip()
    description = soup.find("div", class_="author-description").text.strip()

    return {
        "fullname": fullname,
        "born_date": born_date,
        "born_location": born_location,
        "description": description,
    }

if __name__ == "__main__":
    scrape_quotes_and_authors()