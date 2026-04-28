"""
Watchlist Manager
Persists supplier evaluations to a local JSON file.
"""

import json
import os
from datetime import datetime

WATCHLIST_FILE = "watchlist.json"


def load_watchlist() -> dict:
    if not os.path.exists(WATCHLIST_FILE):
        return {}
    try:
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_to_watchlist(supplier_name: str, score: float, risk_level: str, summary: str):
    watchlist = load_watchlist()
    previous_score = watchlist.get(supplier_name, {}).get("score", None)
    watchlist[supplier_name] = {
        "score": score,
        "previous_score": previous_score,
        "risk_level": risk_level,
        "summary": summary,
        "last_evaluated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f, indent=2)
    return previous_score


def get_ranked_watchlist() -> list:
    watchlist = load_watchlist()
    ranked = sorted(watchlist.items(), key=lambda x: x[1].get("score", 99))
    return [(name, data) for name, data in ranked]


def detect_score_changes() -> list:
    watchlist = load_watchlist()
    alerts = []
    for name, data in watchlist.items():
        current = data.get("score", 0)
        previous = data.get("previous_score")
        if previous is not None and (current - previous) >= 1.5:
            alerts.append({
                "supplier": name,
                "previous_score": previous,
                "current_score": current,
                "risk_level": data.get("risk_level", "UNKNOWN"),
                "last_evaluated": data.get("last_evaluated", ""),
            })
    return alerts


def remove_from_watchlist(supplier_name: str) -> bool:
    watchlist = load_watchlist()
    if supplier_name in watchlist:
        del watchlist[supplier_name]
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(watchlist, f, indent=2)
        return True
    return False
