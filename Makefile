.PHONY: viewer viewer-check architecture-check linkml-ingest-check

# Prefer Python 3.11+ (pyproject requires-python). Override: make PYTHON="py -3.14" …
# Default `python` on many Windows hosts is 3.10 and cannot install this package.
PYTHON ?= python

viewer:
	$(PYTHON) -m pip install -e "./viewer[dev]"
	$(PYTHON) -m moex_publication_viewer.cli build --root .

viewer-check:
	$(PYTHON) -m pip install -e "./viewer[dev]"
	$(PYTHON) -m pytest viewer/tests -q
	$(PYTHON) -m moex_publication_viewer.cli check --root .

architecture-check:
	$(PYTHON) -m pip install -e "./tools/architecture-check[dev]"
	$(PYTHON) -m pytest tools/architecture-check/tests -q
	$(PYTHON) -m architecture_check.cli --root .

# Uses package .venv (Python 3.11+). Without make:
#   powershell -NoProfile -File packages/standard-linkml/scripts/check.ps1
linkml-ingest-check:
	powershell -NoProfile -ExecutionPolicy Bypass -File packages/standard-linkml/scripts/check.ps1
