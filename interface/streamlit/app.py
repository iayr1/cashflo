import streamlit as st
import json
import os
import sys
from pathlib import Path

# Ensure the root of the project is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.usecases.extract_rules import ExtractRulesUseCase
from core.usecases.execute_rules import ExecuteRulesUseCase
from core.usecases.validate_rules import ValidateRulesUseCase
from infrastructure.llm.llm_client import LLMClient
from infrastructure.parsers.document_parser import DocumentParser
from infrastructure.storage.json_store import JsonStore

st.set_page_config(page_title="AP Rule Engine", layout="wide")

st.title("📄 Accounts Payable (AP) Rule Engine")

# Dependency injection for session state
if "llm_client" not in st.session_state:
    st.session_state.llm_client = LLMClient()
if "document_parser" not in st.session_state:
    st.session_state.document_parser = DocumentParser()
if "json_store" not in st.session_state:
    st.session_state.json_store = JsonStore()

st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("OpenAI API Key (Optional for mock rules)", type="password")
if api_key:
    # Update client if new key is provided
    st.session_state.llm_client = LLMClient(api_key=api_key)

tab1, tab2 = st.tabs(["1. Extract Rules", "2. Evaluate Invoice"])

with tab1:
    st.header("Extract Rules from AP Policy")
    
    # Preload the sample policy if available
    default_policy = ""
    try:
        with open("ap_policy.txt", "r", encoding="utf-8") as f:
            default_policy = f.read()
    except FileNotFoundError:
        pass

    policy_input = st.text_area(
        "Current AP Policy Text:", 
        value=default_policy,
        height=300, 
        placeholder="1. Every invoice must contain..."
    )
    
    if st.button("Extract Rules via LLM"):
        if not policy_input.strip():
            st.error("Please provide policy text.")
        else:
            with st.spinner("Extracting rules..."):
                # Write to temporary file for parser interface
                temp_file = "temp_policy.txt"
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(policy_input)
                
                uc = ExtractRulesUseCase(st.session_state.llm_client, st.session_state.document_parser)
                try:
                    rules = uc.execute(temp_file)
                    st.session_state.json_store.save_rules(rules)
                    st.success(f"Successfully extracted {len(rules)} rules!")
                    
                    val_uc = ValidateRulesUseCase()
                    val_res = val_uc.execute(rules)
                    if val_res["conflicts"]:
                        st.warning("⚠️ Potential Rule Overlaps Detected:")
                        for c in val_res["conflicts"]:
                            st.write(f"- Field `{c['field']}` has multiple rules attached to it.")
                            
                    st.write("### Exracted JSON Schema View")
                    # Display rules properly formatted via model_dump() + enums
                    st.json([r.model_dump(mode="json") for r in rules])
                except Exception as e:
                    st.error(f"Error parsing or extracting rules: {e}")
                finally:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

with tab2:
    st.header("Evaluate Invoice")
    
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
        
    invoice_str = st.text_area("Invoice JSON Payload", value=json.dumps(default_invoice, indent=2), height=250)
    
    if st.button("Evaluate against Extract Rules"):
        try:
            invoice_dict = json.loads(invoice_str)
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON format for invoice.")
            st.stop()
            
        rules = st.session_state.json_store.load_rules()
        if not rules:
            st.error("No rules extracted yet! Please go to the 'Extract Rules' tab first.")
        else:
            uc = ExecuteRulesUseCase()
            result = uc.execute(invoice_dict, rules)
            
            st.subheader(f"Execution Status: {result['status']}")
            if result['status'] == "APPROVED":
                st.success("✅ Invoice Auto-Approved! All standard constraints passed without escalation.")
            elif result['status'] == "REQUIRES_APPROVAL":
                st.warning("⚠️ Invoice Requires Manual Approval / Escalation.")
            else:
                st.error("🚨 Invoice Rejected based on compliance/policy constraints.")
                
            if result['explanation']:
                st.write("### Rule Actions Triggered & Explanations:")
                for exp in result['explanation']:
                    st.write(f"- {exp}")
            else:
                st.info("No matching rules were triggered for this payload.")
                
            with st.expander("View Full Context JSON"):
                st.json(result)
