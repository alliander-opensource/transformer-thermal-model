# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import math

import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.model.thermal_model import Model
from transformer_thermal_model.schemas.specifications.transformer import (
    UserThreeWindingTransformerSpecifications,
    UserTransformerSpecifications,
)
from transformer_thermal_model.schemas.thermal_model.input_profile import ThreeWindingInputProfile
from transformer_thermal_model.schemas.thermal_model.onaf_switch import (
    FanSwitchConfig,
    ONAFSwitch,
    ONANParameters,
    ONANWindingParameters,
    ThreeWindingONAFSwitch,
    ThreeWindingONANParameters,
)
from transformer_thermal_model.transformer.power import PowerTransformer
from transformer_thermal_model.transformer.threewinding import ThreeWindingTransformer


def test_start_cooling_type(default_user_trafo_specs: UserTransformerSpecifications):
    """Check that the transformer starts with the correct cooling type."""
    default_user_trafo_specs.top_oil_temp_rise = 60
    default_user_trafo_specs.winding_oil_gradient = 25
    default_user_trafo_specs.hot_spot_fac = 1.1

    is_on = [True] * 100

    onan_parameters = ONANParameters(
        top_oil_temp_rise=50.5,
        time_const_oil=150,
        time_const_windings=7,
        load_loss=default_user_trafo_specs.load_loss,
        nom_load_sec_side=1600,
        winding_oil_gradient=23,
        hot_spot_fac=1.2,
    )

    onaf_switch = ONAFSwitch(
        fans_status=is_on,
        temperature_threshold=None,
        onan_parameters=onan_parameters,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, onaf_switch=onaf_switch
    )
    assert transformer.specs.nom_load_sec_side == default_user_trafo_specs.nom_load_sec_side
    assert transformer.specs.top_oil_temp_rise == default_user_trafo_specs.top_oil_temp_rise
    assert transformer.specs.winding_oil_gradient == default_user_trafo_specs.winding_oil_gradient
    assert transformer.specs.hot_spot_fac == default_user_trafo_specs.hot_spot_fac

    is_on = [False] * 100
    onaf_switch.fans_status = is_on
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, onaf_switch=onaf_switch
    )
    assert transformer.specs.nom_load_sec_side == onaf_switch.onan_parameters.nom_load_sec_side
    assert transformer.specs.top_oil_temp_rise == onaf_switch.onan_parameters.top_oil_temp_rise
    assert transformer.specs.winding_oil_gradient == onaf_switch.onan_parameters.winding_oil_gradient
    assert transformer.specs.hot_spot_fac == onaf_switch.onan_parameters.hot_spot_fac

    onaf_switch = ONAFSwitch(
        fans_status=None,
        temperature_threshold=FanSwitchConfig(activation_temp=85, deactivation_temp=75),
        onan_parameters=onan_parameters,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, onaf_switch=onaf_switch
    )
    assert transformer.specs.nom_load_sec_side == onaf_switch.onan_parameters.nom_load_sec_side
    assert transformer.specs.top_oil_temp_rise == onaf_switch.onan_parameters.top_oil_temp_rise
    assert transformer.specs.winding_oil_gradient == onaf_switch.onan_parameters.winding_oil_gradient
    assert transformer.specs.hot_spot_fac == onaf_switch.onan_parameters.hot_spot_fac


def test_wrong_onaf_switch(default_user_trafo_specs: UserTransformerSpecifications, iec_load_profile):
    """Check that a ValueError is raised when the length of fans_status does not match the temperature profile."""
    is_on = [True] * 100
    onan_parameters = ONANParameters(
        top_oil_temp_rise=50.5,
        time_const_oil=150,
        time_const_windings=7,
        load_loss=default_user_trafo_specs.load_loss,
        nom_load_sec_side=1600,
        winding_oil_gradient=23,
        hot_spot_fac=1.2,
    )
    onaf_switch = ONAFSwitch(fans_status=is_on, temperature_threshold=None, onan_parameters=onan_parameters)

    with pytest.raises(ValueError, match=("ONAF switch only works when the cooling type is ONAF.")):
        PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAN, onaf_switch=onaf_switch)

    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, onaf_switch=onaf_switch
    )
    with pytest.raises(
        ValueError,
        match=(
            "The length of the fans_status list in the onaf_switch must be equal to the length of "
            "the temperature profile."
        ),
    ):
        Model(transformer=transformer, temperature_profile=iec_load_profile)


