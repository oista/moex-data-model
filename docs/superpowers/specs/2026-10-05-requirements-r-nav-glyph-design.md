# Requirements R nav glyph (DAMS «Требования»)

**Status:** approved for implementation  
**Date:** 2026-10-05  
**Project:** moex-data-model

## Problem

The three children of DAMS explorer «Требования» used inconsistent marks:
CDM plaque on «Концептуальная модель», generic group letter on «ИТ-решения»
and «Публикация». They should share one Requirements document+R icon.

## Decisions

| Topic | Choice |
|-------|--------|
| Glyph id | `nav_glyph: requirements` |
| Targets | `requirements-conceptual`, `requirements-it-solutions`, `requirements-publication` |
| Visual | Dog-ear document stroke `#ff6641` + letter **R** (mirror yaml mark slot) |
| Letter size | Match `.nav-kind` letters (C/T/G), not oversized source artwork |
| Conceptual CDM | Replaced by `requirements` on this folder only |

## Out of scope

- `source_file` yaml icons on leaves
- CDM/LDM/PDM plaques on section folders / Impl nav
- Requirement card letter `T`
