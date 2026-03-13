from __future__ import annotations

import pandas as pd


def build_ingestion_status(client: dict, verified_products: pd.DataFrame) -> dict:
    validation_passed = bool(len(verified_products)) and verified_products["verification_status"].eq("verified").all()
    return {
        "client_name": client["client_name"],
        "ingestion_status": client["ingestion_status"],
        "gateway_layer_active": "Active" if client["gateway_layer_active"] else "Inactive",
        "last_updated": client["last_updated"],
        "validated_records": int(len(verified_products)),
        "validation_passed": validation_passed,
    }


def build_gateway_status(verified_products: pd.DataFrame, gateway_actions: pd.DataFrame) -> dict:
    published_records = len(verified_products) * len(
        ["annual_fee", "rewards_rate", "foreign_transaction_fee", "signup_bonus", "intro_apr", "audience", "category"]
    )
    transformed_records = len(verified_products) * 8
    distribution_targets = [
        {"target": "AI-friendly schema registry", "status": "Published", "latency": "4 min"},
        {"target": "Internal prompt monitoring cache", "status": "Published", "latency": "2 min"},
        {"target": "Structured comparison payloads", "status": "Published", "latency": "6 min"},
        {"target": "Analyst reporting snapshot", "status": "Published", "latency": "1 min"},
    ]
    return {
        "ingested_products": len(verified_products),
        "verified_fields": published_records,
        "transformed_records": transformed_records,
        "gateway_status": "Healthy",
        "distribution_targets": distribution_targets,
        "recent_actions": gateway_actions.head(4).to_dict("records"),
    }


def build_gateway_payload_preview(verified_products: pd.DataFrame) -> pd.DataFrame:
    preview = verified_products.copy()
    preview["gateway_payload"] = preview.apply(
        lambda row: (
            f"product={row['product_name']}; audience={row['audience']}; category={row['category']}; "
            f"annual_fee={row['annual_fee']}; rewards={row['rewards_rate']}; foreign_txn_fee={row['foreign_transaction_fee']}; "
            f"bonus={row['signup_bonus']}; intro_apr={row['intro_apr']}"
        ),
        axis=1,
    )
    return preview[["product_name", "segment", "category", "gateway_payload"]]
