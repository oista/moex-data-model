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


REASON = "ещё не описано; появится в PR-2 или PR-3"


def _write_user_docs(
    root: Path,
    *,
    page_body: str | None = None,
    glossary_terms: list[dict] | None = None,
    not_covered: list[dict] | None = None,
    sources: list[str] | None = None,
    verified_at: str = "2099-01-01",
    include_adr_fixture: bool = True,
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
                    }
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
    return docs_user


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
