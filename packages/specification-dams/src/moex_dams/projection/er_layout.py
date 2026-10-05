"""Seed / merge ER diagram layout files (positions + colors; not generated digests)."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any, Literal

from moex_dams.projection.dbml import HEADER_COLORS

Profile = Literal["logical", "physical", "conceptual"]

LAYOUT_VERSION = 1
COL_WIDTH = 360
ROW_HEIGHT = 280
ORIGIN_X = 40
ORIGIN_Y = 40


def node_key(node: dict[str, Any]) -> str:
    """Stable layout key: prefer element_id, else table name."""
    eid = str(node.get("element_id") or "").strip()
    if eid:
        return eid
    return str(node.get("name") or "")


def edge_key(edge: dict[str, Any]) -> str:
    eid = str(edge.get("element_id") or edge.get("id") or "").strip()
    return eid


def seed_layout(
    scene: dict[str, Any],
    *,
    profile: Profile,
) -> dict[str, Any]:
    """Deterministic BFS layered grid layout from scene nodes/edges."""
    nodes = [n for n in (scene.get("nodes") or []) if isinstance(n, dict)]
    edges = [e for e in (scene.get("edges") or []) if isinstance(e, dict)]
    name_to_key: dict[str, str] = {}
    keys: list[str] = []
    for node in nodes:
        key = node_key(node)
        if not key:
            continue
        keys.append(key)
        name_to_key[str(node.get("name") or "")] = key

    adj: dict[str, list[str]] = {k: [] for k in keys}
    indeg: dict[str, int] = {k: 0 for k in keys}
    for edge in edges:
        src = name_to_key.get(str(edge.get("source") or ""))
        tgt = name_to_key.get(str(edge.get("target") or ""))
        if not src or not tgt or src == tgt:
            continue
        adj[src].append(tgt)
        indeg[tgt] = indeg.get(tgt, 0) + 1

    roots = [k for k in keys if indeg.get(k, 0) == 0]
    if not roots and keys:
        roots = [keys[0]]

    layer_of: dict[str, int] = {}
    queue: deque[str] = deque()
    for r in roots:
        layer_of[r] = 0
        queue.append(r)
    while queue:
        cur = queue.popleft()
        for nxt in adj.get(cur, []):
            cand = layer_of[cur] + 1
            if nxt not in layer_of or cand < layer_of[nxt]:
                layer_of[nxt] = cand
                queue.append(nxt)
    for k in keys:
        layer_of.setdefault(k, 0)

    by_layer: dict[int, list[str]] = {}
    for k in keys:
        by_layer.setdefault(layer_of[k], []).append(k)
    for layer in by_layer:
        by_layer[layer].sort()

    default_color = HEADER_COLORS.get(profile, "#4285F4")
    layout_nodes: dict[str, dict[str, Any]] = {}
    for layer, layer_keys in sorted(by_layer.items()):
        for row, key in enumerate(layer_keys):
            layout_nodes[key] = {
                "x": ORIGIN_X + layer * COL_WIDTH,
                "y": ORIGIN_Y + row * ROW_HEIGHT,
                "color": default_color,
            }

    return {
        "version": LAYOUT_VERSION,
        "profile": profile,
        "nodes": layout_nodes,
        "edges": {},
    }


def merge_layout(
    existing: dict[str, Any],
    scene: dict[str, Any],
    *,
    profile: Profile,
) -> dict[str, Any]:
    """Keep known positions; add missing nodes; drop removed; keep edge bends."""
    seed = seed_layout(scene, profile=profile)
    old_nodes = existing.get("nodes") if isinstance(existing.get("nodes"), dict) else {}
    old_edges = existing.get("edges") if isinstance(existing.get("edges"), dict) else {}
    new_nodes: dict[str, Any] = {}
    occupied: set[tuple[int, int]] = set()

    for key, pos in old_nodes.items():
        if key not in seed["nodes"]:
            continue
        if not isinstance(pos, dict):
            continue
        x = int(pos.get("x", seed["nodes"][key]["x"]))
        y = int(pos.get("y", seed["nodes"][key]["y"]))
        entry: dict[str, Any] = {"x": x, "y": y}
        color = pos.get("color") or seed["nodes"][key].get("color")
        if color:
            entry["color"] = color
        new_nodes[key] = entry
        occupied.add((x // COL_WIDTH, y // ROW_HEIGHT))

    for key, pos in seed["nodes"].items():
        if key in new_nodes:
            continue
        x, y = int(pos["x"]), int(pos["y"])
        cell = (x // COL_WIDTH, y // ROW_HEIGHT)
        while cell in occupied:
            cell = (cell[0], cell[1] + 1)
        occupied.add(cell)
        new_nodes[key] = {
            "x": ORIGIN_X + cell[0] * COL_WIDTH,
            "y": ORIGIN_Y + cell[1] * ROW_HEIGHT,
            "color": pos.get("color"),
        }

    valid_edge_ids = {edge_key(e) for e in (scene.get("edges") or []) if edge_key(e)}
    new_edges: dict[str, Any] = {}
    for eid, payload in old_edges.items():
        if eid in valid_edge_ids and isinstance(payload, dict):
            new_edges[eid] = payload

    return {
        "version": LAYOUT_VERSION,
        "profile": profile,
        "nodes": new_nodes,
        "edges": new_edges,
    }


def validate_layout(layout: dict[str, Any]) -> list[str]:
    """Return validation errors (empty = ok)."""
    errors: list[str] = []
    if not isinstance(layout, dict):
        return ["layout must be an object"]
    version = layout.get("version")
    if version != LAYOUT_VERSION:
        errors.append(f"unsupported layout version: {version!r}")
    nodes = layout.get("nodes")
    if nodes is None:
        errors.append("missing nodes")
    elif not isinstance(nodes, dict):
        errors.append("nodes must be an object")
    else:
        for key, pos in nodes.items():
            if not isinstance(pos, dict):
                errors.append(f"nodes[{key}] must be an object")
                continue
            if "x" not in pos or "y" not in pos:
                errors.append(f"nodes[{key}] requires x and y")
            else:
                try:
                    float(pos["x"])
                    float(pos["y"])
                except (TypeError, ValueError):
                    errors.append(f"nodes[{key}] x/y must be numbers")
    edges = layout.get("edges")
    if edges is not None and not isinstance(edges, dict):
        errors.append("edges must be an object")
    return errors


def write_or_merge_layout(
    *,
    scene: dict[str, Any],
    layout_path: Path,
    profile: Profile,
    reset: bool = False,
) -> dict[str, Any]:
    """
    Write layout file.

    - If missing or ``reset``: write a fresh seed.
    - Else: merge with existing (never clobber user positions).
    """
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    if reset or not layout_path.is_file():
        layout = seed_layout(scene, profile=profile)
    else:
        try:
            existing = json.loads(layout_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
        if not isinstance(existing, dict):
            existing = {}
        layout = merge_layout(existing, scene, profile=profile)
    layout_path.write_text(
        json.dumps(layout, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return layout
