"""DataStructure / SchemaNode / Message semantic checks (ADR-038…041)."""

from __future__ import annotations

from typing import Any

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)

RELATIONAL_SLOTS: frozenset[str] = frozenset(
    {
        "column_position",
        "is_primary_key",
        "is_unique",
        "foreign_key_target",
    }
)

MESSAGE_REFS_ALLOWED_KINDS: frozenset[str] = frozenset({"operation", "channel"})


def _diag(
    *,
    code: str,
    message: str,
    subject: str | None,
    remediation: str | None = None,
    requirement_code: str | None = None,
    invariant_id: str | None = None,
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
) -> Diagnostic:
    details: list[DiagnosticDetail] = [
        DiagnosticDetail(detail_key="finding", detail_value=message)
    ]
    if invariant_id:
        details.append(
            DiagnosticDetail(detail_key="invariant_id", detail_value=str(invariant_id))
        )
    if requirement_code:
        details.append(
            DiagnosticDetail(
                detail_key="requirement_code",
                detail_value=str(requirement_code),
            )
        )
    if remediation:
        details.append(
            DiagnosticDetail(
                detail_key="remediation",
                detail_value=str(remediation),
            )
        )
    parts = [message]
    if remediation:
        parts.append(f"Remediation: {remediation}")
    return Diagnostic(
        diagnostic_code=code,
        severity=severity,
        diagnostic_message=" ".join(parts),
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=tuple(details),
    )


def parse_structure_node_ref(ref: str) -> tuple[str, str] | None:
    """Parse ``structure_id#local_key``; return None if not that shape."""
    if not ref or "#" not in ref:
        return None
    sid, lk = ref.split("#", 1)
    if not sid or not lk:
        return None
    return sid, lk


def structure_node_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map ``structure_id#local_key`` → SchemaNode dict."""
    out: dict[str, dict[str, Any]] = {}
    for ds in data.get("data_structures") or []:
        if not isinstance(ds, dict):
            continue
        sid = str(ds.get("element_id") or "")
        if not sid:
            continue
        for node in ds.get("nodes") or []:
            if not isinstance(node, dict):
                continue
            lk = str(node.get("local_key") or "")
            if lk:
                out[f"{sid}#{lk}"] = node
    return out


def data_structure_ids(data: dict[str, Any]) -> set[str]:
    return {
        str(ds["element_id"])
        for ds in (data.get("data_structures") or [])
        if isinstance(ds, dict) and ds.get("element_id")
    }


