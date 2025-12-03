# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import math

import numpy as np
import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.model.thermal_model import Model
from transformer_thermal_model.schemas.specifications.transformer import (
    UserThreeWindingTransformerSpecifications,
    UserTransformerSpecifications,
)
from transformer_thermal_model.schemas.thermal_model.input_profile import ThreeWindingInputProfile
from transformer_thermal_model.schemas.thermal_model.onaf_switch import (
    CoolingSwitchConfig,
    CoolingSwitchSettings,
    ONANParameters,
    ThreeWindingCoolingSwitchSettings,
    ThreeWindingONANParameters,
    WindingSpecifications,
)
from transformer_thermal_model.transformer.power import PowerTransformer
from transformer_thermal_model.transformer.threewinding import ThreeWindingTransformer


def test_start_cooling_type(default_user_trafo_specs: UserTransformerSpecifications):
    """Check that the transformer starts with the correct cooling type."""
    default_user_trafo_specs.top_oil_temp_rise = 60
    default_user_trafo_specs.winding_oil_gradient = 25
    default_user_trafo_specs.hot_spot_fac = 1.1

    is_on = np.array([True] * 100)

    onan_parameters = ONANParameters(
        top_oil_temp_rise=50.5,
        time_const_oil=150,
        time_const_windings=7,
        load_loss=default_user_trafo_specs.load_loss,
        nom_load_sec_side=1600,
        winding_oil_gradient=23,
        hot_spot_fac=1.2,
    )

    onaf_switch = CoolingSwitchSettings(
        fan_on=is_on,
        temperature_threshold=None,
        onan_parameters=onan_parameters,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, cooling_switch_settings=onaf_switch
    )
    transformer.set_ONAN_ONAF_first_timestamp(init_top_oil_temp=20)
    assert transformer.specs.nom_load_sec_side == default_user_trafo_specs.nom_load_sec_side
    assert transformer.specs.top_oil_temp_rise == default_user_trafo_specs.top_oil_temp_rise
    assert transformer.specs.winding_oil_gradient == default_user_trafo_specs.winding_oil_gradient
    assert transformer.specs.hot_spot_fac == default_user_trafo_specs.hot_spot_fac

    is_on = np.array([False] * 100)
    onaf_switch.fan_on = is_on
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, cooling_switch_settings=onaf_switch
    )
    transformer.set_ONAN_ONAF_first_timestamp(init_top_oil_temp=20)
    assert transformer.specs.nom_load_sec_side == onaf_switch.onan_parameters.nom_load_sec_side
    assert transformer.specs.top_oil_temp_rise == onaf_switch.onan_parameters.top_oil_temp_rise
    assert transformer.specs.winding_oil_gradient == onaf_switch.onan_parameters.winding_oil_gradient
    assert transformer.specs.hot_spot_fac == onaf_switch.onan_parameters.hot_spot_fac

    onaf_switch = CoolingSwitchSettings(
        fan_on=None,
        temperature_threshold=CoolingSwitchConfig(activation_temp=85, deactivation_temp=75),
        onan_parameters=onan_parameters,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, cooling_switch_settings=onaf_switch
    )
    transformer.set_ONAN_ONAF_first_timestamp(init_top_oil_temp=20)
    assert transformer.specs.nom_load_sec_side == onaf_switch.onan_parameters.nom_load_sec_side
    assert transformer.specs.top_oil_temp_rise == onaf_switch.onan_parameters.top_oil_temp_rise
    assert transformer.specs.winding_oil_gradient == onaf_switch.onan_parameters.winding_oil_gradient
    assert transformer.specs.hot_spot_fac == onaf_switch.onan_parameters.hot_spot_fac

    # If the initial top-oil temperature is above the activation temperature, it should start in ONAF mode
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, cooling_switch_settings=onaf_switch
    )
    transformer.set_ONAN_ONAF_first_timestamp(init_top_oil_temp=90)
    assert transformer.specs.nom_load_sec_side == default_user_trafo_specs.nom_load_sec_side
    assert transformer.specs.top_oil_temp_rise == default_user_trafo_specs.top_oil_temp_rise
    assert transformer.specs.winding_oil_gradient == default_user_trafo_specs.winding_oil_gradient
    assert transformer.specs.hot_spot_fac == default_user_trafo_specs.hot_spot_fac


