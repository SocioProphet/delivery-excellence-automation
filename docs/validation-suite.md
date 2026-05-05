# Validation Suite

## Purpose

This document indexes the validation surfaces in `delivery-excellence-automation` and defines the single operator entrypoint.

## Primary command

```bash
python scripts/run_validation_suite.py
```

The suite runner executes every known validator that exists in the repository and skips validators that are not present on a given branch.

## Validation surfaces

### Governance automation
- `scripts/validate_configs.py`
- validates group, RBAC, email, and calendar referential integrity

### Agentic services contracts
- `scripts/validate_all_contracts.py`
- validates service-offer, engagement, control-loop, autonomy-envelope, gate, dependency, exception, board, reusable-asset, customer-success, and gate-review objects

### Metadata operations
- `scripts/validate_metadata_operations.py`
- validates KMASS metric and metadata remediation examples

### CoC service and SLA contracts
- `scripts/validate_service_catalog_and_sla.py`
- validates service catalog entry and SLA examples

### Incentive and payout contracts
- `scripts/validate_payout_objects.py`
- validates payout and escrow objects
- `scripts/validate_incentive_policy.py`
- validates bounty/incentive policy examples

### Professional Intelligence program contracts
- `scripts/validate_professional_intelligence.py`
- validates Professional Intelligence work item, demo acceptance, and repo readiness fixtures

## Rule

Specialized workflows may remain for fast targeted checks, but `validation-suite.yml` is the main consolidation path for repo-wide contract health.
