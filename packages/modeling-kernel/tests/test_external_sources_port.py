"""Shape checks for SpecificationSource port (ADR-017)."""

from __future__ import annotations

from moex_modeling.external_sources.public import (
    LocalArtifact,
    LockEntry,
    MaterializationPolicy,
    RawArtifactBundle,
    SourceKind,
    SourceVersionRef,
    SpecDiff,
    SpecDiffChange,
    SpecificationSource,
)


def test_source_version_ref_and_bundle() -> None:
    version = SourceVersionRef(
        source_id="fibo",
        upstream_ref="2026Q2",
        resolved_uri="https://github.com/edmcouncil/fibo/releases/tag/master_2026Q2",
    )
    bundle = RawArtifactBundle(
        source_id="fibo",
        version=version,
        root_path="/tmp/mirror/fibo",
        artifact_paths=("FND/Master/Master.rdf",),
        content_digest="sha256:abc",
    )
    assert bundle.version.upstream_ref == "2026Q2"
    assert len(bundle.artifact_paths) == 1


def test_local_artifact_and_lock_entry() -> None:
    version = SourceVersionRef(source_id="fibo", upstream_ref="2026Q2")
    artifact = LocalArtifact(
        source_id="fibo",
        kind=SourceKind.ONTOLOGY,
        path="modules/fibo-counterparty.ttl",
        content_digest="sha256:mod",
        version=version,
        extraction_method="BOT",
        seed_digest="sha256:seed",
    )
    entry = LockEntry(
        source_id=artifact.source_id,
        kind=artifact.kind,
        upstream_ref=artifact.version.upstream_ref,
        content_hash=artifact.content_digest,
        extraction_method=artifact.extraction_method,
        seed_hash=artifact.seed_digest,
        tool_versions={"robot": "1.9.5"},
        artifact_path=artifact.path,
    )
    assert entry.kind == SourceKind.ONTOLOGY
    assert entry.tool_versions["robot"] == "1.9.5"


def test_spec_diff_and_policy() -> None:
    diff = SpecDiff(
        source_id="openapi-fix44",
        old_digest="sha256:a",
        new_digest="sha256:b",
        breaking=True,
        changes=(
            SpecDiffChange(
                path="spec/fix44.yaml",
                change_kind="modified",
                summary="paths removed",
            ),
        ),
    )
    policy = MaterializationPolicy(
        out_dir="model-assets/external-sources/fibo/modules",
        seed_path="seeds/counterparty.txt",
        extraction_method="BOT",
        dry_run=True,
    )
    assert diff.breaking is True
    assert policy.dry_run is True


def test_specification_source_protocol_is_runtime_checkable() -> None:
    class Stub:
        @property
        def source_id(self) -> str:
            return "fibo"

        @property
        def kind(self) -> SourceKind:
            return SourceKind.ONTOLOGY

        def resolve_latest(self) -> SourceVersionRef:
            return SourceVersionRef(source_id=self.source_id, upstream_ref="latest")

        def fetch(self, version_ref: SourceVersionRef) -> RawArtifactBundle:
            return RawArtifactBundle(
                source_id=self.source_id,
                version=version_ref,
                root_path="/tmp",
            )

        def materialize(
            self,
            bundle: RawArtifactBundle,
            policy: MaterializationPolicy,
        ) -> LocalArtifact:
            return LocalArtifact(
                source_id=self.source_id,
                kind=self.kind,
                path=policy.out_dir,
                content_digest="sha256:x",
                version=bundle.version,
            )

        def diff(self, old: LocalArtifact, new: LocalArtifact) -> SpecDiff:
            return SpecDiff(
                source_id=self.source_id,
                old_digest=old.content_digest,
                new_digest=new.content_digest,
            )

        def lock(self, artifact: LocalArtifact) -> LockEntry:
            return LockEntry(
                source_id=artifact.source_id,
                kind=artifact.kind,
                upstream_ref=artifact.version.upstream_ref,
                content_hash=artifact.content_digest,
            )

    assert isinstance(Stub(), SpecificationSource)
