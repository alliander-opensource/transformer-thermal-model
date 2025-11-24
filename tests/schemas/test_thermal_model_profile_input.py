# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from contextlib import nullcontext as does_not_raise
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from transformer_thermal_model.schemas.thermal_model.input_profile import InputProfile


@pytest.mark.parametrize(
    "datetime_index, load_profile, ambient_temperature_profile, top_oil_temperature_profile, expectation, message",
    [
        (
            pd.date_range("2021-01-01 00:00:00", periods=3),
            [1, 2, 3],
            [1, 2, 3],
            None,
            does_not_raise(),
            None,
        ),
        (
            pd.date_range("2021-01-01 00:00:00", periods=3),
            np.array([1, 2, 3]),
            [1, 2, 3],
            None,
            does_not_raise(),
            None,
        ),
        (
            pd.date_range("2021-01-01 00:00:00", periods=3),
            [1, -2, 3],
            [1, 2, 3],
            None,
            pytest.raises(ValueError),
            "The load profile must not contain negative values",
        ),
        (
            pd.date_range("2021-01-01 00:00:00", periods=3),
            np.array([1, 2, -3]),
            [1, 2, 3],
            None,
            pytest.raises(ValueError),
            "The load profile must not contain negative values",
        ),
        (
            pd.date_range("2021-01-01 00:00:00", periods=3),
            np.array([1, 2, 3]),
            [1, 2, 3],
            [2, 3, 4],
            does_not_raise(),
            None,
        ),
        (
            pd.date_range("2021-01-01 00:00:00", periods=3),
            pd.Series([1, 2, 3]),
            [1, 2, 3],
            None,
            does_not_raise(),
            None,
        ),
        (
            pd.date_range("2021-01-01 00:00:00", periods=3),
            pd.Series([1, 2, 3], index=pd.date_range("2021-01-01 00:00:00", periods=3)),
            [1, 2, 3],
            None,
            does_not_raise(),
            None,
        ),
        (
            np.array([datetime(2021, 1, 1, 0, 0, 0), datetime(2021, 1, 1, 0, 15, 0), datetime(2021, 1, 1, 0, 30, 0)]),
            [1, 2, 3],
            [1, 2, 3],
            None,
            does_not_raise(),
            None,
        ),
        (
            pd.date_range("2021-01-01 00:00:00", periods=3),
            [1, 2, 3],
            [1, 2],
            None,
            pytest.raises(ValueError),
            "The length of the profiles and index should be the same",
        ),
        (
            pd.date_range("2021-01-01 00:00:00", periods=3),
            [1, 2],
            [1, 2, 3],
            None,
            pytest.raises(ValueError),
            "The length of the profiles and index should be the same",
        ),
        (
            pd.to_datetime(["2021-01-01 00:00:00", "2021-01-01 00:15:00", "2021-01-01 00:05:00"]),
            [1, 2, 3],
            [1, 2, 3],
            None,
            pytest.raises(ValueError),
            "The datetime index should be sorted.",
        ),
        (
            np.array(["a", "b", "c"]),
            [1, 2, 3],
            [1, 2, 3],
            None,
            pytest.raises(ValueError),
            None,
        ),
        (
            {"a": 1, "b": 3, "c": 3},
            [1, 2, 3],
            [1, 2, 3],
            None,
            pytest.raises(ValueError),
            "Could not convert object to NumPy datetime",
        ),
        (
            np.array(["2021-01-01 00:00:00", "2021-01-01 00:15:00", "2021-01-01 00:25:00"], dtype="datetime64[s]"),
            [2, 4, 5],
            {"a": 1, "b": 3, "c": 3},
            None,
            pytest.raises(TypeError),
            None,
        ),
        (
            np.array(["2021-01-01 00:00:00", "2021-01-01 00:15:00", "2021-01-01 00:25:00"], dtype="datetime64[s]"),
            [2, 4, 5],
            [2, 4, 5],
            {"a": 1, "b": 3, "c": 3},
            pytest.raises(TypeError),
            None,
        ),
        (
            np.array(["2021-01-01 00:00:00", "2021-01-01 00:15:00", "2021-01-01 00:25:00"], dtype="datetime64[s]"),
            [[2, 4, 5], [2, 4, 5]],
            [2, 3, 4],
            None,
            pytest.raises(ValueError),
            None,
        ),
        (
            np.array(["2021-01-01 00:00:00", "2021-01-01 00:15:00", "2021-01-01 00:25:00"], dtype="datetime64[s]"),
            (2, 4, 5),
            pd.DataFrame([2, 3, 4], [2, 3, 4]),
            None,
            pytest.raises(ValueError),
            "array must be one-dimensional",
        ),
        (
            np.array(["2021-01-01 00:00:00", "2021-01-01 00:15:00", "2021-01-01 00:25:00"], dtype="datetime64[s]"),
            (2, 4, 5),
            [2, 3, 4],
            pd.DataFrame([2, 3, 4], [2, 3, 4]),
            pytest.raises(ValueError),
            "array must be one-dimensional.",
        ),
        (
            [1, 2, 3],  # unixtimes
            [1, 2, 3],
            [1, 2, 3],
            None,
            pytest.raises(ValueError),
            "Converting an integer to a NumPy datetime requires a specified unit",
        ),
        (
            np.array(["2021-01-01 00:00:00", "2021-01-01 00:15:00", "2021-01-01 00:25:00"], dtype="datetime64[s]"),
            (2, 4, 5),
            [2, 3, 4],
            [2, 3, 4, 2, 3, 4],
            pytest.raises(ValueError),
            "The length of the top_oil_temperature_profile should match",
        ),
    ],
)
def test_that_the_input_data_for_thermal_model_is_validated_properly(
    datetime_index, load_profile, ambient_temperature_profile, top_oil_temperature_profile, expectation, message
):
    """Test that the InputProfile can be created from two Series."""
    with expectation as e:
        assert (
            InputProfile.create(
                datetime_index=datetime_index,
                load_profile=load_profile,
                ambient_temperature_profile=ambient_temperature_profile,
                top_oil_temperature_profile=top_oil_temperature_profile,
            )
            is not None
        )
    assert message is None or message in str(e)


