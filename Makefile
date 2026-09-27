.PHONY: viewer viewer-check architecture-check linkml-ingest-check vertical-slice-check check validate-schemas

# Prefer Python 3.11+ (pyproject requires-python). Override: make PYTHON="py -3.14" …
# Default `python` on many Windows hosts is 3.10 and cannot install this package.
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

# Slice + CLI + architecture + schema lint/validate + path-layout guards.
# Without make:
#   powershell -NoProfile -File apps/cli/scripts/check.ps1
check:
	powershell -NoProfile -ExecutionPolicy Bypass -File apps/cli/scripts/check.ps1
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate-schemas.ps1
