from typing import List, Dict, Any
from core.entities.rule import Rule

class ExecuteRulesUseCase:
    def execute(self, invoice: Dict[str, Any], rules: List[Rule]) -> Dict[str, Any]:
        """
        Input: invoice JSON
        Output: PASS/FAIL, triggered rules, explanation
        """
        triggered_rules = []
        is_rejected = False
        is_escalated = False
        explanations = []

        for rule in rules:
            if not rule.conditions:
                continue

            # Evaluate all conditions mathematically - ALL conditions must be True (Logical AND)
            rule_triggered = True
            for condition in rule.conditions:
                try:
                    is_triggered = condition.evaluate(invoice)
                except Exception as e:
                    is_triggered = False # Fail safely
                
                if not is_triggered:
                    rule_triggered = False
                    break

            if rule_triggered:
                # Include stringified output for API response safety
                rule_dict = rule.model_dump()
                rule_dict["action"] = rule.action.value
                triggered_rules.append(rule_dict)
                explanations.append(f"Rule [{rule.rule_id}]: {rule.description} | Action: {rule.action.value}")
                
                # Check outcome severity
                if rule.action.value == "REJECT":
                    is_rejected = True
                elif rule.action.value in ["ESCALATE_TO_FINANCE_CONTROLLER", "FLAG_FOR_REVIEW"]:
                    is_escalated = True

        if is_rejected:
            status = "REJECTED"
        elif is_escalated:
            status = "REQUIRES_APPROVAL"
        else:
            status = "APPROVED"

        return {
            "status": status,
            "triggered_rules": triggered_rules,
            "explanation": explanations,
            "evaluated_count": len(rules)
        }
