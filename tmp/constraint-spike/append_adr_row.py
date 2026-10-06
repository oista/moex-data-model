"""Byte-level append of the ADR-045 row to docs/adr/README.md (file has mixed encodings: do not re-save)."""
from pathlib import Path

p = Path(__file__).resolve().parents[2] / "docs" / "adr" / "README.md"
raw = p.read_bytes()
eol = b"\r\n" if b"\r\n" in raw else b"\n"
row = (
    b"| [ADR-045](ADR-045-executable-constraint-matrix.md) | Executable constraint matrix (L1 rules / L2 validators / L3 SHACL) "
    b"| Proposed; P0 invariants; INV-xxx; check-constraints |"
)
if b"ADR-045" in raw:
    raise SystemExit("ADR-045 row already present")
if not raw.endswith(eol):
    raw += eol
p.write_bytes(raw + row + eol)
print("eol", eol, "appended", len(row), "bytes")
