"""Щоденний пошук winner-товарів для дропшипінгу.

Порядок кроків не випадковий — від дешевого до дорогого:

    1. Тренди (~$0.0024 за 5 ключів)  -> відсіює мертві теми до будь-яких витрат
    2. Amazon  (~$0.003 за ключ)      -> ціни, продажі, відгуки по тих, що вижили
    3. Скоринг (безкоштовно)          -> продажі/відгуки x маржа
    4. Історія (безкоштовно)          -> приріст відносно вчора
    5. Apify   (за тарифом Apify)     -> віральність тільки для фіналістів

Запуск:  python -m winner_hunt.run
"""

from __future__ import annotations

import csv
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from winner_hunt.aisa import Aisa, AisaError, BudgetExceeded  # noqa: E402
from winner_hunt.apify import Apify, ApifyError, virality_signal  # noqa: E402
from winner_hunt.score import apply_velocity, score_item  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
HISTORY = ROOT / "reports" / "history.json"
TRENDS_OP = "post_dataforseo_keywords_trends_explore_live"
AMZ_SUBMIT = "post_dataforseo_merchant_amazon_products_submit"
AMZ_FETCH = "get_dataforseo_merchant_amazon_products_fetch"


def load_config() -> dict:
    import yaml

    return yaml.safe_load((Path(__file__).parent / "config.yaml").read_text())


# --- крок 1: тренди ---------------------------------------------------

def filter_by_trend(aisa: Aisa, keywords: list[str], cfg: dict) -> list[str]:
    """Відсіює ключі з мертвим попитом до того, як витрачати на Amazon.

    Тренди порівнюються лише ВСЕРЕДИНІ одного виклику — значення відносні
    до максимуму в п'ятірці. Тому ключі йдуть групами по 5, і поріг
    застосовується в межах групи, а не між групами.
    """
    if not cfg["trends"]["enabled"]:
        return keywords

    survivors: list[str] = []
    for chunk in _chunks(keywords, 5):
        try:
            data = aisa.use(
                TRENDS_OP,
                {
                    "body": [
                        {
                            "keywords": chunk,
                            "type": cfg["trends"]["type"],
                            "time_range": cfg["trends"]["time_range"],
                        }
                    ]
                },
            )
        except BudgetExceeded:
            raise
        except AisaError as exc:
            print(f"  тренди впали ({exc}) — пропускаю групу без відсіву")
            survivors.extend(chunk)
            continue

        averages = _dig(data, "data", "tasks", 0, "result", 0, "items", 0, "averages")
        if not averages:
            survivors.extend(chunk)
            continue

        threshold = cfg["trends"]["min_avg_interest"]
        for keyword, avg in zip(chunk, averages):
            if avg >= threshold:
                survivors.append(keyword)
            else:
                print(f"  ✗ {keyword}: інтерес {avg} < {threshold}")
    return survivors


# --- крок 2: Amazon ---------------------------------------------------

def fetch_amazon(aisa: Aisa, keywords: list[str], market: dict, cfg: dict) -> dict:
    """Ставить задачі, потім забирає. Fetch безкоштовний, тому чекати дешево."""
    tasks: dict[str, str] = {}
    for keyword in keywords:
        try:
            data = aisa.use(
                AMZ_SUBMIT,
                {
                    "body": [
                        {
                            "keyword": keyword,
                            "location_code": market["location_code"],
                            "language_code": market["language_code"],
                            "se_domain": market["se_domain"],
                            "depth": cfg["amazon"]["depth"],
                        }
                    ]
                },
            )
        except BudgetExceeded:
            print("  бюджет вичерпано — далі не ставлю задачі")
            break
        except AisaError as exc:
            print(f"  ✗ submit {keyword}: {exc}")
            continue

        task_id = _dig(data, "data", "tasks", 0, "id")
        if task_id:
            tasks[keyword] = task_id

    results: dict[str, list] = {}
    pending = dict(tasks)
    for attempt in range(12):
        if not pending:
            break
        if attempt:
            import time

            time.sleep(10)
        for keyword, task_id in list(pending.items()):
            try:
                data = aisa.use(AMZ_FETCH, {"id": task_id})
            except AisaError as exc:
                print(f"  ✗ fetch {keyword}: {exc}")
                pending.pop(keyword, None)
                continue
            status = _dig(data, "data", "tasks", 0, "status_message") or ""
            if "Queue" in status:
                continue
            items = _dig(data, "data", "tasks", 0, "result", 0, "items") or []
            results[keyword] = [i for i in items if i.get("type") == "amazon_serp"]
            pending.pop(keyword, None)

    for keyword in pending:
        print(f"  ⏳ {keyword}: не дочекався результату")
    return results


# --- крок 4: історія --------------------------------------------------

def load_history() -> dict:
    if HISTORY.exists():
        return json.loads(HISTORY.read_text())
    return {}


def save_history(history: dict, candidates: list) -> None:
    for cand in candidates:
        if cand.asin and cand.sold_per_month:
            history[cand.asin] = {
                "sold": cand.sold_per_month,
                "price": cand.price,
                "votes": cand.votes,
                "seen": date.today().isoformat(),
            }
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False))


# --- звіт -------------------------------------------------------------

