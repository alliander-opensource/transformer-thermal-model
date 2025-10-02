# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.model.thermal_model import Model
from transformer_thermal_model.schemas.specifications.transformer import UserTransformerSpecifications
from transformer_thermal_model.schemas.thermal_model.input_profile import InputProfile
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
    transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, 
                                   ONAF_switch=onaf_switch)
    assert transformer.specs.nom_load_sec_side == default_user_trafo_specs.nom_load_sec_side
    assert transformer.specs.top_oil_temp_rise == default_user_trafo_specs.top_oil_temp_rise
    assert transformer.specs.winding_oil_gradient == default_user_trafo_specs.winding_oil_gradient
    assert transformer.specs.hot_spot_fac == default_user_trafo_specs.hot_spot_fac

    is_on = [False] * 100
    onaf_switch.fans_status = is_on
    transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, 
                                   ONAF_switch=onaf_switch)
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
    transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, 
                                   ONAF_switch=onaf_switch)
    assert transformer.specs.nom_load_sec_side == onaf_switch.nom_load_sec_side_ONAN
    assert transformer.specs.top_oil_temp_rise == onaf_switch.top_oil_temp_rise_ONAN
    assert transformer.specs.winding_oil_gradient == onaf_switch.winding_oil_gradient_ONAN
    assert transformer.specs.hot_spot_fac == onaf_switch.hot_spot_fac_ONAN


def test_wrong_length_fans_status(default_user_trafo_specs: UserTransformerSpecifications, 
                                  iec_load_profile):
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
    transformer = PowerTransformer(user_specs=default_user_trafo_specs, cooling_type=CoolerType.ONAF, 
                        ONAF_switch=onaf_switch)
    with pytest.raises(
        ValueError,
        match=(
            "The length of the fans_status list in the ONAF_switch must be equal to the length of "
            "the temperature profile."
        ),
    ):
        Model(transformer=transformer, temperature_profile=iec_load_profile)

