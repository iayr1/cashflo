import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
from core.entities.rule import Rule, Condition, ActionType
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
env_path = ROOT_DIR / ".env"

load_dotenv(dotenv_path=env_path, override=True)

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.getenv("OPENAI_API_KEY")
        if key:
            key = key.strip().strip('"').strip("'")
            
        # In case API key is missing (e.g., in a test environment or dummy run), handle it gracefully
        self.client = OpenAI(api_key=key) if key else None

    def extract_rules(self, text: str) -> List[Rule]:
        if not self.client:
            # For demonstration without API key, we return a mock rule
            print("WARNING: No OpenAI API key found. Returning mock rule based on sample.")
            return [
                Rule(
                    rule_id="AP-001",
                    source_clause="Section 2.2(c)",
                    description="Escalate when invoice > PO * 1.10",
                    conditions=[Condition(field="invoice_amount", operator=">", value="po_amount * 1.10")],
                    action=ActionType.ESCALATE_TO_FINANCE_CONTROLLER
                )
            ]

        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(text=text)}
            ],
            temperature=0.0
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        rules_list = data.get("rules", [])
        rules = []
        for r in rules_list:
            try:
                action = ActionType(r.get("action"))
            except ValueError:
                action = ActionType.FLAG_FOR_REVIEW

            condition_list = r.get("conditions", [])
            
            # Fallback for old schema if AI messes up
            if not condition_list and r.get("condition"):
                condition_list = [r.get("condition")]

            conditions = []
            for cond_data in condition_list:
                conditions.append(
                    Condition(
                        field=cond_data.get("field"),
                        operator=cond_data.get("operator", "=="),
                        value=cond_data.get("value")
                    )
                )

            rule = Rule(
                rule_id=r.get("rule_id", "UNKNOWN"),
                source_clause=r.get("source_clause", "UNKNOWN"),
                description=r.get("description", ""),
                conditions=conditions,
                action=action,
                exception=r.get("exception"),
                notification=r.get("notification")
            )
            rules.append(rule)
            
        return rules
