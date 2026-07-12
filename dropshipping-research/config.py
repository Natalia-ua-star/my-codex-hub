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

# --- Google Sheets sync (optional — only needed for --push-to-sheets) -------------
# Service account JSON key path (see sheets_sync.py docstring for one-time setup).
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
# Leave blank on first run — sheets_sync.py will create the spreadsheet and log
# its ID so you can paste it in here for subsequent runs to append to the same file.
MAIN_SPREADSHEET_ID = os.getenv("MAIN_SPREADSHEET_ID", "")
ALIEXPRESS_SPREADSHEET_ID = os.getenv("ALIEXPRESS_SPREADSHEET_ID", "")

# --- Geo scope ---------------------------------------------------------------------
# English-speaking markets only.
COUNTRIES = ["US", "GB", "AU", "CA", "NZ"]

# TikTok Shop is only live/active in these markets.
TIKTOK_SHOP_COUNTRIES = ["US", "GB"]

# --- Apify actor IDs (override via .env if you use different actors/authors) -------
TIKTOK_ACTOR_ID = os.getenv("TIKTOK_ACTOR_ID", "clockworks/tiktok-scraper")
TIKTOK_SHOP_ACTOR_ID = os.getenv("TIKTOK_SHOP_ACTOR_ID", "novi/tiktok-shop-scraper")
INSTAGRAM_ACTOR_ID = os.getenv("INSTAGRAM_ACTOR_ID", "apify/instagram-scraper")
ALIEXPRESS_ACTOR_ID = os.getenv("ALIEXPRESS_ACTOR_ID", "thirdwatch/aliexpress-product-scraper")

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
SHOPIFY_TOP_N_PER_NICHE = 20
ALIEXPRESS_RESULTS_PER_QUERY = 30

# A seller is flagged "trusted" if its star rating or positive-feedback % clears these.
ALIEXPRESS_TRUSTED_SELLER_RATING = 4.5     # out of 5 stars
ALIEXPRESS_TRUSTED_SELLER_FEEDBACK_PCT = 95  # % positive feedback

# --- Niches --------------------------------------------------------------------
# exclude_keywords filters out non-product / service listings that would
# otherwise pollute results (insurance, licensing, consulting services, etc.)
# — not the underlying product category itself.
NICHES = {
    "auto_accessories": {
        "label": "Auto Accessories (car gadgets & accessories)",
        "youtube_queries": [
            "car accessory TikTok made me buy it",
            "viral car gadget",
            "must have car accessory",
            "cool car interior gadget",
            "car detailing product viral",
        ],
        "tiktok_hashtags": [
            "caraccessories", "cargadgets", "carguytiktok",
            "cartiktok", "cardetailing", "carmusthaves", "carhacks",
        ],
        "instagram_hashtags": [
            "caraccessories", "cargadgets", "cardetailing",
            "carmusthaves", "carhacks",
        ],
        "shopify_queries": [
            "car accessories store", "car gadgets shop",
            "auto accessories dropshipping", "car detailing store",
        ],
        "aliexpress_queries": [
            "car accessories", "car gadget", "car interior accessories",
            "car phone holder", "car detailing kit",
        ],
        "exclude_keywords": [
            "car insurance", "auto loan", "car dealership",
            "car rental", "auto repair shop", "car finance",
        ],
    },
    "pet_products": {
        "label": "Pet Products (all pets — dogs, cats, small animals)",
        "youtube_queries": [
            "pet gadget TikTok made me buy it",
            "viral pet product",
            "must have pet accessory",
            "cool pet product invention",
            "pet toy that went viral",
        ],
        "tiktok_hashtags": [
            "petproducts", "petsoftiktok", "petaccessories",
            "petmusthaves", "pettech", "pettoys", "petfinds",
        ],
        "instagram_hashtags": [
            "petproducts", "petaccessories", "petmusthaves",
            "pettoys", "petfinds",
        ],
        "shopify_queries": [
            "pet products store", "pet accessories shop",
            "pet gadgets store", "pet supplies dropshipping",
        ],
        "aliexpress_queries": [
            "pet gadget", "pet accessories", "pet toy",
            "pet grooming tool", "pet carrier",
        ],
        "exclude_keywords": [
            "pet insurance", "veterinary clinic",
            "pet adoption agency", "pet boarding service",
        ],
    },
    "diy_home_improvement": {
        "label": "DIY / Home Improvement (tools, hardware, small renovation gadgets)",
        "youtube_queries": [
            "DIY tool TikTok made me buy it",
            "viral home improvement gadget",
            "must have DIY tool",
            "cool home improvement invention",
            "handyman gadget viral",
        ],
        "tiktok_hashtags": [
            "diytools", "homeimprovement", "diyhacks",
            "handymantips", "toolsoftiktok", "diygadgets", "homerenovation",
        ],
        "instagram_hashtags": [
            "diytools", "homeimprovement", "diyhacks",
            "handymantips", "diygadgets",
        ],
        "shopify_queries": [
            "diy tools store", "home improvement shop",
            "hardware gadgets store", "handyman tools dropshipping",
        ],
        "aliexpress_queries": [
            "diy tool", "home improvement gadget", "hand tool set",
            "hardware gadget", "renovation tool",
        ],
        "exclude_keywords": [
            "real estate", "mortgage", "home insurance",
            "contractor service", "construction company",
        ],
    },
    "gardening": {
        "label": "Gardening (tools, planters, outdoor gadgets)",
        "youtube_queries": [
            "gardening gadget TikTok made me buy it",
            "viral garden tool",
            "must have gardening product",
            "cool garden invention",
            "garden hack viral",
        ],
        "tiktok_hashtags": [
            "gardeningtiktok", "gardentools", "gardenhacks",
            "gardengadgets", "plantsoftiktok", "gardenfinds",
        ],
        "instagram_hashtags": [
            "gardening", "gardentools", "gardenhacks",
            "gardengadgets", "gardenfinds",
        ],
        "shopify_queries": [
            "gardening tools store", "garden gadgets shop",
            "planter store", "garden supplies dropshipping",
        ],
        "aliexpress_queries": [
            "garden tool", "gardening gadget", "planter pot",
            "watering tool", "garden gloves",
        ],
        "exclude_keywords": [
            "landscaping service", "lawn care service",
            "garden design consultant",
        ],
    },
    "fishing": {
        "label": "Fishing (gear, lures, accessories)",
        "youtube_queries": [
            "fishing gadget TikTok made me buy it",
            "viral fishing lure",
            "must have fishing gear",
            "cool fishing invention",
            "fishing hack viral",
        ],
        "tiktok_hashtags": [
            "fishingtiktok", "fishinggear", "fishinglures",
            "fishinghacks", "fishingaccessories", "fishingfinds",
        ],
        "instagram_hashtags": [
            "fishing", "fishinggear", "fishinglures",
            "fishinghacks", "fishingaccessories",
        ],
        "shopify_queries": [
            "fishing gear store", "fishing tackle shop",
            "fishing accessories store", "fishing lures dropshipping",
        ],
        "aliexpress_queries": [
            "fishing gear", "fishing lure", "fishing tackle",
            "fishing accessories", "fishing rod holder",
        ],
        "exclude_keywords": [
            "fishing license", "fishing charter", "fishing guide service",
        ],
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

# AliExpress winners are scored on best-seller signal (orders) + trust (rating,
# review volume) rather than social engagement.
ALIEXPRESS_SCORE_WEIGHTS = {
    "orders": 0.5,
    "rating": 0.3,
    "review_count": 0.2,
}
