# Identity-Reconciler

Production-ready Identity and Access Management (IAM) reconciliation engine designed to synchronize HR records (Source of Truth) with target application accounts while strictly preserving unmanaged/legacy group memberships.

## Features

- **HR as Source of Truth**: Computes precise lifecycle actions (`CREATE_ACCOUNT`, `DISABLE_ACCOUNT`, `ENABLE_ACCOUNT`, `RECONCILE_GROUPS`).
- **Policy Enforcement**: Automatically maps department-based policies to managed application groups.
- **Legacy Preservation**: Safely preserves unmanaged, custom, or legacy group memberships (idempotent reconciliation).
- **Input Validation**: Validates structural integrity and unmapped department policies.
- **Robust Test Suite**: Fully covered by `pytest` ensuring high reliability and compliance.

## Project Structure

```text
identity-reconciler/
├── src/
│   └── engine.py        # Core reconciliation logic and input validation
├── tests/
│   └── test_engine.py   # Comprehensive unit test suite
├── main.py              # CLI demonstration runner
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Getting Started

### Prerequisites

Ensure you have Python 3.10+ installed on your system.

### Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/bouttg/Indentity-Reconciler.git
cd Indentity-Reconciler
pip install -r requirements.txt
```

## Usage

### Run Unit Tests
To execute the comprehensive test suite and verify architectural integrity:
```bash
pytest -v
```

### Run Demonstration Script
To simulate a full IAM reconciliation batch (covering Joiners, Movers, Leavers, and legacy group preservation):
```bash
python main.py
```

## License

This project is licensed under the MIT License.