def structures_by_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index DataStructure.element_id → structure dict."""
    out: dict[str, dict[str, Any]] = {}
    for s in data.get("data_structures") or []:
        if isinstance(s, dict) and s.get("element_id"):
            out[str(s["element_id"])] = s
    return out


def scalar_nodes_for_carrier(
    carrier: dict[str, Any],
    by_id: dict[str, dict[str, Any]] | None = None,
    *,
    data: dict[str, Any] | None = None,
) -> list[tuple[str, dict[str, Any]]]:
    """Return (structure_id#local_key, node) for scalar nodes of carrier.structure_ref."""
    index = by_id if by_id is not None else structures_by_id(data or {})
    sref = str(carrier.get("structure_ref") or "").strip()
    structure = index.get(sref)
    if not structure:
        return []
    out: list[tuple[str, dict[str, Any]]] = []
    for node in structure.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        if str(node.get("node_kind") or "") != "scalar":
            continue
        key = str(node.get("local_key") or "").strip()
        if not key:
            continue
        out.append((f"{sref}#{key}", node))
    return out


def _nodes_by_local_key(ds: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for node in ds.get("nodes") or []:
        if isinstance(node, dict) and node.get("local_key"):
            out[str(node["local_key"])] = node
    return out


def check_local_key_unique(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-022: local_key must be unique within each DataStructure.nodes (PDM-013)."""
    out: list[Diagnostic] = []
    for ds in data.get("data_structures") or []:
        if not isinstance(ds, dict):
            continue
        sid = str(ds.get("element_id") or ds.get("name") or "")
        seen: dict[str, int] = {}
        for node in ds.get("nodes") or []:
            if not isinstance(node, dict):
                continue
            lk = str(node.get("local_key") or "")
            if not lk:
                continue
            seen[lk] = seen.get(lk, 0) + 1
        for lk, count in seen.items():
            if count > 1:
                out.append(
                    _diag(
                        code="DAMS-REQ-PDM-013.c1",
                        invariant_id="INV-022",
                        message=(
                            f'DataStructure "{sid}" has duplicate local_key {lk!r} '
                            f"({count} nodes)."
                        ),
                        subject=f"{sid}#{lk}" if sid else lk,
                        remediation=(
                            "Ensure local_key is unique within DataStructure.nodes. INV-022."
                        ),
                        requirement_code="PDM-013",
                    )
                )
    return out


def check_node_edge_cycles(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-020: detect cycles via children / item_node edges (PDM-014)."""
    out: list[Diagnostic] = []
    for ds in data.get("data_structures") or []:
        if not isinstance(ds, dict):
            continue
        sid = str(ds.get("element_id") or ds.get("name") or "")
        by_key = _nodes_by_local_key(ds)

        def neighbors(lk: str) -> list[str]:
            node = by_key.get(lk)
            if not node:
                return []
            nbs: list[str] = []
            for child in node.get("children") or []:
                if child is not None and str(child):
                    nbs.append(str(child))
            item = node.get("item_node")
            if item is not None and str(item):
                nbs.append(str(item))
            return nbs

        visiting: set[str] = set()
        visited: set[str] = set()
        cycle_reported = False

        def dfs(lk: str) -> bool:
            nonlocal cycle_reported
            if lk in visiting:
                return True
            if lk in visited:
                return False
            visiting.add(lk)
            for nb in neighbors(lk):
                if dfs(nb):
                    return True
            visiting.remove(lk)
            visited.add(lk)
            return False

        for lk in by_key:
            if lk in visited:
                continue
            if dfs(lk) and not cycle_reported:
                cycle_reported = True
                out.append(
                    _diag(
                        code="DAMS-REQ-PDM-014.c1",
                        invariant_id="INV-020",
                        message=(
                            f'DataStructure "{sid}" has a cycle in children/item_node edges.'
                        ),
                        subject=sid or None,
                        remediation=(
                            "Remove cycles; use node_kind=reference for recursive schemas. "
                            "INV-020."
                        ),
                        requirement_code="PDM-014",
                    )
                )
    return out


def check_root_local_key(data: dict[str, Any]) -> list[Diagnostic]:
    """root_local_key must exist in nodes; root kind constrained by schema_format."""
    out: list[Diagnostic] = []
    for ds in data.get("data_structures") or []:
        if not isinstance(ds, dict):
            continue
        sid = str(ds.get("element_id") or ds.get("name") or "")
        root_lk = str(ds.get("root_local_key") or "")
        by_key = _nodes_by_local_key(ds)
        if not root_lk:
            continue
        if root_lk not in by_key:
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-015.c1",
                    message=(
                        f'DataStructure "{sid}" root_local_key {root_lk!r} '
                        "does not exist in nodes."
                    ),
                    subject=sid or None,
                    remediation="Point root_local_key at an existing node local_key.",
                    requirement_code="PDM-015",
                )
            )
            continue
        root = by_key[root_lk]
        kind = str(root.get("node_kind") or "")
        fmt = str(ds.get("schema_format") or "")
        if fmt == "relational":
            if kind != "object":
                out.append(
                    _diag(
                        code="DAMS-REQ-PDM-015.c2",
                        message=(
                            f'DataStructure "{sid}" with schema_format=relational '
                            f"requires root node_kind=object (got {kind!r})."
                        ),
                        subject=f"{sid}#{root_lk}" if sid else root_lk,
                        remediation="Set the root SchemaNode node_kind to object.",
                        requirement_code="PDM-015",
                    )
                )
        elif kind not in ("object", "array"):
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-015.c2",
                    message=(
                        f'DataStructure "{sid}" root node_kind must be object or array '
                        f"(got {kind!r})."
                    ),
                    subject=f"{sid}#{root_lk}" if sid else root_lk,
                    remediation="Use object or array as the structure root.",
                    requirement_code="PDM-015",
                )
            )
    return out