def write_report(candidates: list, cfg: dict, spent: float, stopped: str | None) -> Path:
    today = date.today().isoformat()
    REPORTS.mkdir(parents=True, exist_ok=True)

    winners = [c for c in candidates if c.is_winner and c.score >= cfg["report"]["min_score"]]
    winners.sort(key=lambda c: c.score, reverse=True)
    winners = winners[: cfg["report"]["top_n"]]

    csv_path = REPORTS / f"{today}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        # Search date — вимога з AGENTS.md: кожен рядок дослідження датований.
        writer.writerow(
            ["Search date", "Score", "Keyword", "Market", "Price USD",
             "Sold/month", "Reviews", "Rating", "ASIN", "Signals", "Title", "URL"]
        )
        for c in winners:
            writer.writerow([
                today, c.score, c.keyword, c.market, c.price, c.sold_per_month,
                c.votes, c.rating, c.asin, "; ".join(c.signals), c.title,
                f"https://www.amazon.com/dp/{c.asin}" if c.asin else "",
            ])

    lines = [
        f"# Winner-кандидати — {today}",
        "",
        f"Перевірено позицій: {len(candidates)} · пройшли фільтр: "
        f"{len([c for c in candidates if c.is_winner])} · у звіті: {len(winners)}",
        f"Витрачено AIsa: **${spent:.4f}**",
    ]
    if stopped:
        lines.append(f"\n> ⚠️ Прогін зупинено достроково: {stopped}")

    if not winners:
        lines += ["", "Сьогодні нічого не пройшло поріг. Це нормальний результат —",
                  "означає, що витрачати на рекламу нема на що."]
    else:
        lines += ["", "| # | Score | Товар | Ціна | Прод./міс | Відгуків | Сигнали |",
                  "|---|-------|-------|------|-----------|----------|---------|"]
        for n, c in enumerate(winners, 1):
            lines.append(
                f"| {n} | **{c.score}** | [{c.title[:45]}]"
                f"(https://www.amazon.com/dp/{c.asin}) | ${c.price} | "
                f"{c.sold_per_month} | {c.votes} | {'; '.join(c.signals) or '—'} |"
            )
        lines += [
            "",
            "**Як читати score:** це продажі, поділені на відгуки, помножені на маржу.",
            "Високий score = товар продається, але відгуків ще мало, тобто лістинг",
            "молодий і місце ще не зайняте. Низький score при великих продажах",
            "означає зрілий ринок, куди заходити пізно.",
            "",
            f"Дані CSV: `reports/{today}.csv`",
        ]

    md_path = REPORTS / f"{today}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


# --- головне ----------------------------------------------------------

def main() -> int:
    cfg = load_config()
    aisa = Aisa(budget_usd=cfg["budget"]["max_usd_per_run"])
    stopped: str | None = None

    print(f"Старт {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")
    print(f"Ліміт витрат: ${cfg['budget']['max_usd_per_run']:.2f}")

    keywords = cfg["keywords"]
    candidates = []
    history = load_history()

    try:
        print(f"\n[1/4] Тренди — {len(keywords)} ключів")
        keywords = filter_by_trend(aisa, keywords, cfg)
        print(f"  вижило: {len(keywords)}")

        for market in cfg["markets"]:
            print(f"\n[2/4] Amazon {market['name']} — {len(keywords)} ключів")
            found = fetch_amazon(aisa, keywords, market, cfg)
            for keyword, items in found.items():
                for item in items:
                    cand = score_item(item, keyword, market["name"])
                    previous = history.get(cand.asin, {}).get("sold")
                    candidates.append(apply_velocity(cand, previous))
    except BudgetExceeded as exc:
        stopped = str(exc)
        print(f"\n⚠️ {stopped}")

    print(f"\n[3/4] Скоринг — {len(candidates)} позицій")

    print("\n[4/4] Віральність")
    _add_virality(candidates, cfg)

    save_history(history, candidates)
    report = write_report(candidates, cfg, aisa.spent_usd, stopped)
    print(f"\nЗвіт: {report}")
    print(f"Витрачено: ${aisa.spent_usd:.4f}")
    return 0


def _add_virality(candidates: list, cfg: dict) -> None:
    """TikTok тільки для фіналістів — Apify платний, гнати по всіх немає сенсу."""
    if not cfg["apify"]["enabled"]:
        print("  вимкнено в config")
        return
    apify = Apify()
    if not apify.enabled:
        print("  APIFY_TOKEN не заданий — пропускаю")
        return

    top = sorted([c for c in candidates if c.is_winner],
                 key=lambda c: c.score, reverse=True)[:5]
    for cand in top:
        try:
            items = apify.run_actor(
                cfg["apify"]["actor"],
                {"searchQueries": [cand.keyword],
                 "resultsPerPage": cfg["apify"]["results_per_keyword"]},
            )
        except ApifyError as exc:
            print(f"  ✗ {cand.keyword}: {exc}")
            continue
        signal = virality_signal(items, cfg["apify"]["min_views_for_hit"])
        if signal["hits"]:
            cand.signals.append(f"TikTok: {signal['hits']} відео >500k")
            cand.score = round(cand.score * 1.3, 2)
        print(f"  {cand.keyword}: {signal}")


def _chunks(seq: list, size: int):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def _dig(data, *path):
    """Обережний прохід по вкладеному JSON — None замість винятку."""
    current = data
    for key in path:
        try:
            current = current[key]
        except (KeyError, IndexError, TypeError):
            return None
    return current


if __name__ == "__main__":
    raise SystemExit(main())
