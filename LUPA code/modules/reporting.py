from __future__ import annotations

import pandas as pd


def _resolve_product_column(frame: pd.DataFrame) -> str:
    for candidate in ["primary_product", "primary_product_y", "primary_product_x"]:
        if candidate in frame.columns:
            return candidate
    raise KeyError("No primary product column found in scored responses.")


def monthly_snapshot(scored_responses: pd.DataFrame, benchmark: pd.DataFrame) -> dict:
    critical_issues = int((scored_responses["issue_count"] > 0).sum())
    visible_prompts = int(scored_responses["capital_one_present"].sum())
    total = len(scored_responses)
    product_column = _resolve_product_column(scored_responses)
    major_issues = scored_responses[scored_responses["issue_count"] > 0][
        ["assistant_name", product_column, "audit_status", "trust_flags"]
    ].rename(columns={product_column: "primary_product"}).head(3)
    competitor_snapshot = benchmark.head(4).to_dict("records")
    return {
        "month": "March 2026",
        "visible_prompt_rate": round((visible_prompts / total) * 100, 1),
        "critical_issues": critical_issues,
        "top_assistant": scored_responses.groupby("assistant_name")["discovery_score"].mean().idxmax(),
        "best_prompt_family": scored_responses.groupby("category")["discovery_score"].mean().idxmax(),
        "current_visibility_score": round(scored_responses["visibility_score"].mean(), 1),
        "current_accuracy_score": round(scored_responses["accuracy_score"].mean(), 1),
        "current_trust_score": round(scored_responses["trust_score"].mean(), 1),
        "major_issues": major_issues.to_dict("records"),
        "competitor_benchmark_snapshot": competitor_snapshot,
    }


def build_reporting_payloads(
    scored_responses: pd.DataFrame, trends: pd.DataFrame, benchmark: pd.DataFrame, recommendations: list[dict]
) -> tuple[dict, dict]:
    quarterly = trends[trends["period_type"] == "quarterly"].copy()
    monthly = monthly_snapshot(scored_responses, benchmark)
    quarterly_summary = {
        "score_trends": quarterly[
            ["period", "visibility_score", "accuracy_score", "trust_score", "discovery_score", "issue_volume"]
        ].to_dict("records"),
        "performance_summary": (
            "Visibility and trust improved across the last four modeled quarters as Dell gateway actions "
            "standardized product metadata and reduced fee-related misinformation."
        ),
        "forecast_projection": (
            "Q2 2026 is projected to improve further if Dell continues distributing normalized comparison attributes "
            "for student and small-business card prompts."
        ),
        "strategic_recommendations": recommendations[:4],
    }
    return monthly, quarterly_summary


def quarterly_trends(trends: pd.DataFrame) -> pd.DataFrame:
    return trends[trends["period_type"] == "quarterly"].copy()


def forecast_text() -> str:
    return (
        "Modeled Q2 2026 improvement is driven by cleaner annual-fee metadata, stronger student-card comparison "
        "fields, and wider distribution of normalized rewards payloads through the Dell gateway layer."
    )
