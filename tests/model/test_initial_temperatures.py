# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

"""Tests for the thermal model initialization with different initial temperatures."""

import math

import numpy as np
import pandas as pd
import pytest

from transformer_thermal_model.model import Model
from transformer_thermal_model.schemas import InputProfile
from transformer_thermal_model.schemas.thermal_model.initial_state import InitialLoad, InitialTopOilTemp


@pytest.fixture
def base_input_profile():
    """Create a base input profile for testing initialization."""
    datetime_index = [pd.to_datetime("2025-07-01 00:00:00") + pd.Timedelta(minutes=5 * i) for i in range(30)]
    load_series = pd.Series(data=700, index=datetime_index)
    ambient_series = pd.Series(data=20, index=datetime_index)

    return InputProfile.create(
        datetime_index=datetime_index, load_profile=load_series, ambient_temperature_profile=ambient_series
    )


def test_default_init_starts_at_ambient_temperature(base_input_profile, distribution_transformer):
    """Test that without any initialization parameters, the model starts at ambient temperature."""
    model = Model(temperature_profile=base_input_profile, transformer=distribution_transformer)
    results = model.run()

    # First temperature should be at ambient temperature
    assert results.top_oil_temp_profile.iloc[0] == base_input_profile.ambient_temperature_profile[0]

    # Hot-spot should also start at ambient for default initialization
    assert results.hot_spot_temp_profile.iloc[0] == base_input_profile.ambient_temperature_profile[0]


def test_init_top_oil_temp_starts_at_specified_value(base_input_profile, distribution_transformer):
    """Test that initialization with init_top_oil_temp starts at that temperature."""
    init_temp = 50.0
    model = Model(
        temperature_profile=base_input_profile,
        transformer=distribution_transformer,
        initial_condition=InitialTopOilTemp(initial_top_oil_temp=init_temp),
    )
    results = model.run()

    assert math.isclose(results.top_oil_temp_profile.iloc[0], init_temp)
    assert math.isclose(results.hot_spot_temp_profile.iloc[0], init_temp)


def test_different_init_top_oil_temp(base_input_profile, distribution_transformer):
    """Test that different init_top_oil_temp values lead to different starting temperatures."""
    init_temp_low = 30.0
    init_temp_high = 70.0

    model_low = Model(
        temperature_profile=base_input_profile,
        transformer=distribution_transformer,
        initial_condition=InitialTopOilTemp(initial_top_oil_temp=init_temp_low),
    )
    model_high = Model(
        temperature_profile=base_input_profile,
        transformer=distribution_transformer,
        initial_condition=InitialTopOilTemp(initial_top_oil_temp=init_temp_high),
    )

    results_low = model_low.run()
    results_high = model_high.run()

    # At least the first 5 time steps should be higher for the higher initial temperature
    for i in range(5):
        assert results_high.top_oil_temp_profile.iloc[i] > results_low.top_oil_temp_profile.iloc[i]


def test_multiple_init_temperatures_convergence(distribution_transformer):
    """Test that different initial temperatures converge to similar steady state."""
    datetime_index = [pd.to_datetime("2025-07-01 00:00:00") + pd.Timedelta(minutes=5 * i) for i in range(500)]
    load_series = pd.Series(data=700, index=datetime_index)
    ambient_series = pd.Series(data=20, index=datetime_index)

    profile = InputProfile.create(
        datetime_index=datetime_index, load_profile=load_series, ambient_temperature_profile=ambient_series
    )

    init_temps = [20.0, 50.0, 80.0]
    models = [
        Model(
            temperature_profile=profile,
            transformer=distribution_transformer,
            initial_condition=InitialTopOilTemp(initial_top_oil_temp=init_temp),
        )
        for init_temp in init_temps
    ]

    results_list = [model.run() for model in models]

    # All should converge to similar final temperatures
    final_temps = [results.top_oil_temp_profile.iloc[-1] for results in results_list]
    for i in range(1, len(final_temps)):
        assert abs(final_temps[i] - final_temps[0]) < 0.1  # within 0.1 degree


def test_initial_load_stabilizes_temperature(base_input_profile, distribution_transformer):
    """Test that initial_load parameter stabilizes the temperature at that load level."""
    initial_load = 500.0
    model = Model(
        temperature_profile=base_input_profile,
        transformer=distribution_transformer,
        initial_condition=InitialLoad(initial_load=initial_load),
    )
    results = model.run()

    # The initial temperatures should be higher than with default init
    model_default = Model(temperature_profile=base_input_profile, transformer=distribution_transformer)
    results_default = model_default.run()

    assert results.top_oil_temp_profile.iloc[0] > results_default.top_oil_temp_profile.iloc[0]
    assert results.hot_spot_temp_profile.iloc[0] > results.top_oil_temp_profile.iloc[0]


def test_higher_initial_load_higher_temperature(base_input_profile, distribution_transformer):
    """Test that higher initial load results in higher initial temperature."""
    load_low = 300.0
    load_high = 700.0

    model_low = Model(
        temperature_profile=base_input_profile,
        transformer=distribution_transformer,
        initial_condition=InitialLoad(initial_load=load_low),
    )
    model_high = Model(
        temperature_profile=base_input_profile,
        transformer=distribution_transformer,
        initial_condition=InitialLoad(initial_load=load_high),
    )

    results_low = model_low.run()
    results_high = model_high.run()

    # Higher load should result in higher initial temperature
    assert results_high.top_oil_temp_profile.iloc[0] > results_low.top_oil_temp_profile.iloc[0]


def test_initial_load_matches_profile_load(base_input_profile, distribution_transformer):
    """Test that when initial_load equals profile load, temperature stabilizes quickly."""
    profile_load = 700.0
    model = Model(
        temperature_profile=base_input_profile,
        transformer=distribution_transformer,
        initial_condition=InitialLoad(initial_load=profile_load),
    )
    results = model.run()

    # When initial load equals profile load, initial temperature should match steady state behavior
    # The transient should be minimal
    top_oil_temps = results.top_oil_temp_profile.values
    temp_range = np.max(top_oil_temps) - np.min(top_oil_temps)
    assert temp_range < 0.001, "Temperature should not vary when initial load matches profile"
