import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

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

def crawl_page(url):
    html = fetch_page(url)
    links = extract_links(html)

    normalize_links = []

    for link in links:
        normalize_link = normalize_url(url,link)
        normalize_links.append(normalize_link)

    return normalize_links

def crawl(start_url, max_pages):
    queue = [start_url]
    visited = []

    domain = urlparse(start_url).netloc

    while queue and len (visited) < max_pages:
        url = queue.pop(0)

        if url in visited:
            continue

        links = crawl_page(url)
        visited.append(url)

        for link in links:
            if urlparse(link).netloc != domain:
                continue

            if link not in visited and link not in queue:
                queue.append(link)

    return visited