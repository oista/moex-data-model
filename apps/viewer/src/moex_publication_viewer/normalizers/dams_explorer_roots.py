"""Build DAMS Spec explorer roots: classes wrap, source files, ref graph."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from moex_publication_viewer.models.publication_models import PublicationItem


def is_dams_specification_dir(schema_path: Path) -> bool:
    """True when schema lives under …/moex-dams/…/schemas/ next to specification.yaml."""
    schemas_dir = schema_path.resolve().parent
    if schemas_dir.name != "schemas":
        return False
    return (schemas_dir.parent / "specification.yaml").is_file()


def _file_item_id(rel_path: str) -> str:
    return f"file:{rel_path.replace(chr(92), '/')}"


def _read_yaml_meta(path: Path) -> tuple[str | None, str | None, dict[str, Any]]:
    """Return (version, description, raw_mapping) best-effort."""
    text = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text)
    except Exception:
        return None, None, {}
    if not isinstance(data, dict):
        return None, None, {}
    version = data.get("version")
    if version is not None:
        version = str(version)
    description = data.get("description")
    if description is not None:
        description = str(description)
    return version, description, data


def _local_schema_file_id(import_ref: str, schemas_dir: Path) -> str | None:
    """Map a LinkML import path to a file:schemas/… id when local."""
    raw = import_ref.strip()
    if not raw or raw.startswith("http://") or raw.startswith("https://"):
        return None
    if ":" in raw and not raw.endswith(".yaml") and "/" not in raw.split(":", 1)[0]:
        # CURIE-like (e.g. linkml:types) — external
        if not raw.endswith(".yaml"):
            return None
    name = Path(raw).name
    if not name.endswith((".yaml", ".yml")):
        name = f"{name}.yaml"
    candidate = schemas_dir / name
    if candidate.is_file():
        return _file_item_id(f"schemas/{name}")
    # relative import from schemas/
    rel = (schemas_dir / raw).resolve()
    try:
        rel.relative_to(schemas_dir.resolve())
    except ValueError:
        return None
    if rel.is_file():
        return _file_item_id(f"schemas/{rel.name}")
    return None


def build_spec_file_items(spec_dir: Path) -> list[PublicationItem]:
    """
    Build source_file items for specification.yaml + schemas/*.yaml.

    Paths and ids are relative to ``spec_dir`` (moex-dams/0.1/).
    """
    spec_dir = spec_dir.resolve()
    schemas_dir = spec_dir / "schemas"
    entries: list[tuple[str, Path]] = []
    envelope = spec_dir / "specification.yaml"
    if not envelope.is_file():
        raise FileNotFoundError(f"missing specification.yaml under {spec_dir}")
    entries.append(("specification.yaml", envelope))
    if schemas_dir.is_dir():
        for path in sorted(schemas_dir.glob("*.yaml")):
            entries.append((f"schemas/{path.name}", path))

    # First pass: meta + text + provisional refs_out
    raw_by_id: dict[str, dict[str, Any]] = {}
    items_data: list[dict[str, Any]] = []
    for rel, path in entries:
        fid = _file_item_id(rel)
        version, description, data = _read_yaml_meta(path)
        text = path.read_text(encoding="utf-8")
        raw_by_id[fid] = data
        refs_out: list[str] = []
        if rel == "specification.yaml":
            for key in ("schema_body", "normative_sources"):
                val = data.get(key)
                targets = val if isinstance(val, list) else ([val] if val else [])
                for t in targets:
                    if not isinstance(t, str):
                        continue
                    t_norm = t.replace("\\", "/")
                    if t_norm.endswith((".yaml", ".yml")):
                        target_id = _file_item_id(t_norm)
                        if any(r == t_norm for r, _ in entries):
                            refs_out.append(target_id)
        else:
            imports = data.get("imports") or []
            if isinstance(imports, str):
                imports = [imports]
            for imp in imports:
                if not isinstance(imp, str):
                    continue
                local = _local_schema_file_id(imp, schemas_dir)
                if local:
                    refs_out.append(local)
        items_data.append(
            {
                "id": fid,
                "rel": rel,
                "path": path,
                "version": version,
                "description": description,
                "text": text,
                "refs_out": list(dict.fromkeys(refs_out)),
            }
        )

    known = {d["id"] for d in items_data}
    refs_in: dict[str, list[str]] = {i: [] for i in known}
    for d in items_data:
        for target in d["refs_out"]:
            if target in refs_in:
                refs_in[target].append(d["id"])

    items: list[PublicationItem] = []
    for d in items_data:
        name = Path(d["rel"]).name
        items.append(
            PublicationItem(
                id=d["id"],
                title=name,
                description=d["description"],
                attributes={
                    "kind": "source_file",
                    "path": d["rel"],
                    "version": d["version"],
                    "description": d["description"],
                    "text": d["text"],
                    "refs_out": d["refs_out"],
                    "refs_in": refs_in[d["id"]],
                },
            )
        )
    return items


def _section_ref(section_id: str, title: str) -> PublicationItem:
    return PublicationItem(
        id=f"section:{section_id}",
        title=title,
        description=f"Open publication section «{title}».",
        attributes={
            "kind": "section_ref",
            "section_id": section_id,
            "description": f"Open publication section «{title}».",
        },
    )


def _load_requirement_items(
    spec_dir: Path,
    catalog_rel: str = "requirements/it-solution-requirements.yaml",
) -> list[PublicationItem]:
    """Load SpecificationRequirement instances from a requirements catalog YAML."""
    catalog_path = spec_dir / catalog_rel
    if not catalog_path.is_file():
        return []
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return []
    items: list[PublicationItem] = []
    for req in data.get("requirements") or []:
        if not isinstance(req, dict):
            continue
        code = str(req.get("code") or "")
        if not code:
            continue
        items.append(
            PublicationItem(
                id=f"req:{code}",
                title=code,
                description=req.get("title") or req.get("name"),
                attributes={
                    "kind": "requirement",
                    "code": code,
                    "name": req.get("name"),
                    "title": req.get("title"),
                    "requirement_level": req.get("requirement_level"),
                    "requirement_section": req.get("requirement_section"),
                    "statement": req.get("statement"),
                    "description": req.get("description"),
                    "lifecycle_status": req.get("lifecycle_status"),
                    "formal_checks": req.get("formal_checks") or [],
                    "element_id": req.get("element_id"),
                },
            )
        )
    return items


def _source_file_items(
    projected: dict[str, str],
    *,
    description: str,
    version: str = "0.1.0",
) -> list[PublicationItem]:
    items: list[PublicationItem] = []
    for rel, text in projected.items():
        items.append(
            PublicationItem(
                id=_file_item_id(rel),
                title=Path(rel).name,
                description=description,
                attributes={
                    "kind": "source_file",
                    "path": rel,
                    "version": version,
                    "description": description,
                    "text": text,
                    "refs_out": [],
                    "refs_in": [],
                },
            )
        )
    return items


def _build_minimal_spec_file_items(spec_dir: Path) -> list[PublicationItem]:
    """Derived required-only schema as source_file cards."""
    from linkml_runtime.utils.schemaview import SchemaView

    from moex_publication_viewer.normalizers.minimal_schema_projection import (
        project_required_only_schema,
    )

    schema_path = spec_dir / "schemas" / "moex-dams.yaml"
    if not schema_path.is_file():
        return []
    sv = SchemaView(str(schema_path))
    projected = project_required_only_schema(sv)
    return _source_file_items(
        projected,
        description=(
            "Derived required-only projection "
            "(required / minimum_cardinality≥1 slots)."
        ),
    )


def _build_model_skeleton_file_items(spec_dir: Path) -> list[PublicationItem]:
    """Derived ModelPackage skeleton from IT-solution formal_checks."""
    from moex_publication_viewer.normalizers.model_skeleton_projection import (
        project_it_solution_model_skeleton,
    )

    catalog = spec_dir / "requirements" / "it-solution-requirements.yaml"
    projected = project_it_solution_model_skeleton(catalog)
    return _source_file_items(
        projected,
        description=(
            "Derived ModelPackage skeleton from IT-solution formal_checks "
            "(placeholders for required / ref_resolves slots)."
        ),
    )


def _build_conceptual_model_skeleton_file_items(
    spec_dir: Path,
) -> list[PublicationItem]:
    """Derived ModelPackage skeleton from conceptual-model formal_checks."""
    from moex_publication_viewer.normalizers.model_skeleton_projection import (
        project_conceptual_model_skeleton,
    )

    catalog = spec_dir / "requirements" / "conceptual-model-requirements.yaml"
    projected = project_conceptual_model_skeleton(catalog)
    return _source_file_items(
        projected,
        description=(
            "Derived ModelPackage skeleton from conceptual-model formal_checks "
            "(placeholders for required / ref_resolves slots)."
        ),
    )


def _build_model_example_file_items(spec_dir: Path) -> list[PublicationItem]:
    """Curated minimal ModelPackage example as source_file cards."""
    examples_dir = spec_dir / "requirements" / "examples"
    if not examples_dir.is_dir():
        return []
    items: list[PublicationItem] = []
    for path in sorted(examples_dir.glob("*.yaml")):
        rel = f"requirements/examples/{path.name}"
        text = path.read_text(encoding="utf-8")
        _, description, _ = _read_yaml_meta(path)
        items.append(
            PublicationItem(
                id=_file_item_id(rel),
                title=path.name,
                description=description
                or "Curated minimal ModelPackage example for IT-solution owners.",
                attributes={
                    "kind": "source_file",
                    "path": rel,
                    "version": "0.1.0",
                    "description": description
                    or "Curated minimal ModelPackage example for IT-solution owners.",
                    "text": text,
                    "refs_out": [],
                    "refs_in": [],
                },
            )
        )
    return items


def wrap_dams_explorer_roots(
    package_groups: list[PublicationItem],
    spec_dir: Path,
) -> list[PublicationItem]:
    """Wrap under Overview / Классы / Спецификация / Требования / Реализации."""
    overview_root = PublicationItem(
        id="group:overview",
        title="Overview",
        description="Package README and flat inventory tables.",
        attributes={
            "kind": "group",
            "section_root": "overview",
            "section_id": "overview",
            "purpose": "Вход в спецификацию: описание пакета и полные таблицы.",
            "member_ids": [
                "section:overview",
                "section:classes",
                "section:slots",
                "section:enums",
            ],
        },
        children=[
            _section_ref("overview", "Overview"),
            _section_ref("classes", "All classes"),
            _section_ref("slots", "All slots"),
            _section_ref("enums", "All enumerations"),
        ],
    )

    class_count = sum(
        1
        for g in package_groups
        for c in g.children
        if (c.attributes or {}).get("kind") == "class"
    )
    classes_root = PublicationItem(
        id="group:classes",
        title="Классы",
        description="Пакеты схемы и классы/перечисления DAMS.",
        attributes={
            "kind": "group",
            "section_root": "classes",
            "purpose": "Навигация по классам и enum (renderer data-structure, ADR-016 linkml-specification).",
            "structure_why": "Пакеты соответствуют LinkML-модулям DAMS; классы — тело TSpecBody.",
            "class_count": class_count,
            "enum_count": sum(
                1
                for g in package_groups
                for c in g.children
                if (c.attributes or {}).get("kind") == "enum"
            ),
            "member_ids": [g.id for g in package_groups],
        },
        children=package_groups,
    )

    file_items = build_spec_file_items(spec_dir)
    files_root = PublicationItem(
        id="group:spec-files",
        title="Спецификация",
        description="Нормативные YAML-файлы эталона DAMS.",
        attributes={
            "kind": "group",
            "section_root": "schema-files",
            "purpose": "Просмотр envelope и схем, составляющих reference specification.",
            "structure_why": "specification.yaml — дескриптор; schemas/* — нормативное тело LinkML.",
            "class_count": 0,
            "enum_count": 0,
            "member_ids": [f.id for f in file_items],
            "file_count": len(file_items),
        },
        children=file_items,
    )

    req_items = _load_requirement_items(spec_dir)
    conceptual_req_items = _load_requirement_items(
        spec_dir,
        catalog_rel="requirements/conceptual-model-requirements.yaml",
    )
    list_group = PublicationItem(
        id="group:requirements-list",
        title="Требования к модели",
        description="Каталог требований к модели данных ИТ-решения.",
        attributes={
            "kind": "group",
            "section_root": "requirements-list",
            "purpose": "Пункты требований к модели ИТ-решения с формальными проверками.",
            "requirement_count": len(req_items),
            "member_ids": [r.id for r in req_items],
        },
        children=req_items,
    )
    conceptual_list_group = PublicationItem(
        id="group:requirements-conceptual-list",
        title="Требования к модели",
        description="Каталог требований к корпоративной концептуальной модели.",
        attributes={
            "kind": "group",
            "section_root": "requirements-conceptual-list",
            "purpose": (
                "Пункты требований к enterprise-conceptual модели "
                "с формальными проверками (ADR-021)."
            ),
            "requirement_count": len(conceptual_req_items),
            "member_ids": [r.id for r in conceptual_req_items],
        },
        children=conceptual_req_items,
    )
    min_files = _build_minimal_spec_file_items(spec_dir)
    min_spec_group = PublicationItem(
        id="group:requirements-min-spec",
        title="Спецификация требований",
        description="Required-only срез схемы DAMS по обязательным слотам.",
        attributes={
            "kind": "group",
            "section_root": "requirements-min-spec",
            "purpose": "Тот же шаблон, что «Спецификация», но только обязательные слоты.",
            "file_count": len(min_files),
            "member_ids": [f.id for f in min_files],
        },
        children=min_files,
    )
    conceptual_min_spec_group = PublicationItem(
        id="group:requirements-conceptual-min-spec",
        title="Спецификация требований",
        description="Required-only срез схемы DAMS по обязательным слотам.",
        attributes={
            "kind": "group",
            "section_root": "requirements-conceptual-min-spec",
            "purpose": (
                "Тот же шаблон, что «Спецификация», но только обязательные слоты "
                "(общий schema projection для conceptual level)."
            ),
            "file_count": len(min_files),
            "member_ids": [f.id for f in min_files],
        },
        children=min_files,
    )
    skeleton_files = _build_model_skeleton_file_items(spec_dir)
    model_spec_group = PublicationItem(
        id="group:requirements-model-spec",
        title="Спецификация модели",
        description="Минимально допустимый скелет ModelPackage по formal_checks.",
        attributes={
            "kind": "group",
            "section_root": "requirements-model-spec",
            "purpose": (
                "Референсная форма инстанса модели, которую владельцы решений "
                "должны уметь заполнить."
            ),
            "file_count": len(skeleton_files),
            "member_ids": [f.id for f in skeleton_files],
        },
        children=skeleton_files,
    )
    conceptual_skeleton_files = _build_conceptual_model_skeleton_file_items(spec_dir)
    conceptual_model_spec_group = PublicationItem(
        id="group:requirements-conceptual-model-spec",
        title="Спецификация модели",
        description=(
            "Минимально допустимый скелет enterprise-conceptual ModelPackage "
            "по formal_checks."
        ),
        attributes={
            "kind": "group",
            "section_root": "requirements-conceptual-model-spec",
            "purpose": (
                "Референсная форма инстанса корпоративной концептуальной модели."
            ),
            "file_count": len(conceptual_skeleton_files),
            "member_ids": [f.id for f in conceptual_skeleton_files],
        },
        children=conceptual_skeleton_files,
    )
    example_files = _build_model_example_file_items(spec_dir)
    model_example_group = PublicationItem(
        id="group:requirements-model-example",
        title="Пример модели",
        description="Кураторский пример ModelPackage по референсному скелету.",
        attributes={
            "kind": "group",
            "section_root": "requirements-model-example",
            "purpose": "Заполненный минимальный пример модели ИТ-решения.",
            "file_count": len(example_files),
            "member_ids": [f.id for f in example_files],
        },
        children=example_files,
    )
    conceptual_group = PublicationItem(
        id="group:requirements-conceptual",
        title="Концептуальная модель",
        description=(
            "Раздел описывает требования к корпоративной концептуальной модели."
        ),
        attributes={
            "kind": "group",
            "section_root": "requirements-conceptual",
            "purpose": (
                "Требования, схема и скелет модели уровня enterprise-conceptual "
                "(без примера модели)."
            ),
            "structure_why": (
                "Требования к модели — каталог SpecificationRequirement "
                "(requirement_level: conceptual_model); "
                "спецификация требований — required-only LinkML; "
                "спецификация модели — derived skeleton. "
                "Пример модели на этом уровне не публикуется."
            ),
            "requirement_count": len(conceptual_req_items),
            "file_count": len(min_files) + len(conceptual_skeleton_files),
            "member_ids": [
                conceptual_list_group.id,
                conceptual_min_spec_group.id,
                conceptual_model_spec_group.id,
            ],
        },
        children=[
            conceptual_list_group,
            conceptual_min_spec_group,
            conceptual_model_spec_group,
        ],
    )
    it_solutions_group = PublicationItem(
        id="group:requirements-it-solutions",
        title="ИТ-решения",
        description="Раздел описывает требования к модели данных ИТ-решений.",
        attributes={
            "kind": "group",
            "section_root": "requirements-it-solutions",
            "purpose": "Требования, схема, скелет и пример модели уровня ИТ-решения.",
            "structure_why": (
                "Требования к модели — каталог SpecificationRequirement; "
                "спецификация требований — required-only LinkML; "
                "спецификация модели — derived skeleton; "
                "пример модели — curated ModelPackage."
            ),
            "requirement_count": len(req_items),
            "file_count": len(min_files) + len(skeleton_files) + len(example_files),
            "member_ids": [
                list_group.id,
                min_spec_group.id,
                model_spec_group.id,
                model_example_group.id,
            ],
        },
        children=[
            list_group,
            min_spec_group,
            model_spec_group,
            model_example_group,
        ],
    )

    pub_req_path = spec_dir / "publication-requirements.yaml"
    pub_req_count = 0
    if pub_req_path.is_file():
        from moex_publication_viewer.normalizers.helpers import (
            flatten_publication_requirements,
        )

        try:
            pub_data = yaml.safe_load(pub_req_path.read_text(encoding="utf-8"))
        except Exception:
            pub_data = None
        pub_req_count = len(flatten_publication_requirements(pub_data))

    pub_list_group = PublicationItem(
        id="group:requirements-publication-list",
        title="Требования публикации",
        description="PublicationRequirement из publication-requirements.yaml (ADR-019).",
        attributes={
            "kind": "group",
            "section_root": "requirements-publication-list",
            "purpose": (
                "Обязательства publication profile эталона: "
                "что Impl должен покрыть через satisfies."
            ),
            "requirement_count": pub_req_count,
            "member_ids": ["section:publication-requirements"],
        },
        children=[
            _section_ref("publication-requirements", "Требования публикации"),
        ],
    )
    pub_spec_files: list[PublicationItem] = []
    if pub_req_path.is_file():
        text = pub_req_path.read_text(encoding="utf-8")
        _, description, _ = _read_yaml_meta(pub_req_path)
        pub_spec_files.append(
            PublicationItem(
                id=_file_item_id("publication-requirements.yaml"),
                title="publication-requirements.yaml",
                description=description
                or "DAMS publication requirements (ADR-019).",
                attributes={
                    "kind": "source_file",
                    "path": "publication-requirements.yaml",
                    "version": "0.1",
                    "description": description
                    or "DAMS publication requirements (ADR-019).",
                    "text": text,
                    "refs_out": [],
                    "refs_in": [],
                },
            )
        )
    pub_spec_group = PublicationItem(
        id="group:requirements-publication-spec",
        title="Спецификация",
        description="Исходный YAML publication requirements эталона DAMS.",
        attributes={
            "kind": "group",
            "section_root": "requirements-publication-spec",
            "purpose": "Raw source publication-requirements.yaml (ADR-019).",
            "file_count": len(pub_spec_files),
            "member_ids": [f.id for f in pub_spec_files],
        },
        children=pub_spec_files,
    )
    publication_group = PublicationItem(
        id="group:requirements-publication",
        title="Публикация",
        description="Требования к публикации реализаций эталона (ADR-019).",
        attributes={
            "kind": "group",
            "section_root": "requirements-publication",
            "purpose": (
                "Контракт публикации: список PublicationRequirement и исходный YAML."
            ),
            "structure_why": (
                "Требования публикации — flatten profiles[].requirements "
                "(entity-table); спецификация — raw publication-requirements.yaml."
            ),
            "requirement_count": pub_req_count,
            "file_count": len(pub_spec_files),
            "member_ids": [pub_list_group.id, pub_spec_group.id],
        },
        children=[pub_list_group, pub_spec_group],
    )
    requirements_root = PublicationItem(
        id="group:requirements",
        title="Требования",
        description="Требования к моделям и к публикации по уровням применения.",
        attributes={
            "kind": "group",
            "section_root": "requirements",
            "purpose": "Каталог нормативных требований и связанные проекции.",
            "structure_why": (
                "Концептуальная модель (ADR-021): enterprise-conceptual; "
                "ИТ-решения (ADR-013): модель данных решения; "
                "Публикация (ADR-019): обязательства publication profile для Impl."
            ),
            "requirement_count": (
                len(conceptual_req_items) + len(req_items) + pub_req_count
            ),
            "file_count": len(min_files)
            + len(conceptual_skeleton_files)
            + len(skeleton_files)
            + len(example_files)
            + len(pub_spec_files),
            "member_ids": [
                conceptual_group.id,
                it_solutions_group.id,
                publication_group.id,
            ],
        },
        children=[conceptual_group, it_solutions_group, publication_group],
    )

    # Placeholder; build.py fills children from architecture catalog.
    impls_root = PublicationItem(
        id="group:implementations",
        title="Реализации",
        description="Specification implementations, registered against DAMS.",
        attributes={
            "kind": "group",
            "section_root": "implementations",
            "purpose": "Переход к зарегистрированным реализациям (conforms_to DAMS).",
            "structure_why": "Список из architecture-catalog; тела живут в своих модулях.",
            "class_count": 0,
            "enum_count": 0,
            "member_ids": [],
        },
        children=[],
    )
    return [overview_root, classes_root, files_root, requirements_root, impls_root]
