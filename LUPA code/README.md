# Dell VeriPrompt Prototype

Offline Streamlit prototype for an internal Dell analyst dashboard that simulates how Dell VeriPrompt monitors and improves how Capital One appears in AI-assisted shopping results.

## What this prototype does

- Uses local mock data only.
- Simulates AI recommendation outputs from ChatGPT, Gemini, and Perplexity.
- Verifies Capital One product claims against a local source of truth.
- Generates deterministic visibility, accuracy, trust, and discovery scores.
- Shows modeled signal diagnostics, competitor benchmarking, gateway actions, monthly reporting, quarterly trends, security status, and rule-based recommendations.

## What is mocked

- AI assistant responses and ranking positions
- Signal attribution / diagnostic inputs
- Gateway distribution statuses and optimization actions
- Monthly and quarterly performance history
- Security posture metadata
- Recommendations logic inputs

## What a production version would add

- Live ingestion from approved prompt monitoring pipelines
- Stronger entity extraction and fact matching
- Real source provenance and attribution analysis
- Workflow integrations for publishing verified data
- Auth, audit controls, analyst collaboration, and client reporting exports

## Run instructions

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

## Suggested demo flow

1. Open the dashboard overview and explain Capital One as the selected client.
2. Use the prompt monitor to show where Capital One appears across ChatGPT, Gemini, and Perplexity.
3. Open a response with inaccuracies and show the hallucination audit firing against verified data.
4. Move to signal diagnostics to explain modeled influence patterns.
5. Show the gateway panel to demonstrate Dell is not only monitoring, but also transforming and distributing verified product data.
6. Close with monthly scorecards, quarterly trend improvement, and rule-based recommendations.
