# Dell VeriPrompt

Dell VeriPrompt is an AI Product Representation Intelligence platform that helps companies monitor how their products appear in AI-assisted shopping responses across platforms such as ChatGPT, Gemini, and Perplexity.

As AI assistants increasingly act as the entry point for product discovery, companies face two major risks:
- losing visibility in AI-generated recommendations
- being misrepresented through inaccurate or hallucinated product information

Dell VeriPrompt addresses this challenge by monitoring AI responses, verifying product claims against trusted product data, and identifying opportunities to improve visibility, accuracy, and customer trust.

This prototype demonstrates how Dell VeriPrompt analysts would monitor AI product discovery performance for an enterprise client such as Capital One.

---

## What the Application Does

The dashboard simulates how Dell analysts monitor AI-assisted product discovery.

The prototype evaluates AI responses and generates insights using four core metrics:

- **AI Visibility Score** – how often a product appears in AI recommendations
- **Accuracy Score** – how closely AI responses match verified product data
- **Trust Score** – likelihood that AI responses contain misleading information
- **AI Discovery Score** – combined performance indicator for AI discovery

Additional features include:

- AI response monitoring across ChatGPT, Gemini, and Perplexity
- hallucination and accuracy detection
- signal diagnostics identifying sources influencing AI recommendations
- competitor analysis
- gateway data status monitoring
- reporting summary generation

The prototype uses Capital One credit cards as the example client scenario.

---

## Technology Stack

- Python
- Streamlit
- Pandas
- Custom HTML/CSS dashboard styling

---

## Running the Application

### Prerequisites

Install Python 3.10 or later.

### Step 1 – Extract the Project

Unzip the project folder and open the extracted folder in a terminal.

Make sure the folder contains:
- `app.py`
- `run_app.ps1`

### Step 2 – Run the App

From the project folder, run:

```powershell
.\run_app.ps1
```

This script installs the required dependencies if needed and launches the dashboard.

### Step 3 – Open the Dashboard

After the script runs, open the local URL shown in the terminal:

```text
http://127.0.0.1:8503/
```

---

## How Judges Should Navigate the Prototype

1. Select the example client (Capital One).
2. Choose AI platform filters such as ChatGPT, Gemini, or Perplexity.
3. Select a monitoring prompt.
4. Run the monitoring analysis.
5. Review the major analytics sections:
   - Score Tracking
   - Signal Diagnostics
   - AI Response Monitor
   - Accuracy and Hallucination Detection
   - Competitor Analysis
   - Gateway Data Status
   - Reporting Summary

These sections demonstrate how Dell VeriPrompt analyzes AI-generated product discovery results.

---

## How to Tell the Application Started Successfully

The application has started successfully when the terminal displays a local Streamlit link and opening it shows the Dell VeriPrompt dashboard.

Expected local URL:

```text
http://127.0.0.1:8503/
```

---

## Prototype Notes

This submission is a functional prototype built for the HBCU Battle of the Brains Challenge.

The system uses simulated AI responses and mock datasets to demonstrate the Dell VeriPrompt monitoring workflow without requiring external AI APIs.

The focus of the prototype is to demonstrate:
- technical feasibility
- dashboard functionality
- business value of improving AI-assisted product discovery
