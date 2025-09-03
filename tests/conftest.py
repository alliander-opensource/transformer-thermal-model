# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import pandas as pd
import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import InputProfile, UserTransformerSpecifications
from transformer_thermal_model.transformer import DistributionTransformer, PowerTransformer


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
def onan_power_sample_profile_dataframe(onan_power_transformer):
    """Create a sample profile for testing."""
    tau_time = onan_power_transformer.specs.oil_const_k11 * onan_power_transformer.specs.time_const_oil
    ambient_temp = 20
    time_step_list = [pd.to_datetime("2021-01-01 00:00:00") + pd.Timedelta(minutes=i * tau_time) for i in range(0, 16)]
    profile = pd.DataFrame(
        {
            "timestamp": time_step_list,
            "load": [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 0, 0, 0, 0, 0, 0, 0, 0],
            "ambient_temperature": [ambient_temp] * len(time_step_list),
        }
    )
    return profile
