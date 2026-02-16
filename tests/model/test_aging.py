# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0
import numpy as np
import pandas as pd
import pytest

from transformer_thermal_model.aging import days_aged
from transformer_thermal_model.transformer import PaperInsulationType


def test_paper_aging_98():
    """Test the paper aging model for constant 98 degrees."""
    one_day = 24 * 4 + 1
    datetime_index = pd.date_range("2020-01-01", periods=one_day, freq="15min", tz="UTC")
    hotspot_profile = pd.Series(98, index=datetime_index)

    total_aging = days_aged(hotspot_profile, PaperInsulationType.NORMAL)
    assert np.isclose(total_aging, 1.0)


def test_paper_aging():
    """Test the paper aging model."""
    one_day = 24 * 4 + 1
    datetime_index = pd.date_range("2020-01-01", periods=one_day, freq="15min", tz="UTC")
    hotspot_profile = pd.Series(100, index=datetime_index)
    total_aging = days_aged(hotspot_profile, PaperInsulationType.NORMAL)
    assert np.isclose(total_aging, 1.259921, rtol=1e-5)

    total_aging = days_aged(hotspot_profile, PaperInsulationType.THERMAL_UPGRADED)
    assert np.isclose(total_aging, 0.349942, rtol=1e-5)


def test_assert_never_is_reached_with_invalid_values():
    """Test that assert_never is reached with invalid values."""
    one_day = 24 * 4 + 1
    datetime_index = pd.date_range("2020-01-01", periods=one_day, freq="15min", tz="UTC")
    hotspot_profile = pd.Series(100, index=datetime_index)

    with pytest.raises(AssertionError):
        days_aged(hotspot_profile, "invalid_value")
