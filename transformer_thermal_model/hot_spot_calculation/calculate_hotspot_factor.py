# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import copy
import logging

import numpy as np

from transformer_thermal_model.transformer import PowerTransformer, ThreeWindingTransformer

logger = logging.getLogger(__name__)


def calculate_hotspot_factor(
    uncalibrated_transformer: PowerTransformer | ThreeWindingTransformer,
    hot_spot_temp_rise_limit: float,
    hot_spot_factor_min: float,
    hot_spot_factor_max: float,
) -> PowerTransformer | ThreeWindingTransformer:
    """Calculate a hot-spot factor for a transformer from its temperature rise limit.

    At nominal load and the reference ambient temperature of 20 degrees Celsius, the hot-spot temperature is
    calculated as ``20 + top_oil_temp_rise + hot_spot_factor * winding_oil_gradient``. The calculated factor is
    clipped to the interval defined by ``hot_spot_factor_min`` and ``hot_spot_factor_max``.

    Args:
        uncalibrated_transformer (PowerTransformer | ThreeWindingTransformer): A transformer without a specified
            hot-spot factor.
        hot_spot_temp_rise_limit (float): Maximum hot-spot temperature rise above ambient temperature at nominal
            load [K].
        hot_spot_factor_min (float): minimum allowed value for the hot-spot factor.
        hot_spot_factor_max (float): maximum allowed value for the hot-spot factor.

    Returns:
        PowerTransformer | ThreeWindingTransformer: A copy of the transformer with the calculated hot-spot factor.

    """
    if hot_spot_factor_min > hot_spot_factor_max:
        raise ValueError("The upper bound cannot be smaller than the lower bound of the hot-spot factor limits.")

    winding_oil_gradient = _get_max_winding_oil_gradient(uncalibrated_transformer)

    hot_spot_factor = (
        hot_spot_temp_rise_limit - uncalibrated_transformer.specs.top_oil_temp_rise
    ) / winding_oil_gradient

    calculated_hot_spot_factor = np.clip(hot_spot_factor, a_min=hot_spot_factor_min, a_max=hot_spot_factor_max)
    calibrated_transformer = copy.deepcopy(uncalibrated_transformer)
    calibrated_transformer._set_hs_fac(calculated_hot_spot_factor)

    logger.info(
        "The hot-spot factor of the transformer is calculated. The new hot-spot factor equals"
        + f"{calculated_hot_spot_factor}."
    )
    return calibrated_transformer


def _get_max_winding_oil_gradient(transformer: PowerTransformer | ThreeWindingTransformer) -> float:
    """Return the winding-oil gradient used for calculating the hot-spot factor.

    A three-winding transformer uses the maximum gradient because the same hot-spot factor is applied to all three
    windings. For a power transformer, the transformer has only one winding-oil gradient, which is returned directly.
    """
    if isinstance(transformer, ThreeWindingTransformer):
        winding_oil_gradients = (
            transformer.specs.lv_winding.winding_oil_gradient,
            transformer.specs.mv_winding.winding_oil_gradient,
            transformer.specs.hv_winding.winding_oil_gradient,
        )
        if any(gradient is None for gradient in winding_oil_gradients):
            raise ValueError("Winding oil gradients must be specified for all three windings.")
        return max(gradient for gradient in winding_oil_gradients if gradient is not None)

    return transformer.specs.winding_oil_gradient
