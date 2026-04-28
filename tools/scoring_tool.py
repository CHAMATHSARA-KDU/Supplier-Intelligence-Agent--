from langchain.tools import tool

NEGATIVE_SIGNALS = {
    "bankruptcy": 3.0, "insolvent": 3.0, "closed": 2.5, "fraud": 3.0,
    "sanction": 2.5, "banned": 2.5, "restricted": 1.5,
    "labour unrest": 2.0, "strike": 1.5, "protest": 1.0,
    "complaint": 1.0, "lawsuit": 1.5, "recall": 2.0,
    "delay": 1.0, "late": 0.8, "shortage": 0.8,
    "instability": 1.5, "conflict": 2.0, "war": 2.5,
    "flood": 1.0, "earthquake": 1.5, "typhoon": 1.0,
    "poor quality": 1.5, "defect": 1.0, "rejected": 1.0,
}

POSITIVE_SIGNALS = {
    "certified": 1.0, "iso": 1.0, "award": 0.5,
    "on-time": 1.0, "reliable": 0.8, "trusted": 0.8,
    "stable": 0.8, "profitable": 0.8, "growing": 0.5,
    "partnership": 0.5, "long-term": 0.5,
}

TRUST_LEVELS = {
    (0, 3):  "LOW RISK — Highly recommended",
    (3, 5):  "MODERATE RISK — Proceed with care",
    (5, 7):  "HIGH RISK — Caution advised",
    (7, 11): "CRITICAL RISK — Do not proceed",
}


@tool
def score_supplier(combined_intelligence: str) -> str:
    """
    Calculate an overall supplier trust score from 0 (best) to 10 (worst risk).
    Input: a combined string of all research findings about the supplier.
    Returns: a risk score, trust level, key signals found, and final recommendation.
    """
    text = combined_intelligence.lower()
    risk_score = 0.0
    negative_found = []
    positive_found = []

    for signal, weight in NEGATIVE_SIGNALS.items():
        if signal in text:
            risk_score += weight
            negative_found.append(f"{signal} (-{weight})")

    positive_boost = 0.0
    for signal, weight in POSITIVE_SIGNALS.items():
        if signal in text:
            positive_boost += weight
            positive_found.append(f"{signal} (+{weight})")

    net_score = max(0.0, min(10.0, round(risk_score - positive_boost, 1)))

    trust_label = "MODERATE RISK — Proceed with care"
    for (low, high), label in TRUST_LEVELS.items():
        if low <= net_score < high:
            trust_label = label
            break

    neg_str = ", ".join(negative_found[:5]) if negative_found else "None detected"
    pos_str = ", ".join(positive_found[:3]) if positive_found else "None detected"

    recommendations = {
        "LOW RISK":      "Safe to proceed with full contract.",
        "MODERATE RISK": "Request trial order before full commitment.",
        "HIGH RISK":     "Seek alternative suppliers or demand due diligence.",
        "CRITICAL RISK": "Do not proceed. Escalate to procurement leadership.",
    }
    rec_key = trust_label.split(" —")[0]
    recommendation = recommendations.get(rec_key, "Seek additional verification.")

    return (
        f"Supplier Intelligence Score\n"
        f"{'='*40}\n"
        f"Overall Risk Score : {net_score} / 10\n"
        f"Trust Level        : {trust_label}\n"
        f"\nRisk signals found : {neg_str}\n"
        f"Positive signals   : {pos_str}\n"
        f"\nRecommendation     : {recommendation}"
    )
