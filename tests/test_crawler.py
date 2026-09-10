import httpx

from src.crawler import (
    fetch_page,
    extract_links,
    normalize_url,
    crawl_page,
    crawl,
    is_allowed_by_robots,
    fetch_robots,
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


def test_crawl_output(monkeypatch, capsys):
    pages = {
        "https://example.com":"""
            <a href = "/about">About</a>
            <a href = "https://google.com">Google</a>
        """,
        "https://example.com/about":"""
        """,
    }

    def mock_fetch_page(url):
        return pages[url]

    monkeypatch.setattr("src.crawler.fetch_page", mock_fetch_page)

    crawl("https://example.com", max_pages=10)

    captured = capsys.readouterr()

    assert "Crawling: https://example.com" in captured.out
    assert "Found: 2 links" in captured.out
    assert "Skipping external URL: https://google.com" in captured.out

def test_crawl_depth(monkeypatch):
    pages = {
        "https://example.com":"""
            <a href = "/about">About</a>
        """,
        "https://example.com/about":"""
            <a href = "/team">Team</a>
        """,
        "https://example.com/team":"""
        """,
    }

    def mock_fetch_page(url):
        return pages[url]

    monkeypatch.setattr("src.crawler.fetch_page", mock_fetch_page)

    visited = crawl("https://example.com", max_pages=10, max_depth=1)

    assert visited == [
        "https://example.com",
        "https://example.com/about",
    ]

def test_fetch_page_timeout(monkeypatch):
    def mock_get(url, timeout, headers):
        assert timeout == 10

        class MockResponse:
            text = "<html></html>"

            def raise_for_status(self):
                pass

        return MockResponse()

    monkeypatch.setattr("src.crawler.httpx.get", mock_get)

    html = fetch_page("https://example.com")

    assert html == "<html></html>"


def test_fetch_page_request_error(monkeypatch):
    def mock_get(url, timeout, headers):
        raise httpx.RequestError("Connection Failed")

    monkeypatch.setattr("src.crawler.httpx.get", mock_get)

    html = fetch_page("https://example.com")

    assert html is None


def test_fetch_page_http_error(monkeypatch):
    def mock_get(url, timeout, headers):
        request = httpx.Request("GET", url)
        response = httpx.Response(404, request=request)

        raise httpx.HTTPStatusError(
            "404 Not Found",
            request=request,
            response=response,
        )

    monkeypatch.setattr("src.crawler.httpx.get", mock_get)

    html = fetch_page("https://example.com/not-found")

    assert html is None


def test_crawl_page_request_error(monkeypatch):
    def mock_fetch_page(url):
        return None

    monkeypatch.setattr("src.crawler.fetch_page", mock_fetch_page)

    links = crawl_page("https://example.com")

    assert links == []


def test_crawl_continues_after_request_error(monkeypatch):
    pages = {
        "https://example.com": """
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        """,
        "https://example.com/contact": """
        """,
    }

    def mock_fetch_page(url):
        if url == "https://example.com/about":
            return None

        return pages[url]

    monkeypatch.setattr("src.crawler.fetch_page", mock_fetch_page)

    visited = crawl("https://example.com", max_pages=10)

    assert visited == [
        "https://example.com",
        "https://example.com/about",
        "https://example.com/contact",
    ]

def test_crawl_continues_after_http_error(monkeypatch):
    pages = {
        "https://example.com": """
            <a href="/not-found">Not Found</a>
            <a href="/contact">Contact</a>
        """,
        "https://example.com/contact": """
        """,
    }

    def mock_fetch_page(url):
        if url == "https://example.com/not-found":
            return None

        return pages[url]

    monkeypatch.setattr("src.crawler.fetch_page", mock_fetch_page)

    visited = crawl("https://example.com", max_pages=10)

    assert visited == [
        "https://example.com",
        "https://example.com/not-found",
        "https://example.com/contact",
    ]


def test_fetch_page_user_agent(monkeypatch):
    def mock_get(url, timeout, headers):
        assert headers["User-Agent"] == "WebCrawler/0.1"

        class MockResponse:
            text = "<html></html>"

            def raise_for_status(self):
                pass

        return MockResponse()

    monkeypatch.setattr("src.crawler.httpx.get", mock_get)

    html = fetch_page("https://example.com")

    assert html == "<html></html>"


def test_is_allowed_by_robots(monkeypatch):
    robots = """
        User-agent: WebCrawler
        Allow: /
    """

    assert is_allowed_by_robots(
        robots,
        "https://example.com/about"
    )


def test_is_not_allowed_by_robots():
    robots = """
        User-agent: WebCrawler
        Disallow: /private/
    """

    assert not is_allowed_by_robots(
        robots,
        "https://example.com/private/data"
    )


def test_crawl_respect_robots(monkeypatch):
    pages = {
        "https://example.com": """
            <a href="/about">About</a>
            <a href="/private">Private</a>
        """,
        "https://example.com/about": """
        """,
        "https://example.com/private": """
        """,
    }

    robots = """
        User-agent: WebCrawler
        Disallow: /private
    """

    def mock_fetch_page(url):
        return pages[url]

    def mock_fetch_robots(url):
        return robots

    monkeypatch.setattr("src.crawler.fetch_page", mock_fetch_page)
    monkeypatch.setattr("src.crawler.fetch_robots", mock_fetch_robots)

    visited = crawl("https://example.com", max_pages=10)

    assert visited == [
        "https://example.com",
        "https://example.com/about",
    ]


def test_fetch_robots(monkeypatch):
    def mock_get(url, timeout, headers):
        assert url == "https://example.com/robots.txt"
        assert timeout == 10
        assert headers["User-Agent"] == "WebCrawler/0.1"

        class MockResponse:
            text = """
                User-agent: WebCrawler
                Disallow: /private/
            """

            def raise_for_status(self):
                pass

        return MockResponse()

    monkeypatch.setattr("src.crawler.httpx.get", mock_get)

    robots = fetch_robots("https://example.com")

    assert "Disallow: /private/" in robots


def test_fetch_robots_http_error(monkeypatch):
    def mock_get(url, timeout, headers):
        request = httpx.Request("GET", url)
        response = httpx.Response(404, request=request)

        raise httpx.HTTPStatusError(
            "404 Not Found",
            request=request,
            response=response,
        )

    monkeypatch.setattr("src.crawler.httpx.get", mock_get)

    robots = fetch_robots("https://example.com")

    assert robots is None