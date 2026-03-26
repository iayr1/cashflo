import streamlit as st
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure root path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

# ✅ Load .env properly
env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Import usecases
from core.usecases.extract_rules import ExtractRulesUseCase
from core.usecases.execute_rules import ExecuteRulesUseCase
from core.usecases.validate_rules import ValidateRulesUseCase
from infrastructure.llm.llm_client import LLMClient
from infrastructure.parsers.document_parser import DocumentParser
from infrastructure.storage.json_store import JsonStore

# ✅ Remove sidebar completely
st.set_page_config(
    page_title="AP Rule Engine",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📄 Accounts Payable (AP) Rule Engine")

# Initialize dependencies
llm_client = LLMClient()
document_parser = DocumentParser()
json_store = JsonStore()

# Tabs
tab1, tab2 = st.tabs(["1. Extract Rules", "2. Evaluate Invoice"])

# ---------------- TAB 1 ----------------
with tab1:
    st.header("Extract Rules from AP Policy")
    
    # Load default policy
    default_policy = ""
    try:
        with open("ap_policy.txt", "r", encoding="utf-8") as f:
            default_policy = f.read()
    except FileNotFoundError:
        pass

    uploaded_file = st.file_uploader("📂 Upload AP Policy Document (PDF, DOCX, TXT, MD)", type=["pdf", "docx", "txt", "md"])
    
    if uploaded_file:
        # Save temp file for DocumentParser to natively handle
        temp_upload_path = f"temp_upload_{uploaded_file.name}"
        with open(temp_upload_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Re-use our DocumentParser seamlessly
            default_policy = document_parser.parse(temp_upload_path)
            st.success(f"Successfully extracted text from `{uploaded_file.name}`. Verify below before proceeding!")
        except Exception as e:
            st.error(f"Error reading file: {e}")
        finally:
            if os.path.exists(temp_upload_path):
                os.remove(temp_upload_path)

    policy_input = st.text_area(
        "📝 Current AP Policy Text:",
        value=default_policy,
        height=300,
        placeholder="Paste policy here or upload a file above..."
    )

    if st.button("Extract Rules via LLM"):
        if not policy_input.strip():
            st.error("Please provide policy text.")
        else:
            with st.spinner("Extracting rules..."):
                temp_file = "temp_policy.txt"
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(policy_input)

                uc = ExtractRulesUseCase(llm_client, document_parser)

                try:
                    rules = uc.execute(temp_file)
                    json_store.save_rules(rules)

                    st.success(f"✅ Successfully extracted {len(rules)} rules!")

                    # Validate rules
                    val_uc = ValidateRulesUseCase()
                    val_res = val_uc.execute(rules)

                    if val_res["conflicts"]:
                        st.warning("⚠️ Potential Rule Conflicts Detected:")
                        for c in val_res["conflicts"]:
                            st.write(f"- Field `{c['field']}` has multiple rules.")

                    st.subheader("📊 Extracted Rules")
                    st.json([r.model_dump(mode="json") for r in rules])

                except Exception as e:
                    st.error(f"❌ Error: {e}")

                finally:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

# ---------------- TAB 2 ----------------
with tab2:
    st.header("Evaluate Invoice")

    # Default invoice
    default_invoice = {
        "invoice_amount": 120000,
        "po_amount": 100000,
        "invoice_date": "2026-06-01",
        "grand_total": 120000,
        "vendor_gstin": "27AAACW1234QA"
    }

    try:
        with open("sample_invoice.json", "r") as f:
            default_invoice = json.load(f)
    except FileNotFoundError:
        pass

    invoice_str = st.text_area(
        "Invoice JSON Payload",
        value=json.dumps(default_invoice, indent=2),
        height=250
    )

    if st.button("Evaluate against Extracted Rules"):
        try:
            invoice_dict = json.loads(invoice_str)
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON format.")
            st.stop()

        rules = json_store.load_rules()

        if not rules:
            st.error("❌ No rules found. Please extract rules first.")
        else:
            uc = ExecuteRulesUseCase()
            result = uc.execute(invoice_dict, rules)

            st.subheader(f"📌 Execution Status: {result['status']}")

            if result["status"] == "APPROVED":
                st.success("✅ Invoice Auto-Approved")
            elif result["status"] == "REQUIRES_APPROVAL":
                st.warning("⚠️ Requires Manual Approval / Escalation")
            else:
                st.error("🚨 Invoice Rejected")

            if result.get("explanation"):
                st.subheader("🧠 Explanation")
                for exp in result["explanation"]:
                    st.write(f"- {exp}")
            else:
                st.info("No rules triggered.")

            with st.expander("🔍 Full Result JSON"):
                st.json(result)