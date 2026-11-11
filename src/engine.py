"""
Identity-Reconciler Engine
Core logic for reconciling HR identity records against target application accounts.
"""

def validate_inputs(hr_records, app_records, department_policy):
    """
    Validates input records and policies for structural integrity.
    Returns a list of error strings if any issues are found, or an empty list if valid.
    """
    errors = []
    for hr in hr_records:
        dept = hr.get("department")
        if dept and dept not in department_policy:
            errors.append(f"Department '{dept}' is not mapped in access policy.")
    return errors


def compute_reconciliation_plan(hr_records, app_records, department_policy):
    """
    Computes the reconciliation plan comparing HR records (Source of Truth) 
    against current application records, enforcing department policies 
    and preserving unmanaged/legacy group memberships.
    Returns a tuple of (plan, errors).
    """
    errors = validate_inputs(hr_records, app_records, department_policy)
    
    app_map = {}
    for app in app_records:
        app_id = app.get("id") or app.get("employee_id")
        if app_id:
            app_map[app_id] = app

    plan = []

    for hr in hr_records:
        user_id = hr.get("id") or hr.get("employee_id")
        
        raw_status = hr.get("status")
        if raw_status is not None:
            hr_active = (raw_status == "active")
        else:
            hr_active = True

        department = hr.get("department")

        target_groups = []
        actions = []

        # Case 1: Inactive Employee (Leaver) or terminated in HR
        if not hr_active:
            app_user = app_map.get(user_id)
            app_enabled = app_user.get("status") == "active" or app_user.get("enabled", True) if app_user else False
            
            if app_user and app_enabled:
                actions.append("DISABLE_ACCOUNT")
                current_groups = app_user.get("groups", [])
                managed_groups = department_policy.get(department, [])
                active_managed = [g for g in current_groups if g in managed_groups]
                if active_managed:
                    actions.append(f"REMOVE_MANAGED_GROUPS: {active_managed}")
            
            plan.append({
                "id": user_id,
                "employee_id": user_id,
                "target_groups": [],
                "target_enabled": False,
                "actions": actions
            })
            continue

        # Managed policy groups defined for the department
        managed_policy_groups = set(department_policy.get(department, []))

        # Case 2: User already exists in the target application system
        if user_id in app_map:
            current_app_user = app_map[user_id]
            current_groups = set(current_app_user.get("groups", []))

            # Identify unmanaged/legacy custom groups that must be strictly preserved
            all_policy_groups = {g for groups in department_policy.values() for g in groups}
            unmanaged_groups = current_groups - all_policy_groups

            # Target groups are the union of department policy groups and custom/legacy groups
            target_groups = sorted(list(managed_policy_groups.union(unmanaged_groups)))

            # Determine app enabled status
            app_enabled = current_app_user.get("status") == "active" or current_app_user.get("enabled", False)
            if not app_enabled:
                actions.append("ENABLE_ACCOUNT")
            
            if current_groups != set(target_groups):
                to_remove = list(current_groups - set(target_groups))
                to_add = list(set(target_groups) - current_groups)
                actions.append(f"RECONCILE_GROUPS: remove {to_remove}, add {to_add}")
        else:
            # Case 3: New Employee (Joiner) - Does not exist in target application yet
            actions.append("CREATE_ACCOUNT")
            target_groups = sorted(list(managed_policy_groups))

        plan.append({
            "id": user_id,
            "employee_id": user_id,
            "target_groups": target_groups,
            "target_enabled": True,
            "actions": actions
        })

    return plan, errors