.PHONY: viewer viewer-check architecture-check

# Prefer Python 3.11+ (pyproject requires-python). Override: make PYTHON=py -3.14 architecture-check
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
