"""Winner scoring: 0-100 min-max normalized weighted engagement score.

Normalization happens *within* each (niche[, country]) group so a video
isn't penalized for competing against a bigger market — a US TikTok winner
and an NZ TikTok winner are each scored against their own peers.
"""

import pandas as pd

import config


def _minmax(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(50.0, index=series.index)  # flat group -> neutral score
    return (series - lo) / (hi - lo) * 100


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

    def _score_group(group: pd.DataFrame) -> pd.Series:
        weighted = pd.Series(0.0, index=group.index)
        for col in metric_cols:
            if col not in group.columns:
                continue
            values = pd.to_numeric(group[col], errors="coerce").fillna(0)
            weighted += _minmax(values) * weights[col]
        return round(weighted, 2)

    df["score"] = df.groupby(group_cols, dropna=False, group_keys=False).apply(_score_group)
    return df.sort_values(group_cols + ["score"], ascending=[True] * len(group_cols) + [False])
