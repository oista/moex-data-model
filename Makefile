.PHONY: viewer viewer-check architecture-check linkml-ingest-check vertical-slice-check check validate-schemas lint-schemas validate-examples generate-contracts compare-golden api-check web-check

# Prefer Python 3.11+ (pyproject requires-python). Override: make PYTHON="py -3.14" …
# Default `python` on many Windows hosts is 3.10 and cannot install this package.
# CI pin: .python-version (3.12). LinkML pin: requirements-linkml.txt
PYTHON ?= python

VIEWER := apps/viewer

viewer:
	$(PYTHON) -m pip install -e "./$(VIEWER)[dev]"
	$(PYTHON) -m moex_publication_viewer.cli build --root .

viewer-check:
	$(PYTHON) -m pip install -e "./$(VIEWER)[dev]"
	$(PYTHON) -m pytest $(VIEWER)/tests -q
	$(PYTHON) -m moex_publication_viewer.cli check --root .

architecture-check:
	$(PYTHON) -m pip install -e "./tools/architecture-check[dev]"
	$(PYTHON) -m pytest tools/architecture-check/tests -q
	$(PYTHON) -m architecture_check.cli --root .

# Uses package .venv (Python 3.11+). Without make:
#   powershell -NoProfile -File packages/standard-linkml/scripts/check.ps1
linkml-ingest-check:
	powershell -NoProfile -ExecutionPolicy Bypass -File packages/standard-linkml/scripts/check.ps1

# First vertical slice: kernel → linkml provider → dams rules → publication JSON
# Without make:
#   powershell -NoProfile -File packages/publication/scripts/check.ps1
vertical-slice-check:
	powershell -NoProfile -ExecutionPolicy Bypass -File packages/publication/scripts/check.ps1

# linkml-lint + validate trading-solution (uses apps/cli .venv when present)
validate-schemas:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-schemas.ps1

lint-schemas: validate-schemas

validate-examples:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-examples.ps1

# gen-pydantic → generated/contracts/moex-dams/0.1 (moex_dams_contracts)
generate-contracts:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/generate-contracts.ps1

# Digest check: committed contracts (+ json-schema if present) vs regenerate
compare-golden:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/compare-golden.ps1

# Slice + CLI + architecture + schema lint/validate + path-layout guards.
# Without make:
#   powershell -NoProfile -File apps/cli/scripts/check.ps1
api-check:
	powershell -NoProfile -ExecutionPolicy Bypass -File apps/api/scripts/check.ps1

web-check:
	powershell -NoProfile -ExecutionPolicy Bypass -File apps/web/scripts/check.ps1

# Stage 0 gate: contracts → slice tests → schemas → examples → golden
check:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/generate-contracts.ps1
	powershell -NoProfile -ExecutionPolicy Bypass -File apps/cli/scripts/check.ps1
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-schemas.ps1
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-examples.ps1
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/compare-golden.ps1
