# Dell VeriPrompt

Dell VeriPrompt is an AI Discovery Intelligence and Optimization platform that helps companies monitor how their products appear in AI-assisted shopping responses across platforms such as ChatGPT, Gemini, and Perplexity.

As AI assistants increasingly act as the entry point for product discovery, companies face two major risks:

- losing visibility in AI-generated recommendations
- being misrepresented through inaccurate or hallucinated product information

Dell VeriPrompt addresses this challenge by monitoring AI responses, verifying product claims against trusted product data, and identifying opportunities to improve visibility, accuracy, and customer trust.

This prototype demonstrates how Dell VeriPrompt analysts would monitor AI product discovery performance for an enterprise client such as **Capital One**.

---

# What the Application Does

The dashboard simulates how Dell analysts monitor AI-assisted product discovery.

The prototype evaluates AI responses and generates insights using four core metrics:

- **AI Visibility Score** – how often a product appears in AI recommendations  
- **Accuracy Score** – how closely AI responses match verified product data  
- **Trust Score** – likelihood that AI responses contain misleading information  
- **AI Discovery Score** – combined indicator of AI discovery performance  

Additional dashboard capabilities include:

- AI response monitoring across ChatGPT, Gemini, and Perplexity
- hallucination and accuracy detection
- signal diagnostics identifying which sources influence AI recommendations
- competitor benchmarking
- gateway data status monitoring
- reporting summary generation

The prototype uses **Capital One credit cards** as the example client scenario.

---

# Technology Stack

- Python
- Streamlit
- Pandas
- Custom HTML/CSS dashboard styling

---

# Running the Application

## Windows (Fastest Method)

### Step 1 — Extract the ZIP File

Download the ZIP submission and extract it.

Open the extracted project folder and navigate to the "LUPA code" folder

In there, you should see files such as:

- `app.py`
- `requirements.txt`
- `README.md`
- `run_app.bat`

---

### Step 2 — Launch the Application

Simply **double-click the file**:

```
run_app.bat
```

The launcher will:

1. Install required Python packages
2. Start the Dell VeriPrompt application

---

### Step 3 — Open the Dashboard

After the application starts, open this address in your browser:

```
http://127.0.0.1:8503/
```

---

# Mac Instructions

### Step 1 — Check Python

Open **Terminal** and run:

```bash
python3 --version
```

If Python is installed, continue to the next step.

---

### Step 2 — Navigate to the Project Folder

In Terminal, move into the extracted project folder.

Example:

```bash
cd ~/Downloads/LUPA_Tech_031326/LUPA code
```

---

### Step 3 — Install Dependencies

Run:

```bash
python3 -m pip install -r requirements.txt
```

---

### Step 4 — Launch the Application

Run:

```bash
python3 -m streamlit run app.py --server.port 8503
```

---

### Step 5 — Open the Dashboard

Open this address in your browser:

```
http://127.0.0.1:8503/
```

---

# How Judges Should Navigate the Prototype

1. Select the example client (**Capital One**)
2. Choose AI platforms such as **ChatGPT, Gemini, or Perplexity**
3. Select a monitoring prompt
4. Run the monitoring analysis
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

# How to Tell the Application Started Successfully

The application started successfully when:

- the terminal or launcher displays a Streamlit server message
- opening the local URL loads the **Dell VeriPrompt dashboard**

Expected address:

```
http://127.0.0.1:8503/
```

---

# Prototype Notes

This submission is a functional prototype built for the **HBCU Battle of the Brains Challenge**.

The system uses **simulated AI responses and mock datasets** to demonstrate the Dell VeriPrompt monitoring workflow without requiring external AI APIs.

The goal of this prototype is to demonstrate:

- technical feasibility
- platform functionality
- the business value of improving AI-assisted product discovery.
