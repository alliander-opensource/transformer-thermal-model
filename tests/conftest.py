# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import pandas as pd
import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import InputProfile, UserTransformerSpecifications, ThreeWindingInputProfile
from transformer_thermal_model.schemas.specifications.transformer import (
    ThreePhaseTransformerSpecifications,
    WindingSpecifications,
)
from transformer_thermal_model.transformer import DistributionTransformer, PowerTransformer, ThreePhaseTransformer


@pytest.fixture(scope="function")
def default_user_trafo_specs() -> UserTransformerSpecifications:
    """Define default transformer specs that can be used to quickly init transformers."""
    return UserTransformerSpecifications(
        load_loss=1000,  # Transformer load loss [W]
        nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
        no_load_loss=200,  # Transformer no-load loss [W]
        amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
    )


@pytest.fixture(scope="function")
def onan_power_transformer() -> PowerTransformer:
    """Create a ONAN power transformer object."""
    user_specs = UserTransformerSpecifications(
        load_loss=1000,  # Transformer load loss [W]
        nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
        no_load_loss=200,  # Transformer no-load loss [W]
        amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
        hot_spot_fac=1.1,
    )
    trafo = PowerTransformer(user_specs=user_specs, cooling_type=CoolerType.ONAN)
    return trafo


@pytest.fixture(scope="function")
def onaf_power_transformer() -> PowerTransformer:
    """Create a ONAF power transformer object."""
    user_specs = UserTransformerSpecifications(
        load_loss=1000,  # Transformer load loss [W]
        nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
        no_load_loss=200,  # Transformer no-load loss [W]
        amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
        hot_spot_fac=1.1,
    )
    trafo = PowerTransformer(user_specs=user_specs, cooling_type=CoolerType.ONAF)
    return trafo


@pytest.fixture(scope="function")
def distribution_transformer() -> DistributionTransformer:
    """Create a distribution transformer object."""
    user_specs = UserTransformerSpecifications(
        load_loss=1000,  # Transformer load loss [W]
        nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
        no_load_loss=200,  # Transformer no-load loss [W]
        amb_temp_surcharge=20,  # Ambient temperature surcharge [K],
        hot_spot_fac=1.1,
    )
    trafo = DistributionTransformer(user_specs=user_specs)
    return trafo


@pytest.fixture(scope="function")
def iec_load_profile():
    """Create a load profile based on the IECs data."""
    # Define the breakpoints (minutes) and corresponding load factors
    breakpoints = [0, 190, 365, 500, 705, 730, 745]
    load_factors = [1.0, 0.6, 1.5, 0.3, 2.1, 0.0]

    # Generate the time series
    timestamps = []
    loads = []

    start_time = pd.to_datetime("2021-01-01 00:00:00")

    timestep = 5
    for i in range(len(breakpoints) - 1):
        start = breakpoints[i]
        end = breakpoints[i + 1]
        n_steps = (end - start) // timestep
        for step in range(1, n_steps + 1):
            timestamps.append(start_time + pd.Timedelta(minutes=start + step * timestep))
            loads.append(load_factors[i])

    # Example: constant ambient temperature
    ambient_temperature = [25.6] * len(timestamps)

    profile = pd.DataFrame(
        {
            "datetime_index": timestamps,
            "load_profile": loads,
            "ambient_temperature_profile": ambient_temperature,
        }
    )
    input_profile = InputProfile.from_dataframe(df=profile)
    return input_profile


@pytest.fixture(scope="function")
def three_phase_transformer() -> ThreePhaseTransformer:
    """Create a three-phase transformer object."""
    three_phase_specs = ThreePhaseTransformerSpecifications(
        lv_winding=WindingSpecifications(nom_load=1000, winding_oil_gradient=2),
        mv_winding=WindingSpecifications(nom_load=2000, winding_oil_gradient=3),
        hv_winding=WindingSpecifications(nom_load=3000, winding_oil_gradient=4),
        load_loss_hv_lv=50,
        load_loss_hv_mv=75,
        load_loss_mv_lv=25,
    )

    user_specs = UserTransformerSpecifications(
        load_loss=1000,  # Transformer load loss [W]
        nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
        no_load_loss=200,  # Transformer no-load loss [W]
        amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
        hot_spot_fac=1.1,
        three_phase=three_phase_specs,
    )

    trafo = ThreePhaseTransformer(user_specs=user_specs, cooling_type=CoolerType.ONAN)
    return trafo


@pytest.fixture(scope="function")
def three_fase_profile_input() -> ThreeWindingInputProfile:
    """Create a three-phase transformer input profile."""
    datetime_index = pd.date_range("2021-01-01 00:00:00", periods=3)
    load_profile_high_voltage_side = [1, 2, 3]
    load_profile_middle_voltage_side = [4, 5, 6]
    load_profile_low_voltage_side = [7, 8, 9]
    ambient_temperature_profile = [10, 20, 30]

    thermal_model_input = ThreeWindingInputProfile.create(
        datetime_index=datetime_index,
        load_profile_high_voltage_side=load_profile_high_voltage_side,
        load_profile_middle_voltage_side=load_profile_middle_voltage_side,
        load_profile_low_voltage_side=load_profile_low_voltage_side,
        ambient_temperature_profile=ambient_temperature_profile
    )
    return thermal_model_input
