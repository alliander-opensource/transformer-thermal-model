# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0
import numpy as np

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.transformer import ThreePhaseTransformer


def test_initialization(user_three_phase_transformer_specs, three_phase_input_profile):
    """Test the initialization of the ThreePhaseTransformer."""
    transformer = ThreePhaseTransformer(
        user_specs=user_three_phase_transformer_specs,
        cooling_type=CoolerType.ONAN,
    )
    
    assert isinstance(transformer, ThreePhaseTransformer)

    load_profile = three_phase_input_profile.load_profile
    end_temp_top_oil = transformer._end_temperature_top_oil(load_profile)
    assert end_temp_top_oil.shape == (len(three_phase_input_profile.datetime_index), )