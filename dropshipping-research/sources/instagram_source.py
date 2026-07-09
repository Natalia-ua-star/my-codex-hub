"""Apify Instagram Scraper (apify/instagram-scraper) — English hashtag content per niche.

No per-country breakdown: Instagram hashtag pages aren't geo-scoped, so results
are grouped by niche only (English-language hashtags across all target markets).
"""

import logging

from apify_client import ApifyClient

import config
from sources.apify_utils import run_actor_and_get_items
from sources.common import contains_excluded, safe_get, today_str

logger = logging.getLogger(__name__)


def _build_input(hashtags: list) -> dict:
    """Input for apify/instagram-scraper, scraping hashtag explore pages directly.

    Verify field names against the actor's current Input tab if the schema
    has changed since writing.
    """
    return {
        "directUrls": [f"https://www.instagram.com/explore/tags/{tag}/" for tag in hashtags],
        "resultsType": "posts",
        "resultsLimit": config.INSTAGRAM_RESULTS_PER_HASHTAG,
        "searchLimit": 1,
        "addParentData": False,
    }


def _normalize_item(item: dict, niche_key: str) -> dict:
    caption = safe_get(item, "caption", default="") or ""
    likes = int(safe_get(item, "likesCount", default=0) or 0)
    comments = int(safe_get(item, "commentsCount", default=0) or 0)
    views = int(safe_get(item, "videoViewCount", "videoPlayCount", default=0) or 0)
    engagement_rate = round((likes + comments) / views, 4) if views else None

    return {
        "niche": niche_key,
        "url": safe_get(item, "url", default=""),
        "author": safe_get(item, "ownerUsername", default=""),
        "caption": caption,
        "hashtags": ", ".join(safe_get(item, "hashtags", default=[]) or []),
        "views": views or None,
        "likes": likes,
        "comments": comments,
        "engagement_rate": engagement_rate if engagement_rate is not None else round(likes + comments, 4),
        "posted_at": safe_get(item, "timestamp", default=""),
        "search_date": today_str(),
    }


def fetch_instagram_winners(niches: dict) -> list:
    if not config.APIFY_API_TOKEN:
        logger.warning("APIFY_API_TOKEN is not set — skipping Instagram source.")
        return []

    client = ApifyClient(config.APIFY_API_TOKEN)
    records = []

    for niche_key, niche_cfg in niches.items():
        hashtags = niche_cfg["instagram_hashtags"]
        exclude_keywords = niche_cfg.get("exclude_keywords", [])

        run_input = _build_input(hashtags)
        items = run_actor_and_get_items(client, config.INSTAGRAM_ACTOR_ID, run_input)

        for item in items:
            record = _normalize_item(item, niche_key)
            if contains_excluded(record["caption"], exclude_keywords):
                continue
            records.append(record)

    return records
