# Definition of managed groups (directly governed by corporate policies)
MANAGED_GROUPS = {"retail", "finance"}

def validate_inputs(hr_records: list[dict], app_records: list[dict], policy: dict) -> list[str]:
    """
    Validates the consistency and correctness of input data (HR, App, and Policy).
    Returns a list of detected critical errors.
    """
    errors = []
    seen_hr = set()
    seen_app = set()

    # 1. Validate HR records
    for emp in hr_records:
        emp_id = emp.get("employee_id")
        if not emp_id:
            errors.append("Found HR record missing employee_id.")
            continue
        if emp_id in seen_hr:
            errors.append(f"Duplicate employee ID in HR: {emp_id}")
        seen_hr.add(emp_id)

        if emp.get("status") == "active":
            dept = emp.get("department")
            if dept not in policy:
                errors.append(f"Critical error: Active employee {emp_id} has a department not mapped in the policy: '{dept}'.")

    # 2. Validate Application records
    for acc in app_records:
        acc_id = acc.get("employee_id")
        if not acc_id:
            errors.append("Found App record missing employee_id.")
            continue
        if acc_id in seen_app:
            errors.append(f"Duplicate ID in App: {acc_id}")
        seen_app.add(acc_id)

    return errors


def compute_reconciliation_plan(hr_records: list[dict], app_records: list[dict], policy: dict) -> tuple[list[dict], list[str]]:
    """
    Computes the reconciliation plan by comparing the HR state (source of truth) 
    with the current application state. Ensures the preservation of unmanaged groups.
    """
    errors = validate_inputs(hr_records, app_records, policy)
    if errors:
        return [], errors

    app_map = {acc["employee_id"]: acc for acc in app_records}
    hr_map = {emp["employee_id"]: emp for emp in hr_records}
    
    plan = []

    for emp_id, hr_emp in hr_map.items():
        status = hr_emp["status"]
        dept = hr_emp.get("department")
        
        app_acc = app_map.get(emp_id)
        app_exists = app_acc is not None
        app_enabled = app_acc.get("enabled", False) if app_exists else False
        app_groups = set(app_acc.get("groups", [])) if app_exists else set()

        # Isolate unmanaged groups (e.g., 'legacy-vpn-access') to preserve them
        unmanaged_groups = app_groups - MANAGED_GROUPS
        
        # Determine expected managed groups based on policy and active status
        desired_managed = set(policy.get(dept, [])) if status == "active" else set()
        
        # Final target groups include policy groups + preserved unmanaged groups
        target_groups = list(desired_managed | unmanaged_groups)

        actions = []
        target_enabled = (status == "active")

        if status == "active":
            if not app_exists:
                actions.append("CREATE_ACCOUNT")
                actions.append(f"ASSIGN_GROUPS: {list(desired_managed)}")
            else:
                if not app_enabled:
                    actions.append("ENABLE_ACCOUNT")
                
                current_managed = app_groups & MANAGED_GROUPS
                if current_managed != desired_managed:
                    actions.append(f"RECONCILE_GROUPS: remove {list(current_managed - desired_managed)}, add {list(desired_managed - current_managed)}")
        
        elif status == "inactive":
            if app_exists and app_enabled:
                actions.append("DISABLE_ACCOUNT")
                if app_groups & MANAGED_GROUPS:
                    actions.append(f"REMOVE_MANAGED_GROUPS: {list(app_groups & MANAGED_GROUPS)}")

        plan.append({
            "employee_id": emp_id,
            "target_enabled": target_enabled,
            "target_groups": target_groups,
            "actions": actions
        })

    return plan, []