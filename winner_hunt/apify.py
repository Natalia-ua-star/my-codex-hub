"""Клієнт Apify — віральність товару в соцмережах.

Навіщо він тут: AIsa дає попит і ціни, але TikTok у неї немає взагалі.
А для дропшипінгу TikTok — головне джерело winner-товарів: спочатку відео
на 2 млн переглядів, потім сплеск продажів. Apify цю дірку закриває.

Актор задається в config.yaml, а не зашитий у код: у кожного свій набір
акторів, і схема входу в них різна. За замовчуванням — популярний
tiktok-scraper; перевірте його input_schema під своїм акаунтом.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.apify.com/v2"


class ApifyError(RuntimeError):
    pass


class Apify:
    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("APIFY_TOKEN", "")

    @property
    def enabled(self) -> bool:
        """Агент працює і без Apify — просто без сигналу віральності."""
        return bool(self.token)

    def run_actor(self, actor_id: str, payload: dict, timeout_s: int = 300) -> list[dict]:
        """Запускає актора синхронно і повертає елементи датасету."""
        if not self.enabled:
            raise ApifyError("APIFY_TOKEN не заданий")

        actor = actor_id.replace("/", "~")
        url = (
            f"{API_BASE}/acts/{actor}/run-sync-get-dataset-items?"
            + urllib.parse.urlencode({"token": self.token, "timeout": timeout_s})
        )
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_s + 30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise ApifyError(f"Apify HTTP {exc.code}: {exc.read().decode()[:300]}") from exc


def virality_signal(items: list[dict], min_views: int = 500_000) -> dict:
    """Зводить сирі пости у три числа, які реально впливають на рішення.

    Ключове — `recent_hits`: не загальна популярність теми, а скільки саме
    свіжих відео пробили поріг переглядів. Тема може мати мільярд переглядів
    за всі часи й бути мертвою просто зараз.
    """
    views = []
    for post in items:
        for key in ("playCount", "views", "viewCount", "video_view_count"):
            value = post.get(key)
            if isinstance(value, (int, float)):
                views.append(int(value))
                break

    if not views:
        return {"posts": len(items), "hits": 0, "max_views": 0}

    return {
        "posts": len(items),
        "hits": sum(1 for v in views if v >= min_views),
        "max_views": max(views),
    }
