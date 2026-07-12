"""Winner scoring: 0-100 min-max normalized weighted engagement score.

Normalization happens *within* each (niche[, country]) group so a video
isn't penalized for competing against a bigger market — a US TikTok winner
and an NZ TikTok winner are each scored against their own peers.
"""

import pandas as pd

import config


def _minmax_via_transform(df: pd.DataFrame, group_cols: list, values: pd.Series) -> pd.Series:
    """Per-group min-max scaling to 0-100 using groupby().transform(), which
    always returns a Series aligned to df's original index — unlike
    groupby().apply(), it doesn't misbehave when there's only one group."""
    grouped = values.groupby([df[c] for c in group_cols])
    lo = grouped.transform("min")
    hi = grouped.transform("max")
    flat = (hi == lo) | lo.isna() | hi.isna()
    scaled = (values - lo) / (hi - lo).replace(0, pd.NA) * 100
    return scaled.where(~flat, 50.0)  # flat group -> neutral score


def add_score(df: pd.DataFrame, group_cols: list, metric_cols: list, weights: dict = None) -> pd.DataFrame:
    """Adds a 'score' column (0-100) to df, grouped by group_cols.

    metric_cols are weighted per `weights` (defaults to config.SCORE_WEIGHTS;
    missing weights default to equal split of the remainder).
    """
    if df.empty:
        df["score"] = pd.Series(dtype=float)
        return df

    df = df.copy()
    source_weights = weights if weights is not None else config.SCORE_WEIGHTS
    weights = {col: source_weights.get(col, 0) for col in metric_cols if col in df.columns}
    weight_sum = sum(weights.values())
    if weight_sum == 0:
        weights = {col: 1 / len(weights) for col in weights}
    else:
        # Renormalize to 1 so scores stay 0-100 comparable even when a metric
        # (e.g. "shares") isn't available for this platform.
        weights = {col: w / weight_sum for col, w in weights.items()}

    weighted_total = pd.Series(0.0, index=df.index)
    for col, weight in weights.items():
        values = pd.to_numeric(df[col], errors="coerce").fillna(0)
        weighted_total += _minmax_via_transform(df, group_cols, values).fillna(50.0) * weight

    df["score"] = weighted_total.round(2)
    return df.sort_values(group_cols + ["score"], ascending=[True] * len(group_cols) + [False])
