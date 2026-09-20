import csv
from datetime import datetime

def log_outcome():
    print("Log a resolved market outcome")
    market_id = input("Market ID: ")
    question = input("Question: ")
    market_probability = input("Market's probability at the time (e.g. 0.679): ")
    actual_outcome = input("Actual outcome (YES or NO): ").upper()
    notes = input("Any notes (optional): ")

    with open("outcomes_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            market_id,
            question,
            market_probability,
            actual_outcome,
            notes
        ])
    print("Logged!")

if __name__ == "__main__":
    log_outcome()