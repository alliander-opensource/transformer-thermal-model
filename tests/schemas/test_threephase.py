# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import pandas as pd
import pytest

from transformer_thermal_model.schemas import DefaultTransformerSpecifications, ThreePhaseTransformerSpecifications
from transformer_thermal_model.schemas.thermal_model.input_profile import ThreeWindingInputProfile


def test_three_phase_transformer(user_three_phase_transformer_specs):
    """Test the creation of a three-phase transformer specifications object."""
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
    transformer = ThreePhaseTransformerSpecifications.create(defaults=defaults, user=user_three_phase_transformer_specs)

    assert transformer.lv_winding.nom_load == user_three_phase_transformer_specs.lv_winding.nom_load
    assert transformer.time_const_oil == 180


def test_three_phase_input_profile(three_phase_input_profile):
    """Test the creation of a three-phase input profile."""
    assert len(three_phase_input_profile.datetime_index) == len(
        three_phase_input_profile.load_profile_high_voltage_side
    )
    assert len(three_phase_input_profile.load_profile) == 3


def test_wrong_three_phase_input_profile():
    """Test the creation of a three-phase input profile with wrong data."""
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
