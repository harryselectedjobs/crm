import os
import requests
from pathlib import Path
from dotenv import load_dotenv


# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def fetch_guardian_technology_news(
    query: str = "technology",
    section: str = "technology",
    page_size: int = 10
):
    """
    Fetch latest technology news from The Guardian API.
    """

    api_key = os.getenv("GUARDIAN_API_KEY")

    if not api_key:
        raise ValueError("GUARDIAN_API_KEY not found in .env")

    url = "https://content.guardianapis.com/search"

    params = {
        "q": query,
        "section": section,
        "order-by": "newest",
        "show-fields": "headline,trailText,byline,thumbnail",
        "page-size": page_size,
        "api-key": api_key,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()