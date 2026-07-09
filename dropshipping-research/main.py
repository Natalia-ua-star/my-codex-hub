"""Dropshipping research pipeline: pulls TikTok/Instagram/YouTube/Shopify/AliExpress
data, scores winners, and writes everything into results.xlsx.

Usage:
    python main.py                       # full run, all sources
    python main.py --niches dogs home     # limit to specific niches
    python main.py --countries US GB      # limit to specific countries
    python main.py --skip youtube shopify # skip specific sources (cost control)
    python main.py --demo                 # generate results.xlsx from synthetic
                                           # sample data, no API calls — use this
                                           # to preview the workbook format first
    python main.py --output my_results.xlsx
"""

import argparse
import logging
import random
import sys
from datetime import date

import pandas as pd

import config
import excel_export
import scoring
from sources.common import today_str

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dropshipping_research")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--niches", nargs="+", choices=list(config.NICHES.keys()), default=None,
                        help="Limit to specific niches (default: all configured niches).")
    parser.add_argument("--countries", nargs="+", default=None,
                        help="Limit to specific countries (default: %s)." % config.COUNTRIES)
    parser.add_argument("--skip", nargs="+",
                        choices=["youtube", "tiktok", "tiktok_shop", "instagram", "shopify", "aliexpress"],
                        default=[], help="Skip one or more sources.")
    parser.add_argument("--output", default="results.xlsx", help="Output .xlsx path (default: results.xlsx).")
    parser.add_argument("--demo", action="store_true",
                        help="Skip all API calls and build results.xlsx from synthetic sample data, "
                             "so you can check the workbook format before spending API quota.")
    return parser.parse_args()


def _generate_demo_data(niches: dict, countries: list):
    rng = random.Random(42)
    tiktok, instagram, youtube, shopify, aliexpress = [], [], [], [], []

    for niche_key in niches:
        for country in countries:
            for i in range(3):
                views = rng.randint(5_000, 2_000_000)
                likes = int(views * rng.uniform(0.02, 0.15))
                comments = int(likes * rng.uniform(0.01, 0.08))
                shares = int(likes * rng.uniform(0.01, 0.05))
                tiktok.append({
                    "niche": niche_key, "country": country, "source": "TikTok Organic (demo)",
                    "url": f"https://www.tiktok.com/@demo/video/{niche_key}{country}{i}",
                    "author": f"demo_creator_{i}", "caption": f"Demo {niche_key} viral video #{i}",
                    "views": views, "likes": likes, "comments": comments, "shares": shares,
                    "engagement_rate": round((likes + comments + shares) / views, 4),
                    "posted_at": today_str(), "search_date": today_str(),
                })

            youtube_views = rng.randint(10_000, 5_000_000)
            youtube_likes = int(youtube_views * rng.uniform(0.02, 0.1))
            youtube_comments = int(youtube_likes * rng.uniform(0.01, 0.05))
            youtube.append({
                "niche": niche_key, "country": country, "query": "demo query",
                "url": f"https://www.youtube.com/watch?v=demo{niche_key}{country}",
                "channel": f"Demo Channel {niche_key}", "title": f"Demo {niche_key} video ({country})",
                "published_at": today_str(), "views": youtube_views, "likes": youtube_likes,
                "comments": youtube_comments, "shares": 0,
                "engagement_rate": round((youtube_likes + youtube_comments) / youtube_views, 4),
                "search_date": today_str(),
            })

        for i in range(3):
            likes = rng.randint(500, 50_000)
            comments = int(likes * rng.uniform(0.01, 0.05))
            instagram.append({
                "niche": niche_key, "url": f"https://www.instagram.com/p/demo{niche_key}{i}/",
                "author": f"demo_ig_{i}", "caption": f"Demo {niche_key} IG post #{i}",
                "hashtags": "demo, hashtags", "views": None, "likes": likes, "comments": comments,
                "engagement_rate": likes + comments, "posted_at": today_str(), "search_date": today_str(),
            })

        for i in range(5):
            shopify.append({
                "niche": niche_key, "domain": f"demo-{niche_key}-store-{i}.myshopify.com",
                "url": f"https://demo-{niche_key}-store-{i}.myshopify.com",
                "title": f"Demo {niche_key} Store {i}", "mentions": rng.randint(1, 4),
                "search_date": today_str(),
            })

        for i in range(5):
            rating = round(rng.uniform(3.8, 5.0), 1)
            feedback_pct = rng.randint(90, 100)
            aliexpress.append({
                "niche": niche_key, "query": "demo query",
                "title": f"Demo {niche_key} AliExpress product #{i}",
                "url": f"https://www.aliexpress.com/item/demo{niche_key}{i}.html",
                "price": round(rng.uniform(3, 40), 2),
                "orders": rng.randint(50, 20_000),
                "rating": rating,
                "review_count": rng.randint(10, 5000),
                "seller_name": f"Demo Store {i}",
                "seller_rating": rating,
                "seller_positive_feedback": f"{feedback_pct}%",
                "trusted_seller": rating >= config.ALIEXPRESS_TRUSTED_SELLER_RATING or feedback_pct >= config.ALIEXPRESS_TRUSTED_SELLER_FEEDBACK_PCT,
                "search_date": today_str(),
            })

    return tiktok, instagram, youtube, shopify, aliexpress