def check_relational_slots(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-021: relational node facets only when schema_format=relational (PDM-016)."""
    out: list[Diagnostic] = []
    for ds in data.get("data_structures") or []:
        if not isinstance(ds, dict):
            continue
        sid = str(ds.get("element_id") or ds.get("name") or "")
        fmt = str(ds.get("schema_format") or "")
        if fmt == "relational":
            continue
        for node in ds.get("nodes") or []:
            if not isinstance(node, dict):
                continue
            lk = str(node.get("local_key") or "")
            bad = [s for s in RELATIONAL_SLOTS if s in node]
            if bad:
                out.append(
                    _diag(
                        code="DAMS-REQ-PDM-016.c1",
                        invariant_id="INV-021",
                        message=(
                            f'SchemaNode "{sid}#{lk}" declares relational slots '
                            f"{', '.join(bad)} but DataStructure schema_format is {fmt!r}."
                        ),
                        subject=f"{sid}#{lk}" if sid and lk else (sid or lk or None),
                        remediation=(
                            "Remove relational slots or set schema_format=relational. "
                            "INV-021."
                        ),
                        requirement_code="PDM-016",
                    )
                )
    return out


def check_occurs_bounds(data: dict[str, Any]) -> list[Diagnostic]:
    """max_occurs >= min_occurs when both are set."""
    out: list[Diagnostic] = []
    for ds in data.get("data_structures") or []:
        if not isinstance(ds, dict):
            continue
        sid = str(ds.get("element_id") or ds.get("name") or "")
        for node in ds.get("nodes") or []:
            if not isinstance(node, dict):
                continue
            if node.get("min_occurs") is None or node.get("max_occurs") is None:
                continue
            try:
                mn = int(node["min_occurs"])
                mx = int(node["max_occurs"])
            except (TypeError, ValueError):
                continue
            if mx < mn:
                lk = str(node.get("local_key") or "")
                out.append(
                    _diag(
                        code="DAMS-REQ-PDM-017.c1",
                        message=(
                            f'SchemaNode "{sid}#{lk}" has max_occurs={mx} < min_occurs={mn}.'
                        ),
                        subject=f"{sid}#{lk}" if sid and lk else (sid or lk or None),
                        remediation="Ensure max_occurs >= min_occurs.",
                        requirement_code="PDM-017",
                    )
                )
    return out


def check_node_kind_shape(data: dict[str, Any]) -> list[Diagnostic]:
    """array|map need item_node without children; scalar|enum forbid both."""
    out: list[Diagnostic] = []
    for ds in data.get("data_structures") or []:
        if not isinstance(ds, dict):
            continue
        sid = str(ds.get("element_id") or ds.get("name") or "")
        for node in ds.get("nodes") or []:
            if not isinstance(node, dict):
                continue
            lk = str(node.get("local_key") or "")
            subject = f"{sid}#{lk}" if sid and lk else (sid or lk or None)
            kind = str(node.get("node_kind") or "")
            children = node.get("children") or []
            item = node.get("item_node")
            has_children = bool(children)
            has_item = item is not None and str(item).strip() != ""

            if kind in ("array", "map"):
                if not has_item:
                    out.append(
                        _diag(
                            code="DAMS-REQ-PDM-020.c1",
                            invariant_id="INV-012",
                            message=(
                                f'SchemaNode "{subject}" with node_kind={kind} '
                                "requires item_node."
                            ),
                            subject=subject,
                            remediation=(
                                "Set item_node to the element/value node local_key. INV-012."
                            ),
                            requirement_code="PDM-020",
                        )
                    )
                if has_children:
                    out.append(
                        _diag(
                            code="DAMS-REQ-PDM-020.c2",
                            invariant_id="INV-012",
                            message=(
                                f'SchemaNode "{subject}" with node_kind={kind} '
                                "must not declare children."
                            ),
                            subject=subject,
                            remediation=(
                                "Remove children; use item_node for array/map. INV-012."
                            ),
                            requirement_code="PDM-020",
                        )
                    )
            elif kind in ("scalar", "enum"):
                if has_children:
                    out.append(
                        _diag(
                            code="DAMS-REQ-PDM-020.c3",
                            invariant_id="INV-013",
                            message=(
                                f'SchemaNode "{subject}" with node_kind={kind} '
                                "must not declare children."
                            ),
                            subject=subject,
                            remediation="Remove children from scalar/enum nodes. INV-013.",
                            requirement_code="PDM-020",
                        )
                    )
                if has_item:
                    out.append(
                        _diag(
                            code="DAMS-REQ-PDM-020.c4",
                            invariant_id="INV-013",
                            message=(
                                f'SchemaNode "{subject}" with node_kind={kind} '
                                "must not declare item_node."
                            ),
                            subject=subject,
                            remediation="Remove item_node from scalar/enum nodes. INV-013.",
                            requirement_code="PDM-020",
                        )
                    )
    return out


def check_field_mapping_structure_ends(data: dict[str, Any]) -> list[Diagnostic]:
    """field_mapping ends: LogicalAttribute + structure_id#local_key that resolves."""
    attr_ids: set[str] = set()
    for e in data.get("logical_entities") or []:
        if not isinstance(e, dict):
            continue
        for a in e.get("attributes") or []:
            if isinstance(a, dict) and a.get("element_id"):
                attr_ids.add(str(a["element_id"]))
    node_index = structure_node_index(data)

    out: list[Diagnostic] = []
    for m in data.get("mappings") or []:
        if not isinstance(m, dict):
            continue
        if str(m.get("mapping_type") or "") != "field_mapping":
            continue
        mid = str(m.get("element_id") or m.get("name") or "")
        refs = [str(x) for x in (m.get("source_refs") or []) + (m.get("target_refs") or [])]
        has_attr = any(r in attr_ids for r in refs)
        structure_refs = [r for r in refs if parse_structure_node_ref(r) is not None]
        unresolved = [r for r in structure_refs if r not in node_index]
        has_resolved_node = any(r in node_index for r in structure_refs)

        if unresolved:
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-009.c3",
                    message=(
                        f'Mapping "{mid}" field_mapping references missing SchemaNode '
                        f"end(s): {', '.join(unresolved)}."
                    ),
                    subject=mid or None,
                    remediation=(
                        "Use structure_id#local_key that exists in data_structures.nodes."
                    ),
                    requirement_code="PDM-009",
                )
            )
        elif not (has_attr and has_resolved_node):
            # Pairing failure without unresolved refs is handled by technical_assets PDM-009.c2
            pass
    return out


