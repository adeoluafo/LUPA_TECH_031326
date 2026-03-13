from __future__ import annotations

import pandas as pd

from modules.verification import FACT_COLUMNS, build_audit_table
from utils.helpers import clipped_score


def visibility_score(rank_position: int | float, capital_one_present: bool) -> float:
    # Visibility measures whether Capital One is present and how prominently it ranks in assistant output.
    if not capital_one_present:
        return 0.0
    rank = max(int(rank_position), 1)
    return clipped_score(100.0 - ((rank - 1) * 15.0))


def accuracy_score(audit_status: str, issue_count: int, missing_fields: int, total_fields: int) -> float:
    # Accuracy rewards direct fact alignment and penalizes misinformation more than omissions.
    if audit_status == "Not Present":
        return 55.0
    if audit_status == "Accurate":
        return 100.0
    if audit_status == "Incomplete":
        return clipped_score(82.0 - (missing_fields * 7.0))
    base = (max(total_fields - issue_count - missing_fields, 0) / total_fields) * 100.0
    penalty = (issue_count * 24.0) + (missing_fields * 6.0)
    return clipped_score(base - penalty)


def trust_score(
    audit_status: str,
    accuracy: float,
    critical_misinformation_count: int,
    missing_fields: int,
    visibility: float,
) -> float:
    # Trust models consumer risk: misinformation gets the strongest penalty, absence a smaller one.
    if audit_status == "Not Present":
        return 68.0

    penalty = critical_misinformation_count * 18.0
    if audit_status == "Incomplete":
        penalty += 12.0 + (missing_fields * 4.0)
    elif audit_status == "Inaccurate":
        penalty += 20.0

    trust = accuracy - penalty + (visibility * 0.12)
    return clipped_score(trust)


def discovery_score(visibility: float, accuracy: float, trust: float) -> float:
    # AI Discovery Score combines presence, factual quality, and consumer-trust risk into one health metric.
    return clipped_score((visibility * 0.35) + (accuracy * 0.30) + (trust * 0.35))


def score_responses(responses: pd.DataFrame, verified_products: pd.DataFrame) -> pd.DataFrame:
    audit = build_audit_table(responses, verified_products)
    merged = responses.merge(audit, on=["prompt_id", "assistant_name"], how="left", suffixes=("", "_audit"))
    if "primary_product_audit" in merged.columns:
        merged["primary_product"] = merged["primary_product"].fillna("").replace("", pd.NA).fillna(merged["primary_product_audit"])
        merged = merged.drop(columns=["primary_product_audit"])
    total_fields = len(FACT_COLUMNS)
    merged["visibility_score"] = merged.apply(
        lambda row: visibility_score(row["rank_position"], row["capital_one_present"]), axis=1
    )
    merged["accuracy_score"] = merged.apply(
        lambda row: accuracy_score(row["audit_status"], row["issue_count"], row["missing_fields"], total_fields),
        axis=1,
    )
    merged["trust_score"] = merged.apply(
        lambda row: trust_score(
            row["audit_status"],
            row["accuracy_score"],
            row["critical_misinformation_count"],
            row["missing_fields"],
            row["visibility_score"],
        ),
        axis=1,
    )
    merged["discovery_score"] = merged.apply(
        lambda row: discovery_score(row["visibility_score"], row["accuracy_score"], row["trust_score"]),
        axis=1,
    )
    return merged


def aggregate_scorecards(scored_responses: pd.DataFrame) -> dict[str, float]:
    return {
        "AI Visibility Score": round(scored_responses["visibility_score"].mean(), 1),
        "Accuracy Score": round(scored_responses["accuracy_score"].mean(), 1),
        "Trust Score": round(scored_responses["trust_score"].mean(), 1),
        "AI Discovery Score": round(scored_responses["discovery_score"].mean(), 1),
    }
