from src.engine import compute_reconciliation_plan

def main():
    # 1. Source of Truth (HR Records)
    hr_records = [
        {"employee_id": "EMP-001", "status": "active", "department": "Retail"},
        {"employee_id": "EMP-002", "status": "active", "department": "Finance"},
        {"employee_id": "EMP-003", "status": "inactive", "department": "Retail"}
    ]

    # 2. Current State (Application Accounts, including a legacy unmanaged group)
    app_records = [
        {"employee_id": "EMP-001", "enabled": True, "groups": ["retail", "legacy-vpn-access"]},
        {"employee_id": "EMP-002", "enabled": False, "groups": []},
        {"employee_id": "EMP-003", "enabled": True, "groups": ["retail"]}
    ]

    # 3. Access Policy mapping departments to managed groups
    policy = {
        "Retail": ["retail"],
        "Finance": ["finance"]
    }

    print("--- Running IAM Reconciliation ---")
    plan, errors = compute_reconciliation_plan(hr_records, app_records, policy)

    if errors:
        print("❌ Validation Errors Found:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("✅ Reconciliation Plan Computed Successfully:\n")
        for item in plan:
            print(f"Employee ID    : {item['employee_id']}")
            print(f"Target Enabled : {item['target_enabled']}")
            print(f"Target Groups  : {item['target_groups']}")
            print(f"Actions        : {item['actions']}")
            print("-" * 40)

if __name__ == "__main__":
    main()