# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import copy

import numpy as np
import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import (
    UserTransformerSpecifications,
)
from transformer_thermal_model.transformer import DistributionTransformer, PowerTransformer, ThreeWindingTransformer


def test_transformer_initialization():
    """Test the initialization of the Transformer class."""
    tr_specs = UserTransformerSpecifications(
        load_loss=1000,  # Transformer load loss [W]
        nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
        no_load_loss=200,  # Transformer no-load loss [W]
        amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
    )
    onaf_transformer = PowerTransformer(user_specs=tr_specs, cooling_type=CoolerType.ONAF)

    assert onaf_transformer.cooling_type == CoolerType.ONAF

    onan_transformer = PowerTransformer(user_specs=tr_specs, cooling_type=CoolerType.ONAN)

    assert onan_transformer.cooling_type == CoolerType.ONAN


@pytest.fixture
def some_specs_override(default_user_trafo_specs) -> UserTransformerSpecifications:
    """Define some basic specifications to check if the user overrides come through."""
    return default_user_trafo_specs.model_copy(
        update={
            "winding_oil_gradient": 20,
            "nom_load_sec_side": 20,
        }
    )


def test_set_default_power_transformer_values(default_user_trafo_specs, some_specs_override):
    """Test the _set_default_values method of the Transformer class."""
    default_transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF)
    transformer = PowerTransformer(user_specs=some_specs_override, cooling_type=CoolerType.ONAF)

    # These values are provided in the tr_specs dictionary, so they should not be loaded from the default values
    assert transformer.specs.nom_load_sec_side == 20
    assert transformer.specs.winding_oil_gradient == 20

    # These values are not provided in the tr_specs dictionary, so they should be loaded from the default values
    assert transformer.specs.oil_const_k11 == default_transformer.defaults.oil_const_k11
    assert transformer.specs.winding_const_k21 == default_transformer.defaults.winding_const_k21
    assert transformer.specs.winding_const_k22 == default_transformer.defaults.winding_const_k22
    assert transformer.specs.oil_exp_x == default_transformer.defaults.oil_exp_x
    assert transformer.specs.winding_exp_y == default_transformer.defaults.winding_exp_y
    assert transformer.specs.time_const_oil == default_transformer.defaults.time_const_oil

    default_transformer = DistributionTransformer(user_specs=default_user_trafo_specs)
    transformer = DistributionTransformer(user_specs=some_specs_override)

    # These values are provided in the tr_specs dictionary, so they should not be loaded from the default values
    assert transformer.specs.nom_load_sec_side == 20
    assert transformer.specs.winding_oil_gradient == 20

    # These values are not provided in the tr_specs dictionary, so they should be loaded from the default values
    assert transformer.specs.oil_const_k11 == default_transformer.defaults.oil_const_k11
    assert transformer.specs.winding_const_k21 == default_transformer.defaults.winding_const_k21
    assert transformer.specs.winding_const_k22 == default_transformer.defaults.winding_const_k22
    assert transformer.specs.oil_exp_x == default_transformer.defaults.oil_exp_x
    assert transformer.specs.winding_exp_y == default_transformer.defaults.winding_exp_y
    assert transformer.specs.time_const_oil == default_transformer.defaults.time_const_oil


def test_that_creating_an_onaf_trafo_after_onan_trafo_does_not_affect_the_classvar_defaults(default_user_trafo_specs):
    """Test that the defaults of the PowerTransformer class are not affected when creating a new instance."""
    onan_transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAN)
    first_defaults = copy.deepcopy(PowerTransformer.defaults)
    assert onan_transformer.defaults == PowerTransformer._onan_defaults
    assert first_defaults == PowerTransformer.defaults

    # This set to onan should NOT change the defaults of PowerTransformer
    onaf_transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF)
    assert onaf_transformer.defaults == PowerTransformer._onaf_defaults
    assert onaf_transformer._onaf_defaults == PowerTransformer._onaf_defaults
    assert onaf_transformer.defaults != PowerTransformer.defaults
    assert first_defaults == PowerTransformer.defaults


