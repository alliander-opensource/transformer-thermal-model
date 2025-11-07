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
    ThreeWindingInputProfile,
)
from transformer_thermal_model.transformer import PowerTransformer, ThreeWindingTransformer

logger = logging.getLogger(__name__)


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
        uncalibrated_transformer (PowerTransformer): A power transformer without a specified hot-spot factor.
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
    calibrated_transformer = copy.deepcopy(uncalibrated_transformer)
    calibrated_transformer.specs.amb_temp_surcharge = 0.0
    # Because the transformer should be calibrated to have a max hot-spot temperature at a constant
    # ambient temperature (generally 20 degrees celsius), the transformer.temp_verh should not be used
    # during calibration.
    # differentiate between threewinding and normal transformer
    if isinstance(uncalibrated_transformer, PowerTransformer):
        logger.info(
            "Calibrating the hot-spot factor of the transformer. The current hot-spot factor equals"
            + f"{uncalibrated_transformer.specs.hot_spot_fac}."
        )
        continuous_load = pd.Series(
            [calibrated_transformer.specs.nom_load_sec_side] * one_week_steps, index=datetime_index
        )
        ambient_temp_profile = pd.Series([ambient_temp] * one_week_steps, index=datetime_index)
        model_input = InputProfile.create(
            datetime_index=datetime_index,
            load_profile=continuous_load,
            ambient_temperature_profile=ambient_temp_profile,
        )
        # only 1 side for powertransformer
        sides = ["single_side"]
    else:
        # create model input for the three different windings
        logger.info(
            "Calibrating the hot-spot factor of the threewinding transformer. The current minimum hot-spot factor equals"
            + f"{
                min(
                    uncalibrated_transformer.specs.lv_winding.hot_spot_fac,
                    uncalibrated_transformer.specs.mv_winding.hot_spot_fac,
                    uncalibrated_transformer.specs.hv_winding.hot_spot_fac,
                )
            }."
        )
        continuous_load_lv = pd.Series(
            [calibrated_transformer.specs.lv_winding.nom_load] * one_week_steps, index=datetime_index
        )
        continuous_load_mv = pd.Series(
            [calibrated_transformer.specs.mv_winding.nom_load] * one_week_steps, index=datetime_index
        )
        continuous_load_hv = pd.Series(
            [calibrated_transformer.specs.hv_winding.nom_load] * one_week_steps, index=datetime_index
        )
        ambient_temp_profile = pd.Series([ambient_temp] * one_week_steps, index=datetime_index)
        model_input = ThreeWindingInputProfile.create(
            datetime_index=datetime_index,
            ambient_temperature_profile=ambient_temp_profile,
            load_profile_high_voltage_side=continuous_load_hv,
            load_profile_middle_voltage_side=continuous_load_mv,
            load_profile_low_voltage_side=continuous_load_lv,
        )
        sides = ["low_voltage_side", "middle_voltage_side", "high_voltage_side"]

    hot_spot_factors = {}

    for side in sides:
        # Initiate the difference, one of the termination criteria, to a positive number.
        difference = 100.0
        # Initiate the new_hot_spot_factor with the upper limit. This is the starting point for the search algorithm which
        # iterativily lowers the new_hot_spot_factor until a valid value is found.
        new_hot_spot_factor = hot_spot_factor_max
        calibrated_transformer._set_HS_fac(new_hot_spot_factor)

        while difference > 0 and new_hot_spot_factor >= hot_spot_factor_min - 0.01:
            old_hot_spot_factor = new_hot_spot_factor
            model = Model(temperature_profile=model_input, transformer=calibrated_transformer)

            if isinstance(uncalibrated_transformer, PowerTransformer):
                results = model.run().convert_to_dataframe()
                hot_spot_max = results["hot_spot_temperature"].max()
            else:
                results = model.run()
                hot_spot_max = results.hot_spot_temp_profile[side].max()
            # Calculate the difference which is used as a termination criterium in the while loop:
            # the maximum temperature of the hot-spot should be below the hot-spot temperature limit.
            difference = hot_spot_max - hot_spot_limit
            # Lower the hot-spot factor with a small number for the next iteration.
            new_hot_spot_factor = old_hot_spot_factor - 0.01
            calibrated_transformer._set_HS_fac(new_hot_spot_factor)
        hot_spot_factors[side] = np.clip(old_hot_spot_factor, hot_spot_factor_min, hot_spot_factor_max)

    calibrated_hot_spot_factor = min(hot_spot_factors.values())
    calibrated_transformer._set_HS_fac(calibrated_hot_spot_factor)
    calibrated_transformer.specs.amb_temp_surcharge = uncalibrated_transformer.specs.amb_temp_surcharge

    logger.info(
        f"The hot-spot factor of the transformer is calibrated. "
        f"The new hot-spot factor equals {calibrated_hot_spot_factor:.3f}"
    )
    return calibrated_transformer
