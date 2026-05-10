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

## Semantic Enterprise adoption coverage

This repo also meters estate adoption for `semantic-enterprise-v0.1.0` from `SocioProphet/ontogenesis`.

The adoption schema and example live under:

- `contracts/semantic-enterprise/adoption-coverage.schema.json`
- `examples/semantic-enterprise/adoption-coverage.example.json`

Validate the adoption model with:

```bash
python3 scripts/validate_semantic_enterprise_adoption.py
```

The GitHub Actions workflow `.github/workflows/semantic-enterprise-adoption.yml` validates this coverage model when Semantic Enterprise adoption artifacts change.

The model tracks the six downstream adoption surfaces:

- Prophet Platform import spine
- Sherlock Search evidence index
- Policy Fabric governance input
- AgentPlane context/admission boundary
- SourceOS syncd state-integrity mapping
- DeliveryExcellence automation metering