def test_complete_onan_onaf_switch_fans_status(
    default_user_trafo_specs: UserTransformerSpecifications, constant_load_profile
):
    """Check that the transformer can handle a complete ONAF switch scenario."""
    default_user_trafo_specs.top_oil_temp_rise = 60
    default_user_trafo_specs.winding_oil_gradient = 25
    default_user_trafo_specs.hot_spot_fac = 1.1
    default_user_trafo_specs.nom_load_sec_side = constant_load_profile.load_profile[0] * 1.2

    is_on = [False] * 50 + [True] * (len(constant_load_profile.datetime_index) - 50)
    onan_parameters = ONANParameters(
        top_oil_temp_rise=50.5,
        time_const_oil=150,
        time_const_windings=7,
        load_loss=default_user_trafo_specs.load_loss,
        nom_load_sec_side=constant_load_profile.load_profile[0] * 0.8,
        winding_oil_gradient=23,
        hot_spot_fac=1.2,
    )
    onaf_switch = ONAFSwitch(fans_status=is_on, temperature_threshold=None, onan_parameters=onan_parameters)
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, onaf_switch=onaf_switch
    )
    model = Model(transformer=transformer, temperature_profile=constant_load_profile)
    output = model.run()

    # After 50 steps, the cooling should switch to ONAF and the top-oil temperature should be lower
    assert output.top_oil_temp_profile.iloc[45] > output.top_oil_temp_profile.iloc[55]

    # Test that it correctly switches back to ONAN if the fans are turned off again
    is_on = [False] * 50 + [True] * 30 + [False] * (len(constant_load_profile.datetime_index) - 80)
    onaf_switch.fans_status = is_on
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, onaf_switch=onaf_switch
    )
    model = Model(transformer=transformer, temperature_profile=constant_load_profile)
    output_2 = model.run()
    assert output_2.top_oil_temp_profile.iloc[45] > output_2.top_oil_temp_profile.iloc[55]
    assert output_2.top_oil_temp_profile.iloc[75] < output_2.top_oil_temp_profile.iloc[85]

    # Check that an onan onaf switch with long periods of onaf reaches the same steady state as a constant onaf
    onaf_transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF)
    onaf_model = Model(transformer=onaf_transformer, temperature_profile=constant_load_profile)
    onaf_output = onaf_model.run()
    assert math.isclose(onaf_output.top_oil_temp_profile.iloc[-1], output.top_oil_temp_profile.iloc[-1], rel_tol=1e-2)
    assert math.isclose(onaf_output.hot_spot_temp_profile.iloc[-1], output.hot_spot_temp_profile.iloc[-1], rel_tol=1e-2)


def test_complete_onan_onaf_switch_temp_threshold(
    default_user_trafo_specs: UserTransformerSpecifications, constant_load_profile_minutes
):
    """Check that the transformer can handle a complete ONAF switch scenario based on temperature thresholds."""
    default_user_trafo_specs.amb_temp_surcharge = 0
    default_user_trafo_specs.top_oil_temp_rise = 60
    default_user_trafo_specs.winding_oil_gradient = 25
    default_user_trafo_specs.hot_spot_fac = 1.1
    default_user_trafo_specs.nom_load_sec_side = constant_load_profile_minutes.load_profile[0] * 5
    temp_threshold = FanSwitchConfig(activation_temp=60, deactivation_temp=50)
    onan_parameters = ONANParameters(
        top_oil_temp_rise=50.5,
        time_const_oil=150,
        time_const_windings=7,
        load_loss=default_user_trafo_specs.load_loss,
        nom_load_sec_side=constant_load_profile_minutes.load_profile[0] * 0.8,
        winding_oil_gradient=23,
        hot_spot_fac=1.2,
    )
    onaf_switch = ONAFSwitch(
        fans_status=None,
        temperature_threshold=temp_threshold,
        onan_parameters=onan_parameters,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, onaf_switch=onaf_switch
    )
    model = Model(transformer=transformer, temperature_profile=constant_load_profile_minutes)
    output = model.run()

    # The transformer now cools really fast in ONAF and heats up fast in ONAN

    # after warmup period, the top-oil temperature should be above 45 degrees
    assert output.top_oil_temp_profile[20:].min() > 45

    # at some point, the top-oil temperature should exceed the activation temperature and switch to ONAF,
    # then it should cool down
    assert output.top_oil_temp_profile.max() < 65


def test_threewinding_onan_onaf_switch(
    user_three_winding_transformer_specs: UserThreeWindingTransformerSpecifications,
    three_winding_input_profile: ThreeWindingInputProfile,
):
    """Check that a three-winding transformer can be created with an ONAF switch."""
    is_on = [False] * 50 + [True] * (len(three_winding_input_profile.datetime_index) - 50)
    onan_parameters = ThreeWindingONANParameters(
        onan_lv_winding=ONANWindingParameters(
            time_const_winding=10, nom_load=800, winding_oil_gradient=18, hot_spot_fac=1.1
        ),
        onan_mv_winding=ONANWindingParameters(
            time_const_winding=10, nom_load=800, winding_oil_gradient=18, hot_spot_fac=1.1
        ),
        onan_hv_winding=ONANWindingParameters(
            time_const_winding=10, nom_load=800, winding_oil_gradient=18, hot_spot_fac=1.1
        ),
        top_oil_temp_rise=55,
        time_const_oil=160,
        load_loss_mv_lv=300,
        load_loss_hv_lv=300,
        load_loss_hv_mv=300,
    )
    onaf_switch = ThreeWindingONAFSwitch(fans_status=is_on, temperature_threshold=None, onan_parameters=onan_parameters)
    transformer = ThreeWindingTransformer(
        user_specs=user_three_winding_transformer_specs, cooling_type=CoolerType.ONAF, onaf_switch=onaf_switch
    )
    model = Model(transformer=transformer, temperature_profile=three_winding_input_profile)
    model.run()
