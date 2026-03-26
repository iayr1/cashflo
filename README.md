# 🏦 Cashflo Accounts Payable (AP) Rule Engine

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.20+-red.svg)](https://streamlit.io/)
[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean-orange.svg)](#)

A production-ready system that deterministically converts Accounts Payable policies into executable JSON rules using Large Language Models (LLMs), featuring a robust evaluation engine for automated invoice approvals.

---

## 🏗️ Clean Architecture

This project strictly adheres to **Clean Architecture** and SOLID principles to guarantee maintainability, separation of concerns, and scalability.

```text
ap_rule_engine/
├── core/                       # 🧠 Domain Entities and Use Cases
│   ├── entities/               # Rule, Condition, Action
│   └── usecases/               # Extract, Validate, and Execute policies
├── infrastructure/             # 🔌 External Tooling & Integrations
│   ├── llm/                    # OpenAI API integration & Structured Prompts
│   ├── parsers/                # Document text parsers
│   └── storage/                # JSON Persistence for rules and output
├── interface/                  # 💻 Presentational Adapters
│   ├── streamlit/              # Interactive GUI Dashboard
│   ├── api/                    # FastAPI endpoints (REST)
│   └── cli/                    # Headless CLI tool
└── tests/                      # 🧪 Pytest Unit test suite
```

---

## 📌 Features

- **Automated Extraction:** Uses OpenAI's `gpt-4o` to map natural language policies into structured, logically bounded Pydantic schemas.
- **Deterministic Evaluation:** Translates complex logical AND bounds (e.g., `> 10% PO` and `< 50L`) to automatically grade invoices.
- **Conflict Validation:** Alerts administrators if overlapping or conflicting rules are extracted.
- **Three Interfaces:** Use the system entirely via GUI (Streamlit), REST API (FastAPI), or headless CLI!

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python installed on your machine.
- Python 3.9+
- pip

### 2. Installation
Clone the repository to your local machine and install the Python dependencies:
```bash
# Clone the repository
git clone https://github.com/your-username/ap-rule-engine.git

# Navigate into the project folder
cd ap-rule-engine

# Install dependencies strictly
pip install -r requirements.txt
```

### 3. Environment Configuration
The application requires an OpenAI API key to perform dynamic LLM extractions. 
Create a file exactly named **`.env`** in the root of the project directory (`ap_rule_engine/.env`) and add your secret key:
```env
OPENAI_API_KEY="sk-proj-your-api-key-here"
```
*(Note: Do not commit the `.env` file to version control. Let Git ignore it.)*

---

## 🖥️ Running the Application

This software was engineered with completely detached interfaces, meaning you can run it three different ways depending on your preferred style!

### 🌟 Option A: Streamlit Interactive Dashboard (Recommended)
Launch the beautiful frontend user interface to visually parse documents and securely test rules:
```bash
streamlit run interface/streamlit/app.py
```
*A new browser window will automatically launch at **`http://localhost:8501`**!*

### ⚡ Option B: REST API (FastAPI)
Launch the API server for enterprise backend integrations and webhooks:
```bash
uvicorn interface.api.main:app --reload
```
*Navigate to **`http://localhost:8000/docs`** to explore the Swagger UI documentation and use the `/extract` or `/evaluate` HTTP endpoints directly!*

### 🛠️ Option C: Command Line Interface (CLI)
Perfect for CI/CD pipelines, cronjobs, or automated headless batch processing:

**(1) Extract Rules to JSON:**
```bash
python interface/cli/run.py --extract ap_policy.txt
```
**(2) Evaluate an Invoice Payload:**
```bash
python interface/cli/run.py --evaluate sample_invoice.json
```

---

## 🧪 Testing
To run the automated validation suite on the core execution engine logic against strictly typed conditions:
```bash
pytest tests/test_rule_engine.py
```

## 📝 Limitations & Next Steps
- Implement persistent database storage (PostgreSQL/MongoDB) in the `infrastructure/storage` adapter to structurally phase out `json_store.py`.
- Add advanced custom expression sandboxing (e.g., `ast.literal_eval`) to safely execute highly complex mathematical or conditional text derivations dynamically.
