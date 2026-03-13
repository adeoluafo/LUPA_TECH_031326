from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def _require_columns(frame: pd.DataFrame, required_columns: list[str], dataset_name: str) -> pd.DataFrame:
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{dataset_name} is missing required columns: {', '.join(missing)}")
    return frame


def load_clients() -> list[dict]:
    with (DATA_DIR / "clients.json").open("r", encoding="utf-8") as file:
        clients = json.load(file)
    required = {"client_id", "client_name", "industry", "last_updated", "ingestion_status", "gateway_layer_active"}
    for client in clients:
        missing = [field for field in required if field not in client]
        if missing:
            raise ValueError(f"clients.json record for {client.get('client_name', 'unknown')} is missing: {', '.join(missing)}")
    return clients


def load_prompts() -> pd.DataFrame:
    frame = pd.read_csv(DATA_DIR / "prompts.csv")
    return _require_columns(frame, ["prompt_id", "category", "prompt_text", "priority"], "prompts.csv")


def load_mock_ai_responses() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "mock_ai_responses.csv")
    _require_columns(
        df,
        [
            "prompt_id",
            "assistant_name",
            "rank_position",
            "capital_one_present",
            "primary_product",
            "competitors",
            "response_text",
            "mentioned_facts",
            "modeled_signal_mix",
        ],
        "mock_ai_responses.csv",
    )
    df["capital_one_present"] = df["capital_one_present"].astype(str).str.lower().map({"true": True, "false": False})
    return df


def load_verified_products() -> pd.DataFrame:
    frame = pd.read_csv(DATA_DIR / "verified_products.csv", dtype=str).fillna("")
    return _require_columns(
        frame,
        [
            "client_id",
            "product_name",
            "segment",
            "category",
            "audience",
            "annual_fee",
            "rewards_rate",
            "foreign_transaction_fee",
            "signup_bonus",
            "intro_apr",
            "last_verified",
            "verification_status",
        ],
        "verified_products.csv",
    )


def load_gateway_actions() -> pd.DataFrame:
    frame = pd.read_csv(DATA_DIR / "gateway_actions.csv")
    return _require_columns(
        frame,
        [
            "timestamp",
            "action_type",
            "action_title",
            "product_scope",
            "status",
            "distribution_status",
            "analyst_owner",
            "impact_summary",
        ],
        "gateway_actions.csv",
    )


def load_historical_trends() -> pd.DataFrame:
    frame = pd.read_csv(DATA_DIR / "historical_trends.csv")
    return _require_columns(
        frame,
        [
            "period_type",
            "period",
            "visibility_score",
            "accuracy_score",
            "trust_score",
            "discovery_score",
            "issue_volume",
            "capital_one_share",
            "chase_share",
            "amex_share",
            "discover_share",
            "boa_share",
        ],
        "historical_trends.csv",
    )


def load_security_status() -> dict:
    with (DATA_DIR / "security_status.json").open("r", encoding="utf-8") as file:
        payload = json.load(file)
    required = {
        "encryption_status",
        "access_control_status",
        "client_data_isolation_status",
        "audit_logging_status",
        "last_reviewed",
        "risk_posture",
    }
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValueError(f"security_status.json is missing required fields: {', '.join(missing)}")
    return payload


def load_signal_catalog() -> pd.DataFrame:
    frame = pd.read_csv(DATA_DIR / "signal_catalog.csv")
    return _require_columns(
        frame,
        ["signal_type", "influence_score", "confidence", "summary", "analyst_action"],
        "signal_catalog.csv",
    )
