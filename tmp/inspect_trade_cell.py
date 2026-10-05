from pathlib import Path

p = Path(
    r"f:\!PASSPORT\!H_DATASC\!Data Architecture\MOEX_DataModel"
    r"\MOEX Data Model Standart\enterpise_cdm_src\CModel_content04.drawio"
)
raw = p.read_text(encoding="utf-8")
idx = raw.find("Сделки ТКС")
print("count", raw.count("Сделки ТКС"))
print("idx", idx)
print(raw[max(0, idx - 500) : idx + 900])
print("---")
print("shape=table count", raw.count("shape=table"))
print("entity_id Trade cell from inventory: mXX1lFB-GyiXgtXh9Rfv-2")
idx2 = raw.find("mXX1lFB-GyiXgtXh9Rfv-2")
print("id idx", idx2)
print(raw[idx2 : idx2 + 1200] if idx2 >= 0 else "not found")
