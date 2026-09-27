---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# StandardProvider protocol fitness test (deferred)

**When:** first commit that adds `packages/modeling-kernel` with `StandardProvider`.  
**Where:** `tests/architecture/test_public_apis.py`  
**Why:** Architecture pack review 2026-09-27 Critical #2 — a single `TBody` TypeVar for both `load_specification_body` and `load_implementation_body` collapses LinkML schema and DAMS instance into one type and breaks typed conformance checkers.

## Required shape

```python
class StandardProvider(Protocol, Generic[TSpecBody, TImplBody, TElement]):
    family: StandardFamily

    def load_specification_body(...) -> TSpecBody: ...
    def load_implementation_body(...) -> TImplBody: ...
```

`TSpecBody` and `TImplBody` must be distinct type parameters (not aliases of the same TypeVar).

## Test to land with the package

```python
from typing import get_type_hints

def test_standard_provider_has_distinct_body_types():
    """StandardProvider must not collapse specification body and
    implementation body into a single TypeVar — that was Critical #2
    in docs/architecture review 2026-09-27."""
    from moex_modeling.standards.public import StandardProvider  # adjust to real path

    hints = get_type_hints(StandardProvider.load_specification_body)
    impl_hints = get_type_hints(StandardProvider.load_implementation_body)
    assert hints["return"] is not impl_hints["return"], (
        "spec and implementation body types must differ per standard"
    )
```

Until `packages/modeling-kernel` exists, this file is the source of truth for the deferred test. Do not mark the vertical slice done without it.