def main():
    args = parse_args()
    niches = {k: v for k, v in config.NICHES.items() if args.niches is None or k in args.niches}
    countries = args.countries or config.COUNTRIES

    logger.info("Niches: %s | Countries: %s | Skip: %s", list(niches.keys()), countries, args.skip)

    if args.demo:
        logger.info("DEMO MODE — generating synthetic sample data, no API calls will be made.")
        tiktok_records, instagram_records, youtube_records, shopify_records, aliexpress_records = (
            _generate_demo_data(niches, countries)
        )
    else:
        from sources.aliexpress_source import fetch_aliexpress_winners
        from sources.instagram_source import fetch_instagram_winners
        from sources.shopify_serp_source import fetch_shopify_competitors
        from sources.tiktok_shop_source import fetch_tiktok_shop_winners
        from sources.tiktok_source import fetch_tiktok_winners
        from sources.youtube_source import fetch_youtube_winners

        youtube_records = [] if "youtube" in args.skip else fetch_youtube_winners(niches, countries)

        tiktok_records = [] if "tiktok" in args.skip else fetch_tiktok_winners(niches, countries)
        if "tiktok_shop" not in args.skip:
            tiktok_records += fetch_tiktok_shop_winners(niches)

        instagram_records = [] if "instagram" in args.skip else fetch_instagram_winners(niches)
        shopify_records = [] if "shopify" in args.skip else fetch_shopify_competitors(niches)
        aliexpress_records = [] if "aliexpress" in args.skip else fetch_aliexpress_winners(niches)

    tiktok_df = pd.DataFrame(tiktok_records)
    instagram_df = pd.DataFrame(instagram_records)
    youtube_df = pd.DataFrame(youtube_records)
    shopify_df = pd.DataFrame(shopify_records)
    aliexpress_df = pd.DataFrame(aliexpress_records)

    if not tiktok_df.empty:
        tiktok_df = scoring.add_score(tiktok_df, ["niche", "country"], ["views", "likes", "comments", "shares"])
    if not instagram_df.empty:
        instagram_df = scoring.add_score(instagram_df, ["niche"], ["likes", "comments", "views"])
    if not youtube_df.empty:
        youtube_df = scoring.add_score(youtube_df, ["niche", "country"], ["views", "likes", "comments"])
    if not shopify_df.empty:
        shopify_df = shopify_df.sort_values(["niche", "mentions"], ascending=[True, False])
    if not aliexpress_df.empty:
        aliexpress_df = scoring.add_score(
            aliexpress_df, ["niche"], ["orders", "rating", "review_count"],
            weights=config.ALIEXPRESS_SCORE_WEIGHTS,
        )

    output_path = excel_export.build_workbook(
        args.output, tiktok_df, instagram_df, youtube_df, shopify_df, aliexpress_df,
    )

    logger.info(
        "Done. %s: TikTok=%d, Instagram=%d, YouTube=%d, Shopify=%d, AliExpress=%d -> %s",
        today_str(), len(tiktok_df), len(instagram_df), len(youtube_df), len(shopify_df),
        len(aliexpress_df), output_path,
    )


if __name__ == "__main__":
    sys.exit(main())
