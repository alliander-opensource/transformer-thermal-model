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
    hot_spot_limit: float,
    hot_spot_factor_min: float,
    hot_spot_factor_max: float,
) -> PowerTransformer | ThreeWindingTransformer:
    """Calculate a hot-spot factor for a transformer from its temperature limit.

    At nominal load and the reference ambient temperature of 20 degrees Celsius, the hot-spot temperature is
    calculated as ``20 + top_oil_temp_rise + hot_spot_factor * winding_oil_gradient``. The calculated factor is
    clipped to the interval defined by ``hot_spot_factor_min`` and ``hot_spot_factor_max``.

    Args:
        uncalibrated_transformer (PowerTransformer | ThreeWindingTransformer): A transformer without a specified
        hot-spot factor.
        hot_spot_limit (float): Maximum hot-spot temperature at nominal load and 20 degrees Celsius ambient.
        hot_spot_factor_min (float): minimum allowed value for the hot-spot factor.
        hot_spot_factor_max (float): maximum allowed value for the hot-spot factor.

    Returns:
        PowerTransformer | ThreeWindingTransformer: A copy of the transformer with the calculated hot-spot factor.

    """
    if hot_spot_factor_min > hot_spot_factor_max:
        raise ValueError("The upper bound cannot be smaller than the lower bound of the hot-spot factor limits.")

    if not isinstance(uncalibrated_transformer, (PowerTransformer, ThreeWindingTransformer)):
        raise ValueError(
            "Incorrect Transformer Type: Hot-spot calculation is only implemented for transformers "
            "of type PowerTransformer or ThreeWindingTransformer"
        )

    if isinstance(uncalibrated_transformer, ThreeWindingTransformer):
        lv_winding_gradient = uncalibrated_transformer.specs.lv_winding.winding_oil_gradient
        mv_winding_gradient = uncalibrated_transformer.specs.mv_winding.winding_oil_gradient
        hv_winding_gradient = uncalibrated_transformer.specs.hv_winding.winding_oil_gradient
        if lv_winding_gradient is None or mv_winding_gradient is None or hv_winding_gradient is None:
            raise ValueError("Winding oil gradients must be specified for all three windings.")
        winding_oil_gradient = max(
            lv_winding_gradient,
            mv_winding_gradient,
            hv_winding_gradient,
        )

    else:
        winding_oil_gradient = uncalibrated_transformer.specs.winding_oil_gradient
    reference_ambient_temperature = 20.0
    hot_spot_factor = (
        hot_spot_limit - reference_ambient_temperature - uncalibrated_transformer.specs.top_oil_temp_rise
    ) / winding_oil_gradient

    calibrated_hot_spot_factor = np.clip(hot_spot_factor, a_min=hot_spot_factor_min, a_max=hot_spot_factor_max)
    calibrated_transformer = copy.deepcopy(uncalibrated_transformer)
    calibrated_transformer._set_hs_fac(calibrated_hot_spot_factor)

    logger.info(
        "The hot-spot factor of the transformer is calculated. The new hot-spot factor equals"
        + f"{calibrated_hot_spot_factor}."
    )
    return calibrated_transformer
