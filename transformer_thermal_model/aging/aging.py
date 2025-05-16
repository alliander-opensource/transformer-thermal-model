# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging
import math
from collections.abc import Callable

import pandas as pd

from transformer_thermal_model.transformer import PaperInsulationType

logger = logging.getLogger(__name__)


def aging_rate_profile(hot_spot_profile: pd.Series, insulation_type: PaperInsulationType) -> pd.Series:
    """The aging rate profile of the provided paper insulation material.

    Given a hot-spot temperature profile, calculate the days aged for each time step in the profile.
    Given a hot-spot temperature profile, calculate the days aged for each time step in the profile.

    Args:
        hot_spot_profile (pd.Series): The hot-spot temperature profile of the transformer.
        insulation_type (PaperInsulationType): The type of paper insulation material.

    Example: Calculating the aging rate profile for a hot-spot temperature profile.
        ```python
        >>> import pandas as pd
        >>> from transformer_thermal_model.aging import aging_rate_profile
        >>> from transformer_thermal_model.transformer import PaperInsulationType

        >>> datetime_index = pd.date_range("2020-01-01", periods=10, freq="15min", tz="UTC")
        >>> hot_spot_profile = pd.Series([100] * 10, index=datetime_index)
        >>> profile = aging_rate_profile(hot_spot_profile, PaperInsulationType.NORMAL)
        >>> print(profile)
        2020-01-01 00:00:00+00:00    1.259921
        2020-01-01 00:15:00+00:00    1.259921
        2020-01-01 00:30:00+00:00    1.259921
        2020-01-01 00:45:00+00:00    1.259921
        2020-01-01 01:00:00+00:00    1.259921
        2020-01-01 01:15:00+00:00    1.259921
        2020-01-01 01:30:00+00:00    1.259921
        2020-01-01 01:45:00+00:00    1.259921
        2020-01-01 02:00:00+00:00    1.259921
        2020-01-01 02:15:00+00:00    1.259921
        Freq: 15min, dtype: float64

        ```

    Returns:
        pd.Series: Aging in day/day over time.
    """
    return hot_spot_profile.apply(_aging_rate_method(insulation_type))


def days_aged(hot_spot_profile: pd.Series, insulation_type: PaperInsulationType) -> float:
    """Number of days the insulation material inside the transformer has aged.

    Calculates the number of days the provided insulation material has aged
    given the hot-spot temperature profile. For a more accurate representation
    of the number of days aged per timestep of the provided hot-spot temperature
    profile, see :func:`aging_rate_profile`.

    Args:
        hot_spot_profile (pd.Series): The hot-spot temperature profile of the transformer.
        insulation_type (PaperInsulationType): The type of paper insulation material.

    Example: Calculating the number of days aged across the entire profile.
        ```python
        >>> import pandas as pd
        >>> from transformer_thermal_model.aging import days_aged
        >>> from transformer_thermal_model.transformer import PaperInsulationType

        >>> one_day = 24 * 4 + 1
        >>> datetime_index = pd.date_range("2020-01-01", periods=one_day, freq="15min", tz="UTC")
        >>> hotspot_profile = pd.Series(100, index=datetime_index)
        >>> total_aging = days_aged(hotspot_profile, PaperInsulationType.NORMAL)
        >>> print(total_aging)
        1.26

        ```

    Returns:
        float: The total aging in days for the period of the given temperature profile.
    """
    aging_profile = hot_spot_profile.apply(_aging_rate_method(insulation_type))
    seconds_aged = aging_profile.index.to_series().diff().dt.total_seconds().fillna(0)
    total_seconds_aged = (aging_profile * seconds_aged).sum()
    total_days_aged = total_seconds_aged / (60 * 60 * 24)  # convert seconds to days

    logger.info(f"Total aging: {total_days_aged} days")
    return total_days_aged


def _normal_paper_aging_rate(hot_spot_temp: float) -> float:
    return 2 ** ((hot_spot_temp - 98) / 6)


def _thermal_upgraded_paper_aging_rate(hot_spot_temp: float) -> float:
    part_1 = 15000 / (110 + 273)
    part_2 = 15000 / (hot_spot_temp + 273)

    return math.exp(part_1 - part_2)


def _aging_rate_method(insulation_type: PaperInsulationType) -> Callable:
    if insulation_type == PaperInsulationType.NORMAL:
        return _normal_paper_aging_rate
    elif insulation_type == PaperInsulationType.THERMAL_UPGRADED:
        return _thermal_upgraded_paper_aging_rate
    else:
        raise ValueError(
            f"Unknown insulation type: {insulation_type}. Must be one of {PaperInsulationType.__members__}."
        )
