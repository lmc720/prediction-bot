import os
import csv
import random
from datetime import datetime
from dotenv import load_dotenv
import anthropic
import requests

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_target_markets(count=5, max_days_to_close=14):
    """
    Fetch a batch of currently open, genuinely uncertain Premier League
    markets closing within the next `max_days_to_close` days.
    """
    url = "https://api.manifold.markets/v0/search-markets"
    params = {
        "term": "Premier League",
        "limit": 50,
        "sort": "close-date"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    markets = response.json()

    now_ms = datetime.now().timestamp() * 1000
    cutoff_ms = now_ms + (max_days_to_close * 24 * 60 * 60 * 1000)

    eligible = [
        m for m in markets
        if not m.get("isResolved")
        and m.get("probability") is not None
        and 0.05 < m.get("probability") < 0.95
        and m.get("closeTime") is not None
        and now_ms < m.get("closeTime") < cutoff_ms
    ]

    if len(eligible) <= count:
        return eligible

    return random.sample(eligible, count)

def research_and_predict(question):
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 3
        }],
        messages=[{
            "role": "user",
            "content": f"""You are forecasting a prediction market question.

Question: {question}

Use at most 2-3 targeted web searches to research this efficiently, then 
estimate the probability (0-100) that this resolves YES. End your response 
with exactly this format on its own line:
PROBABILITY: <number>
REASONING: <2-3 sentence explanation>
"""
        }]
    )

    full_text = ""
    for block in response.content:
        if block.type == "text":
            full_text += block.text
    return full_text

def parse_prediction(text):
    probability = None
    reasoning = ""
    for line in text.split("\n"):
        if line.startswith("PROBABILITY:"):
            probability = line.replace("PROBABILITY:", "").strip()
        if line.startswith("REASONING:"):
            reasoning = line.replace("REASONING:", "").strip()
    return probability, reasoning

def log_prediction(market_id, question, market_probability, claude_probability, reasoning, filename="predictions_log.csv"):
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            market_id,
            question,
            market_probability,
            claude_probability,
            reasoning
        ])

if __name__ == "__main__":
    markets = get_target_markets(count=5, max_days_to_close=14)

    if not markets:
        print("No eligible markets found within the closing-time window.")
    else:
        print(f"Found {len(markets)} eligible markets.\n")

        for market in markets:
            question = market["question"]
            market_probability = market["probability"]
            market_id = market["id"]

            print(f"--- {question} ---")
            print(f"Current market price: {market_probability}")

            result_text = research_and_predict(question)
            claude_probability, reasoning = parse_prediction(result_text)

            print(f"Claude's estimate: {claude_probability}")
            print(f"Reasoning: {reasoning}\n")

            log_prediction(market_id, question, market_probability, claude_probability, reasoning)

        print(f"Done. Logged {len(markets)} predictions.")