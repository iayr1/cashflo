import json
from typing import List, Dict, Any
from pathlib import Path
from core.entities.rule import Rule

class JsonStore:
    def __init__(self, file_path: str = "rules.json"):
        self.file_path = Path(file_path)

    def save_rules(self, rules: List[Rule]):
        data = [rule.model_dump() for rule in rules]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_rules(self) -> List[Rule]:
        if not self.file_path.exists():
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Rule(**item) for item in data]

    def save_execution_result(self, result: Dict[str, Any], result_path: str = "execution_result.json"):
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
