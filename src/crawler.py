import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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


def normalize_url(base_url, link):
    return urljoin(base_url,link)