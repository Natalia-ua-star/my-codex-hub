"""Apify AliExpress Scraper — best-selling products per niche + review/seller-rating analysis.

Sorts by order count (best sellers) and pulls each product's rating, review
count, and seller/store rating so winners can be filtered by trust, not just
sales volume.

Several different authors publish AliExpress scraper actors on Apify with
different input schemas. ALIEXPRESS_ACTOR_ID in config.py (overridable via
.env) picks which one to call — open its "Input" tab on the Apify console
before a real run and confirm the field names below still match.
"""

import logging

import config
from sources.apify_utils import run_actor_and_get_items
from sources.common import contains_excluded, safe_get, today_str

logger = logging.getLogger(__name__)


def _build_input(query: str) -> dict:
    return {
        "query": query,
        "keywords": query,
        "sortBy": "orders",       # best-sellers first
        "sortType": "orders",
        "maxItems": config.ALIEXPRESS_RESULTS_PER_QUERY,
        "resultsLimit": config.ALIEXPRESS_RESULTS_PER_QUERY,
        "endPage": 1,
    }


def _is_trusted_seller(seller_rating, seller_feedback_pct) -> bool:
    try:
        if seller_rating not in (None, "") and float(seller_rating) >= config.ALIEXPRESS_TRUSTED_SELLER_RATING:
            return True
    except (TypeError, ValueError):
        pass
    try:
        if seller_feedback_pct not in (None, ""):
            pct = float(str(seller_feedback_pct).replace("%", ""))
            if pct >= config.ALIEXPRESS_TRUSTED_SELLER_FEEDBACK_PCT:
                return True
    except (TypeError, ValueError):
        pass
    return False


def _normalize_item(item: dict, niche_key: str, query: str) -> dict:
    title = safe_get(item, "title", "productTitle", "name", default="")
    price = safe_get(item, "price", "salePrice", "minPrice", default="")
    orders = safe_get(item, "orders", "orderCount", "soldCount", "sales", default=0)
    rating = safe_get(item, "rating", "averageStarRating", "productRating", "starRating", default="")
    review_count = safe_get(item, "reviewCount", "reviewsCount", "feedbackCount", default=0)
    seller_name = safe_get(item, "storeName", "sellerName", "shopName", default="")
    seller_rating = safe_get(item, "storeRating", "sellerRating", "shopRating", default="")
    seller_feedback_pct = safe_get(item, "positiveFeedbackRate", "sellerPositiveRate", default="")

    try:
        orders_num = float(str(orders).replace(",", "").replace("+", "") or 0)
    except ValueError:
        orders_num = 0.0
    try:
        rating_num = float(rating) if rating not in (None, "") else None
    except ValueError:
        rating_num = None
    try:
        review_count_num = float(str(review_count).replace(",", "") or 0)
    except ValueError:
        review_count_num = 0.0

    return {
        "niche": niche_key,
        "query": query,
        "title": title,
        "url": safe_get(item, "url", "productUrl", default=""),
        "price": price,
        "orders": orders_num,
        "rating": rating_num,
        "review_count": review_count_num,
        "seller_name": seller_name,
        "seller_rating": seller_rating,
        "seller_positive_feedback": seller_feedback_pct,
        "trusted_seller": _is_trusted_seller(seller_rating, seller_feedback_pct),
        "search_date": today_str(),
    }


def fetch_aliexpress_winners(niches: dict) -> list:
    """No per-country split: AliExpress is a global marketplace, so results
    are grouped by niche only, same as Instagram."""
    if not config.APIFY_API_TOKEN:
        logger.warning("APIFY_API_TOKEN is not set — skipping AliExpress source.")
        return []

    token = config.APIFY_API_TOKEN
    records = []

    for niche_key, niche_cfg in niches.items():
        queries = niche_cfg.get("aliexpress_queries", [])
        exclude_keywords = niche_cfg.get("exclude_keywords", [])

        for query in queries:
            run_input = _build_input(query)
            items = run_actor_and_get_items(token, config.ALIEXPRESS_ACTOR_ID, run_input)

            for item in items:
                record = _normalize_item(item, niche_key, query)
                if contains_excluded(record["title"], exclude_keywords):
                    continue
                records.append(record)

    return records
