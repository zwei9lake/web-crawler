from src.crawler import (
    fetch_page,
    extract_links,
    normalize_url,
    crawl_page,
    crawl,
)

def test_fetch_page():
    html = fetch_page("https://example.com")

    assert "<html" in html.lower()

    
def test_extract_links():
    html = """
    <html>
        <a href="https://example.com">Example</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
    """

    links = extract_links(html)

    assert links == [
        "https://example.com",
        "/about",
        "/contact",
    ]


def test_normalize_url():
    assert normalize_url(
        "https://example.com",
        "/about"
    ) == "https://example.com/about"

    assert normalize_url(
        "https://example.com/products/",
        "item-1"
    ) == "https://example.com/products/item-1"

    assert normalize_url(
        "https://example.com",
        "https://google.com"
    ) == "https://google.com"

    assert normalize_url(
        "https://example.com/products/",
        "../about"
    ) == "https://example.com/about"

    assert normalize_url(
        "https://example.com/products/",
        "./item-1"
    ) == "https://example.com/products/item-1"
    

def test_crawl_patch(monkeypatch):
    html = """
    <html>
        <a href = "/about">About</a>
        <a href = "products/">Products</a>
        <a href = "https://google.com">Google</a>
    </html>
    """

    def mock_fetch_page(url):
        return html

    monkeypatch.setattr("src.crawler.fetch_page", mock_fetch_page)

    links = crawl_page("https://example.com")

    assert links == [
        "https://example.com/about",
        "https://example.com/products/",
        "https://google.com",
    ]

        
def test_crawl(monkeypatch):
    pages = {
        "https://example.com":"""
        <a href = "/about">About</a>
        <a href = "/products">Products</a>
        """,
        "https://example.com/about": """
            <a href="/contact">Contact</a>
        """,
        "https://example.com/products": """
            <a href="/about">About</a>
        """,
        "https://example.com/contact": """
        """,
    }

    def mock_fetch_page(url):
        return pages[url]

    monkeypatch.setattr("src.crawler.fetch_page", mock_fetch_page)

    visited = crawl("https://example.com", max_pages=4)

    assert visited == [
        "https://example.com",
        "https://example.com/about",
        "https://example.com/products",
        "https://example.com/contact",
    ]


def test_crawl_same_domain(monkeypatch):
    pages = {
        "https://example.com": """
            <a href="/about">About</a>
            <a href="https://google.com">Google</a>
        """,
        "https://example.com/about": """
        """,
    }

    def mock_fetch_page(url):
        return pages[url]

    monkeypatch.setattr("src.crawler.fetch_page", mock_fetch_page)

    visited = crawl("https://example.com", max_pages=10)

    assert visited == [
        "https://example.com",
        "https://example.com/about",
    ]