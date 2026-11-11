from src.engine import validate_inputs, compute_reconciliation_plan

def test_validate_inputs_success():
    hr = [{"employee_id": "EMP-1", "status": "active", "department": "Retail"}]
    app = [{"employee_id": "EMP-1", "enabled": True, "groups": ["retail"]}]
    policy = {"Retail": ["retail"]}
    errors = validate_inputs(hr, app, policy)
    assert errors == []

def test_validate_inputs_unmapped_department():
    hr = [{"employee_id": "EMP-1", "status": "active", "department": "UnknownDept"}]
    app = []
    policy = {"Retail": ["retail"]}
    errors = validate_inputs(hr, app, policy)
    assert len(errors) > 0
    assert "not mapped" in errors[0]

def test_compute_reconciliation_plan_creation_and_groups():
    hr = [{"employee_id": "EMP-1", "status": "active", "department": "Retail"}]
    app = []
    policy = {"Retail": ["retail"]}
    plan, errors = compute_reconciliation_plan(hr, app, policy)
    
    assert errors == []
    assert len(plan) == 1
    assert plan[0]["employee_id"] == "EMP-1"
    assert plan[0]["target_enabled"] is True
    assert "CREATE_ACCOUNT" in plan[0]["actions"]

def test_unmanaged_groups_preservation():
    hr = [{"employee_id": "EMP-1", "status": "active", "department": "Retail"}]
    app = [{"employee_id": "EMP-1", "enabled": True, "groups": ["retail", "legacy-vpn-access"]}]
    policy = {"Retail": ["retail"]}
    
    plan, errors = compute_reconciliation_plan(hr, app, policy)
    assert errors == []
    assert "legacy-vpn-access" in plan[0]["target_groups"]