def check_source_pointer_requires_artifact(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-010: source_pointer only meaningful inside source_artifact_ref (slot text).

    Example error::

        DataStructure \"dams:structure/x\": source_pointer задан без source_artifact_ref.
        Remediation: Задайте source_artifact_ref или удалите source_pointer. INV-010.
    """
    out: list[Diagnostic] = []
    for ds in data.get("data_structures") or []:
        if not isinstance(ds, dict):
            continue
        sid = str(ds.get("element_id") or ds.get("name") or "")
        pointer = ds.get("source_pointer")
        if pointer is None or not str(pointer).strip():
            continue
        artifact = ds.get("source_artifact_ref")
        if artifact is None or not str(artifact).strip():
            out.append(
                _diag(
                    code="DAMS-INV-010",
                    invariant_id="INV-010",
                    message=(
                        f'DataStructure "{sid}": source_pointer задан без '
                        "source_artifact_ref (слот: указатель внутри артефакта)."
                    ),
                    subject=sid or None,
                    remediation=(
                        "Задайте source_artifact_ref на документ-источник или удалите "
                        "source_pointer. INV-010."
                    ),
                )
            )
    return out


def check_schema_dialect_format_family(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-011: schema_dialect only when schema_format is json_schema|openapi_schema.

    Does **not** extend the rule to AsyncAPI Multi Format Schema — divergence from
    ADR-038 remains an open question (ADR-045 / C3 report). L2 mirrors the existing
    LinkML rule.

    Example error::

        DataStructure \"dams:structure/x\": schema_dialect задан при schema_format=avro.
        Remediation: Удалите schema_dialect или смените schema_format на json_schema /
        openapi_schema. INV-011.
    """
    allowed = frozenset({"json_schema", "openapi_schema"})
    out: list[Diagnostic] = []
    for ds in data.get("data_structures") or []:
        if not isinstance(ds, dict):
            continue
        dialect = ds.get("schema_dialect")
        if dialect is None or not str(dialect).strip():
            continue
        sid = str(ds.get("element_id") or ds.get("name") or "")
        fmt = str(ds.get("schema_format") or "")
        if fmt not in allowed:
            out.append(
                _diag(
                    code="DAMS-INV-011",
                    invariant_id="INV-011",
                    message=(
                        f'DataStructure "{sid}": schema_dialect задан при '
                        f"schema_format={fmt!r} (допустимо только json_schema|"
                        "openapi_schema по правилу схемы)."
                    ),
                    subject=sid or None,
                    remediation=(
                        "Удалите schema_dialect или смените schema_format на "
                        "json_schema / openapi_schema. INV-011 "
                        "(расхождение с AsyncAPI в ADR-038 — см. ADR-045)."
                    ),
                )
            )
    return out


def check_reference_node_target(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-014: node_kind=reference requires reference_target (slot text).

    Example error::

        SchemaNode \"dams:structure/x#ref\": node_kind=reference без reference_target.
        Remediation: Задайте reference_target (CURIE/URI цели). INV-014.
    """
    out: list[Diagnostic] = []
    for ds in data.get("data_structures") or []:
        if not isinstance(ds, dict):
            continue
        sid = str(ds.get("element_id") or ds.get("name") or "")
        for node in ds.get("nodes") or []:
            if not isinstance(node, dict):
                continue
            if str(node.get("node_kind") or "") != "reference":
                continue
            lk = str(node.get("local_key") or "")
            subject = f"{sid}#{lk}" if sid and lk else (sid or lk or None)
            target = node.get("reference_target")
            if target is None or not str(target).strip():
                out.append(
                    _diag(
                        code="DAMS-INV-014",
                        invariant_id="INV-014",
                        message=(
                            f'SchemaNode "{subject}": node_kind=reference без '
                            "reference_target (слот: цель ссылки)."
                        ),
                        subject=subject,
                        remediation=(
                            "Задайте reference_target на DataStructure или узел "
                            "(uriorcurie). INV-014."
                        ),
                    )
                )
    return out


def check_message_refs_kinds(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-019 / INV-017 (message_refs): only operation|channel; forbidden on interface.

    Source for interface ban of message_refs: ADR-040 / PDM-018. Other operation
    fields on interface remain L1-only (source partial beyond message_refs).
    """
    out: list[Diagnostic] = []
    for el in data.get("access_points") or []:
        if not isinstance(el, dict):
            continue
        refs = el.get("message_refs") or []
        if not refs:
            continue
        sid = str(el.get("element_id") or el.get("name") or "")
        kind = str(el.get("asset_kind") or "")
        if kind == "interface":
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-018.c1",
                    invariant_id="INV-017",
                    message=(
                        f'AccessPoint "{sid}" with asset_kind=interface must not declare '
                        "message_refs."
                    ),
                    subject=sid or None,
                    remediation="Put message_refs on operation or channel AccessPoints. INV-017.",
                    requirement_code="PDM-018",
                )
            )
        elif kind and kind not in MESSAGE_REFS_ALLOWED_KINDS:
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-018.c2",
                    invariant_id="INV-019",
                    message=(
                        f'AccessPoint "{sid}" with asset_kind={kind!r} must not declare '
                        "message_refs."
                    ),
                    subject=sid or None,
                    remediation=(
                        "message_refs is only for asset_kind operation or channel. INV-019."
                    ),
                    requirement_code="PDM-018",
                )
            )
    return out


