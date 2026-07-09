"""Shared Apify actor-run helper.

Follows the exact pattern requested: start the actor run, wait for it to
finish, then pull results from its default dataset.
"""

import logging

from apify_client import ApifyClient

logger = logging.getLogger(__name__)


def run_actor_and_get_items(client: ApifyClient, actor_id: str, run_input: dict) -> list:
    """Start an Apify actor run, wait for completion, and return dataset items.

    Returns an empty list (and logs a warning) instead of raising, so one
    failed niche/country combination doesn't abort the whole research run.
    """
    try:
        run = client.actor(actor_id).start(run_input=run_input)
        client.run(run["id"]).wait_for_finish()

        run_details = client.run(run["id"]).get()
        status = run_details.get("status") if run_details else None
        if status != "SUCCEEDED":
            logger.warning(
                "Apify actor %s run %s finished with status=%s (input=%s)",
                actor_id, run.get("id"), status, run_input,
            )

        dataset_id = run["defaultDatasetId"]
        return list(client.dataset(dataset_id).iterate_items())
    except Exception:
        logger.exception(
            "Apify actor %s failed for input=%s", actor_id, run_input
        )
        return []
