.PHONY: viewer viewer-check

PYTHON ?= python

viewer:
	$(PYTHON) -m pip install -e "./viewer[dev]"
	$(PYTHON) -m moex_publication_viewer.cli build --root .

viewer-check:
	$(PYTHON) -m pip install -e "./viewer[dev]"
	$(PYTHON) -m pytest viewer/tests -q
	$(PYTHON) -m moex_publication_viewer.cli check --root .
