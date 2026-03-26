import operator
from typing import Any, Dict
from pydantic import BaseModel

OPERATORS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

class Condition(BaseModel):
    field: str
    operator: str
    value: Any

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate the condition against the provided context (e.g. invoice data).
        Handles basic expressions like "po_amount * 1.10" if required.
        """
        if self.field not in context:
            return False
            
        context_val = context[self.field]
        target_val = self.value
        
        # Simple evaluation of expressions on the right-hand side (e.g. 'po_amount * 1.10')
        if isinstance(target_val, str) and "*" in target_val:
            parts = target_val.split("*")
            if len(parts) == 2:
                field_ref = parts[0].strip()
                try:
                    multiplier = float(parts[1].strip())
                    if field_ref in context:
                        target_val = float(context[field_ref]) * multiplier
                except ValueError:
                    pass

        op_func = OPERATORS.get(self.operator)
        if not op_func:
            raise ValueError(f"Unsupported operator: {self.operator}")

        try:
            return op_func(float(context_val), float(target_val))
        except (ValueError, TypeError):
            # Fallback to string comparison
            return op_func(str(context_val), str(target_val))
