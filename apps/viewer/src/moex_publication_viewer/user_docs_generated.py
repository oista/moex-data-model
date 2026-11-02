"""Pages assembled from the repository for docs/user (ADR-057)."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

import yaml

from moex_publication_viewer.package_docs import split_frontmatter

GENERATED_KINDS = frozenset(
    {"adr-status", "cli-commands", "make-targets", "check-steps"}
)
PHRASE_KINDS = frozenset({"cli-commands", "make-targets", "check-steps"})
DESCRIPTIONS_REL = Path("docs/user/90-reference/descriptions.yaml")
DESCRIPTION_GROUPS = (
    "moex-model",
    "moex-publication-viewer",
    "make",
    "check_all",
)
_RESERVED_DESCRIPTION_KEYS = frozenset({"draft", "verified_at"})

TOOL_SOURCES = {
    "moex-model": Path("apps/cli/src/moex_model_cli/__main__.py"),
    "moex-publication-viewer": Path("apps/viewer/src/moex_publication_viewer/cli.py"),
}
MAKEFILE_REL = Path("Makefile")
CHECK_ALL_REL = Path("scripts/check_all.py")
ADR_DIR_REL = Path("docs/adr")

_STATUS_LABEL = {
    "Accepted": "Принято",
    "Proposed": "Не принято",
    "Draft": "Черновик",
    "Superseded": "Заменено",
}
_TARGET_RE = re.compile(
    r"^([A-Za-z0-9_.-]+(?:[ \t]+[A-Za-z0-9_.-]+)*)[ \t]*:(?!=)"
)
_HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_ADR_TITLE_RE = re.compile(r"^ADR-\d+\s*[:—-]\s*", re.IGNORECASE)


def generated_specs(toc: dict[str, Any]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for chapter in toc.get("chapters") or []:
        if not isinstance(chapter, dict):
            continue
        if str(chapter.get("id") or "").strip() == "glossary":
            continue
        for page in chapter.get("pages") or []:
            if isinstance(page, dict) and "generated" in page:
                specs.append(page)
    return specs


def load_descriptions(
    path: Path,
) -> tuple[dict[str, Any] | None, dict[str, dict[str, str]], list[str]]:
    """Return the raw mapping, phrase groups, and load errors."""
    label = DESCRIPTIONS_REL.as_posix()
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, {}, [f"{label}: cannot read: {exc}"]
    except Exception as exc:
        return None, {}, [f"{label}: cannot parse YAML: {exc}"]
    if not isinstance(raw, dict):
        return None, {}, [f"{label}: root must be a mapping"]
    errors: list[str] = []
    groups: dict[str, dict[str, str]] = {}
    for key, value in raw.items():
        name = str(key).strip()
        if name in _RESERVED_DESCRIPTION_KEYS:
            continue
        if name not in DESCRIPTION_GROUPS:
            errors.append(f"{label}: unknown group '{name}'")
            continue
        if not isinstance(value, dict):
            errors.append(f"{label}: {name} must be a mapping")
            continue
        phrases: dict[str, str] = {}
        for phrase_key, phrase in value.items():
            ident = str(phrase_key).strip()
            if not isinstance(phrase, str):
                errors.append(f"{label}: {name}: phrase for '{ident}' must be text")
                continue
            phrases[ident] = phrase
        groups[name] = phrases
    return raw, groups, errors


def render_generated(
    root: Path,
    specs: list[dict[str, Any]],
    groups: dict[str, dict[str, str]] | None,
    *,
    descriptions_state: str,
) -> tuple[dict[str, str], list[str]]:
    """Build markdown keyed by page id.

    ``descriptions_state`` is ``absent``, ``ready``, or ``broken``.
    """
    root = root.resolve()
    errors: list[str] = []
    plans: list[dict[str, Any]] = []
    tools: set[str] = set()
    want_make = False
    want_steps = False

    for spec in specs:
        kind = str(spec.get("generated") or "").strip()
        page_id = str(spec.get("id") or "").strip() or kind or "?"
        title = str(spec.get("title") or "").strip()
        loc = f"toc.yaml: page '{page_id}'"
        if not title:
            errors.append(f"{loc}: title is required")
        if not kind or kind not in GENERATED_KINDS:
            errors.append(f"{loc}: unknown generated kind '{kind or 'empty'}'")
            continue
        if str(spec.get("path") or "").strip():
            errors.append(f"{loc}: path and generated cannot both be set")
        tool = str(spec.get("tool") or "").strip()
        page_tools: tuple[str, ...] = ()
        if kind == "cli-commands":
            if tool:
                if tool not in TOOL_SOURCES:
                    errors.append(f"{loc}: unknown tool '{tool}'")
                    continue
                page_tools = (tool,)
            else:
                page_tools = tuple(TOOL_SOURCES)
            tools.update(page_tools)
        elif tool:
            errors.append(f"{loc}: tool is only valid for cli-commands")
        if kind == "make-targets":
            want_make = True
        if kind == "check-steps":
            want_steps = True
        plans.append(
            {
                "id": page_id,
                "kind": kind,
                "title": title,
                "tools": page_tools,
            }
        )

    if errors:
        return {}, errors

    commands: dict[str, list[str]] = {}
    for tool in sorted(tools):
        found, tool_errors = _commands_for_tool(root, tool)
        errors.extend(tool_errors)
        commands[tool] = found

    targets: list[str] = []
    steps: list[str] = []
    if want_make or want_steps:
        steps, step_errors = _check_steps(root)
        errors.extend(step_errors)
    if want_make:
        targets, target_errors = _make_targets(root)
        errors.extend(target_errors)
    if errors:
        return {}, errors

    need_phrases = bool(tools) or want_make or want_steps
    if need_phrases and descriptions_state == "absent":
        return {}, [f"{DESCRIPTIONS_REL.as_posix()}: missing"]
    if need_phrases and descriptions_state != "ready":
        return {}, errors

    phrase_groups = groups or {}
    if tools or want_make or want_steps:
        errors.extend(
            _phrase_errors(
                phrase_groups,
                commands=commands,
                targets=targets if want_make else None,
                steps=steps if want_steps else None,
            )
        )
    if errors:
        return {}, errors

    rendered: dict[str, str] = {}
    for plan in plans:
        kind = plan["kind"]
        if kind == "adr-status":
            rendered[plan["id"]] = _adr_status_markdown(root, plan["title"])
        elif kind == "cli-commands":
            rendered[plan["id"]] = _cli_markdown(
                plan["title"],
                plan["tools"],
                commands,
                phrase_groups,
            )
        elif kind == "make-targets":
            rendered[plan["id"]] = _make_markdown(
                plan["title"], targets, steps, phrase_groups.get("make") or {}
            )
        elif kind == "check-steps":
            rendered[plan["id"]] = _steps_markdown(
                plan["title"], steps, phrase_groups.get("check_all") or {}
            )
    return rendered, []


def _commands_for_tool(root: Path, tool: str) -> tuple[list[str], list[str]]:
    rel = TOOL_SOURCES[tool]
    path = root / rel
    if not path.is_file():
        return [], [f"{rel.as_posix()}: missing"]
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], [f"{rel.as_posix()}: cannot read: {exc}"]
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [], [f"{rel.as_posix()}: cannot parse: {exc}"]
    return _commands_in_tree(tree, rel.as_posix())


def _commands_in_tree(tree: ast.AST, label: str) -> tuple[list[str], list[str]]:
    extractor = _CommandExtractor()
    extractor.visit(tree)
    errors: list[str] = []
    seen: set[str] = set()
    ordered: list[str] = []
    for key in extractor.commands:
        if key in seen:
            errors.append(f"{label}: duplicate command '{key}'")
            continue
        seen.add(key)
        ordered.append(key)
    return ordered, errors


class _CommandExtractor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.paths: dict[str, tuple[str, ...]] = {}
        self.commands: list[str] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Call)
        ):
            info = self._call(node.value)
            if info is not None:
                kind, path = info
                self.paths[node.targets[0].id] = path
                if kind == "add_parser" and path:
                    self.commands.append(" ".join(path))
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Call):
            info = self._call(node.value)
            if info is not None and info[0] == "add_parser" and info[1]:
                self.commands.append(" ".join(info[1]))
        self.generic_visit(node)

    def _call(self, call: ast.Call) -> tuple[str, tuple[str, ...]] | None:
        func = call.func
        if not isinstance(func, ast.Attribute) or not isinstance(func.value, ast.Name):
            return None
        parent = self.paths.get(func.value.id, ())
        if func.attr == "add_subparsers":
            return ("add_subparsers", parent)
        if func.attr != "add_parser" or not call.args:
            return None
        arg = call.args[0]
        if not isinstance(arg, ast.Constant) or not isinstance(arg.value, str):
            return None
        name = arg.value.strip()
        if not name:
            return None
        return ("add_parser", parent + (name,))


def _make_targets(root: Path) -> tuple[list[str], list[str]]:
    path = root / MAKEFILE_REL
    if not path.is_file():
        return [], [f"{MAKEFILE_REL.as_posix()}: missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], [f"{MAKEFILE_REL.as_posix()}: cannot read: {exc}"]
    ordered: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if not line or line[0].isspace() or line.startswith("#"):
            continue
        match = _TARGET_RE.match(line)
        if not match:
            continue
        for name in match.group(1).split():
            if name.startswith("."):
                continue
            if name in seen:
                continue
            seen.add(name)
            ordered.append(name)
    return ordered, []


def _check_steps(root: Path) -> tuple[list[str], list[str]]:
    rel = CHECK_ALL_REL
    path = root / rel
    if not path.is_file():
        return [], [f"{rel.as_posix()}: missing"]
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], [f"{rel.as_posix()}: cannot read: {exc}"]
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [], [f"{rel.as_posix()}: cannot parse: {exc}"]
    for node in tree.body:
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "STEP_IDS" for t in node.targets):
                value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "STEP_IDS":
                value = node.value
        if value is None:
            continue
        if not isinstance(value, (ast.Tuple, ast.List)):
            return [], [f"{rel.as_posix()}: STEP_IDS must be a list of names"]
        steps: list[str] = []
        for elt in value.elts:
            if not isinstance(elt, ast.Constant) or not isinstance(elt.value, str):
                return [], [f"{rel.as_posix()}: STEP_IDS must be a list of names"]
            steps.append(elt.value.strip())
        return steps, []
    return [], [f"{rel.as_posix()}: STEP_IDS not found"]


def _phrase_errors(
    groups: dict[str, dict[str, str]],
    *,
    commands: dict[str, list[str]],
    targets: list[str] | None,
    steps: list[str] | None,
) -> list[str]:
    label = DESCRIPTIONS_REL.as_posix()
    errors: list[str] = []
    scoped: list[tuple[str, list[str], str]] = []
    for tool, names in commands.items():
        scoped.append((tool, names, "command"))
    if targets is not None:
        scoped.append(("make", targets, "target"))
    if steps is not None:
        scoped.append(("check_all", steps, "step"))
    for group_name, names, noun in scoped:
        phrases = groups.get(group_name)
        if phrases is None:
            phrases = {}
        known = set(names)
        for name in names:
            if name not in phrases:
                errors.append(f"{label}: missing phrase for '{name}'")
                continue
            if not phrases[name].strip():
                errors.append(f"{label}: empty phrase for '{name}'")
        for key in phrases:
            if key not in known:
                errors.append(f"{label}: unknown {noun} '{key}'")
    return errors


def _adr_rows(root: Path) -> list[tuple[str, str, str, str]]:
    adr_dir = root / ADR_DIR_REL
    rows: list[tuple[str, str, str, str]] = []
    if not adr_dir.is_dir():
        return rows
    for path in sorted(adr_dir.glob("ADR-*.md")):
        match = re.match(r"ADR-(\d+)", path.name, re.IGNORECASE)
        if not match:
            continue
        adr_id = f"ADR-{int(match.group(1)):03d}"
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            continue
        meta, body = split_frontmatter(raw)
        status = str(meta.get("status") or "").strip() or "без статуса"
        heading = ""
        found = _HEADING_RE.search(body)
        if found:
            heading = found.group(1).strip()
        title = _ADR_TITLE_RE.sub("", heading).strip() if heading else ""
        if not title:
            title = heading or adr_id
        rel = path.relative_to(root).as_posix()
        rows.append((adr_id, title, status, rel))
    rows.sort(key=lambda row: int(row[0].split("-", 1)[1]))
    return rows


def _adr_status_markdown(root: Path, title: str) -> str:
    rows = _adr_rows(root)
    counts: dict[str, int] = {}
    for _adr_id, _title, status, _rel in rows:
        label = _STATUS_LABEL.get(status, status)
        counts[label] = counts.get(label, 0) + 1
    summary = []
    for label in ("Принято", "Не принято", "Черновик", "Заменено"):
        if counts.get(label):
            summary.append(f"{label}: {counts[label]}")
    for label, count in counts.items():
        if label not in _STATUS_LABEL.values() and label not in ("Принято", "Не принято"):
            summary.append(f"{label}: {count}")
    summary_text = ". ".join(summary) if summary else "Файлов решений нет"
    lines = [
        f"# {title}",
        "",
        "Статусы прочитаны из шапок файлов в `docs/adr/`. "
        f"{summary_text}.",
        "",
    ]
    for adr_id, adr_title, status, rel in rows:
        label = _STATUS_LABEL.get(status, status)
        lines.append(f"- [{adr_id}]({rel}) — {adr_title}. {label}.")
    lines.append("")
    return "\n".join(lines)


def _cli_markdown(
    title: str,
    tools: tuple[str, ...],
    commands: dict[str, list[str]],
    groups: dict[str, dict[str, str]],
) -> str:
    sources = ", ".join(f"`{TOOL_SOURCES[tool].as_posix()}`" for tool in tools)
    lines = [
        f"# {title}",
        "",
        f"Команды прочитаны из {sources}. Рядом с именем сказано, зачем она нужна.",
        "",
    ]
    for tool in tools:
        phrases = groups.get(tool) or {}
        for key in commands.get(tool) or []:
            lines.append(f"- `{tool} {key}` — {phrases[key].strip()}")
    lines.append("")
    return "\n".join(lines)


def _membership_note(name: str, steps: list[str]) -> str:
    if name in {"check", "check-all"}:
        return "Это общая проверка."
    if name in steps:
        return "Имя совпадает с шагом общей проверки."
    return "В общую проверку не входит."


def _make_markdown(
    title: str,
    targets: list[str],
    steps: list[str],
    phrases: dict[str, str],
) -> str:
    lines = [
        f"# {title}",
        "",
        "Цели прочитаны из `Makefile`. "
        "Совпадение имени с шагом общей проверки не значит, что цель и шаг делают одно и то же.",
        "",
    ]
    for name in targets:
        note = _membership_note(name, steps)
        lines.append(f"- `make {name}` — {phrases[name].strip()} {note}")
    lines.append("")
    return "\n".join(lines)


def _steps_markdown(title: str, steps: list[str], phrases: dict[str, str]) -> str:
    lines = [
        f"# {title}",
        "",
        "Шаги идут в этом порядке. Их выполняет общая проверка (`make check`).",
        "",
    ]
    for index, name in enumerate(steps, start=1):
        lines.append(f"{index}. `{name}` — {phrases[name].strip()}")
    lines.append("")
    return "\n".join(lines)
