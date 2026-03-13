from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from modules.data_gateway import build_ingestion_status
from modules.diagnostics import build_competitor_benchmark, build_signal_diagnostics
from modules.recommendations import generate_recommendations
from modules.reporting import build_reporting_payloads
from modules.scoring import aggregate_scorecards, score_responses
from modules.verification import verify_response
from utils.loaders import (
    load_clients,
    load_gateway_actions,
    load_historical_trends,
    load_mock_ai_responses,
    load_prompts,
    load_signal_catalog,
    load_verified_products,
)


st.set_page_config(page_title="Dell VeriPrompt", page_icon="D", layout="wide", initial_sidebar_state="collapsed")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1400px;
            padding-top: 24px;
            padding-left: 32px;
            padding-right: 32px;
            padding-bottom: 32px;
        }
        .stApp { background: #F4F7FB; }
        header[data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { visibility: hidden; height: 0; position: absolute; }
        [data-testid="stDecoration"] { display: none; }
        html, body, [class*="css"] {
            font-family: "IBM Plex Sans", "Source Sans 3", "Segoe UI", sans-serif;
            color: #0F172A;
        }
        .vp-card, .vp-control-card {
            background: #FFFFFF;
            border: 1px solid #D9E2EC;
            border-radius: 20px;
            box-shadow: 0 10px 24px rgba(7, 28, 60, 0.06);
        }
        .open-header {
            padding: 8px 2px 12px 2px;
            margin-bottom: 24px;
        }
        .open-header-row {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 6px;
        }
        .welcome-mark {
            font-family: "Libre Baskerville", Georgia, serif;
            font-size: 44px;
            font-weight: 600;
            color: #0F172A;
            line-height: 1.05;
            margin-bottom: 2px;
            letter-spacing: -0.02em;
        }
        .header-brand {
            font-family: "Libre Baskerville", Georgia, serif;
            font-size: 30px;
            font-weight: 700;
            color: #071C3C;
        }
        .vp-control-card { padding: 18px 18px 16px 18px; min-height: 148px; }
        .vp-card { padding: 18px 20px 20px 20px; }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF;
            border: 1px solid #D9E2EC;
            border-radius: 20px;
            box-shadow: 0 10px 24px rgba(7, 28, 60, 0.05);
            padding: 18px 20px 20px 20px;
        }
        .section-title {
            font-family: "Libre Baskerville", Georgia, serif;
            font-size: 21px;
            font-weight: 600;
            color: #0F172A;
            margin-bottom: 16px;
        }
        .card-label {
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #64748B;
            margin-bottom: 8px;
        }
        .profile-grid {
            display: grid;
            grid-template-columns: 132px 1fr;
            gap: 8px 16px;
            margin-bottom: 14px;
        }
        .profile-label {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #64748B;
        }
        .profile-value {
            font-size: 15px;
            color: #475569;
            line-height: 1.45;
        }
        .chip-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
        .chip {
            display: inline-flex;
            align-items: center;
            padding: 6px 10px;
            border-radius: 999px;
            background: #F8FBFF;
            border: 1px solid #D9E2EC;
            color: #0A2A66;
            font-size: 12px;
            font-weight: 500;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        .metric-cell {
            background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFE 100%);
            border: 1px solid #E8EEF5;
            border-radius: 16px;
            padding: 18px;
            position: relative;
            box-shadow: 0 6px 18px rgba(7, 28, 60, 0.04);
        }
        .metric-cell::before {
            content: "";
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            height: 5px;
            border-radius: 16px 16px 0 0;
            background: #D9E2EC;
        }
        .metric-primary::before { background: #0B63CE; }
        .metric-discovery::before { background: #071C3C; }
        .metric-accuracy::before { background: #138A36; }
        .metric-trust::before { background: #C47F00; }
        .metric-pill {
            display: inline-flex;
            align-items: center;
            padding: 4px 9px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            margin-bottom: 12px;
            background: #EEF4FB;
            color: #0A2A66;
        }
        .metric-value {
            font-family: "Libre Baskerville", Georgia, serif;
            font-size: 40px;
            font-weight: 700;
            color: #0A2A66;
            margin-bottom: 4px;
            line-height: 1;
        }
        .metric-sub {
            font-size: 15px;
            color: #475569;
        }
        .metric-secondary {
            font-size: 13px;
            color: #64748B;
            margin-top: 10px;
        }
        .response-item {
            border: 1px solid #E8EEF5;
            border-radius: 16px;
            padding: 16px;
            background: linear-gradient(180deg, #FFFFFF 0%, #FCFDFE 100%);
        }
        .response-item + .response-item { margin-top: 12px; }
        .response-name {
            font-size: 17px;
            font-weight: 600;
            color: #0F172A;
            margin-bottom: 4px;
        }
        .response-meta {
            font-size: 14px;
            color: #64748B;
            margin-bottom: 10px;
        }
        .response-summary {
            font-size: 15px;
            color: #475569;
            line-height: 1.5;
        }
        .response-empty {
            border-style: dashed;
            background: #FAFBFC;
        }
        .issue-row {
            border: 1px solid #E8EEF5;
            border-left: 4px solid #C47F00;
            border-radius: 14px;
            padding: 14px;
            background: #FFFCF5;
        }
        .issue-row.critical {
            border-left-color: #B42318;
            background: #FFF7F5;
        }
        .issue-row + .issue-row { margin-top: 12px; }
        .issue-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 8px;
        }
        .issue-assistant {
            font-size: 14px;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 2px;
        }
        .issue-title {
            font-size: 16px;
            color: #0F172A;
            line-height: 1.45;
        }
        .severity-badge {
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            white-space: nowrap;
            background: rgba(196, 127, 0, 0.12);
            color: #C47F00;
            border: 1px solid rgba(196, 127, 0, 0.18);
        }
        .severity-badge.critical {
            background: rgba(180, 35, 24, 0.10);
            color: #B42318;
            border-color: rgba(180, 35, 24, 0.18);
        }
        .issue-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .issue-box {
            background: #FFFFFF;
            border: 1px solid #E8EEF5;
            border-radius: 12px;
            padding: 10px 12px;
        }
        .signal-row { margin-bottom: 14px; }
        .signal-top {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 8px;
            font-size: 16px;
            color: #0F172A;
            font-weight: 600;
        }
        .signal-bar {
            height: 10px;
            border-radius: 999px;
            background: #E8EEF5;
            overflow: hidden;
        }
        .signal-fill {
            height: 100%;
            border-radius: 999px;
            background: #0A2A66;
        }
        .gateway-list {
            margin: 14px 0 16px 0;
            padding-left: 18px;
            color: #475569;
            font-size: 15px;
            line-height: 1.55;
        }
        .gateway-list li + li { margin-top: 6px; }
        .secondary-action {
            display: inline-flex;
            align-items: center;
            padding: 10px 14px;
            border-radius: 12px;
            border: 1px solid #D9E2EC;
            background: #EEF4FB;
            color: #0B63CE;
            font-size: 14px;
            font-weight: 600;
        }
        .report-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }
        .report-block-title {
            font-size: 18px;
            font-weight: 600;
            color: #0F172A;
            margin-bottom: 12px;
        }
        .report-list {
            display: grid;
            gap: 10px;
        }
        .report-item {
            border: 1px solid #E8EEF5;
            border-radius: 14px;
            background: #FFFFFF;
            padding: 14px;
        }
        .placeholder-card {
            background: #FFFFFF;
            border: 1px dashed #D9E2EC;
            border-radius: 20px;
            padding: 32px;
            text-align: center;
            color: #475569;
            font-size: 16px;
            margin-top: 24px;
        }
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            min-height: 46px !important;
            border: 1px solid #D9E2EC !important;
            background: #FFFFFF !important;
            box-shadow: none !important;
            border-radius: 12px !important;
        }
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] input,
        div[data-baseweb="input"] input,
        .stMultiSelect [data-baseweb="tag"] span {
            color: #0F172A !important;
            font-size: 14px !important;
        }
        .stMultiSelect [data-baseweb="tag"] {
            border-radius: 999px !important;
        }
        label[data-testid="stWidgetLabel"] p {
            font-size: 12px !important;
            font-weight: 600 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            color: #64748B !important;
        }
        .stButton > button {
            background: #0B63CE !important;
            color: #FFFFFF !important;
            border: 1px solid #0B63CE !important;
            border-radius: 12px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            padding: 0.62rem 1.1rem !important;
            box-shadow: none !important;
            width: auto !important;
        }
        .stButton > button:hover {
            background: #0A58B8 !important;
            border-color: #0A58B8 !important;
        }
        .signal-muted {
            font-size: 14px;
            color: #64748B;
            margin-top: 6px;
        }
        .stDataFrame {
            border: 1px solid #E8EEF5;
            border-radius: 16px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_all_data() -> tuple[list[dict], pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        load_clients(),
        load_prompts(),
        load_mock_ai_responses(),
        load_verified_products(),
        load_gateway_actions(),
        load_historical_trends(),
        load_signal_catalog(),
    )


def resolve_primary_product(row: pd.Series | dict) -> str:
    for candidate in ["primary_product", "primary_product_y", "primary_product_x"]:
        if isinstance(row, dict) and candidate in row:
            return str(row.get(candidate, "") or "")
        if hasattr(row, "index") and candidate in row.index:
            return str(row.get(candidate, "") or "")
    return ""


def normalize_scored_frame(scored: pd.DataFrame) -> pd.DataFrame:
    normalized = scored.copy()
    if "primary_product" not in normalized.columns:
        normalized["primary_product"] = ""
    for candidate in ["primary_product_y", "primary_product_x"]:
        if candidate in normalized.columns:
            normalized["primary_product"] = normalized["primary_product"].fillna("").replace("", pd.NA).fillna(normalized[candidate])
    normalized["primary_product"] = normalized["primary_product"].fillna("")
    return normalized


def short_response_summary(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    sentences = [segment.strip() for segment in text.split(". ") if segment.strip()]
    summary = ". ".join(sentences[:2]).strip()
    return summary if summary.endswith(".") else f"{summary}."


def relative_day_text(timestamp: str) -> str:
    try:
        delta = datetime(2026, 3, 13) - datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
    except ValueError:
        return timestamp
    if delta.days <= 0:
        return "Today"
    if delta.days == 1:
        return "1 day ago"
    return f"{delta.days} days ago"


def render_header() -> None:
    st.markdown(
        """
        <div class="open-header">
            <div class="open-header-row">
                <div class="welcome-mark">Welcome, Ade</div>
                <div class="header-brand">Dell VeriPrompt</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_float(value: object, fallback: float = 0.0) -> float:
    try:
        if value is None or (isinstance(value, str) and not value.strip()):
            return fallback
        return round(float(value), 1)
    except (TypeError, ValueError):
        return fallback


def safe_int(value: object, fallback: int = 0) -> int:
    try:
        if value is None or (isinstance(value, str) and not value.strip()):
            return fallback
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def render_monitoring_status(timestamp: str) -> None:
    st.markdown(
        f"""
        <div class="section-title" style="margin-bottom:12px;">Monitoring Status</div>
        <div class="profile-grid" style="grid-template-columns: 118px 1fr; margin-bottom:0;">
            <div class="profile-label">Status</div>
            <div class="profile-value">Monitoring Active</div>
            <div class="profile-label">Last Monitored</div>
            <div class="profile-value">{timestamp}</div>
            <div class="profile-label">Cycle</div>
            <div class="profile-value">Daily</div>
            <div class="profile-label">Gateway Sync</div>
            <div class="profile-value">Current</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_client_profile(client: dict, client_products: pd.DataFrame) -> None:
    products = "".join([f'<span class="chip">{product}</span>' for product in client_products["product_name"].tolist()])
    st.markdown(
        f"""
        <div class="vp-card">
            <div class="section-title">Client Profile</div>
            <div class="profile-grid">
                <div class="profile-label">Client</div>
                <div class="profile-value">{client['client_name']}</div>
                <div class="profile-label">Industry</div>
                <div class="profile-value">{client['industry']}</div>
                <div class="profile-label">Coverage</div>
                <div class="profile-value">{client['coverage']}</div>
                <div class="profile-label">Products Monitored</div>
                <div class="profile-value"><div class="chip-wrap">{products}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_response_monitor(prompt_slice: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">AI Response Monitor</div>', unsafe_allow_html=True)
    for _, row in prompt_slice.iterrows():
        product = resolve_primary_product(row)
        rank = safe_int(row.get("rank_position", 0), 0)
        is_surfaced = bool(product) and rank > 0
        rank_label = f"Rank {rank}" if rank > 0 else "No ranked result"
        product_label = product if product else "Capital One not surfaced"
        summary = short_response_summary(row.get("response_text", "")) if is_surfaced else "No monitored Capital One product was surfaced in this response set."
        classes = "response-item" if is_surfaced else "response-item response-empty"
        st.markdown(
            f"""
            <div class="{classes}">
                <div class="response-name">{row.get('assistant_name', 'Assistant')}</div>
                <div class="response-meta">{product_label} | {rank_label}</div>
                <div class="response-summary">{summary}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_issue_rows(prompt_slice: pd.DataFrame, verified_products: pd.DataFrame) -> list[dict]:
    issues: list[dict] = []
    for _, row in prompt_slice.iterrows():
        verification = verify_response(row, verified_products)
        assistant_name = row.get("assistant_name", "Assistant")
        product_name = verification.get("product_name") or resolve_primary_product(row) or "Capital One product"
        if verification["status"] == "inaccurate":
            for field in verification["field_results"]:
                if field["status"] != "inaccurate":
                    continue
                critical = field["field"] in {"annual_fee", "rewards_rate", "signup_bonus"}
                issues.append(
                    {
                        "assistant": assistant_name,
                        "title": f"{product_name} incorrect {field['field'].replace('_', ' ')} listed",
                        "observed": field["observed"],
                        "expected": field["expected"],
                        "severity": "Critical" if critical else "Medium",
                        "critical": critical,
                    }
                )
        elif verification["status"] == "incomplete":
            missing_fields = [field["field"].replace("_", " ") for field in verification["field_results"] if field["status"] == "missing"]
            if missing_fields:
                issues.append(
                    {
                        "assistant": assistant_name,
                        "title": f"{product_name} incomplete claim set",
                        "observed": ", ".join(missing_fields),
                        "expected": "Verified attributes required",
                        "severity": "Medium",
                        "critical": False,
                    }
                )
    return issues


def render_accuracy_card(prompt_slice: pd.DataFrame, verified_products: pd.DataFrame) -> None:
    issues = build_issue_rows(prompt_slice, verified_products)
    if not issues:
        content = """
        <div class="issue-row" style="border-left-color:#138A36;background:#F6FBF7;">
            <div class="issue-head">
                <div>
                    <div class="issue-assistant">Verification</div>
                    <div class="issue-title">No issues detected for the selected response set</div>
                </div>
                <div class="severity-badge" style="background:rgba(19,138,54,0.10);color:#138A36;border-color:rgba(19,138,54,0.18);">Clear</div>
            </div>
        </div>
        """
    else:
        rows: list[str] = []
        for issue in issues[:6]:
            rows.append(
                f"""
                <div class="issue-row {'critical' if issue['critical'] else ''}">
                    <div class="issue-head">
                        <div>
                            <div class="issue-assistant">{issue['assistant']}</div>
                            <div class="issue-title">{issue['title']}</div>
                        </div>
                        <div class="severity-badge {'critical' if issue['critical'] else ''}">{issue['severity']}</div>
                    </div>
                    <div class="issue-grid">
                        <div class="issue-box">
                            <div class="card-label">AI Response</div>
                            <div class="profile-value">{issue['observed']}</div>
                        </div>
                        <div class="issue-box">
                            <div class="card-label">Verified</div>
                            <div class="profile-value">{issue['expected']}</div>
                        </div>
                    </div>
                </div>
                """
            )
        content = "".join(rows)
    st.markdown(f'<div class="vp-card"><div class="section-title">Accuracy and Hallucination Detection</div>{content}</div>', unsafe_allow_html=True)


def render_score_tracking(scorecards: dict[str, float]) -> None:
    visibility = safe_float(scorecards.get("AI Visibility Score", 29.0), 29.0)
    accuracy = safe_float(scorecards.get("Accuracy Score", 31.0), 31.0)
    trust = safe_float(scorecards.get("Trust Score", 28.0), 28.0)
    discovery = safe_float(scorecards.get("AI Discovery Score", 30.0), 30.0)
    metrics = [
        ("AI Visibility Score", visibility, "Primary", "metric-primary", "Prompt presence and rank"),
        ("Accuracy Score", accuracy, "Verified", "metric-accuracy", "Claim alignment"),
        ("Trust Score", trust, "Risk", "metric-trust", "Misinformation exposure"),
        ("AI Discovery Score", discovery, "Priority", "metric-discovery", "Combined operating signal"),
    ]
    metric_html = "".join(
        [
            f"""
            <div class="metric-cell {metric_class}">
                <div class="card-label">{label}</div>
                <div class="metric-pill">{pill}</div>
                <div class="metric-value">{value:.1f}</div>
                <div class="metric-sub">{sub}</div>
                <div class="metric-secondary">{'Monitoring strong' if value >= 75 else 'Needs focus' if value < 65 else 'Stable trajectory'}</div>
            </div>
            """
            for label, value, pill, metric_class, sub in metrics
        ]
    )
    st.markdown(f'<div class="section-title">Score Tracking</div><div class="metric-grid">{metric_html}</div>', unsafe_allow_html=True)


def build_signal_breakdown(scored: pd.DataFrame) -> list[tuple[str, float]]:
    mapping = [
        ("comparison articles", "Financial comparison articles"),
        ("rewards summaries", "Rewards feature summaries"),
        ("product pages", "Product pages"),
        ("financial review sites", "User reviews"),
    ]
    counts = {label: 0 for _, label in mapping}
    for mix in scored.get("modeled_signal_mix", pd.Series(dtype=str)).fillna(""):
        lower_mix = mix.lower()
        for raw, label in mapping:
            if raw in lower_mix:
                counts[label] += 1
    total = sum(counts.values()) or 1
    rows = sorted([(label, round((count / total) * 100, 1)) for label, count in counts.items()], key=lambda item: item[1], reverse=True)
    if all(value == 0 for _, value in rows):
        return [
            ("Financial comparison articles", 42.0),
            ("Rewards feature summaries", 31.0),
            ("Product pages", 19.0),
            ("User reviews", 8.0),
        ]
    return rows


def render_signal_diagnostics(filtered: pd.DataFrame) -> None:
    rows = build_signal_breakdown(filtered)
    signal_html = "".join(
        [
            f"""
            <div class="signal-row">
                <div class="signal-top"><span>{label}</span><span>{value:.1f}%</span></div>
                <div class="signal-bar"><div class="signal-fill" style="width:{value}%;"></div></div>
            </div>
            """
            for label, value in rows
        ]
    )
    st.markdown(
        f'<div class="vp-card"><div class="section-title">Signal Diagnostics</div>{signal_html}<div class="signal-muted">Modeled influence mix for the selected monitoring context</div></div>',
        unsafe_allow_html=True,
    )


def render_gateway_status(ingestion: dict, gateway_actions: pd.DataFrame) -> None:
    rewards_update = gateway_actions[gateway_actions["action_title"].str.contains("rewards schema", case=False, na=False)]
    rewards_update_label = relative_day_text(rewards_update.iloc[0]["timestamp"]) if not rewards_update.empty else "Current"
    action_list = "".join([f"<li>{action}</li>" for action in gateway_actions["action_title"].head(3).tolist()])
    st.markdown(
        f"""
        <div class="vp-card">
            <div class="section-title">Gateway Data Status</div>
            <div class="profile-grid">
                <div class="profile-label">Data Ingestion</div><div class="profile-value">{'Active' if ingestion.get('validation_passed', False) else ingestion.get('ingestion_status', 'Current')}</div>
                <div class="profile-label">Schema Status</div><div class="profile-value">Current</div>
                <div class="profile-label">Distribution Status</div><div class="profile-value">Synced</div>
                <div class="profile-label">Last Structured Rewards Schema Update</div><div class="profile-value">{rewards_update_label}</div>
            </div>
            <ul class="gateway-list">{action_list}</ul>
            <div class="secondary-action">View All Gateway Actions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_competitor_analysis(benchmark: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Competitor Analysis</div>', unsafe_allow_html=True)
    st.dataframe(
        benchmark[["brand", "appearance_frequency", "average_rank_position", "share_of_recommendations"]].rename(
            columns={
                "brand": "Brand",
                "appearance_frequency": "Appearance Frequency",
                "average_rank_position": "Avg. Rank",
                "share_of_recommendations": "Share of AI Recommendations",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_reporting_summary(monthly_report: dict, quarterly_report: dict) -> None:
    visibility_summary = safe_float(monthly_report.get("visible_prompt_rate", 29.0), 29.0)
    trust_summary = safe_float(monthly_report.get("current_trust_score", 28.0), 28.0)
    active_issues = safe_int(monthly_report.get("critical_issues", 0), 0)
    benchmark_snapshot = monthly_report.get("competitor_benchmark_snapshot", [])
    benchmark_line = f"{benchmark_snapshot[0]['brand']} leads current share" if benchmark_snapshot else "Capital One remains in monitored comparison"
    focus_area = quarterly_report["strategic_recommendations"][0]["title"] if quarterly_report.get("strategic_recommendations") else "Maintain current monitoring focus"
    trend_direction = quarterly_report.get("performance_summary", "Quarterly trend remains stable across monitored prompts.")
    projected_opportunity = quarterly_report.get("forecast_projection", "Opportunity remains strongest in structured product comparisons.")
    st.markdown(
        f"""
        <div class="vp-card" style="margin-top:24px;">
            <div class="section-title">Reporting Summary</div>
            <div class="report-grid">
                <div>
                    <div class="report-block-title">Monthly Snapshot</div>
                    <div class="report-list">
                        <div class="report-item"><div class="card-label">Visibility Summary</div><div class="metric-value" style="font-size:34px;">{visibility_summary:.1f}%</div><div class="profile-value">Visible prompt rate</div></div>
                        <div class="report-item"><div class="card-label">Trust Summary</div><div class="metric-value" style="font-size:34px;color:#C47F00;">{trust_summary:.1f}</div><div class="profile-value">Current trust score</div></div>
                        <div class="report-item"><div class="card-label">Active Issues</div><div class="metric-value" style="font-size:34px;color:#B42318;">{active_issues}</div><div class="profile-value">Flagged response records this month</div></div>
                        <div class="report-item"><div class="card-label">Benchmark Snapshot</div><div class="profile-value">{benchmark_line}</div></div>
                    </div>
                </div>
                <div>
                    <div class="report-block-title">Quarterly Outlook</div>
                    <div class="report-list">
                        <div class="report-item"><div class="card-label">Trend Direction</div><div class="profile-value">{trend_direction}</div></div>
                        <div class="report-item"><div class="card-label">Projected Opportunity</div><div class="profile-value">{projected_opportunity}</div></div>
                        <div class="report-item"><div class="card-label">Recommended Focus Area</div><div class="profile-value">{focus_area}</div></div>
                        <div class="report-item"><div class="card-label">Forecast Note</div><div class="profile-value">Continue prioritizing prompts where verified metadata can improve ranking and trust outcomes.</div></div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()
    clients, prompts, responses, verified_products, gateway_actions, historical_trends, signal_catalog = load_all_data()
    all_scored = normalize_scored_frame(score_responses(responses, verified_products).merge(prompts, on="prompt_id", how="left"))

    render_header()

    client_names = [client["client_name"] for client in clients]
    industries = sorted({client["industry"] for client in clients})
    assistant_options = sorted(responses["assistant_name"].dropna().unique().tolist())
    category_options = sorted(prompts["category"].dropna().unique().tolist())

    control_cols = st.columns(4, gap="large")
    with control_cols[0]:
        with st.container(border=True):
            selected_client_name = st.selectbox("Client Selector", client_names, index=0)

    selected_client = next(client for client in clients if client["client_name"] == selected_client_name)
    client_products = verified_products[verified_products["client_id"] == selected_client["client_id"]].copy()
    ingestion = build_ingestion_status(selected_client, client_products)
    latest_monitor_timestamp = gateway_actions.iloc[0]["timestamp"] if not gateway_actions.empty else selected_client["last_updated"]

    with control_cols[1]:
        with st.container(border=True):
            selected_industry = st.selectbox("Industry Filter", industries, index=industries.index(selected_client["industry"]))

    with control_cols[2]:
        with st.container(border=True):
            selected_platforms = st.multiselect("AI Platforms", assistant_options, default=assistant_options)

    with control_cols[3]:
        with st.container(border=True):
            render_monitoring_status(latest_monitor_timestamp)

    prompt_col, profile_col = st.columns([0.58, 0.42], gap="large")
    with prompt_col:
        with st.container(border=True):
            st.markdown('<div class="section-title">Prompt Control</div>', unsafe_allow_html=True)
            selected_category = st.selectbox("Prompt Category", category_options, index=0)
            prompt_options = prompts[prompts["category"] == selected_category]["prompt_text"].tolist()
            selected_prompt = st.selectbox("Prompt", prompt_options, index=0 if prompt_options else None)
            run_analysis = st.button("Run Monitoring Analysis")

    with profile_col:
        render_client_profile(selected_client, client_products)

    current_selection = {
        "client": selected_client_name,
        "industry": selected_industry,
        "platforms": tuple(selected_platforms),
        "category": selected_category,
        "prompt": selected_prompt,
    }
    if run_analysis:
        st.session_state["analysis_selection"] = current_selection
    analysis_ready = st.session_state.get("analysis_selection") == current_selection and bool(selected_platforms) and bool(selected_prompt)

    if not analysis_ready:
        st.markdown('<div class="placeholder-card">Select inputs and run monitoring analysis to load results.</div>', unsafe_allow_html=True)
        return

    selected_prompt_id = prompts.loc[prompts["prompt_text"] == selected_prompt, "prompt_id"].iloc[0]
    client_scored = all_scored[all_scored["assistant_name"].isin(selected_platforms)].copy()
    filtered = client_scored[client_scored["category"] == selected_category].copy()
    prompt_slice = filtered[filtered["prompt_id"] == selected_prompt_id].copy()
    if prompt_slice.empty:
        prompt_slice = client_scored[client_scored["prompt_id"] == selected_prompt_id].copy()

    benchmark = build_competitor_benchmark(prompt_slice if not prompt_slice.empty else filtered)
    diagnostics = build_signal_diagnostics(filtered if not filtered.empty else prompt_slice, signal_catalog)
    recommendations = generate_recommendations(filtered if not filtered.empty else prompt_slice, diagnostics, benchmark)
    monthly_report, quarterly_report = build_reporting_payloads(filtered if not filtered.empty else prompt_slice, historical_trends, benchmark, recommendations)
    scorecards = aggregate_scorecards(prompt_slice if not prompt_slice.empty else filtered)

    response_col, audit_col = st.columns([0.58, 0.42], gap="large")
    with response_col:
        with st.container(border=True):
            render_response_monitor(prompt_slice)
    with audit_col:
        render_accuracy_card(prompt_slice, client_products)

    score_col, signal_col = st.columns([0.58, 0.42], gap="large")
    with score_col:
        with st.container(border=True):
            render_score_tracking(scorecards)
    with signal_col:
        with st.container(border=True):
            render_signal_diagnostics(filtered if not filtered.empty else prompt_slice)

    with st.container(border=True):
        render_competitor_analysis(benchmark)

    with st.container():
        render_gateway_status(ingestion, gateway_actions)
    render_reporting_summary(monthly_report, quarterly_report)


if __name__ == "__main__":
    main()
