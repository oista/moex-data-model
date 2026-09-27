"""Re-export selected ontology package tests against moex_standard_owl fixtures."""

# Ontology package keeps its own tests; this module confirms fibo CLI import path.
from moex_standard_owl.fibo.cli import main


def test_cli_main_importable():
    assert callable(main)
