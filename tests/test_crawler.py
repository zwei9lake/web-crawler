from src.crawler import fetch_page, extract_links, normalize_url

def test_fetch_page():
    html = fetch_page("https://example.com")

    assert "<html" in html.lower()

    
def test_extract_links():
    html="""
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
    