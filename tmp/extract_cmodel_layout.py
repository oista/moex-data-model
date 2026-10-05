"""Extract absolute table coordinates from CModel_content04.drawio into conceptual.layout.json."""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DRAWIO = Path(
    r"f:\!PASSPORT\!H_DATASC\!Data Architecture\MOEX_DataModel"
    r"\MOEX Data Model Standart\enterpise_cdm_src\CModel_content04.drawio"
)
ROOT = Path(__file__).resolve().parents[1]
OUT_LAYOUT = (
    ROOT
    / "model-assets/implementations/enterprise/moex-enterprise-conceptual-model"
    / "0.1/publications/conceptual.layout.json"
)
SCENE = OUT_LAYOUT.parent / "conceptual.scene.json"
DUMP = ROOT / "tmp/cmodel_content04_geometry.json"

DRAWIO_TO = {
    "Юрлица": "LegalEntity",
    "Физлица": "Person",
    "Клиенты": "Client",
    "Компании группы МБ": "CorporateGroup",
    "Участники торгов": "TradingParticipation",
    "Рынки": "TradingVenue",
    "Договора": "Agreement",
    "Учетные записи клиентов": "ClientAccount",
    "Эмитенты": "Issuer",
    "Активы": "Asset",
    "Инструменты": "Instrument",
    "Группы активов": "AssetGroup",
    "Пулы активов": "AssetPool",
    "Состав пулов активов": "AssetPoolMembership",
    "Бенчмарки": "Benchmark",
    "Торговые системы": "TradingSystem",
    "Режимы торгов": "TradingMode",
    "Торговые календари": "TradingCalendar",
    "Торговые сессии": "TradingSession",
    "Календарные дни": "CalendarDay",
    "Заявки ТКС": "Order",
    "Сделки ТКС": "Trade",
    "Открытые позиции": "OpenPosition",
    "Обеспечение участников": "Collateral",
    "Единые лимиты": "UnifiedLimit",
    "Требования и обязательства": "Obligation",
    "ММ программы": "MarketMakingProgram",
    "Участники ММ програм": "MarketMakingParticipation",
    "Корпоративные события": "CorporateAction",
    "Типы подключения": "ConnectionType",
    "Расчетные кода": "SettlementCode",
    "Торговые счета ТКС": "TradingAccount",
    "Логины ТКС": "TradingLogin",
    "Купонные выплаты": "CouponPayment",
    "Риск параметры активов": "AssetRiskParameter",
    "Контрагенты": "Counterparty",
    "Продукты": "Product",
    "Услуги": "Service",
    "Тарифы": "Tariff",
    "Платежи": "Payment",
    "Продажи": "Sale",
    "ЦФО": "CostCenter",
    "Доходы": "Income",
    "Расходы": "Expense",
    "Бюджеты": "Budget",
    "Проекты": "Project",
    "Задачи": "Task",
    "Трудозатраты": "TimeEntry",
    "Рейтинги": "Rating",
    "Фин отчетность": "FinancialReport",
    "Доп соглашения": "ContractAmendment",
    "Маркетинговые компании": "MarketingCampaign",
    "Состав компаний": "CampaignMembership",
    "Департаменты": "Department",
    "Штатное расписание": "StaffPosition",
    "Сотрудники": "Employee",
    "Трудовые договора": "EmploymentContract",
    "Роли": "Role",
    "Пользователь": "User",
    "Состав ролей": "RoleAssignment",
    "АБС": "AccountingSystem",
    "Счета АБС": "LedgerAccount",
    "Лицевые": "SubledgerAccount",
    "Счета пользователя": "UserLedgerLink",
    "Инфо-системы": "InformationSystem",
    "Проводки": "JournalEntry",
    "Акты": "Act",
    "Воронки": "SalesFunnel",
    "Депозиты": "Deposit",
    "Кривые": "Curve",
    "Портфель": "Portfolio",
    "События логинов": "LoginEvent",
    "Торговые терминалы": "TradingTerminal",
    "ЧПД": "ClearingPositionDetail",
}

