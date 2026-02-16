# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import copy
import logging

import numpy as np
import pandas as pd

from transformer_thermal_model.model import Model
from transformer_thermal_model.schemas import (
    InputProfile,
    OutputProfile,
    ThreeWindingInputProfile,
)
from transformer_thermal_model.transformer import PowerTransformer, ThreeWindingTransformer

logger = logging.getLogger(__name__)


def _get_max_hot_spot_temperature(results: OutputProfile) -> float:
    """Helper function to get the maximum hot-spot temperature from the model results.

    Args:
        results (OutputProfile): The output profile from the thermal model containing the hot-spot temperature profile.

    Returns:
        float: The maximum hot-spot temperature.
    """
    if isinstance(results.hot_spot_temp_profile, pd.DataFrame):
        return results.hot_spot_temp_profile.max().max()
    else:
        return results.hot_spot_temp_profile.max()


def calibrate_hotspot_factor(
    uncalibrated_transformer: PowerTransformer | ThreeWindingTransformer,
    hot_spot_limit: float,
    ambient_temp: float,
    hot_spot_factor_min: float,
    hot_spot_factor_max: float,
) -> PowerTransformer | ThreeWindingTransformer:
    """Calibrate a hot-spot factor for given power transformer.

    Based on a continuous nominal load with a duration of one week, a specified constant ambient temperature,
    and a hot-spot temperature limit, the hot-spot factor is calibrated to get as close as
    possible to 100% nominal load while staying within the 'hot_spot_factor_min' and 'hot_spot_factor_max' bounds.

    Args:
        uncalibrated_transformer (PowerTransformer | ThreeWindingTransformer): A transformer without a specified
        hot-spot factor.
        hot_spot_limit (float): temperature limit for the transformer hot-spot.
        ambient_temp (float): constant ambient temperature in degrees Celsius used for the temperature calculations.
        hot_spot_factor_min (float): minimum allowed value for the hot-spot factor.
        hot_spot_factor_max (float): maximum allowed value for the hot-spot factor.

    Returns:
        PowerTransformer: A calibrated power transformer, where the hot-spot factor is now specified.

    """
    if hot_spot_factor_min > hot_spot_factor_max:
        raise ValueError("The upper bound cannot be smaller than the lower bound of the hot-spot factor limits.")

    one_week_steps = 4 * 24 * 7
    datetime_index = pd.date_range("2020-01-01", periods=one_week_steps, freq="15min")
    ambient_temp_profile = np.ones(one_week_steps, dtype=float) * ambient_temp
    calibrated_transformer = copy.deepcopy(uncalibrated_transformer)
    # Because the transformer should be calibrated to have a max hot-spot temperature at a constant
    # ambient temperature (generally 20 degrees Celsius), the transformer.temp_verh should not be used
    # during calibration.
    calibrated_transformer.specs.amb_temp_surcharge = 0.0

    if isinstance(uncalibrated_transformer, PowerTransformer):
        logger.info(
            "Calibrating the hot-spot factor of the transformer. The current hot-spot factor equals"
            + f"{uncalibrated_transformer.specs.hot_spot_fac}."
        )
        continuous_load = np.ones(one_week_steps, dtype=float) * uncalibrated_transformer.specs.nom_load_sec_side

        model_input = InputProfile.create(
            datetime_index=datetime_index,
            load_profile=continuous_load,
            ambient_temperature_profile=ambient_temp_profile,
        )
    elif isinstance(uncalibrated_transformer, ThreeWindingTransformer):
        continuous_load_lv = np.ones(one_week_steps, dtype=float) * uncalibrated_transformer.specs.lv_winding.nom_load
        continuous_load_mv = np.ones(one_week_steps, dtype=float) * uncalibrated_transformer.specs.mv_winding.nom_load
        continuous_load_hv = np.ones(one_week_steps, dtype=float) * uncalibrated_transformer.specs.hv_winding.nom_load

        model_input = ThreeWindingInputProfile.create(  # type: ignore
            datetime_index=datetime_index,
            ambient_temperature_profile=ambient_temp_profile,
            load_profile_high_voltage_side=continuous_load_hv,
            load_profile_middle_voltage_side=continuous_load_mv,
            load_profile_low_voltage_side=continuous_load_lv,
        )
    else:
        raise ValueError(
            "Incorrect Transformer Type: Hot-spot calibration is only implemented for transformers "
            "of type PowerTransformer or ThreeWindingTransformer"
        )
    # Initiate the difference, one of the termination criteria, to a positive number.
    difference = 100.0
    # Initiate the new_hot_spot_factor with the upper limit. This is the starting point for the search algorithm
    # which iteratively lowers the new_hot_spot_factor until a valid value is found.
    new_hot_spot_factor = hot_spot_factor_max
    calibrated_transformer._set_hs_fac(new_hot_spot_factor)

    while difference > 0 and new_hot_spot_factor >= hot_spot_factor_min - 0.01:
        old_hot_spot_factor = new_hot_spot_factor
        model = Model(temperature_profile=model_input, transformer=calibrated_transformer)
        results = model.run()
        hot_spot_max = _get_max_hot_spot_temperature(results)
        # Calculate the difference which is used as a termination criterion in the while loop:
        # the maximum temperature of the hot-spot should be below the hot-spot temperature limit.
        difference = hot_spot_max - hot_spot_limit
        new_hot_spot_factor = old_hot_spot_factor - 0.01
        calibrated_transformer._set_hs_fac(new_hot_spot_factor)

    calibrated_hot_spot_factor = np.clip(old_hot_spot_factor, a_min=hot_spot_factor_min, a_max=hot_spot_factor_max)
    calibrated_transformer._set_hs_fac(calibrated_hot_spot_factor)
    # During calibration the amb_temp_surcharge was set to zero. To return a transformer with correct specs,
    # the amb_temp_surcharge is set to the correct value again.
    calibrated_transformer.specs.amb_temp_surcharge = uncalibrated_transformer.specs.amb_temp_surcharge

    logger.info(
        "The hot-spot factor of the transformer is calibrated. The new hot-spot factor equals"
        + f"{calibrated_hot_spot_factor}."
    )
    return calibrated_transformer
