"""SQLite projection of ontology releases, entities, and relations."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from moex_ontology.domain.entity import OntologyEntity
from moex_ontology.domain.ontology import OntologyRelease
from moex_ontology.domain.relation import OntologyRelation

SCHEMA = """
CREATE TABLE IF NOT EXISTS releases (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entities (
    iri TEXT PRIMARY KEY,
    ontology_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    label TEXT,
    definition TEXT,
    search_text TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS relations (
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    asserted INTEGER NOT NULL,
    source_ontology TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entities_ontology ON entities(ontology_id);
CREATE INDEX IF NOT EXISTS idx_entities_search ON entities(search_text);
CREATE INDEX IF NOT EXISTS idx_relations_subject ON relations(subject);
CREATE INDEX IF NOT EXISTS idx_relations_object ON relations(object);
"""


class SqliteOntologyIndex:
    def __init__(self, path: Path) -> None:
        self.path = path.expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def replace_all(
        self,
        *,
        releases: list[OntologyRelease],
        entities: list[OntologyEntity],
        relations: list[OntologyRelation],
    ) -> None:
        cur = self._conn.cursor()
        cur.execute("DELETE FROM relations")
        cur.execute("DELETE FROM entities")
        cur.execute("DELETE FROM releases")
        for rel in releases:
            cur.execute(
                "INSERT INTO releases(id, payload) VALUES (?, ?)",
                (rel.id, rel.model_dump_json()),
            )
        for ent in entities:
            search = " ".join(
                filter(
                    None,
                    [
                        ent.iri,
                        ent.label,
                        ent.definition,
                        " ".join(ent.alternative_labels),
                        ent.kind,
                    ],
                )
            ).lower()
            cur.execute(
                "INSERT INTO entities(iri, ontology_id, kind, label, definition, search_text, payload) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    ent.iri,
                    ent.ontology_id,
                    ent.kind,
                    ent.label,
                    ent.definition,
                    search,
                    ent.model_dump_json(),
                ),
            )
        for edge in relations:
            cur.execute(
                "INSERT INTO relations(subject, predicate, object, asserted, source_ontology) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    edge.subject,
                    edge.predicate,
                    edge.object,
                    1 if edge.asserted else 0,
                    edge.source_ontology,
                ),
            )
        self._conn.commit()

    def list_releases(self) -> list[OntologyRelease]:
        rows = self._conn.execute("SELECT payload FROM releases ORDER BY id").fetchall()
        return [OntologyRelease.model_validate_json(r["payload"]) for r in rows]

    def get_release(self, ontology_id: str) -> OntologyRelease | None:
        row = self._conn.execute(
            "SELECT payload FROM releases WHERE id = ?", (ontology_id,)
        ).fetchone()
        if row is None:
            return None
        return OntologyRelease.model_validate_json(row["payload"])

    def get_entity(self, iri: str) -> OntologyEntity | None:
        row = self._conn.execute(
            "SELECT payload FROM entities WHERE iri = ?", (iri,)
        ).fetchone()
        if row is None:
            return None
        return OntologyEntity.model_validate_json(row["payload"])

    def search_entities(self, query: str, *, limit: int = 50) -> list[OntologyEntity]:
        q = f"%{query.strip().lower()}%"
        rows = self._conn.execute(
            "SELECT payload FROM entities WHERE search_text LIKE ? ORDER BY label LIMIT ?",
            (q, limit),
        ).fetchall()
        return [OntologyEntity.model_validate_json(r["payload"]) for r in rows]

    def relations_for(
        self,
        iri: str,
        *,
        predicate: str | None = None,
    ) -> list[OntologyRelation]:
        if predicate:
            rows = self._conn.execute(
                "SELECT subject, predicate, object, asserted, source_ontology FROM relations "
                "WHERE (subject = ? OR object = ?) AND predicate = ?",
                (iri, iri, predicate),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT subject, predicate, object, asserted, source_ontology FROM relations "
                "WHERE subject = ? OR object = ?",
                (iri, iri),
            ).fetchall()
        return [
            OntologyRelation(
                subject=r["subject"],
                predicate=r["predicate"],
                object=r["object"],
                asserted=bool(r["asserted"]),
                source_ontology=r["source_ontology"],
            )
            for r in rows
        ]

    def entity_count(self, ontology_id: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) AS c FROM entities WHERE ontology_id = ?",
            (ontology_id,),
        ).fetchone()
        return int(row["c"]) if row else 0

    def list_entities(self, *, ontology_id: str | None = None) -> list[OntologyEntity]:
        if ontology_id:
            rows = self._conn.execute(
                "SELECT payload FROM entities WHERE ontology_id = ? ORDER BY label, iri",
                (ontology_id,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT payload FROM entities ORDER BY label, iri"
            ).fetchall()
        return [OntologyEntity.model_validate_json(r["payload"]) for r in rows]

    def kind_counts(self, ontology_id: str) -> dict[str, int]:
        rows = self._conn.execute(
            "SELECT kind, COUNT(*) AS c FROM entities WHERE ontology_id = ? GROUP BY kind",
            (ontology_id,),
        ).fetchall()
        return {r["kind"]: int(r["c"]) for r in rows}
