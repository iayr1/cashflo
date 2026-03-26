from typing import List, Dict, Any
from core.entities.rule import Rule

class ValidateRulesUseCase:
    def execute(self, rules: List[Rule]) -> Dict[str, Any]:
        """
        Detect overlapping or contradictory rules.
        """
        conflicts = []
        field_rules = {}
        for rule in rules:
            for condition in rule.conditions:
                field = condition.field
                if field not in field_rules:
                    field_rules[field] = []
                # To prevent duplicates if a rule uses the same field twice:
                if rule not in field_rules[field]:
                    field_rules[field].append(rule)

        for field, frules in field_rules.items():
            if len(frules) > 1:
                conflicts.append({
                    "field": field,
                    "rule_ids": [r.rule_id for r in frules],
                    "message": f"Multiple active rules for field '{field}'. Handled sequentially. Ensure order doesn't conflict."
                })
                
        return {
            "is_valid": True, 
            "conflicts": conflicts,
            "total_rules": len(rules)
        }