def test_that_the_length_of_input_data_is_correct():
    """Test that the length of the input data is correct."""
    datetime_index = pd.date_range("2021-01-01 00:00:00", periods=3)
    load_profile = [1, 2, 3]
    ambient_temperature_profile = [1, 2, 3]
    thermal_model_input = InputProfile.create(
        datetime_index=datetime_index,
        load_profile=load_profile,
        ambient_temperature_profile=ambient_temperature_profile,
    )
    assert len(thermal_model_input) == 3


def test_input_profile_from_dataframe():
    """Test that the InputProfile can be created from a DataFrame."""
    data = {
        "datetime_index": pd.date_range("2021-01-01 00:00:00", periods=3),
        "load_profile": [1, 2, 3],
        "ambient_temperature_profile": [10, 20, 30],
    }
    df = pd.DataFrame(data)
    input_profile = InputProfile.from_dataframe(df)

    assert len(input_profile) == 3
    assert np.array_equal(input_profile.load_profile, data["load_profile"])
    assert np.array_equal(input_profile.ambient_temperature_profile, data["ambient_temperature_profile"])
    assert np.array_equal(input_profile.datetime_index, data["datetime_index"])


def test_from_dataframe_missing_columns():
    """Test that a ValueError is raised when the DataFrame is missing required columns."""
    # Create a dataframe missing one of the required columns
    df_missing_columns = pd.DataFrame(
        {
            "datetime_index": ["2025-04-17T00:00:00", "2025-04-17T01:00:00"],
            "load_profile": [0.8, 0.9],
            # 'ambient_temperature_profile' is missing
        }
    )

    with pytest.raises(
        ValueError, match="The dataframe is missing the following required columns: ambient_temperature_profile"
    ):
        InputProfile.from_dataframe(df_missing_columns)
