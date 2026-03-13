from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules.data_gateway import build_gateway_payload_preview, build_gateway_status, build_ingestion_status
from modules.diagnostics import build_competitor_benchmark, build_signal_diagnostics
from modules.recommendations import generate_recommendations
from modules.reporting import build_reporting_payloads, quarterly_trends
from modules.scoring import aggregate_scorecards, score_responses
from modules.security_status import build_security_status_frame
from modules.verification import verify_response
from utils.helpers import ASSISTANT_COLORS, safe_mean
from utils.loaders import (
    load_clients,
    load_gateway_actions,
    load_historical_trends,
    load_mock_ai_responses,
    load_prompts,
    load_security_status,
    load_signal_catalog,
    load_verified_products,
)


st.set_page_config(
    page_title="Dell VeriPrompt",
    page_icon="D",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #f4f7fa;
            --panel: #ffffff;
            --panel-alt: #f8fbfd;
            --ink: #18293f;
            --muted: #5f7188;
            --line: #d6e0ea;
            --accent: #006bbd;
            --accent-soft: #eaf3fb;
            --good: #0f8a5f;
            --warn: #b7791f;
            --bad: #b73a32;
        }
        html, body, [class*="css"] {
            font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            color: var(--ink);
        }
        .stApp {
            background: linear-gradient(180deg, #f3f6f9 0%, #eef3f8 100%);
        }
        [data-testid="stSidebar"] {
            background: #0f2138;
        }
        [data-testid="stSidebar"] * {
            color: #eef4fb;
        }
        .workspace-header {
            background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 18px 22px;
            box-shadow: 0 8px 24px rgba(16, 35, 61, 0.05);
            margin-bottom: 18px;
        }
        .workspace-header h1 {
            margin: 0;
            font-size: 1.85rem;
            font-weight: 750;
            color: var(--ink);
        }
        .workspace-header .subline {
            margin-top: 8px;
            color: var(--muted);
            font-size: 0.94rem;
        }
        .panel {
            background: rgba(255,255,255,0.98);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 16px 16px 12px 16px;
            box-shadow: 0 8px 24px rgba(16, 35, 61, 0.05);
            margin-bottom: 14px;
        }
        .section-title {
            font-size: 0.96rem;
            font-weight: 750;
            margin-bottom: 12px;
            color: var(--ink);
            letter-spacing: 0.01em;
        }
        .metric-card {
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 14px 16px;
            min-height: 112px;
        }
        .metric-label {
            color: var(--muted);
            font-size: 0.82rem;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--ink);
            line-height: 1.1;
        }
        .metric-sub {
            color: var(--muted);
            font-size: 0.82rem;
            margin-top: 4px;
        }
        .status-block {
            background: var(--panel-alt);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 10px 12px;
            margin-bottom: 10px;
        }
        .status-label {
            color: var(--muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .status-value {
            color: var(--ink);
            font-size: 1rem;
            font-weight: 700;
            margin-top: 2px;
        }
        .chip {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            margin-right: 6px;
            margin-bottom: 6px;
            background: var(--accent-soft);
            color: var(--accent);
        }
        .response-card {
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 14px 16px;
            margin-bottom: 12px;
            background: #ffffff;
        }
        .response-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }
        .response-title {
            font-weight: 750;
            color: var(--ink);
        }
        .response-meta {
            color: var(--muted);
            font-size: 0.82rem;
        }
        .flag {
            border-left: 4px solid var(--bad);
            background: #fff7f6;
            border-radius: 10px;
            padding: 10px 12px;
            margin-bottom: 10px;
        }
        .flag-title {
            font-weight: 700;
            color: var(--bad);
            margin-bottom: 4px;
        }
        .flag-body {
            color: var(--ink);
            font-size: 0.88rem;
        }
        .notice {
            background: #f7fafc;
            border: 1px dashed var(--line);
            border-radius: 16px;
            padding: 22px;
            color: var(--muted);
            text-align: center;
            margin-top: 8px;
        }
        .status-good { color: var(--good); font-weight: 700; }
        .status-warn { color: var(--warn); font-weight: 700; }
        .status-bad { color: var(--bad); font-weight: 700; }
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] span,
        div[data-baseweb="input"] input,
        .stMultiSelect [data-baseweb="tag"] span,
        .stSelectbox label,
        .stMultiSelect label,
        .stTextInput label {
            color: #18293f !important;
        }
        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            border-color: #c7d4e1 !important;
        }
        .stButton > button {
            background: #006bbd;
            color: #ffffff;
            border: 1px solid #0060aa;
            border-radius: 12px;
            font-weight: 700;
            padding: 0.55rem 1.1rem;
        }
        .stButton > button:hover {
            background: #005ca3;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_all_data() -> tuple[list[dict], pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    return (
        load_clients(),
        load_prompts(),
        load_mock_ai_responses(),
        load_verified_products(),
        load_gateway_actions(),
        load_historical_trends(),
        load_signal_catalog(),
        load_security_status(),
    )