def test_wrong_onaf_switch(default_user_trafo_specs: UserTransformerSpecifications, iec_load_profile):
    """Check that a ValueError is raised when the length of fan_on does not match the temperature profile."""
    is_on = np.array([True] * 100)
    onan_parameters = ONANParameters(
        top_oil_temp_rise=50.5,
        time_const_oil=150,
        time_const_windings=7,
        load_loss=default_user_trafo_specs.load_loss,
        nom_load_sec_side=1600,
        winding_oil_gradient=23,
        hot_spot_fac=1.2,
    )
    onaf_switch = CoolingSwitchSettings(fan_on=is_on, temperature_threshold=None, onan_parameters=onan_parameters)

    with pytest.raises(ValueError, match=("ONAF switch only works when the cooling type is ONAF.")):
        PowerTransformer(
            user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAN, cooling_switch_settings=onaf_switch
        )

    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, cooling_switch_settings=onaf_switch
    )
    with pytest.raises(
        ValueError,
        match=(
            "The length of the fan_on list in the cooling_switch_settings must be equal to the length of "
            "the temperature profile."
        ),
    ):
        Model(transformer=transformer, temperature_profile=iec_load_profile)

    with pytest.raises(
        ValueError,
        match=("Activation temperature must be higher than deactivation temperature."),
    ):
        CoolingSwitchSettings(
            fan_on=None,
            temperature_threshold=CoolingSwitchConfig(activation_temp=50, deactivation_temp=60),
            onan_parameters=onan_parameters,
        )

    # Provide either 'fan_on' or 'temperature_threshold', not both.
    with pytest.raises(ValueError, match=("Provide either 'fan_on' or 'temperature_threshold', not both")):
        CoolingSwitchSettings(
            temperature_threshold=CoolingSwitchConfig(activation_temp=80, deactivation_temp=70),
            onan_parameters=onan_parameters,
            fan_on=[True, False],
        )
    with pytest.raises(ValueError, match=("Either 'fan_on' or 'temperature_threshold' must be provided.")):
        CoolingSwitchSettings(temperature_threshold=None, onan_parameters=onan_parameters, fan_on=None)


def test_complete_onan_onaf_switch_fan_on(
    default_user_trafo_specs: UserTransformerSpecifications, constant_load_profile
):
    """Check that the transformer can handle a complete ONAF switch scenario."""
    default_user_trafo_specs.top_oil_temp_rise = 60
    default_user_trafo_specs.winding_oil_gradient = 25
    default_user_trafo_specs.hot_spot_fac = 1.1
    default_user_trafo_specs.nom_load_sec_side = constant_load_profile.load_profile[0] * 1.2

    is_on = np.array([False] * 50 + [True] * (len(constant_load_profile.datetime_index) - 50))
    onan_parameters = ONANParameters(
        top_oil_temp_rise=50.5,
        time_const_oil=150,
        time_const_windings=7,
        load_loss=default_user_trafo_specs.load_loss,
        nom_load_sec_side=constant_load_profile.load_profile[0] * 0.8,
        winding_oil_gradient=23,
        hot_spot_fac=1.2,
    )
    onaf_switch = CoolingSwitchSettings(fan_on=is_on, temperature_threshold=None, onan_parameters=onan_parameters)
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, cooling_switch_settings=onaf_switch
    )
    model = Model(transformer=transformer, temperature_profile=constant_load_profile)
    output = model.run()

    # After 50 steps, the cooling should switch to ONAF and the top-oil temperature should be lower
    assert output.top_oil_temp_profile.iloc[45] > output.top_oil_temp_profile.iloc[55]

    # Test that it correctly switches back to ONAN if the fans are turned off again
    is_on = np.array([False] * 50 + [True] * 30 + [False] * (len(constant_load_profile.datetime_index) - 80))
    onaf_switch.fan_on = is_on
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, cooling_switch_settings=onaf_switch
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
    temp_threshold = CoolingSwitchConfig(activation_temp=60, deactivation_temp=50)
    onan_parameters = ONANParameters(
        top_oil_temp_rise=50.5,
        time_const_oil=150,
        time_const_windings=7,
        load_loss=default_user_trafo_specs.load_loss,
        nom_load_sec_side=constant_load_profile_minutes.load_profile[0] * 0.8,
        winding_oil_gradient=23,
        hot_spot_fac=1.2,
    )
    onaf_switch = CoolingSwitchSettings(
        fan_on=None,
        temperature_threshold=temp_threshold,
        onan_parameters=onan_parameters,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, cooling_switch_settings=onaf_switch
    )
    model = Model(transformer=transformer, temperature_profile=constant_load_profile_minutes)
    output = model.run()

    # The transformer now cools really fast in ONAF and heats up fast in ONAN

    # after warmup period, the top-oil temperature should be above 45 degrees
    assert output.top_oil_temp_profile[20:].min() > 45

    # at some point, the top-oil temperature should exceed the activation temperature and switch to ONAF,
    # then it should cool down
    assert output.top_oil_temp_profile.max() < 65


