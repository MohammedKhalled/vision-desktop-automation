import requests
import json
from pathlib import Path


def fetch_posts(limit=10):
    try:
        response = requests.get(
            "https://jsonplaceholder.typicode.com/posts",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )
        response.raise_for_status()
        return response.json()[:limit]

    except Exception as e:
        print(f"API unavailable, using fallback data: {e}")

        fallback_path = Path(__file__).parent.parent / "data" / "fallback_posts.json"
        with open(fallback_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data[:limit]
