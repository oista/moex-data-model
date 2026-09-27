"""ER-dictionary ingest: XLS/CSV → DAMS ModelPackage."""

from moex_standard_linkml.ingest.envelope import build_envelope
from moex_standard_linkml.ingest.mapper import map_er_dictionary
from moex_standard_linkml.ingest.profile import IngestProfile, load_profile
from moex_standard_linkml.ingest.validate import validate_model_package
from moex_standard_linkml.ingest.workbook import load_workbook_tables

__all__ = [
    "IngestProfile",
    "build_envelope",
    "load_profile",
    "load_workbook_tables",
    "map_er_dictionary",
    "validate_model_package",
]
