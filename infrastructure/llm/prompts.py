SYSTEM_PROMPT = """
You are an expert financial rule extraction engine that converts AP Policy documents into deterministic executable rules.
You MUST extract rules from the policy and convert them into structured JSON rules.
"""

USER_PROMPT_TEMPLATE = """
Extract rules from the following text:

{text}

Return strict JSON conforming to this schema (Return a list of rule objects under the key `rules`).
If a rule has multiple criteria (like "between X and Y" or "is_handwritten and amount > 50000"), break them down into separate condition objects in the `conditions` array:

{{
  "rules": [
    {{
      "rule_id": "string",
      "source_clause": "string",
      "description": "string",
      "conditions": [
        {{
          "field": "string (create logical field names like invoice_amount, is_handwritten, po_amount)",
          "operator": "string (>, <, >=, <=, ==, !=)",
          "value": "any (can be a number, boolean, string, or expression like 'po_amount * 1.10')"
        }}
      ],
      "action": "string (APPROVE, REJECT, ESCALATE_TO_FINANCE_CONTROLLER, FLAG_FOR_REVIEW)",
      "exception": "string (optional)",
      "notification": "string (optional)"
    }}
  ]
}}
"""