def test_that_creating_an_onan_trafo_after_onaf_trafo_does_not_affect_the_classvar_defaults(default_user_trafo_specs):
    """Test that the defaults of the PowerTransformer class are not affected when creating a new instance."""
    onaf_transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF)
    first_defaults = copy.deepcopy(PowerTransformer.defaults)
    assert onaf_transformer.defaults == PowerTransformer._onaf_defaults
    assert first_defaults == PowerTransformer.defaults

    # This set to onan should NOT change the defaults of PowerTransformer
    onan_transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAN)
    assert onan_transformer.defaults == PowerTransformer._onan_defaults
    assert onan_transformer._onan_defaults == PowerTransformer._onan_defaults
    assert onan_transformer.defaults != PowerTransformer.defaults
    assert first_defaults == PowerTransformer.defaults


def check_dif_onan_onaf(onan_power_transformer, onaf_power_transformer):
    """Check the difference between the ONAN and ONAF transformer."""
    assert onan_power_transformer.specs.time_const_oil != onaf_power_transformer.specs.time_const_oil
    assert onan_power_transformer.specs.time_const_winding != onaf_power_transformer.specs.time_const_winding


@pytest.mark.parametrize(
    "transformer",
    [
        PowerTransformer(
            cooling_type=CoolerType.ONAN,
            user_specs=UserTransformerSpecifications(
                load_loss=10000,
                nom_load_sec_side=1000,
                no_load_loss=1000,
                amb_temp_surcharge=0,
                hot_spot_fac=None,
            ),
        ),
        PowerTransformer(
            cooling_type=CoolerType.ONAF,
            user_specs=UserTransformerSpecifications(
                load_loss=10000,
                nom_load_sec_side=1000,
                no_load_loss=1000,
                amb_temp_surcharge=0,
                hot_spot_fac=None,
            ),
        ),
        DistributionTransformer(
            user_specs=UserTransformerSpecifications(
                load_loss=10000,
                nom_load_sec_side=1000,
                no_load_loss=1000,
                amb_temp_surcharge=0,
                hot_spot_fac=None,
            ),
        ),
    ],
)
def test_that_hot_spot_factor_is_set_to_default_if_none_provided(transformer):
    """Test that a transformer initiated with `hot_spot_factor=None`, the value is set to the default value."""
    assert transformer.specs.hot_spot_fac == transformer.defaults.hot_spot_fac


def test_initialize_three_winding_transformer(user_three_winding_transformer_specs, three_winding_input_profile):
    """Initialize a ThreeWindingTransformer with the given user specifications."""
    transformer = ThreeWindingTransformer(user_specs=user_three_winding_transformer_specs, cooling_type=CoolerType.ONAN)

    load_profile = three_winding_input_profile.load_profile_array
    end_temp_top_oil = transformer._end_temperature_top_oil(load_profile)

    assert transformer.specs.no_load_loss == user_three_winding_transformer_specs.no_load_loss
    assert transformer.specs.time_const_oil == 210  # Default value for ONAN transformer
    assert end_temp_top_oil.shape == (len(three_winding_input_profile.datetime_index),)


def test_three_winding_top_oil_calculation(user_three_winding_transformer_specs):
    """Test the top oil temperature calculation for a three-winding transformer."""
    transformer = ThreeWindingTransformer(user_specs=user_three_winding_transformer_specs, cooling_type=CoolerType.ONAN)

    # constant load profile should provide constant top oil temperature
    load_profile = np.array([[3000, 3000, 3000, 3000], [2000, 2000, 2000, 2000], [1000, 1000, 1000, 1000]])
    end_temp_top_oil = transformer._end_temperature_top_oil(load_profile)
    assert np.all(end_temp_top_oil == end_temp_top_oil[0])

    # If the load load increases, the top oil temperature should increase
    load_profile = np.array([[3000, 4000, 5000, 6000], [2000, 3000, 4000, 5000], [1000, 2000, 3000, 4000]])
    end_temp_top_oil = transformer._end_temperature_top_oil(load_profile)
    assert all(earlier < later for earlier, later in zip(end_temp_top_oil, end_temp_top_oil[1:], strict=False))

    # If the load load decreases, the top oil temperature should decrease
    load_profile = np.array([[6000, 5000, 4000, 3000], [5000, 4000, 3000, 2000], [4000, 3000, 2000, 1000]])
    end_temp_top_oil = transformer._end_temperature_top_oil(load_profile)
    assert all(earlier > later for earlier, later in zip(end_temp_top_oil, end_temp_top_oil[1:], strict=False))