def example_three_winding_onan_parameters():
    """Example of onan three winding alternative parameters."""
    return ThreeWindingONANParameters(
        lv_winding=WindingSpecifications(
            time_const_winding=10, nom_load=500, winding_oil_gradient=18, hot_spot_fac=1.1, nom_power=30
        ),
        mv_winding=WindingSpecifications(
            time_const_winding=10, nom_load=500, winding_oil_gradient=18, hot_spot_fac=1.1, nom_power=100
        ),
        hv_winding=WindingSpecifications(
            time_const_winding=10, nom_load=50, winding_oil_gradient=18, hot_spot_fac=1.1, nom_power=100
        ),
        top_oil_temp_rise=55,
        time_const_oil=160,
        load_loss_mv_lv=100,
        load_loss_hv_lv=100,
        load_loss_hv_mv=100,
    )


def test_threewinding_onan_onaf_switch(
    user_three_winding_transformer_specs: UserThreeWindingTransformerSpecifications,
    three_winding_input_profile: ThreeWindingInputProfile,
):
    """Check that a three-winding transformer can be created with an ONAF switch."""
    is_on = np.array([False] * 50 + [True] * (len(three_winding_input_profile.datetime_index) - 50))
    onan_parameters = example_three_winding_onan_parameters()
    onaf_switch = ThreeWindingCoolingSwitchSettings(
        fan_on=is_on, temperature_threshold=None, onan_parameters=onan_parameters
    )
    transformer = ThreeWindingTransformer(
        user_specs=user_three_winding_transformer_specs,
        cooling_type=CoolerType.ONAF,
        cooling_switch_settings=onaf_switch,
    )
    model = Model(transformer=transformer, temperature_profile=three_winding_input_profile)
    onan_onaf_results = model.run()

    # Check that an onan onaf switch with long periods of onaf reaches the same steady state as a constant onaf
    onaf_transformer = ThreeWindingTransformer(
        user_specs=user_three_winding_transformer_specs, cooling_type=CoolerType.ONAF
    )
    onaf_model = Model(transformer=onaf_transformer, temperature_profile=three_winding_input_profile)
    onaf_results = onaf_model.run()

    # At position 50 the ONAN-ONAF transformer should be warmer
    assert onan_onaf_results.top_oil_temp_profile.iloc[50] > onaf_results.top_oil_temp_profile.iloc[50] + 10
    assert (
        onan_onaf_results.hot_spot_temp_profile["low_voltage_side"].iloc[-1]
        > onaf_results.hot_spot_temp_profile["low_voltage_side"].iloc[-1]
    )
    assert (
        onan_onaf_results.hot_spot_temp_profile["middle_voltage_side"].iloc[-1]
        > onaf_results.hot_spot_temp_profile["middle_voltage_side"].iloc[-1]
    )
    assert (
        onan_onaf_results.hot_spot_temp_profile["high_voltage_side"].iloc[-1]
        > onaf_results.hot_spot_temp_profile["high_voltage_side"].iloc[-1]
    )

    # At the end it should be the same
    assert math.isclose(
        onaf_results.top_oil_temp_profile.iloc[-1], onan_onaf_results.top_oil_temp_profile.iloc[-1], rel_tol=1e-2
    )
    assert math.isclose(
        onaf_results.hot_spot_temp_profile["low_voltage_side"].iloc[-1],
        onan_onaf_results.hot_spot_temp_profile["low_voltage_side"].iloc[-1],
        rel_tol=1e-2,
    )
    assert math.isclose(
        onaf_results.hot_spot_temp_profile["middle_voltage_side"].iloc[-1],
        onan_onaf_results.hot_spot_temp_profile["middle_voltage_side"].iloc[-1],
        rel_tol=1e-2,
    )
    assert math.isclose(
        onaf_results.hot_spot_temp_profile["high_voltage_side"].iloc[-1],
        onan_onaf_results.hot_spot_temp_profile["high_voltage_side"].iloc[-1],
        rel_tol=1e-2,
    )


