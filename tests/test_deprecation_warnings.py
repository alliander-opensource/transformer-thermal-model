# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0
import pytest

from transformer_thermal_model.components.bushing_config import BushingConfig
from transformer_thermal_model.components.transformer_side import TransformerSide
from transformer_thermal_model.components.vector_config import VectorConfig
from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import TransformerComponentSpecifications, UserTransformerSpecifications
from transformer_thermal_model.transformer import PowerTransformer


def test_bushing_config_warns():
    """Test that accessing BushingConfig raises a DeprecationWarning."""
    with pytest.warns(DeprecationWarning, match="BushingConfig was deprecated"):
        value = BushingConfig.SINGLE_BUSHING
        assert value == "single bushing"


def test_transformer_side_warns():
    """Test that accessing TransformerSide raises a DeprecationWarning."""
    with pytest.warns(DeprecationWarning, match="TransformerSide was deprecated"):
        value = TransformerSide.PRIMARY
        assert value == "primary"


def test_vector_config_warns():
    """Test that accessing VectorConfig raises a DeprecationWarning."""
    with pytest.warns(DeprecationWarning, match="VectorConfig was deprecated"):
        value = VectorConfig.STAR
        assert value == "star"


def test_power_transformer_components_warns():
    """Test that accessing PowerTransformerComponents raises a DeprecationWarning."""
    user_specs = UserTransformerSpecifications(
        load_loss=1000,
        nom_load_sec_side=1500,
        no_load_loss=200,
    )
    cooling_type = CoolerType.ONAN

    comp_specs = TransformerComponentSpecifications(
        tap_chang_capacity=600,  # Tap changer nominal current [A]
        nom_load_prim_side=550,  # Transformer nominal current primary side [A]
        tap_chang_conf=VectorConfig.TRIANGLE_OUTSIDE,
    )
    with pytest.warns(DeprecationWarning, match="PowerTransformerComponents was deprecated"):
        transformer = PowerTransformer(
            user_specs=user_specs,
            cooling_type=cooling_type,
            internal_component_specs=comp_specs,
        )
        assert transformer is not None
