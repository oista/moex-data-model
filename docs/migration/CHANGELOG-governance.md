# Changelog: Governance assignment authority (ADR-049)

## 5.0.0 (PR-5)

Breaking:

- Removed deprecated assignment slots:
  `classified_element_ref`, `policy_target_ref`, `policy_binding_id`.
- Canonical identity/target: `assignment_id`, `target_element_ref`,
  `assignment_scope` on abstract `GovernanceAssignment`.

Migration:

```text
python scripts/migrate_governance_assignments.py --check
python scripts/migrate_governance_assignments.py --write
python -m moex_dams.governance.cli materialize --root .
```

## 4.2.0 (PR-1 on current `main`)

Additive (original series used 4.1.0; renumbered because Wave C already
shipped aggregate **4.1.0**):

- Abstract `GovernanceAssignment` (`assignment_id`, `target_element_ref`,
  `assignment_scope`) with mixins `HasValidity` / `HasProvenance`
- `OwnershipAssignment`; `PolicyBinding.binding_effect`
- Root collection `ownership_assignments`
- Legacy target/id slots deprecated (`required` cleared)
- Sibling module `moex-governance-view` (EffectiveGovernanceView shapes; PR-3)
- L2 invariants **INV-054…INV-056** (original series INV-042…044; renumbered
  to avoid collision with Wave C matrix rows)
