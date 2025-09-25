"""Central definitions for transaction types and strategies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass(frozen=True)
class TypeMeta:
    value: str
    label: str
    description: str
    category: str
    icon: str


@dataclass(frozen=True)
class StrategyMeta:
    value: str
    label: str
    description: str
    icon: str


TYPE_CATEGORIES: Dict[str, Dict[str, Dict[str, str]]] = {
    "trade": {
        "label": "Торговые операции",
        "types": {
            "trade_buy": {
                "label": "Покупка",
                "description": "Увеличение позиции за счет покупки актива",
                "icon": "📈",
            },
            "trade_sell": {
                "label": "Продажа",
                "description": "Частичное или полное закрытие позиции",
                "icon": "📉",
            },
        },
    },
    "transfer": {
        "label": "Переводы",
        "types": {
            "transfer_in": {
                "label": "Ввод на платформу",
                "description": "Перевод средств с другой площадки или кошелька",
                "icon": "↗️",
            },
            "transfer_out": {
                "label": "Вывод с платформы",
                "description": "Перевод средств на другую площадку или кошелек",
                "icon": "↘️",
            },
        },
    },
    "fiat": {
        "label": "Фиат",
        "types": {
            "fiat_deposit": {
                "label": "Пополнение фиатом",
                "description": "Ввод фиатных средств на биржу или сервис",
                "icon": "💵",
            },
            "fiat_withdrawal": {
                "label": "Вывод фиата",
                "description": "Вывод фиатных средств на счет или карту",
                "icon": "🏦",
            },
        },
    },
    "income": {
        "label": "Доход",
        "types": {
            "income_staking": {
                "label": "Стейкинг / фарминг",
                "description": "Получение вознаграждений за участие в стейкинге",
                "icon": "🌱",
            },
            "income_airdrop": {
                "label": "Эйрдроп / бонус",
                "description": "Получение монет в рамках эйрдропов и акций",
                "icon": "🎁",
            },
            "income_other": {
                "label": "Другой доход",
                "description": "Реферальные, программы лояльности и др.",
                "icon": "💡",
            },
        },
    },
    "expense": {
        "label": "Расходы",
        "types": {
            "expense_fee": {
                "label": "Комиссия",
                "description": "Оплата комиссий биржи или сервиса",
                "icon": "💸",
            },
        },
    },
}


STRATEGY_DEFINITIONS: Dict[str, Dict[str, str]] = {
    "long_term": {
        "label": "Долгосрочная",
        "description": "Инвестиции на месяцы и годы, ставка на рост",
        "icon": "🛡️",
    },
    "swing": {
        "label": "Свинг",
        "description": "Среднесрочные сделки от нескольких дней до недель",
        "icon": "🌊",
    },
    "scalp": {
        "label": "Скальпинг",
        "description": "Краткосрочные сделки в течение дня",
        "icon": "⚡",
    },
    "arbitrage": {
        "label": "Арбитраж",
        "description": "Использование ценовых различий между площадками",
        "icon": "🔁",
    },
    "hedge": {
        "label": "Хеджирование",
        "description": "Снижение рисков за счёт противоположных позиций",
        "icon": "🛠️",
    },
    "income_hold": {
        "label": "Доходное удержание",
        "description": "Держу актив ради дохода от стейкинга/дивидендов",
        "icon": "💎",
    },
}


TYPE_ALIASES = {
    "buy": "trade_buy",
    "sell": "trade_sell",
    "exchange_in": "transfer_in",
    "exchange_out": "transfer_out",
    "deposit": "transfer_in",
    "withdrawal": "transfer_out",
}

STRATEGY_ALIASES = {
    "long": "long_term",
    "mid": "swing",
    "short": "swing",
    "scalp": "scalp",
}


def _flatten_types() -> Dict[str, TypeMeta]:
    result: Dict[str, TypeMeta] = {}
    for category_key, category_data in TYPE_CATEGORIES.items():
        category_label = category_data["label"]
        for value, definition in category_data["types"].items():
            result[value] = TypeMeta(
                value=value,
                label=f"{definition['icon']} {definition['label']}",
                description=definition["description"],
                category=category_label,
                icon=definition["icon"],
            )
    return result


TYPE_META: Dict[str, TypeMeta] = _flatten_types()
STRATEGY_META: Dict[str, StrategyMeta] = {
    value: StrategyMeta(
        value=value,
        label=f"{definition['icon']} {definition['label']}",
        description=definition["description"],
        icon=definition["icon"],
    )
    for value, definition in STRATEGY_DEFINITIONS.items()
}


TRADE_TYPES = {"trade_buy", "trade_sell"}
TRANSFER_TYPES = {"transfer_in", "transfer_out"}
FIAT_TYPES = {"fiat_deposit", "fiat_withdrawal"}
INCOME_TYPES = {"income_staking", "income_airdrop", "income_other"}
EXPENSE_TYPES = {"expense_fee"}

INBOUND_POSITION_TYPES = {"trade_buy", "transfer_in", *INCOME_TYPES}
OUTBOUND_POSITION_TYPES = {"trade_sell", "transfer_out", "expense_fee"}


def normalize_transaction_type(value: str | None) -> str:
    if not value:
        return "trade_buy"
    value = value.strip().lower()
    return TYPE_ALIASES.get(value, value)


def normalize_strategy(value: str | None) -> str:
    if not value:
        return "long_term"
    value = value.strip().lower()
    return STRATEGY_ALIASES.get(value, value)


def get_type_meta(value: str) -> TypeMeta | None:
    return TYPE_META.get(value)


def get_strategy_meta(value: str) -> StrategyMeta | None:
    return STRATEGY_META.get(value)


def iter_type_meta(values: Iterable[str] | None = None) -> Iterable[TypeMeta]:
    if values is None:
        return TYPE_META.values()
    return (TYPE_META[v] for v in values if v in TYPE_META)


def iter_strategy_meta(values: Iterable[str] | None = None) -> Iterable[StrategyMeta]:
    if values is None:
        return STRATEGY_META.values()
    return (STRATEGY_META[v] for v in values if v in STRATEGY_META)

