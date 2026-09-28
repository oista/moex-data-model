"""Extract searchable elements from a DAMS ModelPackage dict."""

from __future__ import annotations

from typing import Any

from moex_dams.application.element_index import build_element_index

from moex_model_api.ports import IndexElement


def elements_from_package(data: dict[str, Any]) -> list[IndexElement]:
    return [
        IndexElement(
            element_id=e.element_id,
            element_kind=e.element_kind,
            name=e.name,
            layer=e.layer,
        )
        for e in build_element_index(data)
    ]
