"""Shared helpers used by every source module."""

from datetime import date


def today_str() -> str:
    return date.today().isoformat()


def contains_excluded(text: str, exclude_keywords) -> bool:
    """Case-insensitive check whether text mentions any excluded keyword."""
    if not text:
        return False
    lowered = text.lower()
    return any(kw.lower() in lowered for kw in exclude_keywords)


def safe_get(d: dict, *keys, default=None):
    """Return the first present, non-None value among several possible key names.

    Apify actor output field names vary between actor authors/versions, so we
    probe a few common variants instead of hard-failing on a KeyError.
    """
    for key in keys:
        if key in d and d[key] is not None:
            return d[key]
    return default
