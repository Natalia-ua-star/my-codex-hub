"""SerpAPI (Google Search) — discover Shopify competitor stores per niche."""

import logging
from urllib.parse import urlparse

import requests

import config
from sources.common import today_str

logger = logging.getLogger(__name__)

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


def _domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return ""


def _looks_like_shopify(url: str, snippet: str) -> bool:
    domain = _domain_of(url)
    text = (snippet or "").lower()
    return (
        "myshopify.com" in domain
        or "shopify" in text
        or "/collections/" in url
        or "/products/" in url
    )


def _search(query: str) -> list:
    params = {
        "engine": "google",
        "q": f'{query} site:myshopify.com OR "powered by shopify"',
        "gl": "us",
        "hl": "en",
        "num": config.SHOPIFY_RESULTS_PER_QUERY,
        "api_key": config.SERP_API_KEY,
    }
    try:
        resp = requests.get(SERPAPI_ENDPOINT, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json().get("organic_results", [])
    except requests.RequestException:
        logger.exception("SerpAPI request failed for query=%r", query)
        return []


def fetch_shopify_competitors(niches: dict) -> list:
    """Returns top-10 candidate Shopify competitor domains per niche, ranked
    by how many distinct queries surfaced them (a proxy for market visibility)."""
    if not config.SERP_API_KEY:
        logger.warning("SERP_API_KEY is not set — skipping Shopify competitor source.")
        return []

    records = []

    for niche_key, niche_cfg in niches.items():
        domain_hits = {}  # domain -> {"mentions": int, "url": str, "title": str}

        for query in niche_cfg["shopify_queries"]:
            for result in _search(query):
                url = result.get("link", "")
                title = result.get("title", "")
                snippet = result.get("snippet", "")

                if not url or not _looks_like_shopify(url, snippet):
                    continue

                domain = _domain_of(url)
                if not domain:
                    continue

                if domain not in domain_hits:
                    domain_hits[domain] = {"mentions": 0, "url": url, "title": title}
                domain_hits[domain]["mentions"] += 1

        ranked = sorted(domain_hits.items(), key=lambda kv: kv[1]["mentions"], reverse=True)
        for domain, info in ranked[:10]:
            records.append({
                "niche": niche_key,
                "domain": domain,
                "url": info["url"],
                "title": info["title"],
                "mentions": info["mentions"],
                "search_date": today_str(),
            })

    return records
