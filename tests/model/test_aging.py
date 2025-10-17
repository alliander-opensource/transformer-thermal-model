# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

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
    assert total_aging == pytest.approx(1, rel=1e-2)


def test_paper_aging():
    """Test the paper aging model."""
    one_day = 24 * 4 + 1
    datetime_index = pd.date_range("2020-01-01", periods=one_day, freq="15min", tz="UTC")
    hotspot_profile = pd.Series(100, index=datetime_index)
    total_aging = days_aged(hotspot_profile, PaperInsulationType.NORMAL)
    assert total_aging == pytest.approx(1.26, rel=1e-2)

    total_aging = days_aged(hotspot_profile, PaperInsulationType.THERMAL_UPGRADED)
    assert total_aging == pytest.approx(0.35, rel=1e-2)
