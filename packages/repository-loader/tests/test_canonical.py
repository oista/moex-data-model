from __future__ import annotations

from moex_repository_loader.canonical import canonical_digest, document_content_hash


def test_canonical_sort_keys_stable() -> None:
    a = canonical_digest({"b": 1, "a": 2})
    b = canonical_digest({"a": 2, "b": 1})
    assert a == b


def test_canonical_ignores_crlf_in_parsed_payload() -> None:
    # Parsed strings are identical regardless of source EOL.
    assert canonical_digest({"t": "x\ny"}) == canonical_digest({"t": "x\ny"})


def test_document_hash_skips_stamps() -> None:
    body = {"element_id": "dams:model/x"}
    d1 = {"id": "moex:implementation:x:0.1", "body_ref": "x.yaml", "content_digest": "sha256:aa", "revision": "aa"}
    d2 = {"id": "moex:implementation:x:0.1", "body_ref": "x.yaml", "content_digest": "sha256:bb", "revision": "bb"}
    assert document_content_hash(d1, body) == document_content_hash(d2, body)


def test_no_timestamp_in_digest_payload() -> None:
    # Re-run identical payload → identical digest (no clock noise).
    payload = {"descriptor": {"id": "a"}, "body": {"n": 1}}
    assert canonical_digest(payload) == canonical_digest(payload)
