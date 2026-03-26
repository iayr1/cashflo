# 🚀 AP Rule Engine

A production-ready system to convert an Accounts Payable policy document into deterministic executable rules using Clean Architecture.

## 🏗️ Architecture Stack

This project strictly adheres to **Clean Architecture** and SOLID principles to guarantee maintainability and scalability.

```
ap_rule_engine/
├── core/                       # Domain Entities and Use Cases
│   ├── entities/               # Rule, Condition, Action
│   └── usecases/               # Extract, Validate, and Execute policies
├── infrastructure/             # Tooling and external clients
│   ├── llm/                    # OpenAI API integration & Prompts
│   ├── parsers/                # Document text parser
│   └── storage/                # JSON Persistence for rules and output
├── interface/                  # Presentational layer (Adapters)
│   ├── api/                    # FastAPI endpoints
│   └── cli/                    # CLI tool to run the pipeline
└── tests/                      # Unit tests
```

## 🛠️ Setup Instructions

1. **Install Python Dependencies:**
   Ensure you have Python 3.9+ installed.
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**
   Set the OpenAI API key to process unstructured documents.
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   # On windows: set OPENAI_API_KEY=your_api_key
   ```
   *(Note: The system intercepts missing keys and falls back to a sample mock rule for demonstration).*

## 🏃 Execution Guide

### 🖥️ Streamlit Frontend UI (Recommended)

1. **Launch the interactive dashboard:**
   ```bash
   streamlit run interface/streamlit/app.py
   ```
2. A new browser window will open automatically where you can parse documents and evaluate invoices visually.

### Command Line Interface (CLI)

1. **Extract Rules from Policy Document:**
   ```bash
   python interface/cli/run.py --extract ap_policy.txt
   ```
   *Generates `rules.json`.*

2. **Evaluate Invoice against Extracted JSON Rules:**
   First, create a `sample_invoice.json`:
   ```json
   {
       "invoice_amount": 120000,
       "po_amount": 100000,
       "invoice_date": "2026-06-01",
       "grand_total": 120000,
       "vendor_gstin": "27AAACW1234QA"
   }
   ```
   Evaluate:
   ```bash
   python interface/cli/run.py --evaluate sample_invoice.json
   ```
   *Generates `execution_result.json`.*

### REST API (FastAPI)

1. **Launch Server:**
   ```bash
   uvicorn interface.api.main:app --reload
   ```
2. Navigate to `http://localhost:8000/docs` to use the `/extract` and `/evaluate` endpoints securely formatted adhering to the system.

## 🤖 AI Tools Used & Extensibility
* **LLM Engine**: OpenAI `gpt-4o` with strictly controlled structured outputs (`response_format={"type": "json_object"}`).
* **Prompt Engineering**: Dynamic multi-modal mapping prompting `ActionEnum` extraction to deterministically tie back to execution constraints.

## ⚠️ Limitations
- Real-world deployments require persistent SQL/NoSQL storage over `rules.json` via modifying the `JsonStore` implementing the Repository Pattern.
- Invoice expression validations like (`po_amount * 1.10`) parse simplistically currently. Complex evaluators typically necessitate a safe sandbox like `ast.literal_eval`.
