# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np

from transformer_thermal_model.schemas import DefaultTransformerSpecifications, ThreePhaseTransformerSpecifications


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

    assert transformer.lv_winding.nom_load == 1000
    assert transformer.time_const_oil == 180
    assert (transformer.nominal_load_array == np.array([[3000], [2000], [1000]])).all()
    assert (transformer.winding_oil_gradient_array == np.array([[1500], [1000], [500]])).all()
