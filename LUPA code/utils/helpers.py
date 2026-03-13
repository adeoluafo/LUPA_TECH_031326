from __future__ import annotations

import re
from typing import Iterable


ASSISTANT_COLORS = {
    "ChatGPT": "#2B8A6E",
    "Gemini": "#1F6FEB",
    "Perplexity": "#F08C00",
}


def parse_fact_string(fact_string: str) -> dict[str, str]:
    if not isinstance(fact_string, str) or not fact_string.strip():
        return {}
    parts = [part for part in fact_string.split("|") if "=" in part]
    return {key.strip(): value.strip() for key, value in (part.split("=", 1) for part in parts)}


def extract_competitors(raw_competitors: str) -> list[str]:
    if not isinstance(raw_competitors, str) or not raw_competitors.strip():
        return []
    return [item.strip() for item in raw_competitors.split(";") if item.strip()]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def safe_mean(values: Iterable[float]) -> float:
    items = list(values)
    return round(sum(items) / len(items), 1) if items else 0.0


def format_pct(value: float) -> str:
    return f"{value:.1f}%"


def clipped_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 1)
