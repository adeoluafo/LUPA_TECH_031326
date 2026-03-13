from __future__ import annotations

import pandas as pd


def generate_recommendations(scored_responses: pd.DataFrame, diagnostics: pd.DataFrame, benchmark: pd.DataFrame) -> list[dict]:
    recommendations = []

    if scored_responses["visibility_score"].mean() < 65:
        recommendations.append(
            {
                "priority": "High",
                "title": "Prioritize prompts with low Capital One visibility",
                "reason": "Capital One appears too inconsistently across monitored recommendation prompts.",
            }
        )

    inaccurate = scored_responses[scored_responses["issue_count"] > 0]
    if not inaccurate.empty:
        recommendations.append(
            {
                "priority": "High",
                "title": "Update annual fee and rewards metadata across authoritative sources",
                "reason": "Detected inaccurate fee, rewards, or signup bonus claims in monitored assistant responses.",
            }
        )

    if scored_responses["trust_score"].mean() < 70:
        recommendations.append(
            {
                "priority": "High",
                "title": "Reduce misinformation risk for trust-sensitive prompts",
                "reason": "Trust performance is being dragged down by hallucinated Capital One claims rather than simple absence alone.",
            }
        )

    capital_one_share = benchmark.loc[benchmark["brand"] == "Capital One", "share_of_recommendations"]
    chase_share = benchmark.loc[benchmark["brand"].str.contains("Chase", case=False), "share_of_recommendations"]
    amex_share = benchmark.loc[benchmark["brand"].str.contains("Amex", case=False), "share_of_recommendations"]
    if not capital_one_share.empty and (
        (not chase_share.empty and chase_share.max() > capital_one_share.max())
        or (not amex_share.empty and amex_share.max() > capital_one_share.max())
    ):
        recommendations.append(
            {
                "priority": "Medium",
                "title": "Prioritize prompts where Chase and Amex dominate visibility",
                "reason": "Competitor benchmarking shows stronger recommendation share for Chase or Amex across the monitored set.",
            }
        )

    weak_signal = diagnostics.sort_values("modeled_influence_score").head(1)
    if not weak_signal.empty:
        recommendations.append(
            {
                "priority": "Medium",
                "title": "Improve weak signal coverage",
                "reason": weak_signal.iloc[0]["analyst_action"],
            }
        )

    student_gap = scored_responses[
        (scored_responses["category"] == "Student") & (scored_responses["visibility_score"] < 70)
    ]
    if not student_gap.empty:
        recommendations.append(
            {
                "priority": "Medium",
                "title": "Strengthen comparison content for student credit card prompts",
                "reason": "Student prompts still show competitor dominance or inconsistent Capital One product facts.",
            }
        )

    recommendations.append(
        {
            "priority": "Low",
            "title": "Improve structured rewards tables",
            "reason": "Normalized, machine-readable rewards tables should help assistants interpret category-heavy card benefits more reliably.",
        }
    )
    return recommendations
