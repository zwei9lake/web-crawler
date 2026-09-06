import httpx
from bs4 import BeautifulSoup

def fetch_page(url):
    response = httpx.get(url)
    response.raise_for_status()

    return response.text

def extract_links(html):
    soup = BeautifulSoup(html,"html.parser");

    links = []

    for link in soup.find_all("a"):
        href = link.get("href")

        if href:
            links.append(href)

    return links