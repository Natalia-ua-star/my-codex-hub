"""
Central configuration: niches, geo, per-platform search terms, actor IDs, scoring weights.
Edit this file to tune what the research system looks for — no need to touch source code.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# --- API credentials (from .env) -------------------------------------------------
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
SERP_API_KEY = os.getenv("SERP_API_KEY", "")

# --- Geo scope ---------------------------------------------------------------------
# English-speaking markets only.
COUNTRIES = ["US", "GB", "AU", "CA", "NZ"]

# TikTok Shop is only live/active in these markets.
TIKTOK_SHOP_COUNTRIES = ["US", "GB"]

# --- Apify actor IDs (override via .env if you use different actors/authors) -------
TIKTOK_ACTOR_ID = os.getenv("TIKTOK_ACTOR_ID", "clockworks/tiktok-scraper")
TIKTOK_SHOP_ACTOR_ID = os.getenv("TIKTOK_SHOP_ACTOR_ID", "novi/tiktok-shop-scraper")
INSTAGRAM_ACTOR_ID = os.getenv("INSTAGRAM_ACTOR_ID", "apify/instagram-scraper")

# NOTE on Apify actors: input schemas are defined by each actor's author and can
# change over time. Field names used in sources/*.py reflect the commonly
# documented schemas as of writing. Before a production run, open the actor page
# on the Apify console ("Input" tab) and confirm field names match; adjust the
# `build_input()` helper in the relevant source module if they don't.

# --- Result limits (control cost/quota) --------------------------------------------
YOUTUBE_MAX_QUERIES_PER_NICHE = 3   # search.list costs ~100 quota units per call
YOUTUBE_RESULTS_PER_QUERY = 15
YOUTUBE_PUBLISHED_WITHIN_DAYS = 90  # only look at recent/trending videos

TIKTOK_RESULTS_PER_HASHTAG = 30
INSTAGRAM_RESULTS_PER_HASHTAG = 30
SHOPIFY_RESULTS_PER_QUERY = 20

# --- Niches --------------------------------------------------------------------
# "dogs" niche explicitly EXCLUDES food/treats/grooming/health products (per spec) —
# handled via exclude_keywords filtering on title/caption text.
NICHES = {
    "dogs": {
        "label": "Dogs (accessories & gadgets — no food/grooming)",
        "youtube_queries": [
            "dog gadget TikTok made me buy it",
            "viral dog accessory",
            "must have dog gear",
            "cool dog product invention",
            "dog toy that went viral",
        ],
        "tiktok_hashtags": [
            "dogaccessories", "dogsoftiktok", "dogproducts",
            "dogmusthaves", "dogtech", "dogtoys", "dogfinds",
        ],
        "instagram_hashtags": [
            "dogaccessories", "dogproducts", "dogmusthaves",
            "dogtoys", "dogfinds", "dogtech",
        ],
        "shopify_queries": [
            "dog accessories store", "dog gadgets shop",
            "dog toys online store", "dog gear dropshipping",
        ],
        "exclude_keywords": [
            "food", "kibble", "treat", "treats", "chew supplement",
            "grooming", "shampoo", "vitamin", "dewormer", "flea",
            "tick medicine", "vet visit", "diet plan", "probiotic",
        ],
    },
    "home": {
        "label": "Home (gadgets, decor, organization)",
        "youtube_queries": [
            "home gadget TikTok made me buy it",
            "viral home product",
            "cool kitchen gadget",
            "home organization must have",
            "genius home invention",
        ],
        "tiktok_hashtags": [
            "homefinds", "homegadgets", "tiktokmademebuyit",
            "amazonfinds", "kitchengadgets", "homehacks", "homedecor",
        ],
        "instagram_hashtags": [
            "homefinds", "homegadgets", "homedecor",
            "homehacks", "kitchengadgets",
        ],
        "shopify_queries": [
            "home gadgets store", "home decor dropshipping store",
            "kitchen gadgets shop", "home organization store",
        ],
        "exclude_keywords": [
            "furniture warehouse", "wholesale liquidation",
            "real estate", "mortgage", "home insurance",
        ],
    },
    "hobby": {
        "label": "Hobby (crafts, outdoor, gaming, DIY)",
        "youtube_queries": [
            "hobby gadget viral",
            "cool hobby product TikTok made me buy it",
            "craft tool must have",
            "outdoor gear viral",
            "gaming accessory viral",
        ],
        "tiktok_hashtags": [
            "hobbyfinds", "crafttools", "diytools",
            "outdoorgear", "gamingaccessories", "hobbygadgets",
        ],
        "instagram_hashtags": [
            "hobbyfinds", "crafttools", "diytools",
            "outdoorgear", "gaminggadgets",
        ],
        "shopify_queries": [
            "hobby gear store", "craft supplies dropshipping store",
            "outdoor gear shop", "gaming accessories store",
        ],
        "exclude_keywords": ["casino", "gambling", "lottery"],
    },
}

# --- Scoring weights ------------------------------------------------------------
# Score is a 0-100 min-max normalized value within each (niche, country) group,
# computed from a weighted sum of engagement metrics. See scoring.py.
SCORE_WEIGHTS = {
    "views": 0.4,
    "likes": 0.3,
    "comments": 0.15,
    "shares": 0.15,
}
