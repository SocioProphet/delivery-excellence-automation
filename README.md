# delivery-excellence-automation

Automation bindings for DelEx-OS:
- canonical group ledger (address space)
- RBAC bindings (roles ↔ groups)
- email lists mapping (group ↔ address)
- calendar audiences + meeting definitions
- CI validation (referential integrity)

Governance docs/templates live in:
- SocioProphet/delivery-excellence

## Professional Intelligence OS automation

This repo now carries the first machine-readable automation contracts for the Professional Intelligence OS alignment wave:

- `contracts/professional-intelligence/work-item.schema.json`
- `contracts/professional-intelligence/demo-acceptance.schema.json`
- `contracts/professional-intelligence/repo-readiness.schema.json`

Seed examples live under:

- `examples/professional-intelligence/work-item.example.json`
- `examples/professional-intelligence/demo-acceptance.example.json`
- `examples/professional-intelligence/repo-readiness.example.json`

Validate the examples with:

```bash
python3 scripts/validate_professional_intelligence.py
```

The GitHub Actions workflow `.github/workflows/professional-intelligence-validation.yml` runs this check when the Professional Intelligence contracts, examples, or validator change.
