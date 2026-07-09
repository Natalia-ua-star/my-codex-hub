"""YouTube Data API v3 source — trending/viral videos per niche and region."""

import logging
from datetime import datetime, timedelta, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config
from sources.common import contains_excluded, today_str

logger = logging.getLogger(__name__)


def _published_after_iso() -> str:
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.YOUTUBE_PUBLISHED_WITHIN_DAYS)
    return cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_youtube_winners(niches: dict, countries: list) -> list:
    """Search YouTube per niche/query/country, then enrich with statistics.

    Returns a list of flat dicts, one per video.
    """
    if not config.YOUTUBE_API_KEY:
        logger.warning("YOUTUBE_API_KEY is not set — skipping YouTube source.")
        return []

    youtube = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
    published_after = _published_after_iso()
    records = []

    for niche_key, niche_cfg in niches.items():
        queries = niche_cfg["youtube_queries"][: config.YOUTUBE_MAX_QUERIES_PER_NICHE]
        exclude_keywords = niche_cfg.get("exclude_keywords", [])

        for country in countries:
            for query in queries:
                video_ids = []
                try:
                    search_resp = youtube.search().list(
                        part="snippet",
                        q=query,
                        type="video",
                        regionCode=country,
                        relevanceLanguage="en",
                        order="viewCount",
                        publishedAfter=published_after,
                        maxResults=config.YOUTUBE_RESULTS_PER_QUERY,
                    ).execute()
                except HttpError:
                    logger.exception(
                        "YouTube search failed (niche=%s, country=%s, query=%r)",
                        niche_key, country, query,
                    )
                    continue

                for item in search_resp.get("items", []):
                    video_ids.append(item["id"]["videoId"])

                if not video_ids:
                    continue

                try:
                    videos_resp = youtube.videos().list(
                        part="snippet,statistics",
                        id=",".join(video_ids),
                    ).execute()
                except HttpError:
                    logger.exception(
                        "YouTube videos.list failed (niche=%s, country=%s)",
                        niche_key, country,
                    )
                    continue

                for video in videos_resp.get("items", []):
                    snippet = video.get("snippet", {})
                    stats = video.get("statistics", {})
                    title = snippet.get("title", "")
                    description = snippet.get("description", "")

                    if contains_excluded(f"{title} {description}", exclude_keywords):
                        continue

                    views = int(stats.get("viewCount", 0) or 0)
                    likes = int(stats.get("likeCount", 0) or 0)
                    comments = int(stats.get("commentCount", 0) or 0)
                    engagement_rate = round((likes + comments) / views, 4) if views else 0.0

                    records.append({
                        "niche": niche_key,
                        "country": country,
                        "query": query,
                        "url": f"https://www.youtube.com/watch?v={video['id']}",
                        "channel": snippet.get("channelTitle", ""),
                        "title": title,
                        "published_at": snippet.get("publishedAt", ""),
                        "views": views,
                        "likes": likes,
                        "comments": comments,
                        "shares": 0,  # not exposed by the YouTube API
                        "engagement_rate": engagement_rate,
                        "search_date": today_str(),
                    })

    return records
