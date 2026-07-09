"""Apify TikTok Scraper (clockworks/tiktok-scraper) — organic viral content per niche/country."""

import logging

from apify_client import ApifyClient

import config
from sources.apify_utils import run_actor_and_get_items
from sources.common import contains_excluded, safe_get, today_str

logger = logging.getLogger(__name__)


def _build_input(hashtags: list, country: str) -> dict:
    """Input for clockworks/tiktok-scraper.

    `proxyCountryCode` routes the scrape through a residential proxy in that
    country so results reflect that market's TikTok feed. Verify this field
    name against the actor's current Input tab on the Apify console if you
    swap in a different TikTok scraper actor.
    """
    return {
        "hashtags": hashtags,
        "resultsPerPage": config.TIKTOK_RESULTS_PER_HASHTAG,
        "proxyCountryCode": country,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
    }


def _normalize_item(item: dict, niche_key: str, country: str) -> dict:
    author_meta = item.get("authorMeta", {}) or {}
    caption = safe_get(item, "text", "desc", default="")
    views = int(safe_get(item, "playCount", "videoPlayCount", default=0) or 0)
    likes = int(safe_get(item, "diggCount", "likeCount", default=0) or 0)
    comments = int(safe_get(item, "commentCount", default=0) or 0)
    shares = int(safe_get(item, "shareCount", default=0) or 0)
    engagement_rate = round((likes + comments + shares) / views, 4) if views else 0.0

    return {
        "niche": niche_key,
        "country": country,
        "source": "TikTok Organic",
        "url": safe_get(item, "webVideoUrl", "url", default=""),
        "author": safe_get(author_meta, "name", "nickName", default="") if author_meta else "",
        "caption": caption,
        "views": views,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "engagement_rate": engagement_rate,
        "posted_at": safe_get(item, "createTimeISO", default=""),
        "search_date": today_str(),
    }


def fetch_tiktok_winners(niches: dict, countries: list) -> list:
    if not config.APIFY_API_TOKEN:
        logger.warning("APIFY_API_TOKEN is not set — skipping TikTok source.")
        return []

    client = ApifyClient(config.APIFY_API_TOKEN)
    records = []

    for niche_key, niche_cfg in niches.items():
        hashtags = niche_cfg["tiktok_hashtags"]
        exclude_keywords = niche_cfg.get("exclude_keywords", [])

        for country in countries:
            run_input = _build_input(hashtags, country)
            items = run_actor_and_get_items(client, config.TIKTOK_ACTOR_ID, run_input)

            for item in items:
                record = _normalize_item(item, niche_key, country)
                if contains_excluded(record["caption"], exclude_keywords):
                    continue
                records.append(record)

    return records
