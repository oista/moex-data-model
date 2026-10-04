from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from moex_model_cli.bootstrap import SlicePaths
from moex_model_cli.commands.import_solution import run_import_solution

ROOT = Path(__file__).resolve().parents[1]
XLSX = Path(
    r"F:\!PASSPORT\!H_DATASC\!Data Architecture\MOEX_DataModel"
    r"\MOEX Data Model Standart\solution_src\src_soluitions_model.xlsx"
)
SYSTEMS = sys.argv[1:] or ["MDM", "UCD", "CRM", "ЕСЭД"]

paths = SlicePaths.resolve(root=ROOT)
for system in SYSTEMS:
    code, text = run_import_solution(paths, xlsx=XLSX, system=system, force=True)
    print(f"=== {system} exit={code} ===")
    for line in text.splitlines():
        if (
            line.startswith("SXI+")
            or line.startswith("assess")
            or line.startswith("export")
            or "[ERROR]" in line
        ):
            print(line)
