"""Trend Analysis and Keyword Growth Calculations."""

from typing import Dict, List, Any


def calculate_growth_rate(current: int, previous: int) -> float:
    """Calculates percentage growth rate between current and previous frequency."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100.0, 2)


def rank_trending_keywords(
    current_keywords: List[Dict[str, Any]],
    previous_keywords: List[Dict[str, Any]],
    min_frequency: int = 5,
) -> List[Dict[str, Any]]:
    """Calculates trend scores and ranks keywords comparing today vs yesterday.

    Returns ranked list with growth percentage and absolute changes.
    """
    prev_map = {k["word"]: k.get("frequency", 0) for k in previous_keywords}
    ranked = []

    for curr in current_keywords:
        word = curr["word"]
        curr_freq = curr.get("frequency", 0)
        if curr_freq < min_frequency:
            continue

        prev_freq = prev_map.get(word, 0)
        delta = curr_freq - prev_freq
        growth = calculate_growth_rate(curr_freq, prev_freq)

        ranked.append({
            "word": word,
            "current_frequency": curr_freq,
            "previous_frequency": prev_freq,
            "change": delta,
            "growth_percent": growth,
            "article_count": curr.get("article_count", 0),
        })

    # Sort primarily by delta/growth
    ranked.sort(key=lambda x: (x["change"], x["growth_percent"]), reverse=True)
    return ranked
