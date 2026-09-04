from src.crawler import fetch_page

def test_fetch_page():
    html = fetch_page("https://example.com")

    assert "<html" in html.lower()
    