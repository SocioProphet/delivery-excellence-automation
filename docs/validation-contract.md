# Validation Contract

## Goal

Validation in this repo should prove that the machine-readable contract layer remains internally consistent and aligned to the human-readable method.

## Validation scope

### Referential integrity
Already partly covered by the current config validator:
- every referenced group ID must exist
- every automated group must have a routable email mapping

### Schema conformance
New contract objects should validate against explicit schemas:
- autonomy envelope
- delivery gate
- client dependency manifest

### Policy integrity
Later validation should also ensure:
- A3 actions are reversible and explicitly marked as such
- A4 actions are never marked as autonomous
- approval requirements exist for every A2 action
- every gate declares accountable roles and evidence requirements

### Example validity
Worked examples under `examples/` should validate cleanly against all referenced schemas.

## Downstream consumers

- `delivery-excellence-boards` should consume validated gate and workflow objects.
- `delivery-excellence-innersource` should consume validated readiness and role objects.
- `delivery-excellence-bounties` should consume validated evidence and gate-completion signals, not invent its own truth model.
