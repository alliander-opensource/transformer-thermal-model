# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging

import numpy as np
import pandas as pd

from transformer_thermal_model.schemas import InputProfile, OutputProfile
from transformer_thermal_model.transformer import Transformer

logger = logging.getLogger(__name__)


class Model:
    """A thermal model to calculate transformer temperatures under specified load and ambient temperature profiles.

    Example: Initialising a transformer model with a temperature simulation profile
        ```python
        >>> from datetime import datetime
        >>> from transformer_thermal_model.cooler import CoolerType
        >>> from transformer_thermal_model.schemas import InputProfile, UserTransformerSpecifications
        >>> from transformer_thermal_model.transformer import PowerTransformer
        >>> from transformer_thermal_model.model import Model

        >>> # First, we necreate the input profile
        >>> datetime_index = [
        ...     datetime(2023, 1, 1, 0, 0),
        ...     datetime(2023, 1, 1, 1, 0),
        ...     datetime(2023, 1, 1, 2, 0),
        ... ]
        >>> load_profile = [0.8, 0.9, 1.0]
        >>> ambient_temperature_profile = [25.0, 24.5, 24.0]
        >>> input_profile = InputProfile.create(
        ...     datetime_index=datetime_index,
        ...     load_profile=load_profile,
        ...     ambient_temperature_profile=ambient_temperature_profile,
        ... )
        >>> # Then, we create the transformer with some basic specifications
        >>> tr_specs = UserTransformerSpecifications(
        ...     load_loss=1000,  # Transformer load loss [W]
        ...     nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
        ...     no_load_loss=200,  # Transformer no-load loss [W]
        ...     amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
        ... )
        >>> tr = PowerTransformer(
        ...     user_specs=tr_specs,
        ...     cooling_type=CoolerType.ONAN
        ... )
        >>> # Finally, we can use the input profile in the transformer model
        >>> model = Model(temperature_profile=input_profile, transformer=tr)

        ```

    Attributes:
        transformer (Transformer): The transformer that the model will use to calculate the temperatures.
        data (pd.DataFrame): The data that the model will use to calculate the top-oil and hot-spottemperatures.
        init_top_oil_temp (float | None): The initial top-oil temperature. Defaults to None. If this is provided,
            will start the calculation with this temperature. If not provided, will start the calculation
            with the first value of the ambient temperature profile.
            will start the calculation with this temperature. If not provided, will start the calculation
            with the first value of the ambient temperature profile.
        hot_spot_temp_profile (pd.Series): The modeled hot-spot temperature profile.
        top_oil_temp_profile (pd.Series): The modeled top-oil temperature profile.
    """

    transformer: Transformer
    data: InputProfile
    init_top_oil_temp: float | None
    hot_spot_temp_profile: pd.Series
    top_oil_temp_profile: pd.Series

    def __init__(
        self,
        temperature_profile: InputProfile,
        transformer: Transformer,
        init_top_oil_temp: float | None = None,
    ) -> None:
        """Initialize the thermal model.

        Args:
            temperature_profile (InputProfile): The temperature profile for the model.
            transformer (Transformer): The transformer object.
            init_top_oil_temp (float | None): The initial top-oil temperature. Defaults to None. If this is provided,
                will start the calculation with this temperature. If not provided, will start the calculation
                with the first value of the ambient temperature profile.
                will start the calculation with this temperature. If not provided, will start the calculation
                with the first value of the ambient temperature profile.

        """
        logger.info("Initializing the thermal model.")
        logger.info(f"First timestamp: {temperature_profile.datetime_index[0]}")
        logger.info(f"Last timestamp: {temperature_profile.datetime_index[-1]}")
        logger.info(f"Amount of data points: {len(temperature_profile)}")
        logger.info(f"Max load: {np.max(temperature_profile.load_profile)}")
        if transformer.specs.hot_spot_fac is None:
            raise AttributeError(
                "The given Transformer has no hot-spot factor specified. Please specify the hot-spot "
                "factor or calibrate it using the calibrate_hotspot_factor function."
            )
        self.transformer = transformer
        self.data = temperature_profile
        self.init_top_oil_temp = init_top_oil_temp

    def _get_time_step(self) -> np.ndarray:
        """Get the time step between the data points.

        Returns:
            np.ndarray: The time step between the data points in minutes.

        """
        # Calculate time steps in minutes
        time_deltas = (
            np.diff(self.data.datetime_index, prepend=self.data.datetime_index[0])
            .astype("timedelta64[s]")
            .astype(float)
            / 60
        )
        return time_deltas

    def _get_internal_temp(self) -> np.ndarray:
        """Get the internal temperature of the environment where the transformer is located.

        This calculation takes into account the ambient temperature and the specifications of the transformer.
        For power transformers, an additional increase is applied to the ambient temperature.
        For distribution transformers, the temperature difference between the internal and ambient temperatures is
        greater, but this will be handled in the _end_temperature_top_oil method.
        """
        internal_temperature_profile = self.transformer._calculate_internal_temp(self.data.ambient_temperature_profile)
        return internal_temperature_profile

    def _calculate_f1(self, dt: np.ndarray) -> np.ndarray:
        """Calculate the time delay constant f1 for the top-oil temperature."""
        return 1 - np.exp(-dt / (self.transformer.specs.oil_const_k11 * self.transformer.specs.time_const_oil))

    def _calculate_f2_winding(self, dt: np.ndarray) -> np.ndarray:
        """Calculate the time delay constant f2 for the hot-spot temperature. due to the windings."""
        winding_delay = np.exp(
            -dt / (self.transformer.specs.winding_const_k22 * self.transformer.specs.time_const_windings)
        )
        return winding_delay

    def _calculate_f2_oil(self, dt: np.ndarray) -> np.ndarray:
        """Calculate the time delay constant f2 for the hot-spot temperature due to the oil."""
        oil_delay = np.exp(-dt * self.transformer.specs.winding_const_k22 / self.transformer.specs.time_const_oil)
        return oil_delay

    def _calculate_static_hot_spot_increase(self, load: np.ndarray) -> np.ndarray:
        """Calculate the static hot-spot temperature increase using vectorized operations."""
        return (
            self.transformer.specs.hot_spot_fac
            * self.transformer.specs.winding_oil_gradient
            * (load / self.transformer.specs.nom_load_sec_side) ** self.transformer.specs.winding_exp_y
        )

    def _calculate_temperature_profiles(
        self,
        load: np.ndarray,
        t_internal: np.ndarray,
        f1: np.ndarray,
        f2_windings: np.ndarray,
        f2_oil: np.ndarray,
        top_k: np.ndarray,
        static_hot_spot_incr: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calculate the temperature profiles for the transformer's top-oil and hot-spot.

        Args:
            load (np.ndarray): Array of load values over time.
            t_internal (np.ndarray): Array of internal temperatures over time.
            f1 (np.ndarray): Array of time constants for the top-oil temperature calculation.
            f2_windings (np.ndarray): Array of time constants for the hot-spot temperature calculation due to windings.
            f2_oil (np.ndarray): Array of time constants for the hot-spot temperature calculation due to oil.
            top_k (np.ndarray): Array of end temperatures for the top-oil.
            static_hot_spot_incr (np.ndarray): Array of static hot-spot temperature increases.

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing:
            - top_oil_temp_profile (np.ndarray): The computed top-oil temperature profile over time.
            - hot_spot_temp_profile (np.ndarray): The computed hot-spot temperature profile over time.

        """
        # Preallocate arrays for temperature profiles
        top_oil_temp_profile = np.zeros_like(load, dtype=np.float64)
        hot_spot_temp_profile = np.zeros_like(load, dtype=np.float64)

        # Split the static hot-spot increase into two parts for windings and oil
        static_hot_spot_incr_windings = static_hot_spot_incr * self.transformer.specs.winding_const_k21
        static_hot_spot_incr_oil = static_hot_spot_incr * (self.transformer.specs.winding_const_k21 - 1)

        # Initialize first values
        top_oil_temp = t_internal[0] if self.init_top_oil_temp is None else self.init_top_oil_temp
        hot_spot_increase_windings = 0.0
        hot_spot_increase_oil = 0.0
        top_oil_temp_profile[0] = top_oil_temp
        hot_spot_temp_profile[0] = top_oil_temp

        # Iteratively calculate profiles
        for i in range(1, len(load)):
            top_oil_temp = self._update_top_oil_temp(top_oil_temp, t_internal[i], top_k[i], f1[i])
            # Calculate the hotspot temperature based on formula 17 from IEC 2060076-7_2018.
            # The hot-spot increase of the windings is based on from 15 from IEC 2060076-7_2018.
            hot_spot_increase_windings = self._update_hot_spot_increase(
                hot_spot_increase_windings, static_hot_spot_incr_windings[i], f2_windings[i]
            )
            # The hot-spot increase of the oil is based on from 16 from IEC 2060076-7_2018
            hot_spot_increase_oil = self._update_hot_spot_increase(
                hot_spot_increase_oil, static_hot_spot_incr_oil[i], f2_oil[i]
            )
            hot_spot_temp_profile[i] = top_oil_temp + hot_spot_increase_windings - hot_spot_increase_oil
            top_oil_temp_profile[i] = top_oil_temp

        return top_oil_temp_profile, hot_spot_temp_profile

    def _update_top_oil_temp(self, current_temp: float, t_internal: float, top_k: float, f1: float) -> float:
        """Update the top-oil temperature for a single time step."""
        return current_temp + (t_internal + top_k - current_temp) * f1

    def _update_hot_spot_increase(self, current_increase: float, static_incr: float, f2: float) -> float:
        """Update the hot-spot temperature increase for a single time step."""
        return static_incr + (current_increase - static_incr) * f2

    def run(self) -> OutputProfile:
        """Calculate the top-oil and hot-spot temperatures for the provided Transformer object.

        This method prepares the calculation inputs, calculates intermediate factors, and computes
        the top-oil and hot-spot temperature profiles for the transformer based on the provided
        load and internal parameters.

        Returns:
            OutputProfile: Object containing the top-oil and hot-spot temperature profiles.

        """
        logger.info("Running the thermal model.")
        dt = self._get_time_step()
        load = self.data.load_profile
        t_internal = self._get_internal_temp()

        f1 = self._calculate_f1(dt)
        f2_windings = self._calculate_f2_winding(dt)
        f2_oil = self._calculate_f2_oil(dt)
        top_k = self.transformer._end_temperature_top_oil(load)
        static_hot_spot_incr = self._calculate_static_hot_spot_increase(load)

        top_oil_temp_profile, hot_spot_temp_profile = self._calculate_temperature_profiles(
            load, t_internal, f1, f2_windings, f2_oil, top_k, static_hot_spot_incr
        )
        logger.info("The calculation with the Thermal model is completed.")
        logger.info(f"Max top-oil temperature: {max(top_oil_temp_profile)}")
        logger.info(f"Max hot-spot temperature: {max(hot_spot_temp_profile)}")

        return OutputProfile(
            top_oil_temp_profile=pd.Series(top_oil_temp_profile, index=self.data.datetime_index),
            hot_spot_temp_profile=pd.Series(hot_spot_temp_profile, index=self.data.datetime_index),
        )
