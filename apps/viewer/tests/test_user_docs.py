"""User documentation build and check (ADR-057)."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import yaml

from moex_publication_viewer.user_docs import (
    MODULE_ID,
    SECTION_ID,
    UserDocsError,
    build_user_docs,
    check_user_docs,
    compile_user_docs_module,
    replace_glossary_links,
)


REASON = "ещё не описано: нет главы, которая это рассказывает"


def _write_user_docs(
    root: Path,
    *,
    page_body: str | None = None,
    glossary_terms: list[dict] | None = None,
    not_covered: list[dict] | None = None,
    sources: list[str] | None = None,
    verified_at: str = "2099-01-01",
    include_adr_fixture: bool = True,
    extra_pages: list[dict] | None = None,
    extra_files: dict[str, str] | None = None,
    descriptions: dict | None = None,
) -> Path:
    docs_user = root / "docs" / "user"
    docs_user.mkdir(parents=True)
    (docs_user / "00-start").mkdir(parents=True, exist_ok=True)

    src_rel = "docs/architecture/MODELING_ARCHITECTURE.md"
    if sources is None:
        sources = [src_rel]
    arch = root / src_rel
    arch.parent.mkdir(parents=True, exist_ok=True)
    if not arch.is_file():
        arch.write_text("# modeling\n", encoding="utf-8")

    if include_adr_fixture:
        adr_dir = root / "docs" / "adr"
        adr_dir.mkdir(parents=True, exist_ok=True)
        (adr_dir / "ADR-001-sample.md").write_text(
            "---\nstatus: Accepted\nversion: \"0.1\"\nnormative: false\n"
            "supersedes: []\nsuperseded_by: []\n---\n\n# ADR-001\n",
            encoding="utf-8",
        )
        (adr_dir / "ADR-002-sample.md").write_text(
            "---\nstatus: Proposed\nversion: \"0.1\"\nnormative: false\n"
            "supersedes: []\nsuperseded_by: []\n---\n\n# ADR-002\n",
            encoding="utf-8",
        )

    terms = glossary_terms or [
        {
            "id": "modeling-standard",
            "term": "Стандарт",
            "short": "Язык модели.",
            "explanation": "Формализм для записи модели.",
            "see_also": ["reference-specification"],
            "sources": sources,
        },
        {
            "id": "reference-specification",
            "term": "Спецификация",
            "short": "Норма на стандарте.",
            "explanation": "Профиль применения стандарта.",
            "see_also": ["modeling-standard"],
            "sources": sources,
        },
        {
            "id": "specification-implementation",
            "term": "Реализация",
            "short": "Конкретная модель.",
            "explanation": "Версионированное тело модели.",
            "see_also": [],
            "sources": sources,
        },
    ]
    for term in terms:
        if "draft" not in term and "verified_at" not in term:
            term["draft"] = True
    (docs_user / "glossary.yaml").write_text(
        yaml.safe_dump({"terms": terms}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    body = page_body
    if body is None:
        body = (
            "Краткое описание продукта.\n\n"
            "См. [стандарт](glossary:modeling-standard).\n"
        )
    page = docs_user / "00-start" / "what-is-this.md"
    src_lines = "\n".join(f"  - {s}" for s in sources)
    page.write_text(
        f"---\nid: what-is-this\nsources:\n{src_lines}\n"
        f"verified_at: {verified_at}\n---\n\n{body}",
        encoding="utf-8",
    )

    covered = not_covered
    if covered is None:
        covered = [{"adr": "ADR-001", "reason": REASON}]

    toc = {
        "chapters": [
            {
                "id": "start",
                "title": "Начало",
                "pages": [
                    {
                        "id": "what-is-this",
                        "path": "00-start/what-is-this.md",
                        "title": "Что это за продукт",
                    },
                    *(extra_pages or []),
                ],
            },
            {"id": "glossary", "title": "Глоссарий"},
        ],
        "not_covered": covered,
    }
    (docs_user / "toc.yaml").write_text(
        yaml.safe_dump(toc, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    (docs_user / "user-docs.yaml").write_text(
        "module_id: user-docs\ntitle: Документация продукта\n",
        encoding="utf-8",
    )
    for rel, text in (extra_files or {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    if descriptions is not None:
        desc = docs_user / "90-reference" / "descriptions.yaml"
        desc.parent.mkdir(parents=True, exist_ok=True)
        desc.write_text(
            yaml.safe_dump(descriptions, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
    return docs_user


def _page(module, page_id: str):
    for chapter in module.sections[0].items:
        for child in chapter.children:
            if child.id == page_id:
                return child
    raise AssertionError(page_id)


_CLI_PY = '''
import argparse

def build_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="Check the model")
    lock = sub.add_parser("lock", help="Lock files")
    lock_sub = lock.add_subparsers(dest="lock_action", required=True)
    lock_sub.add_parser("update", help="Rewrite the lock")
    return parser
'''

_VIEWER_PY = '''
import argparse

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build-user-docs", help="Build product docs")
    return parser
'''

_MAKEFILE = """
.PHONY: check user-docs drawdb-up
check:
\tpython scripts/check_all.py
user-docs:
\techo build
drawdb-up:
\techo up
"""

_CHECK_ALL_PY = '''
STEP_IDS = (
    "user-docs",
    "slice-cli",
)
'''

_COMMAND_FILES = {
    "apps/cli/src/moex_model_cli/__main__.py": _CLI_PY,
    "apps/viewer/src/moex_publication_viewer/cli.py": _VIEWER_PY,
    "Makefile": _MAKEFILE,
    "scripts/check_all.py": _CHECK_ALL_PY,
}

_PHRASES = {
    "draft": True,
    "moex-model": {
        "validate": "Проверяет модель.",
        "lock": "Фиксирует состав.",
        "lock update": "Переписывает фиксацию.",
    },
    "moex-publication-viewer": {
        "build-user-docs": "Собирает документацию.",
    },
    "make": {
        "check": "Запускает общую проверку.",
        "user-docs": "Собирает страницы.",
        "drawdb-up": "Поднимает редактор схем.",
    },
    "check_all": {
        "user-docs": "Сверяет страницы.",
        "slice-cli": "Гоняет проверки программы.",
    },
}


def test_replace_glossary_links_ok():
    body, errors = replace_glossary_links(
        "[x](glossary:modeling-standard)", {"modeling-standard"}
    )
    assert errors == []
    assert f"#module={MODULE_ID}&section={SECTION_ID}&item=modeling-standard" in body


def test_replace_glossary_links_unknown():
    _body, errors = replace_glossary_links("[x](glossary:missing)", {"modeling-standard"})
    assert errors


def test_build_deterministic(tmp_path: Path):
    _write_user_docs(tmp_path)
    a = build_user_docs(tmp_path, out_path=tmp_path / "a.html")
    b = build_user_docs(tmp_path, out_path=tmp_path / "b.html")
    assert a.read_text(encoding="utf-8") == b.read_text(encoding="utf-8")


def test_build_contains_glossary_hash(tmp_path: Path):
    _write_user_docs(tmp_path)
    out = build_user_docs(tmp_path, out_path=tmp_path / "out.html")
    html = out.read_text(encoding="utf-8")
    # Jinja autoescape turns & into &amp; inside the HTML document.
    assert (
        f"#module={MODULE_ID}&amp;section={SECTION_ID}&amp;item=modeling-standard"
        in html
    )
    module = compile_user_docs_module(tmp_path)
    assert module.module_id == MODULE_ID
    assert module.sections[0].kind == "documentation"


def test_build_rejects_unknown_glossary_link(tmp_path: Path):
    _write_user_docs(
        tmp_path,
        page_body="См. [нет](glossary:no-such-term).\n",
    )
    try:
        build_user_docs(tmp_path, out_path=tmp_path / "out.html")
        assert False, "expected UserDocsError"
    except UserDocsError as exc:
        assert any("no-such-term" in e for e in exc.errors)


def test_check_requires_sources(tmp_path: Path):
    docs = _write_user_docs(tmp_path)
    page = docs / "00-start" / "what-is-this.md"
    page.write_text(
        "---\nid: what-is-this\nverified_at: 2099-01-01\n---\n\nТекст.\n",
        encoding="utf-8",
    )
    (docs / "index.html").write_text("<html></html>\n", encoding="utf-8")
    errors, _warnings = check_user_docs(tmp_path)
    assert any("sources" in e for e in errors)


def test_check_accepted_adr_without_coverage(tmp_path: Path):
    _write_user_docs(tmp_path, not_covered=[])
    build_user_docs(tmp_path)
    errors, _warnings = check_user_docs(tmp_path)
    assert any("ADR-001" in e and "not_covered" in e for e in errors)


def test_check_not_covered_satisfies(tmp_path: Path):
    _write_user_docs(tmp_path, not_covered=[{"adr": "ADR-001", "reason": REASON}])
    build_user_docs(tmp_path)
    errors, _warnings = check_user_docs(tmp_path)
    assert errors == []


def test_check_tail_only_adr_does_not_cover(tmp_path: Path):
    _write_user_docs(
        tmp_path,
        not_covered=[],
        page_body=(
            "Краткое описание продукта.\n\n"
            "Где прочитать решение: [ADR-001](docs/adr/ADR-001-sample.md).\n"
        ),
        sources=[
            "docs/architecture/MODELING_ARCHITECTURE.md",
            "docs/adr/ADR-001-sample.md",
        ],
    )
    build_user_docs(tmp_path)
    errors, _warnings = check_user_docs(tmp_path)
    assert any("ADR-001" in e and "not_covered" in e for e in errors)


def test_check_paragraph_adr_covers(tmp_path: Path):
    _write_user_docs(
        tmp_path,
        not_covered=[],
        page_body="Правило записано в YAML (ADR-001).\n",
        sources=[
            "docs/architecture/MODELING_ARCHITECTURE.md",
            "docs/adr/ADR-001-sample.md",
        ],
    )
    build_user_docs(tmp_path)
    errors, _warnings = check_user_docs(tmp_path)
    assert not any("ADR-001" in e and "not_covered" in e for e in errors)


def test_check_glossary_only_adr_does_not_cover(tmp_path: Path):
    _write_user_docs(
        tmp_path,
        not_covered=[],
        glossary_terms=[
            {
                "id": "modeling-standard",
                "term": "Стандарт",
                "short": "Язык модели.",
                "explanation": "Формализм для записи модели (ADR-001).",
                "see_also": [],
                "sources": [
                    "docs/architecture/MODELING_ARCHITECTURE.md",
                    "docs/adr/ADR-001-sample.md",
                ],
            },
        ],
    )
    build_user_docs(tmp_path)
    errors, _warnings = check_user_docs(tmp_path)
    assert any("ADR-001" in e and "not_covered" in e for e in errors)


def test_check_stale_verified_at_is_warning(tmp_path: Path, monkeypatch):
    _write_user_docs(tmp_path, verified_at="2000-01-01")
    build_user_docs(tmp_path)

    future = date.today() + timedelta(days=1)

    def fake_git_date(_root: Path, _path: Path):
        return future

    monkeypatch.setattr(
        "moex_publication_viewer.user_docs._git_commit_date",
        fake_git_date,
    )
    # Also pretend git is available
    import moex_publication_viewer.user_docs as ud

    real_run = ud.subprocess.run

    def fake_run(cmd, *args, **kwargs):
        if cmd[:2] == ["git", "-C"] and "rev-parse" in cmd:
            class R:
                returncode = 0
                stdout = "true\n"
                stderr = ""

            return R()
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(ud.subprocess, "run", fake_run)

    errors, warnings = check_user_docs(tmp_path)
    assert errors == []
    assert any("verified_at" in w for w in warnings)


def test_check_html_mismatch(tmp_path: Path):
    _write_user_docs(tmp_path)
    build_user_docs(tmp_path)
    index = tmp_path / "docs" / "user" / "index.html"
    index.write_text(index.read_text(encoding="utf-8") + "\n<!-- drift -->\n", encoding="utf-8")
    errors, _warnings = check_user_docs(tmp_path)
    assert any("does not match a fresh build" in e for e in errors)


def test_glossary_see_also_uses_term_name(tmp_path: Path):
    _write_user_docs(tmp_path)
    module = compile_user_docs_module(tmp_path)
    glossary = next(item for item in module.sections[0].items if item.id == "group:glossary")
    card = next(child for child in glossary.children if child.id == "modeling-standard")
    content = str(card.attributes.get("content") or "")
    assert ">Спецификация</a>" in content
    assert ">reference-specification</a>" not in content


def test_check_draft_with_verified_at_is_error(tmp_path: Path):
    docs = _write_user_docs(tmp_path)
    page = docs / "00-start" / "what-is-this.md"
    text = page.read_text(encoding="utf-8").replace(
        "verified_at: 2099-01-01\n",
        "draft: true\nverified_at: 2099-01-01\n",
    )
    page.write_text(text, encoding="utf-8")
    errors, _warnings = check_user_docs(tmp_path)
    assert any("cannot be combined" in e for e in errors)


def test_check_draft_does_not_count_as_freshness(tmp_path: Path, monkeypatch):
    docs = _write_user_docs(tmp_path)
    page = docs / "00-start" / "what-is-this.md"
    text = page.read_text(encoding="utf-8").replace("verified_at: 2099-01-01\n", "draft: true\n")
    page.write_text(text, encoding="utf-8")
    build_user_docs(tmp_path)

    future = date.today() + timedelta(days=1)

    def fake_git_date(_root: Path, _path: Path):
        return future

    monkeypatch.setattr(
        "moex_publication_viewer.user_docs._git_commit_date",
        fake_git_date,
    )
    import moex_publication_viewer.user_docs as ud

    real_run = ud.subprocess.run

    def fake_run(cmd, *args, **kwargs):
        if cmd[:2] == ["git", "-C"] and "rev-parse" in cmd:
            class R:
                returncode = 0
                stdout = "true\n"
                stderr = ""

            return R()
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(ud.subprocess, "run", fake_run)
    errors, warnings = check_user_docs(tmp_path)
    assert errors == []
    assert any(w.startswith("what-is-this: draft") for w in warnings)
    assert not any("changed in git" in w for w in warnings)


def test_check_glossary_stale_verified_at_is_warning(tmp_path: Path, monkeypatch):
    _write_user_docs(
        tmp_path,
        glossary_terms=[
            {
                "id": "modeling-standard",
                "term": "Стандарт",
                "short": "Язык модели.",
                "explanation": "Формализм для записи модели.",
                "see_also": [],
                "sources": ["docs/architecture/MODELING_ARCHITECTURE.md"],
                "verified_at": "2000-01-01",
            },
            {
                "id": "reference-specification",
                "term": "Спецификация",
                "short": "Норма на стандарте.",
                "explanation": "Профиль применения стандарта.",
                "see_also": [],
                "sources": ["docs/architecture/MODELING_ARCHITECTURE.md"],
                "draft": True,
            },
            {
                "id": "specification-implementation",
                "term": "Реализация",
                "short": "Конкретная модель.",
                "explanation": "Версионированное тело модели.",
                "see_also": [],
                "sources": ["docs/architecture/MODELING_ARCHITECTURE.md"],
                "draft": True,
            },
        ],
    )
    build_user_docs(tmp_path)
    future = date.today() + timedelta(days=1)

    def fake_git_date(_root: Path, _path: Path):
        return future

    monkeypatch.setattr(
        "moex_publication_viewer.user_docs._git_commit_date",
        fake_git_date,
    )
    import moex_publication_viewer.user_docs as ud

    real_run = ud.subprocess.run

    def fake_run(cmd, *args, **kwargs):
        if cmd[:2] == ["git", "-C"] and "rev-parse" in cmd:
            class R:
                returncode = 0
                stdout = "true\n"
                stderr = ""

            return R()
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(ud.subprocess, "run", fake_run)
    errors, warnings = check_user_docs(tmp_path)
    assert errors == []
    assert any(
        w.startswith("modeling-standard:") and "changed in git" in w for w in warnings
    )


def test_check_warns_when_mentioned_adr_missing_from_sources(tmp_path: Path):
    _write_user_docs(tmp_path, page_body="См. ADR-002.\n")
    build_user_docs(tmp_path)
    errors, warnings = check_user_docs(tmp_path)
    assert errors == []
    assert any("ADR-002" in w and "sources" in w for w in warnings)


def test_check_not_covered_rejects_pr_number(tmp_path: Path):
    _write_user_docs(tmp_path, not_covered=[{"adr": "ADR-001", "reason": "позже, PR-3"}])
    try:
        build_user_docs(tmp_path)
        assert False, "expected UserDocsError"
    except UserDocsError as exc:
        assert any("future PR" in e for e in exc.errors)
    errors, _warnings = check_user_docs(tmp_path)
    assert any("future PR" in e for e in errors)


def test_build_shows_not_covered_page(tmp_path: Path):
    _write_user_docs(tmp_path)
    module = compile_user_docs_module(tmp_path)
    chapter_ids = [item.id for item in module.sections[0].items]
    assert chapter_ids.index("group:not-yet-told") < chapter_ids.index("group:glossary")
    chapter = next(item for item in module.sections[0].items if item.id == "group:not-yet-told")
    content = str(chapter.children[0].attributes.get("content") or "")
    assert "ADR-001" in content
    assert REASON in content
    assert "docs/adr/ADR-001-sample.md" in content


def test_check_not_covered_must_be_visible(tmp_path: Path, monkeypatch):
    _write_user_docs(tmp_path)
    build_user_docs(tmp_path)
    monkeypatch.setattr(
        "moex_publication_viewer.user_docs.deferred_page_markdown",
        lambda _root, _rows: "# Пусто\n\nНичего.\n",
    )
    errors, _warnings = check_user_docs(tmp_path)
    assert any("not visible" in e for e in errors)


def _generated_repo(tmp_path: Path, **kwargs) -> None:
    extra_pages = kwargs.pop(
        "extra_pages",
        [
            {"id": "adr-status", "generated": "adr-status", "title": "Статусы решений"},
            {
                "id": "moex-model-commands",
                "generated": "cli-commands",
                "tool": "moex-model",
                "title": "Команды moex-model",
            },
            {
                "id": "viewer-commands",
                "generated": "cli-commands",
                "tool": "moex-publication-viewer",
                "title": "Команды просмотра",
            },
            {"id": "make-targets", "generated": "make-targets", "title": "Цели Makefile"},
            {"id": "check-steps", "generated": "check-steps", "title": "Шаги общей проверки"},
        ],
    )
    files = dict(_COMMAND_FILES)
    files.update(kwargs.pop("extra_files", {}))
    files["docs/adr/ADR-001-sample.md"] = (
        "---\nstatus: Accepted\n---\n\n# ADR-001: Канонический YAML\n"
    )
    _write_user_docs(
        tmp_path,
        extra_pages=extra_pages,
        extra_files=files,
        descriptions=kwargs.pop("descriptions", _PHRASES),
        **kwargs,
    )


def test_generated_adr_status_lists_title_and_counts(tmp_path: Path):
    _generated_repo(tmp_path)
    module = compile_user_docs_module(tmp_path)
    content = str(_page(module, "adr-status").attributes.get("content") or "")
    assert "Канонический YAML" in content
    assert "Принято: 1" in content
    assert "Не принято: 1" in content
    assert "ADR-002" in content


def test_generated_adr_status_does_not_cover_accepted_adr(tmp_path: Path):
    _generated_repo(tmp_path, not_covered=[])
    build_user_docs(tmp_path)
    errors, _warnings = check_user_docs(tmp_path)
    assert any("ADR-001" in e and "not_covered" in e for e in errors)


def test_generated_cli_commands_include_nested_and_russian_phrase(tmp_path: Path):
    _generated_repo(tmp_path)
    module = compile_user_docs_module(tmp_path)
    content = str(_page(module, "moex-model-commands").attributes.get("content") or "")
    assert "lock update" in content
    assert "Переписывает фиксацию." in content
    viewer = str(_page(module, "viewer-commands").attributes.get("content") or "")
    assert "build-user-docs" in viewer
    assert "Собирает документацию." in viewer
    assert "lock update" not in viewer


def test_generated_make_targets_mark_check_membership(tmp_path: Path):
    _generated_repo(tmp_path)
    module = compile_user_docs_module(tmp_path)
    content = str(_page(module, "make-targets").attributes.get("content") or "")
    assert "make user-docs" in content
    assert "Имя совпадает с шагом общей проверки." in content
    assert "make drawdb-up" in content
    assert "В общую проверку не входит." in content


def test_generated_check_steps_keep_source_order(tmp_path: Path):
    _generated_repo(tmp_path)
    module = compile_user_docs_module(tmp_path)
    content = str(_page(module, "check-steps").attributes.get("content") or "")
    assert content.find("user-docs") < content.find("slice-cli")
    assert "Сверяет страницы." in content


def test_missing_command_phrase_is_error(tmp_path: Path):
    phrases = {
        "draft": True,
        "moex-model": {
            "lock": "Фиксирует состав.",
            "lock update": "Переписывает фиксацию.",
        },
        "moex-publication-viewer": _PHRASES["moex-publication-viewer"],
        "make": _PHRASES["make"],
        "check_all": _PHRASES["check_all"],
    }
    _generated_repo(tmp_path, descriptions=phrases)
    try:
        compile_user_docs_module(tmp_path)
        assert False, "expected UserDocsError"
    except UserDocsError as exc:
        assert any("validate" in e and "missing" in e for e in exc.errors)


def test_unknown_command_phrase_is_error(tmp_path: Path):
    phrases = {
        "draft": True,
        "moex-model": {**_PHRASES["moex-model"], "retired": "Уже нет."},
        "moex-publication-viewer": _PHRASES["moex-publication-viewer"],
        "make": _PHRASES["make"],
        "check_all": _PHRASES["check_all"],
    }
    _generated_repo(tmp_path, descriptions=phrases)
    try:
        compile_user_docs_module(tmp_path)
        assert False, "expected UserDocsError"
    except UserDocsError as exc:
        assert any("retired" in e and "unknown" in e for e in exc.errors)


def test_empty_command_phrase_is_error(tmp_path: Path):
    phrases = {
        "draft": True,
        "moex-model": {**_PHRASES["moex-model"], "validate": "  "},
        "moex-publication-viewer": _PHRASES["moex-publication-viewer"],
        "make": _PHRASES["make"],
        "check_all": _PHRASES["check_all"],
    }
    _generated_repo(tmp_path, descriptions=phrases)
    try:
        compile_user_docs_module(tmp_path)
        assert False, "expected UserDocsError"
    except UserDocsError as exc:
        assert any("validate" in e and "empty" in e for e in exc.errors)


def test_descriptions_draft_and_verified_at_conflict(tmp_path: Path):
    phrases = {**_PHRASES, "verified_at": "2099-01-01"}
    _generated_repo(tmp_path, descriptions=phrases)
    try:
        compile_user_docs_module(tmp_path)
        assert False, "expected UserDocsError"
    except UserDocsError as exc:
        assert any("verified_at" in e for e in exc.errors)


def test_descriptions_draft_warns(tmp_path: Path):
    _generated_repo(tmp_path)
    build_user_docs(tmp_path)
    errors, warnings = check_user_docs(tmp_path)
    assert not any("ADR-001" in e and "not mentioned" in e for e in errors)
    assert any("descriptions.yaml" in w and "draft" in w for w in warnings)


def test_unknown_generated_kind_is_error(tmp_path: Path):
    _generated_repo(
        tmp_path,
        extra_pages=[{"id": "nope", "generated": "nope", "title": "Нет"}],
        descriptions={"draft": True},
        extra_files={},
    )
    try:
        compile_user_docs_module(tmp_path)
        assert False, "expected UserDocsError"
    except UserDocsError as exc:
        assert any("unknown generated kind" in e for e in exc.errors)
