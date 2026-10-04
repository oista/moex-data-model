.PHONY: viewer viewer-check viewer-serve packages-check architecture-check linkml-ingest-check vertical-slice-check check validate-schemas lint-schemas validate-examples validate-requirements generate-contracts generate-artifacts generate-bundle compare-golden api-check web-check web-e2e drawdb-up drawdb-adapter-check publish-gate

# Prefer Python 3.11+ (pyproject requires-python). Override: make PYTHON="py -3.14" …
# Default `python` on many Windows hosts is 3.10 and cannot install this package.
# CI pin: .python-version (3.12). LinkML pin: requirements-linkml.txt
PYTHON ?= python

# Windows ships `powershell`; Ubuntu GHA / Linux typically has `pwsh`.
ifeq ($(OS),Windows_NT)
  PWSH ?= powershell
else
  PWSH ?= pwsh
endif

VIEWER := apps/viewer
KERNEL := packages/modeling-kernel
OWL := packages/standard-owl
MAPPINGS := packages/semantic-mappings
CATALOG := packages/ontology-catalog
DRAWDB_ADAPTER := packages/drawdb-adapter
DAMS := packages/specification-dams

viewer:
	$(PYTHON) -m pip install -e "./$(VIEWER)[dev]"
	$(PYTHON) -m moex_publication_viewer.cli build --root .

viewer-check:
	$(PYTHON) -m pip install -e "./$(VIEWER)[dev]"
	$(PYTHON) -m pytest $(VIEWER)/tests -q
	$(PYTHON) -m moex_publication_viewer.cli check --root .

viewer-serve:
	$(PYTHON) -m pip install -e "./$(VIEWER)[dev]"
	$(PYTHON) -m moex_publication_viewer.cli serve --root . --port 8765

# Ontology stack pytest (outside Stage 0 make check; gated in GHA viewer-and-packages)
packages-check:
	$(PYTHON) -m pip install -e "./generated/contracts/moex-dams/0.1" -e "./$(KERNEL)" -e "./packages/standard-linkml" -e "./$(DAMS)" -e "./$(DRAWDB_ADAPTER)" -e "./$(OWL)" -e "./$(MAPPINGS)" -e "./$(CATALOG)" -e "./packages/linkml-tooling[map,automator]" pytest PyYAML
	$(PYTHON) -m pytest $(OWL)/tests $(MAPPINGS)/tests $(CATALOG)/tests $(DRAWDB_ADAPTER)/tests $(DAMS)/tests/test_dbml_projection.py packages/linkml-tooling/tests packages/modeling-kernel/tests/test_stage7_ports.py -q

drawdb-adapter-check:
	$(PYTHON) -m pip install -e "./generated/contracts/moex-dams/0.1" -e "./$(KERNEL)" -e "./packages/standard-linkml" -e "./$(DAMS)" -e "./$(DRAWDB_ADAPTER)[dev]" pytest
	$(PYTHON) -m pytest $(DRAWDB_ADAPTER)/tests $(DAMS)/tests/test_dbml_projection.py -q

# Local drawDB image (optional; not on Stage 0 PR gate)
drawdb-up:
	docker compose -f infra/compose/drawdb.yml up -d --build

architecture-check:
	$(PYTHON) -m pip install -e "./tools/architecture-check[dev]"
	$(PYTHON) -m pytest tools/architecture-check/tests -q
	$(PYTHON) -m architecture_check.cli --root .

# Uses package .venv (Python 3.11+). Without make:
#   powershell -NoProfile -File packages/standard-linkml/scripts/check.ps1
linkml-ingest-check:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File packages/standard-linkml/scripts/check.ps1

# First vertical slice: kernel → linkml provider → dams rules → publication JSON
# Without make:
#   powershell -NoProfile -File packages/publication/scripts/check.ps1
vertical-slice-check:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File packages/publication/scripts/check.ps1

# linkml-lint + validate trading-solution (uses apps/cli .venv when present)
validate-schemas:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/validate-schemas.ps1

lint-schemas: validate-schemas

validate-examples:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/validate-examples.ps1

validate-requirements:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/validate-requirements.ps1

# gen-pydantic → generated/contracts/moex-dams/0.1 (moex_dams_contracts)
generate-contracts:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/generate-contracts.ps1

# gen-owl / gen-shacl / gen-dbml / mermaid / python / doc / rdf → generated/artifacts
generate-artifacts:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/generate-artifacts.ps1

# Release bundle index (+ staged tree under generated/bundles/)
generate-bundle:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/build-release-bundle.ps1

publish-gate:
	$(PYTHON) -m moex_model_cli.gates.publish_gate

# Digest check: contracts + json-schema + Stage 6/7 artifact matrix + bundle vs regenerate
compare-golden:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/compare-golden.ps1

# Slice + CLI + architecture + schema lint/validate + path-layout guards.
# Without make:
#   powershell -NoProfile -File apps/cli/scripts/check.ps1
api-check:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File apps/api/scripts/check.ps1

web-check:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File apps/web/scripts/check.ps1

# Playwright Chromium smoke: Diagram page ↔ drawDB static-bridge postMessage
web-e2e:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File apps/web/scripts/e2e.ps1

# Stage 0 gate: contracts → slice tests → schemas → examples → golden
check:
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/generate-contracts.ps1
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File apps/cli/scripts/check.ps1
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/validate-schemas.ps1
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/validate-examples.ps1
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/validate-requirements.ps1
	$(PWSH) -NoProfile -ExecutionPolicy Bypass -File scripts/compare-golden.ps1