# Extra CDM concepts not present as drawio tables — park next to their hub.
# (name): hub, dx, dy, color
EXTRAS = {
    "Organization": ("LegalEntity", -280, -20, "#0050ef"),
    "OrganizationIdentifier": ("LegalEntity", -280, 70, "#0050ef"),
    "TradingSection": ("TradingVenue", 0, 90, "#60a917"),
    "Admission": ("TradingParticipation", 280, -90, "#60a917"),
    "AccountRelationship": ("Agreement", 0, -90, "#0050ef"),
    "RegistrationAction": ("LegalEntity", -280, 160, "#0050ef"),
    "SupportingDocument": ("Agreement", -280, 90, "#0050ef"),
    "Currency": ("ClearingPositionDetail", 280, 0, "#0050ef"),
}


def unescape(v: str) -> str:
    return html.unescape((v or "").replace("&nbsp;", " ")).strip()


def get_attr(attrs: str, name: str) -> str | None:
    m = re.search(rf'{name}="([^"]*)"', attrs)
    return m.group(1) if m else None


def parse_geom(geom: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for key in ("x", "y", "width", "height"):
        m = re.search(rf'\b{key}="([^"]+)"', geom)
        if m:
            try:
                out[key] = float(m.group(1))
            except ValueError:
                pass
    out["relative"] = 'relative="1"' in geom
    pts = [
        (float(x), float(y))
        for x, y in re.findall(r'<mxPoint x="([^"]+)" y="([^"]+)"', geom)
    ]
    if pts:
        out["points"] = pts  # type: ignore[assignment]
    return out


def main() -> None:
    raw = DRAWIO.read_text(encoding="utf-8")
    blocks = re.findall(
        r'<diagram name="([^"]*)" id="([^"]*)">(.*?)</diagram>', raw, re.DOTALL
    )
    cells: dict[str, dict] = {}
    for _dname, _did, block in blocks:
        for m in re.finditer(r"<mxCell\s([^>]+?)(/?)>", block):
            attrs = m.group(1)
            cid = get_attr(attrs, "id")
            if not cid:
                continue
            geom_blob = ""
            if m.group(2) != "/":
                rest = block[m.end() : m.end() + 500]
                gm = re.match(
                    r"\s*<mxGeometry\b([^>]*)(?:/>|>.*?</mxGeometry>)",
                    rest,
                    re.DOTALL,
                )
                if gm:
                    geom_blob = gm.group(0)
            cells[cid] = {
                "attrs": attrs,
                "value": unescape(get_attr(attrs, "value") or ""),
                "parent": get_attr(attrs, "parent"),
                "style": get_attr(attrs, "style") or "",
                "vertex": get_attr(attrs, "vertex") == "1",
                "edge": get_attr(attrs, "edge") == "1",
                "source": get_attr(attrs, "source"),
                "target": get_attr(attrs, "target"),
                "geom": parse_geom(geom_blob) if geom_blob else {},
            }

    def abs_xy(cid: str, seen: set[str] | None = None) -> tuple[float, float]:
        seen = seen or set()
        if cid in seen:
            return (0.0, 0.0)
        seen.add(cid)
        cell = cells.get(cid) or {}
        g = cell.get("geom") or {}
        x = float(g.get("x") or 0)
        y = float(g.get("y") or 0)
        parent = cell.get("parent")
        if parent and parent not in ("0", "1"):
            px, py = abs_xy(parent, seen)
            if g.get("relative"):
                pg = (cells.get(parent) or {}).get("geom") or {}
                x = px + x * float(pg.get("width") or 0)
                y = py + y * float(pg.get("height") or 0)
            else:
                x += px
                y += py
        return (x, y)

    tables = []
    for cid, cell in cells.items():
        if not cell["vertex"]:
            continue
        if "shape=table;" not in cell["style"] or not cell["value"]:
            continue
        x, y = abs_xy(cid)
        fill_m = re.search(r"fillColor=([^;]+)", cell["style"])
        tables.append(
            {
                "id": cid,
                "name": cell["value"],
                "x": round(x, 1),
                "y": round(y, 1),
                "w": cell["geom"].get("width"),
                "h": cell["geom"].get("height"),
                "fill": fill_m.group(1) if fill_m else None,
                "parent": cell["parent"],
            }
        )

    print(f"tables={len(tables)} cells={len(cells)}")
    xs = [t["x"] for t in tables]
    ys = [t["y"] for t in tables]
    print(f"bbox x=[{min(xs):.0f},{max(xs):.0f}] y=[{min(ys):.0f},{max(ys):.0f}]")

    unmapped = [t["name"] for t in tables if t["name"] not in DRAWIO_TO]
    print("unmapped", unmapped)

    name_to_en = DRAWIO_TO
    pos_by_en: dict[str, dict] = {}
    for t in tables:
        en = name_to_en.get(t["name"])
        if not en:
            continue
        pos_by_en[en] = {
            "x": int(round(t["x"])),
            "y": int(round(t["y"])),
            "color": t["fill"] or "#F4B400",
            "drawio": t["name"],
        }

    BOX_W, BOX_H = 230, 80

    def overlaps(a: dict, b: dict) -> bool:
        return abs(a["x"] - b["x"]) < BOX_W and abs(a["y"] - b["y"]) < BOX_H

    def nudge(pos: dict, occupied: list[dict]) -> dict:
        out = dict(pos)
        for _ in range(40):
            if not any(overlaps(out, o) for o in occupied):
                return out
            out["y"] += BOX_H
        out["x"] += BOX_W
        return out

    occupied = list(pos_by_en.values())
    for extra, (hub, dx, dy, color) in EXTRAS.items():
        hub_pos = pos_by_en.get(hub)
        if not hub_pos:
            print("missing hub for extra", extra, hub)
            continue
        cand = {"x": hub_pos["x"] + dx, "y": hub_pos["y"] + dy, "color": color}
        cand = nudge(cand, occupied)
        pos_by_en[extra] = cand
        occupied.append(cand)

    scene = json.loads(SCENE.read_text(encoding="utf-8"))
    nodes_out: dict[str, dict] = {}
    missing_scene = []
    for node in scene.get("nodes") or []:
        name = node.get("name")
        eid = node.get("element_id")
        if name not in pos_by_en:
            missing_scene.append(name)
            continue
        p = pos_by_en[name]
        nodes_out[eid] = {"x": p["x"], "y": p["y"], "color": p["color"]}

    print("scene nodes", len(scene.get("nodes") or []), "laid out", len(nodes_out))
    print("missing from layout", missing_scene)

    # Compact: conceptual boxes are ~68px tall vs drawio tables ~120-180.
    # Keep original relative placement (structure), just shift origin to 40,40.
    min_x = min(v["x"] for v in nodes_out.values())
    min_y = min(v["y"] for v in nodes_out.values())
    ox, oy = 40 - min_x, 40 - min_y
    for v in nodes_out.values():
        v["x"] += ox
        v["y"] += oy

    layout = {
        "version": 1,
        "profile": "conceptual",
        "nodes": dict(sorted(nodes_out.items())),
        "edges": {},
    }
    OUT_LAYOUT.write_text(
        json.dumps(layout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    DUMP.write_text(
        json.dumps({"tables": tables, "pos_by_en": pos_by_en}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("WROTE", OUT_LAYOUT)
    print("all nodes (y, x):")
    for k in sorted(pos_by_en, key=lambda n: (pos_by_en[n]["y"], pos_by_en[n]["x"])):
        p = pos_by_en[k]
        print(f"  {p['x']:5d},{p['y']:5d}  {k:28s}  {p.get('drawio','')}")


if __name__ == "__main__":
    main()
