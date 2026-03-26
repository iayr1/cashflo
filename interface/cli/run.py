import argparse
import json
import os
import sys

# Ensure the root of the project is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.usecases.extract_rules import ExtractRulesUseCase
from core.usecases.execute_rules import ExecuteRulesUseCase
from core.usecases.validate_rules import ValidateRulesUseCase
from infrastructure.llm.llm_client import LLMClient
from infrastructure.parsers.document_parser import DocumentParser
from infrastructure.storage.json_store import JsonStore

def main():
    parser = argparse.ArgumentParser(description="AP Rule Engine CLI")
    parser.add_argument("--extract", type=str, help="Path to AP Policy Document to extract rules")
    parser.add_argument("--evaluate", type=str, help="Path to Invoice JSON to evaluate")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    # DI
    llm_client = LLMClient()
    document_parser = DocumentParser()
    json_store = JsonStore()
    
    if args.extract:
        print(f"Extracting rules from {args.extract}...")
        uc = ExtractRulesUseCase(llm_client, document_parser)
        rules = uc.execute(args.extract)
        json_store.save_rules(rules)
        print(f"\nExtracted and saved {len(rules)} rules to rules.json.\n")
        
        # Validation
        val_uc = ValidateRulesUseCase()
        val_res = val_uc.execute(rules)
        if val_res["conflicts"]:
            print("WARNING: Validation found potential overlaps:")
            for c in val_res["conflicts"]:
                print(f" - Field {c['field']} has multiple rules. Review required.")
        
    if args.evaluate:
        print(f"Evaluating invoice {args.evaluate}...")
        with open(args.evaluate, "r") as f:
            invoice = json.load(f)
            
        rules = json_store.load_rules()
        if not rules:
            print("No rules found. Please run --extract first.")
            return
            
        uc = ExecuteRulesUseCase()
        result = uc.execute(invoice, rules)
        
        print("\n=== EVALUATION RESULT ===")
        print(f"Status: {result['status']}")
        for exp in result['explanation']:
            print(f" - {exp}")
            
        json_store.save_execution_result(result)
        print("\nResults saved to execution_result.json.")

if __name__ == "__main__":
    main()
