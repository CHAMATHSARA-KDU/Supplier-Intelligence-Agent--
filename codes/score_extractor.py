"""
Score Extractor
Parses numeric risk score and risk level from agent output text.
"""

import re


def extract_score_from_output(agent_output: str) -> tuple:
    score = None
    risk_level = "UNKNOWN"

    # Multiple patterns to catch different formats
    score_patterns = [
        r"overall risk score[:\s]+(\d+\.?\d*)\s*/\s*10",
        r"risk score[:\s]+(\d+\.?\d*)\s*/\s*10",
        r"score[:\s]+(\d+\.?\d*)\s*/\s*10",
        r"(\d+\.?\d*)\s*/\s*10",
        r"risk score of\s+(\d+\.?\d*)\s+out of\s+10",
        r"score of\s+(\d+\.?\d*)\s+out of\s+10",
        r"(\d+\.?\d*)\s+out of\s+10",
        r"scored\s+(\d+\.?\d*)",
        r"score:\s*(\d+\.?\d*)",
    ]

    for pattern in score_patterns:
        match = re.search(pattern, agent_output.lower())
        if match:
            try:
                val = float(match.group(1))
                if 0 <= val <= 10:
                    score = val
                    break
            except ValueError:
                continue

    # Detect risk level
    text_lower = agent_output.lower()
    if "critical risk" in text_lower:
        risk_level = "CRITICAL RISK"
    elif "high risk" in text_lower:
        risk_level = "HIGH RISK"
    elif "moderate risk" in text_lower:
        risk_level = "MODERATE RISK"
    elif "low risk" in text_lower:
        risk_level = "LOW RISK"

    # If no score found but risk level found, assign default score
    if score is None and risk_level != "UNKNOWN":
        defaults = {
            "LOW RISK": 1.5,
            "MODERATE RISK": 4.0,
            "HIGH RISK": 6.5,
            "CRITICAL RISK": 8.5,
        }
        score = defaults.get(risk_level)

    return score, risk_level


def extract_supplier_name(user_input: str) -> str:
    prefixes = [
        "evaluate", "assess", "research", "due diligence on",
        "check", "investigate", "analyse", "analyze",
        "tell me about", "what about", "is", "are",
    ]
    text = user_input.strip()
    for prefix in prefixes:
        if text.lower().startswith(prefix):
            text = text[len(prefix):].strip(" -—:")
            break
    text = re.split(r"[—\-\n]", text)[0].strip()
    return text[:60] if text else user_input[:60]