"""Оцінка товару як winner-кандидата.

Формула виведена з реальних даних Amazon US (вересень 2026) і побудована
навколо одного спостереження: **великі продажі при малій кількості відгуків**
означають молодий лістинг, який щойно почав вистрілювати. Саме туди ще можна
зайти. Великі продажі при десятках тисяч відгуків означають зрілий ринок,
де ціна вже збита і місця немає.

Перевірка на живих цифрах:
    Cat Tunnel Bed   $39.99   4 000 прод.     419 відг.  -> 15.3  вікно відкрите
    Veken 95oz       $19.99  10 000 прод.  43 600 відг.  -> відсів (ціна < $20)
    rabbitgoo harness $16.98  6 000 прод. 197 000 відг.  -> відсів (ціна < $20)
    Peekaboo Donut   $69.99   1 000 прод.   4 900 відг.  ->  0.6  ринок зайнято
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Нижче цієї ціни дропшипінг не окупає рекламу: при CPA $12-18 на Meta
# товар за $17 працює в мінус, скільки б його не продавали.
MIN_PRICE_USD = 20.0
# Менше цього — попиту ще нема, це не товар, а гіпотеза.
MIN_SOLD_PER_MONTH = 300
# Більше цього — бренди вже закріпились, обганяти їх нема чим.
MAX_VOTES = 5_000
# Ділимо на щонайменше цю кількість відгуків, щоб лістинг із 3 відгуками
# і 500 продажами не давав score у сотні.
VOTES_FLOOR = 100
# Ціна, від якої рахується множник маржі.
PRICE_ANCHOR = 25.0
MARGIN_CAP = 3.0


@dataclass
class Candidate:
    keyword: str
    asin: str
    title: str
    price: float | None
    sold_per_month: int | None
    votes: int
    rating: float | None
    market: str
    score: float = 0.0
    rejected: str | None = None
    signals: list[str] = field(default_factory=list)

    @property
    def is_winner(self) -> bool:
        return self.rejected is None


def score_item(item: dict, keyword: str, market: str) -> Candidate:
    """Оцінює один елемент Amazon SERP (amazon_serp) у Candidate."""
    rating = item.get("rating") or {}
    cand = Candidate(
        keyword=keyword,
        asin=item.get("data_asin") or "",
        title=(item.get("title") or "")[:120],
        price=_as_float(item.get("price_from")),
        sold_per_month=_as_int(item.get("bought_past_month")),
        votes=_as_int(rating.get("votes_count")) or 0,
        rating=_as_float(rating.get("value")),
        market=market,
    )

    if cand.price is None:
        cand.rejected = "нема ціни"
        return cand
    if cand.price < MIN_PRICE_USD:
        cand.rejected = f"ціна ${cand.price:.2f} < ${MIN_PRICE_USD:.0f} — реклама з'їсть маржу"
        return cand
    if cand.sold_per_month is None or cand.sold_per_month < MIN_SOLD_PER_MONTH:
        cand.rejected = "продажів замало або невідомо"
        return cand
    if cand.votes > MAX_VOTES:
        cand.rejected = f"{cand.votes} відгуків — ринок зайнято"
        return cand

    freshness = cand.sold_per_month / max(cand.votes, VOTES_FLOOR)
    margin = min(cand.price / PRICE_ANCHOR, MARGIN_CAP)
    cand.score = round(freshness * margin, 2)

    if cand.votes < 500:
        cand.signals.append("молодий лістинг")
    if cand.price >= 35:
        cand.signals.append("преміум-ціна тримається")
    if item.get("is_best_seller"):
        cand.signals.append("Best Seller")
    if item.get("is_amazon_choice"):
        cand.signals.append("Amazon's Choice")
    if cand.rating is not None and cand.rating < 4.2:
        cand.signals.append("низький рейтинг — питання до якості")
    return cand


def apply_velocity(cand: Candidate, previous_sold: int | None) -> Candidate:
    """Множник за приріст продажів відносно попереднього запуску.

    Це те, заради чого агент має ходити щодня: одноразовий зріз показує стан,
    а історія показує рух. Товар, що подвоївся за тиждень, цінніший за товар
    із такими самими абсолютними цифрами, який стоїть на місці.
    """
    if previous_sold is None or previous_sold <= 0 or cand.sold_per_month is None:
        return cand
    growth = cand.sold_per_month / previous_sold
    if growth >= 2.0:
        cand.score = round(cand.score * 1.5, 2)
        cand.signals.append(f"продажі x{growth:.1f} з минулого разу")
    elif growth >= 1.3:
        cand.score = round(cand.score * 1.2, 2)
        cand.signals.append(f"продажі +{(growth - 1) * 100:.0f}%")
    elif growth <= 0.6:
        cand.score = round(cand.score * 0.7, 2)
        cand.signals.append("продажі падають")
    return cand


def _as_float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
