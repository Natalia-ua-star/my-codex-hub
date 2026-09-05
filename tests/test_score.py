"""Тести скорингу на реальних даних Amazon US, знятих 2026-09-05.

Цифри взяті з живої видачі DataForSEO, не вигадані. Якщо змінити формулу так,
що cat tunnel bed перестане обганяти зрілі товари — тести впадуть.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from winner_hunt.score import apply_velocity, score_item  # noqa: E402


def item(price, sold, votes, rating=4.5, **extra):
    return {
        "data_asin": extra.get("asin", "B000TEST"),
        "title": extra.get("title", "test"),
        "price_from": price,
        "bought_past_month": sold,
        "rating": {"value": rating, "votes_count": votes},
        **{k: v for k, v in extra.items() if k not in ("asin", "title")},
    }


# --- те, що агент має знаходити ---------------------------------------

def test_cat_tunnel_bed_is_the_winner():
    """$39.99, 4000 продажів, лише 419 відгуків — молодий лістинг, що вистрілив."""
    c = score_item(item(39.99, 4000, 419), "cat tunnel bed", "US")
    assert c.is_winner
    assert c.score > 14
    assert "молодий лістинг" in c.signals
    assert "преміум-ціна тримається" in c.signals


# --- те, що агент має відсівати ---------------------------------------

def test_saturated_fountain_rejected_on_price():
    """Veken 95oz: 10 000 продажів, але ціна збита до $19.99."""
    c = score_item(item(19.99, 10000, 43600), "cat water fountain", "US")
    assert not c.is_winner
    assert "маржу" in c.rejected


def test_rabbitgoo_harness_rejected():
    """197 000 відгуків і $16.98 — класична мертва зона."""
    c = score_item(item(16.98, 6000, 197000), "no pull dog harness", "US")
    assert not c.is_winner


def test_established_brand_rejected_on_votes():
    """Peekaboo Donut $69.99: ціна є, продажі є, але 4900 відгуків тиснуть score."""
    c = score_item(item(69.99, 1000, 4900), "cat tunnel bed", "US")
    assert c.is_winner  # формально проходить
    assert c.score < 1.0  # але score мізерний — у звіт не потрапить


def test_no_demand_rejected():
    c = score_item(item(29.99, 50, 12), "cat tunnel bed", "US")
    assert not c.is_winner
    assert "продажів замало" in c.rejected


def test_three_reviews_does_not_explode_score():
    """Захист від лістингів із 3 відгуками: ділимо мінімум на VOTES_FLOOR."""
    c = score_item(item(29.99, 500, 3), "test", "US")
    assert c.score < 10


# --- ранжування -------------------------------------------------------

def test_winner_outranks_incumbent():
    winner = score_item(item(39.99, 4000, 419), "cat tunnel bed", "US")
    incumbent = score_item(item(69.99, 1000, 4900), "cat tunnel bed", "US")
    assert winner.score > incumbent.score * 10


# --- динаміка ---------------------------------------------------------

def test_growth_boosts_score():
    c = score_item(item(39.99, 4000, 419), "cat tunnel bed", "US")
    base = c.score
    c = apply_velocity(c, previous_sold=1500)
    assert c.score > base
    assert any("x2" in s for s in c.signals)


def test_decline_penalised():
    c = score_item(item(39.99, 4000, 419), "cat tunnel bed", "US")
    base = c.score
    c = apply_velocity(c, previous_sold=9000)
    assert c.score < base
    assert "продажі падають" in c.signals


def test_missing_history_is_neutral():
    c = score_item(item(39.99, 4000, 419), "cat tunnel bed", "US")
    base = c.score
    assert apply_velocity(c, previous_sold=None).score == base
