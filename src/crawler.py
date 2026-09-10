import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

def fetch_page(url):
    try:
        response = httpx.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "WebCrawler/0.1"
            }
        )
        response.raise_for_status()

        return response.text

    except httpx.RequestError:
        return None

    except httpx.HTTPStatusError:
        return None


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

    if html is None:
        return []

    links = extract_links(html)

    normalize_links = []

    for link in links:
        normalize_link = normalize_url(url,link)
        normalize_links.append(normalize_link)

    return normalize_links

def crawl(start_url, max_pages, max_depth = None):
    queue = [(start_url, 0)]
    visited = []

    domain = urlparse(start_url).netloc
    robots = fetch_robots(start_url)

    while queue and len(visited) < max_pages:
        url, depth = queue.pop(0)

        if url in visited:
            continue

        print(f"Crawling: {url}")

        links = crawl_page(url)

        print(f"Found: {len(links)} links")

        visited.append(url)

        if max_depth is not None and depth >= max_depth:
            continue

        for link in links:
            if urlparse(link).netloc != domain:
                print(f"Skipping external URL: {link}")
                continue

            if robots is not None and not is_allowed_by_robots(robots, link):
                print(f"Skipping disallowed URL: {link}")
                continue

            if link not in visited and link not in [item[0] for item in queue]:
                queue.append((link, depth + 1))

    return visited

def is_allowed_by_robots(robots, url):
    parser = RobotFileParser()
    parser.parse(robots.splitlines())

    return parser.can_fetch("WebCrawler/0.1", url)


def fetch_robots(base_url):
    robots_url = urljoin(base_url, "/robots.txt")

    try:
        response = httpx.get(
            robots_url,
            timeout=10,
            headers={
                "User-Agent": "WebCrawler/0.1"
            }
        )

        response.raise_for_status()

        return response.text

    except httpx.RequestError:
        return None

    except httpx.HTTPStatusError:
        return None
