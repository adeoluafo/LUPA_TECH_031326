from __future__ import annotations

import pandas as pd

from utils.helpers import normalize_text, parse_fact_string


FACT_COLUMNS = [
    "annual_fee",
    "rewards_rate",
    "foreign_transaction_fee",
    "signup_bonus",
    "intro_apr",
]

CRITICAL_FIELDS = {"annual_fee", "rewards_rate", "signup_bonus"}


def normalize_value(value: str) -> str:
    return normalize_text(str(value).replace(".0", ""))


def _resolve_primary_product(response_row: pd.Series) -> str:
    for candidate in ["primary_product", "primary_product_y", "primary_product_x"]:
        if candidate in response_row.index:
            return str(response_row.get(candidate, "") or "")
    return ""


def extract_claims(response_row: pd.Series) -> list[dict]:
    observed_facts = parse_fact_string(response_row.get("mentioned_facts", ""))
    return [{"field": field, "observed": observed_facts.get(field, "")} for field in FACT_COLUMNS]


def verify_response(response_row: pd.Series, verified_products: pd.DataFrame) -> dict:
    primary_product = _resolve_primary_product(response_row)
    capital_one_present = bool(response_row.get("capital_one_present", False))

    if not capital_one_present or not primary_product:
        return {
            "capital_one_present": False,
            "rank_position": int(response_row.get("rank_position", 0) or 0),
            "product_name": None,
            "status": "not present",
            "issue_count": 0,
            "missing_count": 0,
            "critical_misinformation_count": 0,
            "trust_flags": ["Client brand absent from assistant recommendation set."],
            "field_results": [],
            "claims": [],
        }

    matched = verified_products[
        verified_products["product_name"].str.lower() == primary_product.lower()
    ]

    if matched.empty:
        return {
            "capital_one_present": True,
            "rank_position": int(response_row.get("rank_position", 0) or 0),
            "product_name": primary_product,
            "status": "inaccurate",
            "issue_count": 1,
            "missing_count": 0,
            "critical_misinformation_count": 1,
            "trust_flags": ["Surfaced product does not match the verified Capital One product catalog."],
            "field_results": [
                {
                    "field": "product_match",
                    "status": "inaccurate",
                    "expected": "Known verified Capital One product",
                    "observed": primary_product,
                }
            ],
            "claims": extract_claims(response_row),
        }

    verified = matched.iloc[0].to_dict()
    observed_facts = parse_fact_string(response_row.get("mentioned_facts", ""))
    field_results = []
    trust_flags: list[str] = []

    for field in FACT_COLUMNS:
        expected = verified.get(field, "")
        observed = observed_facts.get(field, "")
        expected_normalized = normalize_value(expected)
        observed_normalized = normalize_value(observed)

        if not observed_normalized:
            status = "missing"
        elif observed_normalized == expected_normalized:
            status = "accurate"
        else:
            status = "inaccurate"
            if field in CRITICAL_FIELDS:
                trust_flags.append(f"Potentially misleading {field.replace('_', ' ')} claim detected.")

        field_results.append(
            {
                "field": field,
                "status": status,
                "expected": expected,
                "observed": observed or "Not mentioned",
            }
        )

    issue_count = sum(1 for item in field_results if item["status"] == "inaccurate")
    missing_count = sum(1 for item in field_results if item["status"] == "missing")
    critical_misinformation_count = sum(
        1 for item in field_results if item["status"] == "inaccurate" and item["field"] in CRITICAL_FIELDS
    )

    if issue_count > 0:
        overall_status = "inaccurate"
    elif missing_count > 0:
        overall_status = "incomplete"
    else:
        overall_status = "accurate"

    if overall_status == "incomplete":
        trust_flags.append("Assistant surfaced the product but omitted one or more verified fields.")

    return {
        "capital_one_present": True,
        "rank_position": int(response_row.get("rank_position", 0) or 0),
        "product_name": verified["product_name"],
        "status": overall_status,
        "issue_count": issue_count,
        "missing_count": missing_count,
        "critical_misinformation_count": critical_misinformation_count,
        "trust_flags": trust_flags,
        "field_results": field_results,
        "claims": extract_claims(response_row),
    }


def build_audit_table(responses: pd.DataFrame, verified_products: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in responses.iterrows():
        result = verify_response(row, verified_products)
        accurate_fields = sum(1 for item in result["field_results"] if item["status"] == "accurate")
        inaccurate_fields = sum(1 for item in result["field_results"] if item["status"] == "inaccurate")
        missing_fields = sum(1 for item in result["field_results"] if item["status"] == "missing")
        records.append(
            {
                "prompt_id": row["prompt_id"],
                "assistant_name": row["assistant_name"],
                "primary_product": result["product_name"] or "Not surfaced",
                "audit_status": result["status"].title(),
                "accurate_fields": accurate_fields,
                "inaccurate_fields": inaccurate_fields,
                "missing_fields": missing_fields,
                "issue_count": result["issue_count"],
                "critical_misinformation_count": result["critical_misinformation_count"],
                "trust_flags": " | ".join(result["trust_flags"]),
                "claims_extracted": len([claim for claim in result["claims"] if claim["observed"]]),
            }
        )
    return pd.DataFrame(records)
