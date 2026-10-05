"""Write ER layout.json files matching the three reference screenshots."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write_layout(path: Path, profile: str, nodes: dict, edges: dict | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "profile": profile,
        "nodes": nodes,
        "edges": edges or {},
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("wrote", path.relative_to(ROOT))


# --- MDM: diamond PERSON / link tables / ENTERPRISE ---
# PERSON ~12 rows (~310px), links ~2 rows (~90px), ENTERPRISE ~26 rows.
# Keep a clear vertical band for the junction tables between the two hubs.
mdm_nodes = {
    "dams:logical/mdm/PERSON": {"x": 310, "y": 40, "color": "#2b3a4a"},
    "dams:logical/mdm/PERSON_CEO": {"x": 20, "y": 400, "color": "#2b3a4a"},
    "dams:logical/mdm/PERSON_REPRESENTATIVE": {"x": 800, "y": 400, "color": "#2b3a4a"},
    "dams:logical/mdm/ENTERPRISE": {"x": 310, "y": 620, "color": "#2b3a4a"},
}
mdm_edges = {
    "dams:rel/mdm/PERSON_CEO_to_PERSON_via_PERSON_ID": {
        "points": [{"x": 280, "y": 370}]
    },
    "dams:rel/mdm/PERSON_REPRESENTATIVE_to_PERSON_via_PERSON_ID": {
        "points": [{"x": 760, "y": 370}]
    },
    "dams:rel/mdm/PERSON_CEO_to_ENTERPRISE_via_ENTERPRISE_ID": {
        "points": [{"x": 260, "y": 580}]
    },
    "dams:rel/mdm/PERSON_REPRESENTATIVE_to_ENTERPRISE_via_ENTERPRISE_ID": {
        "points": [{"x": 780, "y": 580}]
    },
}
write_layout(
    ROOT
    / "model-assets/implementations/solutions/mdm/publications/logical.layout.json",
    "logical",
    mdm_nodes,
    mdm_edges,
)

# --- CRM: Contact TL, Lead TR, Customer bottom center ---
crm_nodes = {
    "dams:logical/crm/CONTACT": {"x": 40, "y": 40, "color": "#1e2a3a"},
    "dams:logical/crm/LEAD": {"x": 580, "y": 40, "color": "#1e2a3a"},
    "dams:logical/crm/CUSTOMER": {"x": 200, "y": 560, "color": "#1e2a3a"},
}
crm_edges = {
    "dams:rel/crm/LEAD_to_CONTACT_via_MoexContact": {
        "points": [{"x": 500, "y": 180}]
    },
    "dams:rel/crm/CONTACT_to_CUSTOMER_via_Account": {
        "points": [{"x": 220, "y": 520}]
    },
    "dams:rel/crm/CUSTOMER_to_CONTACT_via_PrimaryContact": {
        "points": [{"x": 300, "y": 520}]
    },
    "dams:rel/crm/LEAD_to_CUSTOMER_via_MoexAccount": {
        "points": [{"x": 540, "y": 520}]
    },
    "dams:rel/crm/CUSTOMER_to_CUSTOMER_via_PrimaryAccount": {
        "points": [{"x": 160, "y": 760}]
    },
}
write_layout(
    ROOT
    / "model-assets/implementations/solutions/crm/publications/logical.layout.json",
    "logical",
    crm_nodes,
    crm_edges,
)

# Physical CRM mirrors the same visual arrangement (different element ids).
crm_phys_nodes = {
    "dams:physical/crm/phys_CONTACT": {"x": 40, "y": 40, "color": "#1e2a3a"},
    "dams:physical/crm/phys_LEAD": {"x": 580, "y": 40, "color": "#1e2a3a"},
    "dams:physical/crm/ACCOUNT": {"x": 200, "y": 560, "color": "#1e2a3a"},
}
write_layout(
    ROOT
    / "model-assets/implementations/solutions/crm/publications/physical.layout.json",
    "physical",
    crm_phys_nodes,
    {},
)

# --- ESED: hub-and-spoke around document ---
esed_nodes = {
    "dams:logical/esed/file_binary": {"x": 20, "y": 40, "color": "#243044"},
    "dams:logical/esed/employee": {"x": 300, "y": 40, "color": "#243044"},
    "dams:logical/esed/division": {"x": 300, "y": 260, "color": "#243044"},
    "dams:logical/esed/file": {"x": 20, "y": 320, "color": "#243044"},
    "dams:logical/esed/document": {"x": 560, "y": 160, "color": "#243044"},
    "dams:logical/esed/organization": {"x": 1060, "y": 40, "color": "#243044"},
    "dams:logical/esed/organization_employee": {
        "x": 1060,
        "y": 320,
        "color": "#243044",
    },
    "dams:logical/esed/common_type": {"x": 1060, "y": 500, "color": "#243044"},
    "dams:logical/esed/common_state": {"x": 1060, "y": 620, "color": "#243044"},
    "dams:logical/esed/instance": {"x": 280, "y": 520, "color": "#243044"},
    "dams:logical/esed/attorney_check_info": {
        "x": 20,
        "y": 720,
        "color": "#243044",
    },
    "dams:logical/esed/universal_item": {"x": 600, "y": 860, "color": "#243044"},
}
esed_edges = {
    # Prefer a distinct bend for the document↔instance link (solid blue on screenshot).
    "dams:rel/esed/document_to_instance_via_document_id": {
        "points": [{"x": 500, "y": 560}]
    },
}
write_layout(
    ROOT
    / "model-assets/implementations/solutions/esed/publications/logical.layout.json",
    "logical",
    esed_nodes,
    esed_edges,
)

# Physical ESED: same geometry, physical element ids from scene.
esed_phys_nodes = {
    "dams:physical/esed/dvsys_binaries": {"x": 20, "y": 40, "color": "#243044"},
    "dams:physical/esed/RefStaff_Employees": {"x": 300, "y": 40, "color": "#243044"},
    "dams:physical/esed/RefStaff_Units": {"x": 300, "y": 260, "color": "#243044"},
    "dams:physical/esed/dvsys_files": {"x": 20, "y": 320, "color": "#243044"},
    "dams:physical/esed/dvsys_instances_date": {
        "x": 560,
        "y": 160,
        "color": "#243044",
    },
    "dams:physical/esed/RefPartners_Companies": {
        "x": 1060,
        "y": 40,
        "color": "#243044",
    },
    "dams:physical/esed/RefPartners_Employees": {
        "x": 1060,
        "y": 320,
        "color": "#243044",
    },
    "dams:physical/esed/RefKinds_CardKinds": {
        "x": 1060,
        "y": 500,
        "color": "#243044",
    },
    "dams:physical/esed/RefStates_States": {
        "x": 1060,
        "y": 620,
        "color": "#243044",
    },
    "dams:physical/esed/dvsys_instances": {"x": 280, "y": 520, "color": "#243044"},
    "dams:physical/esed/CardDocument_ExternalPoaInfo": {
        "x": 20,
        "y": 720,
        "color": "#243044",
    },
    "dams:physical/esed/RefBaseUniversal_Items": {
        "x": 600,
        "y": 860,
        "color": "#243044",
    },
}
write_layout(
    ROOT
    / "model-assets/implementations/solutions/esed/publications/physical.layout.json",
    "physical",
    esed_phys_nodes,
    {},
)

# MDM physical mirror of the diamond (views / ref tables).
mdm_phys_nodes = {
    "dams:physical/mdm/INTERNALDM_MDM_V_PERSON": {
        "x": 310,
        "y": 40,
        "color": "#2b3a4a",
    },
    "dams:physical/mdm/MOSCOW_EXCHANGE_T_REF_CEO": {
        "x": 20,
        "y": 400,
        "color": "#2b3a4a",
    },
    "dams:physical/mdm/MOSCOW_EXCHANGE_T_REF_REPRESENTATIVE": {
        "x": 800,
        "y": 400,
        "color": "#2b3a4a",
    },
    "dams:physical/mdm/INTERNALDM_MDM_V_ENTERPRISE": {
        "x": 310,
        "y": 620,
        "color": "#2b3a4a",
    },
}
write_layout(
    ROOT
    / "model-assets/implementations/solutions/mdm/publications/physical.layout.json",
    "physical",
    mdm_phys_nodes,
    {},
)

print("done")
