# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import UserTransformerSpecifications
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
