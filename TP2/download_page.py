
import requests


def download_html(url):
    """
    Download an HTML page from a URL.
    Returns the HTML content as text.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "text/html" not in content_type.lower():
        raise ValueError("The URL does not point to an HTML page.")

    response.encoding = response.apparent_encoding

    return response.text

