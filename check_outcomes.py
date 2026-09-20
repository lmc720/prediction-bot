import requests
import csv
from datetime import datetime

def get_market_status(market_id):
    url = f"https://api.manifold.markets/v0/market/{market_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_tracked_markets(filename="sports_markets_log.csv"):
    """Return dict of market_id -> (question, last known probability)."""
    markets = {}
    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 4:
                market_id = row[1]
                question = row[2]
                probability = row[3]
                markets[market_id] = (question, probability)
    return markets

def get_already_logged_ids(filename="outcomes_log.csv"):
    ids = set()
    with open(filename, "r") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 2:
                ids.add(row[1])
    return ids

def log_outcome(market_id, question, market_probability, resolution):
    with open("outcomes_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            market_id,
            question,
            market_probability,
            resolution,
            "auto-detected"
        ])

if __name__ == "__main__":
    tracked_markets = get_tracked_markets()
    already_logged = get_already_logged_ids()
    new_ids = set(tracked_markets.keys()) - already_logged

    print(f"Checking {len(new_ids)} untracked markets...")

    resolved_count = 0
    for market_id in new_ids:
        question, probability = tracked_markets[market_id]
        try:
            market = get_market_status(market_id)
            if market.get("isResolved"):
                log_outcome(market_id, question, probability, market.get("resolution"))
                resolved_count += 1
                print(f"Resolved: {question} -> {market.get('resolution')}")
        except Exception as e:
            print(f"Error checking {market_id}: {e}")

    print(f"Done. Logged {resolved_count} newly resolved markets.")