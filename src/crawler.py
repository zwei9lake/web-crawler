import httpx

def fetch_page(url):
    response = httpx.get(url)
    response.raise_for_status()

    return response.text
