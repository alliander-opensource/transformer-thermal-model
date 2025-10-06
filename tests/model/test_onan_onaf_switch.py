# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.model.thermal_model import Model
from transformer_thermal_model.schemas.specifications.transformer import UserTransformerSpecifications
from transformer_thermal_model.schemas.thermal_model.onaf_switch import FanSwitchConfig, ONAFSwitch
from transformer_thermal_model.transformer.power import PowerTransformer


def test_start_cooling_type(default_user_trafo_specs: UserTransformerSpecifications):
    """Check that the transformer starts with the correct cooling type."""
    default_user_trafo_specs.top_oil_temp_rise = 60
    default_user_trafo_specs.winding_oil_gradient = 25
    default_user_trafo_specs.hot_spot_fac = 1.1

    is_on = [True] * 100
    onaf_switch = ONAFSwitch(
        fans_status=is_on,
        temperature_threshold=None,
        nom_load_sec_side_ONAN=1600,
        top_oil_temp_rise_ONAN=50.5,
        winding_oil_gradient_ONAN=23,
        hot_spot_fac_ONAN=1.2,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, ONAF_switch=onaf_switch
    )
    assert transformer.specs.nom_load_sec_side == default_user_trafo_specs.nom_load_sec_side
    assert transformer.specs.top_oil_temp_rise == default_user_trafo_specs.top_oil_temp_rise
    assert transformer.specs.winding_oil_gradient == default_user_trafo_specs.winding_oil_gradient
    assert transformer.specs.hot_spot_fac == default_user_trafo_specs.hot_spot_fac

    is_on = [False] * 100
    onaf_switch.fans_status = is_on
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, ONAF_switch=onaf_switch
    )
    assert transformer.specs.nom_load_sec_side == onaf_switch.nom_load_sec_side_ONAN
    assert transformer.specs.top_oil_temp_rise == onaf_switch.top_oil_temp_rise_ONAN
    assert transformer.specs.winding_oil_gradient == onaf_switch.winding_oil_gradient_ONAN
    assert transformer.specs.hot_spot_fac == onaf_switch.hot_spot_fac_ONAN

    onaf_switch = ONAFSwitch(
        fans_status=None,
        temperature_threshold=FanSwitchConfig(activation_temp=85, deactivation_temp=75),
        nom_load_sec_side_ONAN=1600,
        top_oil_temp_rise_ONAN=50.5,
        winding_oil_gradient_ONAN=23,
        hot_spot_fac_ONAN=1.2,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, ONAF_switch=onaf_switch
    )
    assert transformer.specs.nom_load_sec_side == onaf_switch.nom_load_sec_side_ONAN
    assert transformer.specs.top_oil_temp_rise == onaf_switch.top_oil_temp_rise_ONAN
    assert transformer.specs.winding_oil_gradient == onaf_switch.winding_oil_gradient_ONAN
    assert transformer.specs.hot_spot_fac == onaf_switch.hot_spot_fac_ONAN


def test_wrong_ONAF_switch(default_user_trafo_specs: UserTransformerSpecifications, iec_load_profile):
    """Check that a ValueError is raised when the length of fans_status does not match the temperature profile."""
    is_on = [True] * 100
    onaf_switch = ONAFSwitch(
        fans_status=is_on,
        temperature_threshold=None,
        nom_load_sec_side_ONAN=1600,
        top_oil_temp_rise_ONAN=50.5,
        winding_oil_gradient_ONAN=23,
        hot_spot_fac_ONAN=1.2,
    )
    with pytest.raises(ValueError, match=("ONAF switch only works when the cooling type is ONAF.")):
        transformer = PowerTransformer(
            user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAN, ONAF_switch=onaf_switch
        )

    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, ONAF_switch=onaf_switch
    )
    with pytest.raises(
        ValueError,
        match=(
            "The length of the fans_status list in the ONAF_switch must be equal to the length of "
            "the temperature profile."
        ),
    ):
        Model(transformer=transformer, temperature_profile=iec_load_profile)


def test_complete_ONAN_ONAF_switch_fans_status(
    default_user_trafo_specs: UserTransformerSpecifications, constant_load_profile
):
    """Check that the transformer can handle a complete ONAF switch scenario."""
    default_user_trafo_specs.top_oil_temp_rise = 60
    default_user_trafo_specs.winding_oil_gradient = 25
    default_user_trafo_specs.hot_spot_fac = 1.1
    default_user_trafo_specs.nom_load_sec_side = constant_load_profile.load_profile[0] * 1.2

    is_on = [False] * 50 + [True] * (len(constant_load_profile.datetime_index) - 50)
    onaf_switch = ONAFSwitch(
        fans_status=is_on,
        temperature_threshold=None,
        nom_load_sec_side_ONAN=constant_load_profile.load_profile[0] * 0.8,
        top_oil_temp_rise_ONAN=50.5,
        winding_oil_gradient_ONAN=23,
        hot_spot_fac_ONAN=1.2,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, ONAF_switch=onaf_switch
    )
    model = Model(transformer=transformer, temperature_profile=constant_load_profile)
    output = model.run()

    # After 50 steps, the cooling should switch to ONAF and the top-oil temperature should be lower
    assert output.top_oil_temp_profile.iloc[45] > output.top_oil_temp_profile.iloc[55]


def test_complete_ONAN_ONAF_switch_temp_threshold(
    default_user_trafo_specs: UserTransformerSpecifications, constant_load_profile_minutes
):
    """Check that the transformer can handle a complete ONAF switch scenario based on temperature thresholds."""
    default_user_trafo_specs.amb_temp_surcharge = 0
    default_user_trafo_specs.top_oil_temp_rise = 60
    default_user_trafo_specs.winding_oil_gradient = 25
    default_user_trafo_specs.hot_spot_fac = 1.1
    default_user_trafo_specs.nom_load_sec_side = constant_load_profile_minutes.load_profile[0] * 5
    temp_threshold = FanSwitchConfig(activation_temp=60, deactivation_temp=50)
    onaf_switch = ONAFSwitch(
        fans_status=None,
        temperature_threshold=temp_threshold,
        nom_load_sec_side_ONAN=constant_load_profile_minutes.load_profile[0] * 0.8,
        top_oil_temp_rise_ONAN=50.5,
        winding_oil_gradient_ONAN=23,
        hot_spot_fac_ONAN=1.2,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, ONAF_switch=onaf_switch
    )
    model = Model(transformer=transformer, temperature_profile=constant_load_profile_minutes)
    output = model.run()

    # The transformer now cools really fast in ONAF and heats up fast in ONAN

    # after warmup period, the top-oil temperature should be above 45 degrees
    assert output.top_oil_temp_profile[20:].min() > 45

    # at some point, the top-oil temperature should exceed the activation temperature and switch to ONAF,
    # then it should cool down
    assert output.top_oil_temp_profile.max() < 65