def test_three_winding__onan_onaf_switch_threshold_temp(
    user_three_winding_transformer_specs: UserThreeWindingTransformerSpecifications,
    three_winding_input_profile: ThreeWindingInputProfile,
):
    """Check that a three-winding transformer can be created with an ONAF switch based on temperature thresholds."""
    onan_parameters = example_three_winding_onan_parameters()

    # Use very low activation temps. to make it a ONAF transformer
    onaf_switch = ThreeWindingCoolingSwitchSettings(
        fan_on=None,
        temperature_threshold=CoolingSwitchConfig(activation_temp=10, deactivation_temp=0),
        onan_parameters=onan_parameters,
    )
    transformer = ThreeWindingTransformer(
        user_specs=user_three_winding_transformer_specs,
        cooling_type=CoolerType.ONAF,
        cooling_switch_settings=onaf_switch,
    )
    model = Model(transformer=transformer, temperature_profile=three_winding_input_profile)
    onan_onaf_results = model.run()

    onaf_transformer = ThreeWindingTransformer(
        user_specs=user_three_winding_transformer_specs, cooling_type=CoolerType.ONAF
    )
    onaf_model = Model(transformer=onaf_transformer, temperature_profile=three_winding_input_profile)
    onaf_results = onaf_model.run()

    # They should be the same in all indices
    assert onaf_results.top_oil_temp_profile.equals(onan_onaf_results.top_oil_temp_profile)
    assert onaf_results.hot_spot_temp_profile["low_voltage_side"].equals(
        onan_onaf_results.hot_spot_temp_profile["low_voltage_side"]
    )
    assert onaf_results.hot_spot_temp_profile["middle_voltage_side"].equals(
        onan_onaf_results.hot_spot_temp_profile["middle_voltage_side"]
    )
    assert onaf_results.hot_spot_temp_profile["high_voltage_side"].equals(
        onan_onaf_results.hot_spot_temp_profile["high_voltage_side"]
    )

    # Now we set a very high activation_temp, then it should be warmer in all but the first indice
    onaf_switch = ThreeWindingCoolingSwitchSettings(
        fan_on=None,
        temperature_threshold=CoolingSwitchConfig(activation_temp=200, deactivation_temp=190),
        onan_parameters=onan_parameters,
    )
    transformer = ThreeWindingTransformer(
        user_specs=user_three_winding_transformer_specs,
        cooling_type=CoolerType.ONAF,
        cooling_switch_settings=onaf_switch,
    )
    model = Model(transformer=transformer, temperature_profile=three_winding_input_profile)
    onan_onaf_results_2 = model.run()

    # Check that the temperatures are higher in all but the first index
    assert (onan_onaf_results_2.top_oil_temp_profile.iloc[1:] > onaf_results.top_oil_temp_profile.iloc[1:]).all()
    assert (
        onan_onaf_results_2.hot_spot_temp_profile["low_voltage_side"].iloc[1:]
        > onaf_results.hot_spot_temp_profile["low_voltage_side"].iloc[1:]
    ).all()
    assert (
        onan_onaf_results_2.hot_spot_temp_profile["middle_voltage_side"].iloc[1:]
        > onaf_results.hot_spot_temp_profile["middle_voltage_side"].iloc[1:]
    ).all()
    assert (
        onan_onaf_results_2.hot_spot_temp_profile["high_voltage_side"].iloc[1:]
        > onaf_results.hot_spot_temp_profile["high_voltage_side"].iloc[1:]
    ).all()


