# generate-artifacts (OWL / SHACL / DBML / Mermaid goldens)
make generate-artifacts
moex-model compile --root . --artifacts

# html
cd c:\Users\bons1\IdeaProjects\moex-data-model
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-viewer.ps1

# semantic-diff
moex-model semantic-diff --left a.yaml --right b.yaml --json

# diagram (ModelPackage → DBML)
moex-model diagram --root . --profile logical --out generated/artifacts/diagrams/trading-logical.dbml

# import (ER-dictionary → ModelPackage)
moex-model import --workbook packages/standard-linkml/tests/fixtures/er-dictionary --profile packages/standard-linkml/tests/fixtures/er-dictionary/profile.yaml --out generated/import-pilot --skip-validate

# map (SSSOM / LinkML extract)
moex-model map --sssom model-assets/transformations/mappings/dams-fibo.sssom.yaml
moex-model map --extract-schema packages/semantic-mappings/tests/fixtures/mapped_schema.yaml --json