def metric_card(label: str, value: str, sub: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_block(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="status-block">
            <div class="status-label">{label}</div>
            <div class="status-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def resolve_primary_product(row: pd.Series | dict) -> str:
    for candidate in ["primary_product", "primary_product_y", "primary_product_x"]:
        if isinstance(row, dict) and candidate in row:
            return str(row.get(candidate, "") or "")
        if hasattr(row, "index") and candidate in row.index:
            return str(row.get(candidate, "") or "")
    return ""


def summarize_response(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    first_sentence = text.split(". ")[0].strip()
    if not first_sentence.endswith("."):
        first_sentence += "."
    return first_sentence


def relative_day_text(timestamp: str) -> str:
    try:
        delta = datetime(2026, 3, 13) - datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Current"
    days = max(delta.days, 0)
    if days == 0:
        return "Today"
    if days == 1:
        return "1 day ago"
    return f"{days} days ago"


def build_signal_breakdown(scored: pd.DataFrame) -> pd.DataFrame:
    label_map = {
        "comparison articles": "Financial comparison articles",
        "rewards summaries": "Rewards feature summaries",
        "product pages": "Product pages",
        "financial review sites": "Financial review sites",
        "structured product tables": "Structured product tables",
    }
    counts = {label: 0 for label in label_map.values()}
    for signal_mix in scored.get("modeled_signal_mix", pd.Series(dtype=str)).fillna(""):
        for raw, label in label_map.items():
            if raw in signal_mix.lower():
                counts[label] += 1
    frame = pd.DataFrame(
        [{"signal": label, "count": count} for label, count in counts.items() if count > 0]
    )
    if frame.empty:
        return pd.DataFrame(columns=["signal", "percentage"])
    frame["percentage"] = (frame["count"] / frame["count"].sum() * 100).round(1)
    return frame.sort_values("percentage", ascending=False)


def signal_breakdown_chart(signal_breakdown: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        signal_breakdown,
        x="percentage",
        y="signal",
        orientation="h",
        text="percentage",
        color_discrete_sequence=["#006bbd"],
    )
    fig.update_traces(texttemplate="%{text:.1f}%", hovertemplate="%{y}: %{x:.1f}%<extra></extra>")
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    fig.update_xaxes(title="", range=[0, 100])
    fig.update_yaxes(title="", categoryorder="total ascending")
    return fig


def assistant_summary_chart(scored: pd.DataFrame) -> go.Figure:
    summary = (
        scored.groupby("assistant_name")[["visibility_score", "accuracy_score", "trust_score"]]
        .mean()
        .reset_index()
        .melt(id_vars="assistant_name", var_name="metric", value_name="score")
    )
    fig = px.bar(
        summary,
        x="assistant_name",
        y="score",
        color="assistant_name",
        facet_col="metric",
        color_discrete_map=ASSISTANT_COLORS,
        text_auto=".0f",
    )
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
    fig.update_xaxes(title="")
    fig.update_yaxes(title="", range=[0, 100])
    return fig


def trend_chart(trends: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for metric, color in [
        ("visibility_score", "#006bbd"),
        ("accuracy_score", "#0f8a5f"),
        ("trust_score", "#b7791f"),
        ("discovery_score", "#425c8a"),
    ]:
        fig.add_trace(
            go.Scatter(
                x=trends["period"],
                y=trends[metric],
                mode="lines+markers",
                name=metric.replace("_", " ").title(),
                line=dict(width=3, color=color),
            )
        )
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), yaxis_range=[0, 100])
    return fig


def build_monitoring_snapshot(client: dict, ingestion: dict, gateway_actions: pd.DataFrame) -> dict:
    latest_action = gateway_actions.iloc[0]["timestamp"] if not gateway_actions.empty else client["last_updated"]
    return {
        "status": "Monitoring Active" if ingestion["gateway_layer_active"] == "Active" else "Monitoring Paused",
        "last_monitored": latest_action,
        "daily_cycle": "Daily cycle active",
        "gateway_sync": "Gateway sync current" if ingestion["validation_passed"] else "Gateway sync review",
    }


def build_issue_flags(scored: pd.DataFrame, verified_products: pd.DataFrame) -> list[dict]:
    flags: list[dict] = []
    for _, row in scored.iterrows():
        verification = verify_response(row, verified_products)
        assistant = row.get("assistant_name", "Assistant")
        product_name = verification.get("product_name") or resolve_primary_product(row) or "Capital One product"
        if verification["status"] == "inaccurate":
            for field in verification["field_results"]:
                if field["status"] != "inaccurate":
                    continue
                flags.append(
                    {
                        "title": f"{assistant} — {product_name} incorrect {field['field'].replace('_', ' ')}",
                        "body": f"AI response shows {field['observed']}; verified data shows {field['expected']}.",
                    }
                )
        elif verification["status"] == "incomplete":
            missing_fields = [
                field["field"].replace("_", " ")
                for field in verification["field_results"]
                if field["status"] == "missing"
            ]
            if missing_fields:
                flags.append(
                    {
                        "title": f"{assistant} — {product_name} incomplete claim set",
                        "body": f"Missing verified fields: {', '.join(missing_fields)}.",
                    }
                )
        elif verification["status"] == "not present":
            flags.append(
                {
                    "title": f"{assistant} — Capital One not surfaced",
                    "body": "Selected response context did not include a monitored Capital One product.",
                }
            )
    return flags[:8]


def normalize_scored_frame(scored: pd.DataFrame) -> pd.DataFrame:
    normalized = scored.copy()
    if "primary_product" not in normalized.columns:
        normalized["primary_product"] = ""
    for candidate in ["primary_product_y", "primary_product_x"]:
        if candidate in normalized.columns:
            normalized["primary_product"] = normalized["primary_product"].fillna("").replace("", pd.NA).fillna(normalized[candidate])
    normalized["primary_product"] = normalized["primary_product"].fillna("")
    return normalized


def render_response_monitor(prompt_slice: pd.DataFrame) -> None:
    for _, row in prompt_slice.iterrows():
        rank_text = "Not ranked" if int(row.get("rank_position", 0) or 0) == 0 else str(int(row.get("rank_position", 0)))
        product = resolve_primary_product(row) or "Not surfaced"
        st.markdown(
            f"""
            <div class="response-card">
                <div class="response-head">
                    <div class="response-title">{row.get("assistant_name", "Assistant")}</div>
                    <div class="response-meta">Rank {rank_text} | {product}</div>
                </div>
                <div class="response-meta">{summarize_response(row.get("response_text", ""))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_accuracy_audit(prompt_slice: pd.DataFrame, verified_products: pd.DataFrame) -> None:
    if prompt_slice.empty:
        st.info("No response records are available for the selected prompt.")
        return

    issue_flags = build_issue_flags(prompt_slice, verified_products)
    if issue_flags:
        for flag in issue_flags:
            st.markdown(
                f"""
                <div class="flag">
                    <div class="flag-title">{flag['title']}</div>
                    <div class="flag-body">{flag['body']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="status-good">No audit issues detected for the selected response set.</div>', unsafe_allow_html=True)

    selected_row = prompt_slice.iloc[0]
    verification = verify_response(selected_row, verified_products)
    if verification["field_results"]:
        st.dataframe(pd.DataFrame(verification["field_results"]), use_container_width=True, hide_index=True)


def render_gateway_actions(gateway_actions: pd.DataFrame) -> None:
    st.dataframe(
        gateway_actions[["timestamp", "action_title", "product_scope", "distribution_status"]],
        use_container_width=True,
        hide_index=True,
    )


def main() -> None:
    inject_styles()
    clients, prompts, responses, verified_products, gateway_actions, historical_trends, signal_catalog, security_status = load_all_data()

    all_scored = normalize_scored_frame(score_responses(responses, verified_products).merge(prompts, on="prompt_id", how="left"))

    client_names = [client["client_name"] for client in clients]
    industries = sorted({client["industry"] for client in clients})
    assistant_options = sorted(responses["assistant_name"].dropna().unique().tolist())
    category_options = sorted(prompts["category"].dropna().unique().tolist())

    st.markdown(
        """
        <div class="workspace-header">
            <h1>Dell VeriPrompt</h1>
            <div class="subline">Analyst workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    control_top = st.columns([1.1, 1.0, 1.15, 1.25])
    selected_client_name = control_top[0].selectbox("Client Selector", client_names, index=0)
    selected_client = next(client for client in clients if client["client_name"] == selected_client_name)
    selected_industry = control_top[1].selectbox(
        "Industry Filter",
        industries,
        index=industries.index(selected_client["industry"]) if selected_client["industry"] in industries else 0,
    )
    selected_platforms = control_top[3].multiselect("AI Platforms", assistant_options, default=assistant_options)

    client_products = verified_products[verified_products["client_id"] == selected_client["client_id"]].copy()
    client_scored = all_scored[all_scored["assistant_name"].isin(selected_platforms)].copy() if selected_platforms else all_scored.iloc[0:0].copy()

    ingestion = build_ingestion_status(selected_client, client_products)
    monitoring = build_monitoring_snapshot(selected_client, ingestion, gateway_actions)

    with control_top[2]:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Monitoring Status</div>', unsafe_allow_html=True)
        status_block("Status", monitoring["status"])
        status_block("Last Monitored", monitoring["last_monitored"])
        status_block("Cycle", monitoring["daily_cycle"])
        status_block("Gateway Sync", monitoring["gateway_sync"])
        st.markdown("</div>", unsafe_allow_html=True)

    prompt_col, client_profile_col = st.columns([1.25, 0.95])
    with prompt_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Prompt Control</div>', unsafe_allow_html=True)
        selected_category = st.selectbox("Prompt Category", category_options, index=0)
        prompt_options = prompts[prompts["category"] == selected_category]["prompt_text"].tolist()
        selected_prompt = st.selectbox("Prompt", prompt_options, index=0 if prompt_options else None)
        run_analysis = st.button("Run Monitoring Analysis", type="primary", use_container_width=False)
        st.markdown("</div>", unsafe_allow_html=True)

    with client_profile_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Client Profile</div>', unsafe_allow_html=True)
        st.markdown(f"**{selected_client['client_name']}**")
        st.caption(selected_client["account_owner"])
        st.markdown(f"Coverage: {selected_client['coverage']}")
        for product in client_products["product_name"].tolist():
            st.markdown(f'<span class="chip">{product}</span>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

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
        st.markdown(
            """
            <div class="notice">
                Select the monitoring inputs and run the analysis to load score tracking, diagnostics, gateway status, competitor analysis, responses, and audit results.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    selected_prompt_id = prompts.loc[prompts["prompt_text"] == selected_prompt, "prompt_id"].iloc[0]
    filtered = client_scored[client_scored["category"] == selected_category].copy()
    prompt_slice = filtered[filtered["prompt_id"] == selected_prompt_id].copy()
    if prompt_slice.empty:
        prompt_slice = client_scored[client_scored["prompt_id"] == selected_prompt_id].copy()

    benchmark = build_competitor_benchmark(filtered if not filtered.empty else prompt_slice)
    diagnostics = build_signal_diagnostics(filtered if not filtered.empty else prompt_slice, signal_catalog)
    recommendations = generate_recommendations(filtered if not filtered.empty else prompt_slice, diagnostics, benchmark)
    monthly_report, quarterly_report = build_reporting_payloads(filtered if not filtered.empty else prompt_slice, historical_trends, benchmark, recommendations)
    scorecards = aggregate_scorecards(prompt_slice if not prompt_slice.empty else filtered)
    gateway = build_gateway_status(client_products, gateway_actions)
    gateway_preview = build_gateway_payload_preview(client_products)
    quarterly = quarterly_trends(historical_trends)
    security_frame = build_security_status_frame(security_status)
    signal_breakdown = build_signal_breakdown(filtered if not filtered.empty else prompt_slice)

    st.markdown('<div class="section-title">Score Tracking</div>', unsafe_allow_html=True)
    score_cols = st.columns(4)
    with score_cols[0]:
        metric_card("AI Visibility Score", f"{scorecards['AI Visibility Score']:.1f}", "Selected prompt context")
    with score_cols[1]:
        metric_card("Accuracy Score", f"{scorecards['Accuracy Score']:.1f}", "Verified claim alignment")
    with score_cols[2]:
        metric_card("Trust Score", f"{scorecards['Trust Score']:.1f}", "Misinformation risk control")
    with score_cols[3]:
        metric_card("AI Discovery Score", f"{scorecards['AI Discovery Score']:.1f}", "Combined operating metric")

    top_left, top_right = st.columns([1.05, 0.95])
    with top_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Signal Diagnostics</div>', unsafe_allow_html=True)
        if not signal_breakdown.empty:
            st.plotly_chart(signal_breakdown_chart(signal_breakdown), use_container_width=True)
            st.dataframe(signal_breakdown[["signal", "percentage"]], use_container_width=True, hide_index=True)
        st.dataframe(
            diagnostics[["signal_type", "modeled_influence_score", "coverage", "avg_accuracy", "avg_trust"]],
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with top_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Gateway Data Status</div>', unsafe_allow_html=True)
        gateway_update = gateway_actions[gateway_actions["action_title"].str.contains("rewards schema", case=False, na=False)]
        last_schema_update = relative_day_text(gateway_update.iloc[0]["timestamp"]) if not gateway_update.empty else "Current"
        status_cols = st.columns(2)
        with status_cols[0]:
            status_block("Gateway Status", gateway["gateway_status"])
            status_block("Data Ingestion", ingestion["ingestion_status"])
            status_block("Normalization", "Current")
        with status_cols[1]:
            status_block("Rewards Schema", last_schema_update)
            status_block("Distribution", "Published")
            status_block("Security", security_status["risk_posture"])
        if st.button("View All Gateway Actions", key="view_gateway_actions"):
            st.session_state["show_gateway_actions"] = not st.session_state.get("show_gateway_actions", False)
        if st.session_state.get("show_gateway_actions", False):
            render_gateway_actions(gateway_actions)
        st.dataframe(gateway_preview, use_container_width=True, hide_index=True)
        st.dataframe(security_frame, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    mid_left, mid_right = st.columns([1.0, 1.0])
    with mid_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Competitor Analysis</div>', unsafe_allow_html=True)
        benchmark_view = benchmark.head(6).copy()
        st.dataframe(benchmark_view, use_container_width=True, hide_index=True)
        st.plotly_chart(assistant_summary_chart(filtered if not filtered.empty else prompt_slice), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with mid_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">AI Response Monitor</div>', unsafe_allow_html=True)
        st.caption(selected_prompt)
        render_response_monitor(prompt_slice)
        st.markdown("</div>", unsafe_allow_html=True)

    bottom_left, bottom_right = st.columns([1.0, 1.0])
    with bottom_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Accuracy and Hallucination Detection</div>', unsafe_allow_html=True)
        render_accuracy_audit(prompt_slice, client_products)
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Score Tracking History</div>', unsafe_allow_html=True)
        st.plotly_chart(trend_chart(quarterly), use_container_width=True)
        st.markdown(
            f"Visible prompt rate: `{monthly_report['visible_prompt_rate']}%` | Critical issues: `{monthly_report['critical_issues']}` | "
            f"Average rank when present: `{safe_mean((filtered if not filtered.empty else prompt_slice)[(filtered if not filtered.empty else prompt_slice)['capital_one_present']]['rank_position'])}`"
        )
        st.markdown("**Recommendations**")
        for rec in quarterly_report["strategic_recommendations"]:
            st.markdown(f"- {rec['title']}")
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
