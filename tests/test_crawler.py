from src.crawler import fetch_page, extract_links

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