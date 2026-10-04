import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")

data = yaml.safe_load(
    Path(
        "model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/enterprise-conceptual-model.yaml"
    ).read_text(encoding="utf-8")
)
inv = Path("tmp/cmodel_content04_inventory.md").read_text(encoding="utf-8")

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

sec = inv.split("## Relationships (draw.io edges, entity-resolved)")[1].split("## FK hints")[0]
rows = []
for line in sec.splitlines():
    if not line.startswith("|"):
        continue
    parts = [p.strip() for p in line.strip("|").split("|")]
    a, b = parts[0], parts[1]
    if a in ("From", "------") or a.startswith("-"):
        continue
    rows.append((a, b))

cdm_pairs = set()
for r in data["relationships"]:
    cdm_pairs.add(
        frozenset(
            [
                r["source_entity_ref"].split("/")[-1],
                r["target_entity_ref"].split("/")[-1],
            ]
        )
    )

print("visual edges", len(rows))
broken = []
missing = []
present = []
for a, b in rows:
    if a not in DRAWIO_TO or b not in DRAWIO_TO:
        broken.append((a, b))
        continue
    key = frozenset([DRAWIO_TO[a], DRAWIO_TO[b]])
    if key in cdm_pairs:
        present.append((a, b, DRAWIO_TO[a], DRAWIO_TO[b]))
    else:
        missing.append((a, b, DRAWIO_TO[a], DRAWIO_TO[b]))
print("present", len(present), "missing", len(missing), "broken sketch", len(broken))
for x in missing:
    print(" MISSING", x)
for x in broken:
    print(" BROKEN", x)

fk_expect = [
    ("Trade", "Client"),
    ("Client", "Person"),
    ("Client", "LegalEntity"),
    ("TradingParticipation", "LegalEntity"),
    ("Instrument", "Issuer"),
    ("Instrument", "Asset"),
    ("Order", "TradingParticipation"),
    ("Order", "Instrument"),
    ("TradingLogin", "ConnectionType"),
    ("UserLedgerLink", "Currency"),
    ("UserLedgerLink", "LedgerAccount"),
    ("CorporateAction", "Instrument"),
    ("CorporateAction", "Issuer"),
    ("CouponPayment", "Instrument"),
    ("CouponPayment", "CorporateAction"),
    ("OpenPosition", "TradingParticipation"),
    ("OpenPosition", "Instrument"),
    ("CalendarDay", "TradingCalendar"),
    ("MarketMakingParticipation", "MarketMakingProgram"),
    ("Counterparty", "LegalEntity"),
    ("Rating", "LegalEntity"),
    ("Agreement", "Counterparty"),
    ("Agreement", "CorporateGroup"),
    ("Sale", "Client"),
    ("Sale", "Product"),
    ("FinancialReport", "LegalEntity"),
    ("Issuer", "LegalEntity"),
]
print("\nFK semantic coverage missing:")
any_miss = False
for a, b in fk_expect:
    if frozenset([a, b]) not in cdm_pairs:
        print(" MISSING FK", a, b)
        any_miss = True
if not any_miss:
    print(" (none)")

deg = defaultdict(int)
for a, b in rows:
    if a in DRAWIO_TO:
        deg[DRAWIO_TO[a]] += 1
    if b in DRAWIO_TO:
        deg[DRAWIO_TO[b]] += 1
print("\nDrawio tables with 0 resolved visual edges:")
for ru, en in sorted(DRAWIO_TO.items(), key=lambda x: x[1]):
    if deg[en] == 0:
        print(f"  {ru} -> {en}")

print("\nShort descriptions (<=40 chars):")
for c in data["conceptual_entities"]:
    d = (c.get("description") or "").strip().replace("\n", " ")
    if len(d) <= 40:
        print(f"  {c['name']}: {d!r}")

used = {r.get("relation_term_ref") for r in data["relationships"]}
print("\nUnused terms:")
for t in data["relation_terms"]:
    if t["element_id"] not in used:
        print(" ", t["name"], t["element_id"])

linked = set()
for r in data["relationships"]:
    linked.add(r["source_entity_ref"].split("/")[-1])
    linked.add(r["target_entity_ref"].split("/")[-1])
parents = {
    c["name"]: (c.get("parent_concept_ref") or "").split("/")[-1]
    for c in data["conceptual_entities"]
}
print("\nIsolates with parent:")
for c in data["conceptual_entities"]:
    n = c["name"]
    if n not in linked:
        print(" ", n, "parent=", parents[n] or "-", "tier=", c.get("entity_tier"))
