"""Shared Apify actor-run helper — calls the Apify REST API directly via `requests`.

NOTE: this intentionally does NOT use the `apify-client` SDK. In this sandbox,
apify-client's HTTP backend (`impit`, a Rust HTTP/2 client) fails every
request with `ConnectError: ... Connection reset by peer` even though the
network policy allows api.apify.com and plain `requests`/`curl` reach it fine
— `impit` doesn't negotiate this proxy correctly. `requests` does, so we talk
to the same REST endpoints the SDK wraps: start a run, poll until it
finishes, then read its default dataset. Functionally identical to
`client.actor(id).start()` -> `run.wait_for_finish()` -> `dataset.iterate_items()`.
"""

import logging
import time

import requests

logger = logging.getLogger(__name__)

API_BASE = "https://api.apify.com/v2"
TERMINAL_STATUSES = {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}


def _actor_path(actor_id: str) -> str:
    """Apify REST paths use '~' instead of '/' between owner and actor name."""
    return actor_id.replace("/", "~")


def run_actor_and_get_items(token: str, actor_id: str, run_input: dict, max_wait_seconds: int = 180) -> list:
    """Start an Apify actor run, poll until completion, and return dataset items.

    Returns an empty list (and logs a warning/error) instead of raising, so one
    failed niche/country combination doesn't abort the whole research run.
    """
    try:
        start_resp = requests.post(
            f"{API_BASE}/acts/{_actor_path(actor_id)}/runs",
            params={"token": token},
            json=run_input,
            timeout=30,
        )
        start_resp.raise_for_status()
        run = start_resp.json()["data"]
        run_id = run["id"]

        deadline = time.monotonic() + max_wait_seconds
        status = run.get("status")
        while status not in TERMINAL_STATUSES and time.monotonic() < deadline:
            time.sleep(5)
            poll_resp = requests.get(f"{API_BASE}/actor-runs/{run_id}", params={"token": token}, timeout=30)
            poll_resp.raise_for_status()
            run = poll_resp.json()["data"]
            status = run.get("status")

        if status != "SUCCEEDED":
            logger.warning(
                "Apify actor %s run %s finished with status=%s (input=%s)",
                actor_id, run_id, status, run_input,
            )

        dataset_id = run["defaultDatasetId"]
        items_resp = requests.get(
            f"{API_BASE}/datasets/{dataset_id}/items",
            params={"token": token, "format": "json", "clean": "true"},
            timeout=60,
        )
        items_resp.raise_for_status()
        return items_resp.json()
    except Exception:
        logger.exception("Apify actor %s failed for input=%s", actor_id, run_input)
        return []
