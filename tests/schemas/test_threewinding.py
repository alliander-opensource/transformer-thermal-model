# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pandas as pd
import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import (
    DefaultTransformerSpecifications,
    ThreeWindingTransformerSpecifications,
    UserThreeWindingTransformerSpecifications,
    WindingSpecifications,
)
from transformer_thermal_model.schemas.thermal_model.input_profile import ThreeWindingInputProfile
from transformer_thermal_model.transformer.threewinding import ThreeWindingTransformer


def test_three_winding_transformer(user_three_winding_transformer_specs):
    """Test the creation of a three-winding transformer specifications object."""
    defaults = DefaultTransformerSpecifications(
        time_const_oil=180,
        time_const_windings=4,
        top_oil_temp_rise=60,
        winding_oil_gradient=23,
        hot_spot_fac=1.2,
        oil_const_k11=1.0,
        winding_const_k21=1,
        winding_const_k22=2,
        oil_exp_x=0.8,
        winding_exp_y=1.6,
        end_temp_reduction=0,
    )
    transformer = ThreeWindingTransformerSpecifications.create(
        defaults=defaults, user=user_three_winding_transformer_specs
    )

    assert transformer.lv_winding.nom_load == user_three_winding_transformer_specs.lv_winding.nom_load
    assert transformer.time_const_oil == 180
    assert (
        transformer.nominal_load_array
        == np.array(
            [
                [user_three_winding_transformer_specs.lv_winding.nom_load],
                [user_three_winding_transformer_specs.mv_winding.nom_load],
                [user_three_winding_transformer_specs.hv_winding.nom_load],
            ]
        )
    ).all()
    assert (
        transformer.winding_oil_gradient_array
        == np.array(
            [
                [user_three_winding_transformer_specs.lv_winding.winding_oil_gradient],
                [user_three_winding_transformer_specs.mv_winding.winding_oil_gradient],
                [user_three_winding_transformer_specs.hv_winding.winding_oil_gradient],
            ]
        )
    ).all()


def test_three_winding_input_profile(three_winding_input_profile):
    """Test the creation of a three-winding input profile."""
    assert len(three_winding_input_profile.load_profile_array) == 3


def test_wrong_three_winding_input_profile():
    """Test the creation of a three-winding input profile with wrong data."""
    with pytest.raises(ValueError, match="The length of the profiles and index should be the same"):
        ThreeWindingInputProfile.create(
            datetime_index=pd.date_range("2021-01-01 00:00:00", periods=3),
            load_profile_high_voltage_side=[100, 200],
            load_profile_middle_voltage_side=[200, 300],
            load_profile_low_voltage_side=[300, 400],
            ambient_temperature_profile=[10, 20, 30],
        )
    with pytest.raises(ValueError, match="The length of the profiles and index should be the same"):
        ThreeWindingInputProfile.create(
            datetime_index=pd.date_range("2021-01-01 00:00:00", periods=3),
            load_profile_high_voltage_side=[100, 200, 300],
            load_profile_middle_voltage_side=[200, 300],
            load_profile_low_voltage_side=[300, 400],
            ambient_temperature_profile=[10, 20, 30],
        )


def test_three_winding_transformer_total_loss():
    """Test the total loss calculation of a three-winding transformer."""
    user_specs_three_winding = UserThreeWindingTransformerSpecifications(
        no_load_loss=10000,
        amb_temp_surcharge=0,
        lv_winding=WindingSpecifications(nom_load=1600, winding_oil_gradient=23, hot_spot_fac=1.3, time_const_windings=10),
        mv_winding=WindingSpecifications(nom_load=1600, winding_oil_gradient=23, hot_spot_fac=1.3, time_const_windings=10),
        hv_winding=WindingSpecifications(nom_load=1600, winding_oil_gradient=23, hot_spot_fac=1.3, time_const_windings=10),
        load_loss_hv_lv=20000,
        load_loss_hv_mv=20000,
        load_loss_mv_lv=20000,
    )
    three_winding_transformer = ThreeWindingTransformer(
        user_specs=user_specs_three_winding, cooling_type=CoolerType.ONAN
    )
    total_loss_calculated = three_winding_transformer.specs.load_loss_total

    assert total_loss_calculated == 40000

    user_specs_three_winding = UserThreeWindingTransformerSpecifications(
        no_load_loss=10000,
        amb_temp_surcharge=0,
        lv_winding=WindingSpecifications(nom_load=1600, winding_oil_gradient=23, hot_spot_fac=1.3, time_const_windings=10),
        mv_winding=WindingSpecifications(nom_load=1600, winding_oil_gradient=23, hot_spot_fac=1.3, time_const_windings=10),
        hv_winding=WindingSpecifications(nom_load=1600, winding_oil_gradient=23, hot_spot_fac=1.3, time_const_windings=10),
        load_loss_hv_lv=20000,
        load_loss_hv_mv=20000,
        load_loss_mv_lv=20000,
        load_loss_total=35000,
    )
    three_winding_transformer = ThreeWindingTransformer(
        user_specs=user_specs_three_winding, cooling_type=CoolerType.ONAN
    )
    total_loss_calculated = three_winding_transformer.specs.load_loss_total
    assert total_loss_calculated == 35000
