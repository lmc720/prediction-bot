import requests
import csv
from datetime import datetime

SEARCH_TERMS = [
    "Premier League",
    "Champions League",
    "NBA",
    "NFL",
]

def fetch_markets_for_term(term, limit=50):
    url = "https://api.manifold.markets/v0/search-markets"
    params = {
        "term": term,
        "limit": limit,
        "sort": "close-date"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def save_to_csv(markets, filename="sports_markets_log.csv"):
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        for m in markets:
            probability = m.get("probability")
            if probability is None:
                continue

            close_time_ms = m.get("closeTime")
            if close_time_ms:
                close_time_readable = datetime.fromtimestamp(close_time_ms / 1000).isoformat()
            else:
                close_time_readable = ""

            writer.writerow([
                datetime.now().isoformat(),
                m.get("id"),
                m.get("question"),
                probability,
                close_time_readable
            ])

if __name__ == "__main__":
    total_logged = 0
    for term in SEARCH_TERMS:
        try:
            markets = fetch_markets_for_term(term, limit=50)
            save_to_csv(markets)
            total_logged += len(markets)
            print(f"Fetched {len(markets)} markets for '{term}'")
        except Exception as e:
            print(f"Failed to fetch '{term}': {e}")
            continue  # move on to the next term instead of crashing

    print(f"Done. Total markets processed: {total_logged} at {datetime.now()}")