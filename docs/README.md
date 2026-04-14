# DelEx Automation Contract Layer

This repository holds machine-readable contracts and validation surfaces for DelEx-OS.

## Purpose

- keep the human-readable canon in `delivery-excellence`
- encode the same operating model as schemas and validation-ready config here
- provide worked examples that downstream systems can consume

## Primary artifacts

- `schemas/autonomy-envelope.schema.json`
- `schemas/delivery-gate.schema.json`
- `schemas/client-dependency.schema.json`
- `examples/customer-success-support-accelerator.bundle.yaml`
- `docs/validation-contract.md`

## Design rule

If an object is normative for control, approval, or governance, it should have both:
1. a prose definition upstream in `delivery-excellence`
2. a machine-readable contract here
