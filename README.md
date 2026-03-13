# Dell VeriPrompt

Dell VeriPrompt is an AI Product Representation Intelligence platform that helps companies monitor how their products appear in AI-assisted shopping responses across platforms such as ChatGPT, Gemini, and Perplexity.

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

These steps explain how to run the Dell VeriPrompt prototype locally from the GitHub repository.

---

## Step 1 — Download the Repository

On the GitHub repository page:

1. Click the green **Code** button.
2. Select **Download ZIP**.
3. Extract the ZIP file.

Open the extracted project folder.

You should see files such as:

```
app.py
requirements.txt
run_app.bat
README.md
modules/
data/
utils/
```

---

# Windows Instructions

### Step 2 — Launch the Application

Inside the project folder, **double click the file**:

```
run_app.bat
```

This launcher will automatically:

- install required Python packages
- start the Dell VeriPrompt dashboard

---

### Step 3 — Open the Dashboard

After the application starts, open this address in your browser:

```
http://127.0.0.1:8503
```

---

# Mac Instructions

Mac users will run the application using Terminal.

---

### Step 2 — Check Python

Open **Terminal** and run:

```
python3 --version
```

---

### Step 3 — Navigate to the Project Folder

Use the `cd` command to move into the project directory.

Example:

```
cd ~/Downloads/dell-veriprompt-prototype
```

---

### Step 4 — Install Dependencies

Run:

```
python3 -m pip install -r requirements.txt
```

---

### Step 5 — Start the Application

Run:

```
python3 -m streamlit run app.py --server.port 8503
```

---

### Step 6 — Open the Dashboard

Open this address in your browser:

```
http://127.0.0.1:8503
```

---

# How to Tell the Application Started Successfully

The application started successfully when:

- the terminal displays a Streamlit server message
- opening the URL loads the **Dell VeriPrompt dashboard**

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

# Prototype Notes

This submission is a functional prototype built for the **HBCU Battle of the Brains Challenge**.

The system uses **simulated AI responses and mock datasets** to demonstrate the Dell VeriPrompt monitoring workflow without requiring external AI APIs.

The goal of this prototype is to demonstrate:

- technical feasibility
- platform functionality
- the business value of improving AI-assisted product discovery.
