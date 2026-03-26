from typing import Optional, List
from pydantic import BaseModel
from .condition import Condition
from .action import ActionType

class Rule(BaseModel):
    rule_id: str
    source_clause: str
    description: str
    conditions: List[Condition]
    action: ActionType
    exception: Optional[str] = None
    notification: Optional[str] = None
