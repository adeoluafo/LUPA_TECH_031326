from __future__ import annotations

import pandas as pd

from utils.helpers import extract_competitors, safe_mean


def build_signal_diagnostics(scored: pd.DataFrame, signal_catalog: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, signal_row in signal_catalog.iterrows():
        signal = signal_row["signal_type"]
        subset = scored[scored["modeled_signal_mix"].str.contains(signal, case=False, na=False)]
        rows.append(
            {
                "signal_type": signal.title(),
                "modeled_influence_score": int(signal_row["influence_score"]),
                "coverage": int(len(subset)),
                "avg_accuracy": safe_mean(subset["accuracy_score"]),
                "avg_trust": safe_mean(subset["trust_score"]),
                "confidence": float(signal_row["confidence"]),
                "summary": signal_row["summary"],
                "analyst_action": signal_row["analyst_action"],
            }
        )
    return pd.DataFrame(rows).sort_values(["modeled_influence_score", "coverage"], ascending=[False, False])


def build_competitor_benchmark(scored: pd.DataFrame) -> pd.DataFrame:
    competitor_rows: list[dict] = []
    total_responses = len(scored)

    for _, row in scored.iterrows():
        ranked_brands = extract_competitors(row.get("competitors", ""))
        if row["capital_one_present"]:
            capital_one_brand = "Capital One"
            insert_at = max(int(row["rank_position"]) - 1, 0)
            ranked_brands = ranked_brands[:]
            if capital_one_brand not in ranked_brands:
                ranked_brands.insert(insert_at, capital_one_brand)

        for rank, brand in enumerate(ranked_brands, start=1):
            competitor_rows.append(
                {
                    "brand": brand,
                    "prompt_id": row["prompt_id"],
                    "assistant_name": row["assistant_name"],
                    "rank_position": rank,
                }
            )

    benchmark = pd.DataFrame(competitor_rows)
    if benchmark.empty:
        return pd.DataFrame(columns=["brand", "appearance_frequency", "average_rank_position", "share_of_recommendations"])

    summary = (
        benchmark.groupby("brand")
        .agg(
            appearances=("prompt_id", "count"),
            average_rank_position=("rank_position", "mean"),
        )
        .reset_index()
    )
    summary["appearance_frequency"] = (summary["appearances"] / total_responses * 100).round(1)
    summary["share_of_recommendations"] = (summary["appearances"] / summary["appearances"].sum() * 100).round(1)
    summary["average_rank_position"] = summary["average_rank_position"].round(1)
    return summary.sort_values(["appearance_frequency", "average_rank_position"], ascending=[False, True])[
        ["brand", "appearance_frequency", "average_rank_position", "share_of_recommendations"]
    ]
