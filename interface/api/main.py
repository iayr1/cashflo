from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from core.usecases.extract_rules import ExtractRulesUseCase
from core.usecases.execute_rules import ExecuteRulesUseCase
from core.usecases.validate_rules import ValidateRulesUseCase
from infrastructure.llm.llm_client import LLMClient
from infrastructure.parsers.document_parser import DocumentParser
from infrastructure.storage.json_store import JsonStore

app = FastAPI(title="AP Rule Engine API")

# Dependencies Injection
llm_client = LLMClient()
document_parser = DocumentParser()
json_store = JsonStore()
extract_rules_uc = ExtractRulesUseCase(llm_client, document_parser)
validate_rules_uc = ValidateRulesUseCase()
execute_rules_uc = ExecuteRulesUseCase()

class ExtractRequest(BaseModel):
    file_path: str

class EvaluateRequest(BaseModel):
    invoice: Dict[str, Any]

@app.post("/extract")
def extract_rules(req: ExtractRequest):
    try:
        rules = extract_rules_uc.execute(req.file_path)
        json_store.save_rules(rules)
        validation_result = validate_rules_uc.execute(rules)
        return {
            "message": f"Successfully extracted {len(rules)} rules.",
            "validation": validation_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate")
def evaluate_invoice(req: EvaluateRequest):
    rules = json_store.load_rules()
    if not rules:
        raise HTTPException(status_code=400, detail="No rules found. Please extract rules first.")
    
    result = execute_rules_uc.execute(req.invoice, rules)
    json_store.save_execution_result(result)
    return result
