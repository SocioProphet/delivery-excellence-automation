# START HERE — DelEx Automation Contracts

This repository is the machine-readable contract and validation layer for DelEx-OS.

## Read in this order

1. `docs/README.md`
2. `docs/validation-contract.md`
3. `schemas/` for the current object model
4. `examples/customer-success-support-accelerator.bundle.yaml`
5. `scripts/validate_agentic_contracts.py`
6. `schemas/engagement.schema.json`
7. `scripts/validate_engagement_objects.py`

## Primary role of this repo

- encode the upstream DelEx method as schemas and examples
- validate contract objects in CI
- provide stable objects for downstream consumers

## Upstream and downstream

- Upstream prose canon lives in `delivery-excellence`
- Downstream consumers are `delivery-excellence-boards` and `delivery-excellence-innersource`
