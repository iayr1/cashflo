import pytest
from core.entities.rule import Rule, Condition, ActionType
from core.usecases.execute_rules import ExecuteRulesUseCase

def test_execute_rules_success():
    rule = Rule(
        rule_id="R1",
        source_clause="1.1",
        description="Test Rule",
        conditions=[Condition(field="amount", operator=">", value="100")],
        action=ActionType.REJECT
    )
    uc = ExecuteRulesUseCase()
    
    # Test Failure case
    invoice1 = {"amount": 150}
    res1 = uc.execute(invoice1, [rule])
    assert res1["status"] == "FAIL"
    assert len(res1["triggered_rules"]) == 1
    
    # Test Success case
    invoice2 = {"amount": 50}
    res2 = uc.execute(invoice2, [rule])
    assert res2["status"] == "PASS"
    assert len(res2["triggered_rules"]) == 0
