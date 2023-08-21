import datetime

import numpy as np
import pandas as pd

from lropy.constants import JULIAN_DAY, lro_period


def get_closest_before(df: pd.DataFrame, time) -> pd.DataFrame:
    """
    Gets the rows in df that is closest before the time given. If time is before the
    first timestamp, return the first row.

    Args:
        time: single or multiple timestamps
        df: DataFrame

    Returns:
        Rows corresponding to the closest prior time
    """
    closest_idx = df.index.searchsorted(time, side="right") - 1
    closest_idx = closest_idx.clip(0, len(df.index) - 1)
    return df.iloc[closest_idx]


def get_closest_after(df: pd.DataFrame, time) -> pd.DataFrame:
    """
    Gets the rows in df that is closest after the time given. If time is past the
    last timestamp, return the last row.

    Args:
        time: single or multiple timestamps
        df: DataFrame

    Returns:
        Rows corresponding to the closest next time
    """
    closest_idx = df.index.searchsorted(time)
    closest_idx = closest_idx.clip(0, len(df.index) - 1)
    return df.iloc[closest_idx]


def get_day_index(df: pd.DataFrame) -> pd.Index:
    diff = df.index - df.index[0]
    return diff.days + diff.seconds / JULIAN_DAY + diff.microseconds / (JULIAN_DAY * 1e6)


def get_minute_index(df: pd.DataFrame) -> pd.Index:
    diff = df.index - df.index[0]
    return diff.days * 24 * 60 + diff.seconds / 60 + diff.microseconds / (60 * 1e6)


def get_hour_index(df: pd.DataFrame) -> pd.Index:
    diff = df.index - df.index[0]
    return diff.days * 24 + diff.seconds / 3600 + diff.microseconds / (3600 * 1e6)


def get_revolutions_index(df: pd.DataFrame, orbit_period: float = lro_period) -> pd.Index:
    """
    Get the index in number of revolutions.

    Args:
        df: the DataFrame with datetime index
        orbit_period: orbital period in seconds

    Returns:
        Index in number of revolutions
    """
    diff = df.index - df.index[0]
    index_in_s = diff.days * JULIAN_DAY + diff.seconds + diff.microseconds / 1e6
    return index_in_s / orbit_period


def trim_df(df: pd.DataFrame, start: datetime.datetime, end: datetime.datetime) -> pd.DataFrame:
    if start.tzinfo is None:
        start = start.replace(tzinfo=datetime.timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=datetime.timezone.utc)
    return df.loc[(df.index >= start) & (df.index <= end)]


def trim_df_revolutions(df: pd.DataFrame, start_rev: float = 0, n_rev: float = 1) -> pd.DataFrame:
    df = df.set_index(get_revolutions_index(df))
    df = df.iloc[(df.index >= start_rev) & (df.index <= start_rev + n_rev)]
    df = df.set_index(df.index - df.index[0])
    return df


def rmse(a: pd.Series, b: pd.Series, ignore_zeros: bool = False):
    """RMS error"""
    if ignore_zeros:
        zeros_idx = (a == 0) & (b == 0)
        a = a.loc[~zeros_idx]
        b = b.loc[~zeros_idx]
    return np.sqrt(np.mean((a - b) ** 2))


def rrmse(a: pd.Series, b: pd.Series, ignore_zeros: bool = False):
    """Relative RMS error w.r.t. b"""
    if ignore_zeros:
        zeros_idx = (a == 0) & (b == 0)
        a = a.loc[~zeros_idx]
        b = b.loc[~zeros_idx]
    return np.sqrt(np.sum((a - b) ** 2) / np.sum(b**2))