def test_switch_with_given_top_oil_temp(
    default_user_trafo_specs: UserTransformerSpecifications, constant_load_profile_minutes
):
    """Test switching logic when a top_oil temperature profile is given."""
    constant_top_oil_profile = np.array([80] * len(constant_load_profile_minutes.load_profile))
    constant_load_profile_minutes.top_oil_temperature_profile = constant_top_oil_profile

    temp_threshold_always_on = CoolingSwitchConfig(activation_temp=60, deactivation_temp=50)
    temp_threshold_always_off = CoolingSwitchConfig(activation_temp=90, deactivation_temp=50)

    onan_parameters = ONANParameters(
        top_oil_temp_rise=50.5,
        time_const_oil=150,
        time_const_windings=7,
        load_loss=default_user_trafo_specs.load_loss,
        nom_load_sec_side=constant_load_profile_minutes.load_profile[0] * 0.8,
        winding_oil_gradient=23,
        hot_spot_fac=1.2,
    )
    onaf_switch = CoolingSwitchSettings(
        fan_on=None,
        temperature_threshold=temp_threshold_always_on,
        onan_parameters=onan_parameters,
    )
    transformer = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, cooling_switch_settings=onaf_switch
    )
    model = Model(transformer=transformer, temperature_profile=constant_load_profile_minutes)
    output = model.run()

    full_onaf_transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF)
    full_onaf_model = Model(transformer=full_onaf_transformer, temperature_profile=constant_load_profile_minutes)
    full_onaf_output = full_onaf_model.run()

    # Since the top-oil temperature is always above the activation temp, it should always be in ONAF mode
    assert np.allclose(output.top_oil_temp_profile, full_onaf_output.top_oil_temp_profile)
    assert np.allclose(output.hot_spot_temp_profile, full_onaf_output.hot_spot_temp_profile)

    onaf_switch_always_off = CoolingSwitchSettings(
        fan_on=None,
        temperature_threshold=temp_threshold_always_off,
        onan_parameters=onan_parameters,
    )
    transformer_onan = PowerTransformer(
        user_specs=default_user_trafo_specs,
        cooling_type=CoolerType.ONAF,
        cooling_switch_settings=onaf_switch_always_off,
    )
    model_onan = Model(transformer=transformer_onan, temperature_profile=constant_load_profile_minutes)
    output_onan = model_onan.run()

    # ONAN mode is expected to be hotter than ONAF for all indices except the first,
    # because the cooling fans in ONAF mode reduce the hot spot temperature after the initial state.
    assert (output_onan.hot_spot_temp_profile.iloc[1:] > full_onaf_output.hot_spot_temp_profile.iloc[1:]).all()

    # Create a top-oil temperature profile that is constant at 90 for the first half and 70 for the second half
    split_index = len(constant_load_profile_minutes.load_profile) // 2
    top_oil_temperature_profile = np.array([90] * split_index + [70] * split_index)

    constant_load_profile_minutes.top_oil_temperature_profile = top_oil_temperature_profile
    onaf_switch_mixed = CoolingSwitchSettings(
        fan_on=None,
        temperature_threshold=CoolingSwitchConfig(activation_temp=85, deactivation_temp=75),
        onan_parameters=onan_parameters,
    )
    transformer_mixed = PowerTransformer(
        user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, cooling_switch_settings=onaf_switch_mixed
    )
    model_mixed = Model(transformer=transformer_mixed, temperature_profile=constant_load_profile_minutes)
    output_mixed = model_mixed.run()

    model_mixed_onaf = Model(transformer=full_onaf_transformer, temperature_profile=constant_load_profile_minutes)
    full_onaf_output_mixed = model_mixed_onaf.run()

    # In the first half, it should be in ONAF mode, in the second half in ONAN mode
    assert np.allclose(
        output_mixed.hot_spot_temp_profile.iloc[:split_index],
        full_onaf_output_mixed.hot_spot_temp_profile.iloc[:split_index],
    )
    assert (
        output_mixed.hot_spot_temp_profile.iloc[split_index + 1 :]
        > full_onaf_output_mixed.hot_spot_temp_profile.iloc[split_index + 1 :]
    ).all()