def check_message_payload(data: dict[str, Any]) -> list[Diagnostic]:
    """Message requires payload_structure_ref pointing to an existing DataStructure."""
    known = data_structure_ids(data)
    out: list[Diagnostic] = []
    for msg in data.get("messages") or []:
        if not isinstance(msg, dict):
            continue
        mid = str(msg.get("element_id") or msg.get("name") or "")
        pref = msg.get("payload_structure_ref")
        if pref is None or not str(pref).strip():
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-019.c1",
                    message=f'Message "{mid}" requires payload_structure_ref.',
                    subject=mid or None,
                    remediation="Set payload_structure_ref to a DataStructure element_id.",
                    requirement_code="PDM-019",
                )
            )
            continue
        pref_s = str(pref)
        if pref_s not in known:
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-019.c2",
                    message=(
                        f'Message "{mid}" payload_structure_ref {pref_s!r} '
                        "does not resolve to a DataStructure in this package."
                    ),
                    subject=mid or None,
                    remediation="Point payload_structure_ref at an existing data_structures id.",
                    requirement_code="PDM-019",
                )
            )
        href = msg.get("headers_structure_ref")
        if href is not None and str(href).strip() and str(href) not in known:
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-019.c3",
                    message=(
                        f'Message "{mid}" headers_structure_ref {href!r} '
                        "does not resolve to a DataStructure in this package."
                    ),
                    subject=mid or None,
                    remediation="Point headers_structure_ref at an existing data_structures id.",
                    requirement_code="PDM-019",
                )
            )
    return out


def check_data_structures(data: dict[str, Any]) -> tuple[Diagnostic, ...]:
    """Run all DataStructure / SchemaNode / Message semantic checks."""
    diags: list[Diagnostic] = []
    diags.extend(check_local_key_unique(data))
    diags.extend(check_node_edge_cycles(data))
    diags.extend(check_root_local_key(data))
    diags.extend(check_relational_slots(data))
    diags.extend(check_occurs_bounds(data))
    diags.extend(check_node_kind_shape(data))
    diags.extend(check_source_pointer_requires_artifact(data))
    diags.extend(check_schema_dialect_format_family(data))
    diags.extend(check_reference_node_target(data))
    diags.extend(check_field_mapping_structure_ends(data))
    diags.extend(check_message_refs_kinds(data))
    diags.extend(check_message_payload(data))
    return tuple(diags)
