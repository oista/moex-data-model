from __future__ import annotations

from moex_publication_viewer.normalizers.mapping_label import mapping_display_label


def test_mapping_label_from_refs():
    assert (
        mapping_display_label(
            {
                "source_refs": ["dams:a"],
                "target_refs": ["dams:b", "dams:c"],
                "mapping_type": "field_mapping",
                "name": "ignored",
            }
        )
        == "dams:a -> dams:b, dams:c [field_mapping]"
    )


def test_mapping_label_falls_back_to_name():
    assert mapping_display_label({"name": "legacy"}) == "legacy"
