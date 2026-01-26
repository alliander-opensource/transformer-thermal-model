# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging

import numpy as np
import pandas as pd

from transformer_thermal_model.schemas import OutputProfile
from transformer_thermal_model.schemas.thermal_model.initial_state import (
    ColdStart,
    InitialCondition,
    InitialLoad,
    InitialTopOilTemp,
)
from transformer_thermal_model.schemas.thermal_model.input_profile import (
    BaseInputProfile,
    InputProfile,
    ThreeWindingInputProfile,
)
from transformer_thermal_model.transformer import (
    DistributionTransformer,
    PowerTransformer,
    ThreeWindingTransformer,
    Transformer,
)

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

        >>> # First, we create the input profile
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
        data (BaseInputProfile): The input profile that the model will use to calculate temperatures.
        init_top_oil_temp (float | None): The initial top-oil temperature. Defaults to None. If this is provided,
            will start the calculation with this temperature. If not provided, will start the calculation
            with the first value of the ambient temperature profile.
            will start the calculation with this temperature. If not provided, will start the calculation
            with the first value of the ambient temperature profile.
        top_oil_temp_profile (pd.Series): The modeled top-oil temperature profile.
        initial_load (float | None): Initial load where the temperatures converge to steady state.
    """

    transformer: Transformer
    data: BaseInputProfile
    top_oil_temp_profile: pd.Series
    initial_condition: InitialCondition

    def __init__(
        self,
        temperature_profile: BaseInputProfile,
        transformer: Transformer,
        initial_condition: InitialCondition | None = None,
    ) -> None:
        """Initialize the thermal model.

        Args:
            temperature_profile (BaseInputProfile): The temperature profile for the model.
            transformer (Transformer): The transformer object.
            initial_condition (InitialCondition | None): The initial condition for the model.
        """
        logger.info("Initializing the thermal model.")
        logger.info(f"First timestamp: {temperature_profile.datetime_index[0]}")
        logger.info(f"Last timestamp: {temperature_profile.datetime_index[-1]}")
        logger.info(f"Amount of data points: {len(temperature_profile)}")
        logger.info(f"Max load: {np.max(temperature_profile.load_profile_array)}")
        self.transformer = transformer
        self.data = temperature_profile

        # If no initial condition is provided, use ColdStart
        self.initial_condition = initial_condition or ColdStart()

        self.check_config()

    def check_config(self) -> None:
        """Check if the combination of the transformer and input profile are valid."""
        if isinstance(self.transformer, ThreeWindingTransformer) and not isinstance(
            self.data, ThreeWindingInputProfile
        ):
            raise ValueError("A ThreeWindingTransformer requires a ThreeWindingInputProfile.")
        elif isinstance(self.transformer, PowerTransformer) and not isinstance(self.data, InputProfile):
            raise ValueError("A PowerTransformer requires an InputProfile.")
        elif isinstance(self.transformer, DistributionTransformer) and not isinstance(self.data, InputProfile):
            raise ValueError("A DistributionTransformer requires an InputProfile.")
        if (
            self.transformer.cooling_controller
            and self.transformer.cooling_controller.onaf_switch.fan_on is not None
            and len(self.transformer.cooling_controller.onaf_switch.fan_on) != len(self.data)
        ):
            raise ValueError(
                "The length of the fan_on list in the cooling_switch_settings must be equal to the length of the "
                "temperature profile."
            )

    def _get_time_step(self) -> np.ndarray:
        """Get the time step between the data points in minutes.

        Returns:
            np.ndarray: The time step between the data points in minutes.

        """
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

    def _calculate_f1(self, dt: float, time_const_oil: float) -> float:
        """Calculate the time delay constant f1 for the top-oil temperature."""
        return 1 - np.exp(-dt / (self.transformer.specs.oil_const_k11 * time_const_oil))

    def _calculate_f2_winding(self, dt: float, time_const_windings_array: np.ndarray) -> np.ndarray:
        """Calculate the time delay constant f2 for the hot-spot temperature. due to the windings."""
        winding_delay = np.exp(-dt / (self.transformer.specs.winding_const_k22 * time_const_windings_array))
        return winding_delay

    def _calculate_f2_oil(self, dt: float, time_const_oil: float) -> float:
        """Calculate the time delay constant f2 for the hot-spot temperature due to the oil."""
        oil_delay = np.exp(-dt * self.transformer.specs.winding_const_k22 / time_const_oil)
        return oil_delay

    def _calculate_static_hot_spot_increase(self, load: np.ndarray) -> np.ndarray:
        """Calculate the static hot-spot temperature increase using vectorized operations."""
        return (
            self.transformer.specs.hot_spot_fac_array
            * self.transformer.specs.winding_oil_gradient_array
            * (load / self.transformer.specs.nominal_load_array) ** self.transformer.specs.winding_exp_y
        )

    def get_initial_top_oil_temp(self, first_surrounding_temp: float) -> float:
        """Function that returns the top oil temp for the first timestep."""
        match self.initial_condition:
            case InitialTopOilTemp(value=temp):
                return temp
            case InitialLoad(value=load):
                top_k = self.transformer._end_temperature_top_oil(load=np.array([load]))
                return top_k + first_surrounding_temp
            case ColdStart():
                return first_surrounding_temp

    def get_initial_hot_spot_increase(self) -> float:
        """Function that returns the hot spot temp for the first timestep."""
        match self.initial_condition:
            case InitialLoad(value=load):
                static_hot_spot_incr = self._calculate_static_hot_spot_increase(np.array([load]))[0]
                return static_hot_spot_incr
            case _:
                return 0.0

    def _calculate_top_oil_temp_profile(
        self,
        t_internal: np.ndarray,
        dt: np.ndarray,
        load: np.ndarray,
    ) -> np.ndarray:
        """Calculate the top-oil temperature profile for the transformer.

        Args:
            t_internal (np.ndarray): Array of internal temperatures over time.
            dt (np.ndarray): Array of time steps in minutes.
            load (np.ndarray): Array of load values over time.

        Returns:
            np.ndarray: The computed top-oil temperature profile over time.
        """
        top_oil_temp_profile = np.zeros_like(t_internal, dtype=np.float64)
        top_oil_temp_profile[0] = self.get_initial_top_oil_temp(t_internal[0])

        self.transformer.set_ONAN_ONAF_first_timestamp(init_top_oil_temp=top_oil_temp_profile[0])

        # Handle both 1D (two-winding) and 2D (three-winding) load arrays
        for i in range(1, len(t_internal)):
            f1 = self._calculate_f1(dt[i], self.transformer.specs.time_const_oil)
            if load.ndim == 1:
                top_k = self.transformer._end_temperature_top_oil(np.array([load[i]]))
            else:
                top_k = self.transformer._end_temperature_top_oil(load[:, i])
            top_oil_temp_profile[i] = self._update_top_oil_temp(top_oil_temp_profile[i - 1], t_internal[i], top_k, f1)

            new_specs = self.transformer.set_cooling_switch_controller_specs(
                top_oil_temp_profile[i], top_oil_temp_profile[i - 1], i
            )
            if new_specs:
                self.transformer.specs = new_specs

        return top_oil_temp_profile

    def _calculate_hot_spot_temp_profile(
        self,
        load: np.ndarray,
        top_oil_temp_profile: np.ndarray,
        dt: np.ndarray,
    ) -> np.ndarray:
        """Calculate the hot-spot temperature profile for the transformer.

        Args:
            load (np.ndarray): Array of load values over time.
            top_oil_temp_profile (np.ndarray): The computed top-oil temperature profile over time.
            dt (np.ndarray): Array of time steps in minutes.

        Returns:
            np.ndarray: The computed hot-spot temperature profile over time.
                - For two-winding transformers, returns a 1D array of shape (n_steps,).
                - For three-winding transformers, returns a 2D array of shape (3, n_steps),
                  where each row corresponds to one winding: [low_voltage_side, middle_voltage_side, high_voltage_side].
        """
        hot_spot_temp_profile = np.zeros_like(load, dtype=np.float64)

        # For a two winding transformer:
        if load.ndim == 1:
            self.transformer.set_ONAN_ONAF_first_timestamp(init_top_oil_temp=top_oil_temp_profile[0])
            hot_spot_increase_windings = np.zeros_like(load)
            hot_spot_increase_oil = np.zeros_like(load)

            init_hot_spot_incr = self.get_initial_hot_spot_increase()
            hot_spot_increase_windings[0] = init_hot_spot_incr * self.transformer.specs.winding_const_k21
            hot_spot_increase_oil[0] = init_hot_spot_incr * (self.transformer.specs.winding_const_k21 - 1)
            hot_spot_temp_profile[0] = (
                top_oil_temp_profile[0] + hot_spot_increase_windings[0] - hot_spot_increase_oil[0]
            )

            for i in range(1, len(load)):
                static_hot_spot_incr = self._calculate_static_hot_spot_increase(np.array([load[i]]))[0]
                static_hot_spot_incr_windings = static_hot_spot_incr * self.transformer.specs.winding_const_k21
                static_hot_spot_incr_oil = static_hot_spot_incr * (self.transformer.specs.winding_const_k21 - 1)

                f2_windings = self._calculate_f2_winding(dt[i], self.transformer.specs.time_const_windings_array)
                f2_oil = self._calculate_f2_oil(dt[i], self.transformer.specs.time_const_oil)

                hot_spot_increase_windings[i] = self._update_hot_spot_increase(
                    hot_spot_increase_windings[i - 1], static_hot_spot_incr_windings, f2_windings[0]
                )
                hot_spot_increase_oil[i] = self._update_hot_spot_increase(
                    hot_spot_increase_oil[i - 1], static_hot_spot_incr_oil, f2_oil
                )
                hot_spot_temp_profile[i] = (
                    top_oil_temp_profile[i] + hot_spot_increase_windings[i] - hot_spot_increase_oil[i]
                )
                new_specs = self.transformer.set_cooling_switch_controller_specs(
                    top_oil_temp_profile[i], top_oil_temp_profile[i - 1], i
                )
                if new_specs:
                    self.transformer.specs = new_specs

        # For a three winding transformer with multiple load profiles:
        else:
            hot_spot_temp_profile[:, 0] = top_oil_temp_profile[0]
            n_profiles = load.shape[0]
            n_steps = load.shape[1]
            for profile in range(n_profiles):
                self.transformer.set_ONAN_ONAF_first_timestamp(init_top_oil_temp=top_oil_temp_profile[0])
                hot_spot_increase_windings = np.zeros(n_steps)
                hot_spot_increase_oil = np.zeros(n_steps)
                for i in range(1, n_steps):
                    static_hot_spot_incr = self._calculate_static_hot_spot_increase(load[:, i])
                    static_hot_spot_incr_windings = static_hot_spot_incr * self.transformer.specs.winding_const_k21
                    static_hot_spot_incr_oil = static_hot_spot_incr * (self.transformer.specs.winding_const_k21 - 1)

                    f2_windings = self._calculate_f2_winding(dt[i], self.transformer.specs.time_const_windings_array)
                    f2_oil = self._calculate_f2_oil(dt[i], self.transformer.specs.time_const_oil)

                    hot_spot_increase_windings[i] = self._update_hot_spot_increase(
                        hot_spot_increase_windings[i - 1],
                        static_hot_spot_incr_windings[profile],
                        f2_windings[profile].item(),
                    )
                    hot_spot_increase_oil[i] = self._update_hot_spot_increase(
                        hot_spot_increase_oil[i - 1], static_hot_spot_incr_oil[profile], f2_oil
                    )
                    hot_spot_temp_profile[profile, i] = (
                        top_oil_temp_profile[i] + hot_spot_increase_windings[i] - hot_spot_increase_oil[i]
                    )
                    new_specs = self.transformer.set_cooling_switch_controller_specs(
                        top_oil_temp_profile[i], top_oil_temp_profile[i - 1], i
                    )
                    if new_specs:
                        self.transformer.specs = new_specs

        return hot_spot_temp_profile

    def _update_top_oil_temp(self, current_temp: float, t_internal: float, top_k: float, f1: float) -> float:
        """Update the top-oil temperature for a single time step."""
        return current_temp + (t_internal + top_k - current_temp) * f1

    def _update_hot_spot_increase(self, current_increase: float, static_incr: float, f2: float) -> float:
        """Update the hot-spot temperature increase for a single time step."""
        return static_incr + (current_increase - static_incr) * f2

    def run(self, force_use_ambient_temperature: bool = False) -> OutputProfile:
        """Calculate the top-oil and hot-spot temperatures for the provided Transformer object.

        This method prepares the calculation inputs, calculates intermediate factors, and computes
        the top-oil and hot-spot temperature profiles for the transformer based on the provided
        load and internal parameters. If the top oil temperature is provided in the `temperature_profile` it gets
        priority over the ambient temperature. The ambient temperature is then ignored. You can change this behaviour
        using the `force_use_ambient_temperature` parameter.

        Args:
            force_use_ambient_temperature:
                Use the ambient temperature to perform the calculation,
                even if the top oil temperature is given (optional, False by default)

        Returns:
            OutputProfile: Object containing the top-oil and hot-spot temperature profiles.

        """
        logger.info("Running the thermal model.")

        # decide if we use the top oil or ambient temperature as input and perform basic validation
        use_top_oil = not force_use_ambient_temperature and self.data.top_oil_temperature_profile is not None

        dt = self.data.time_step
        load = self.data.load_profile_array
        t_internal = self._get_internal_temp()

        # Check if top oil temperature profile is provided and use it if available
        # If not, calculate it
        if use_top_oil and self.data.top_oil_temperature_profile is not None:
            top_oil_temp_profile = self.data.top_oil_temperature_profile
        else:
            top_oil_temp_profile = self._calculate_top_oil_temp_profile(t_internal, dt, load)

        # Calculate hot-spot temperature profile
        hot_spot_temp_profile = self._calculate_hot_spot_temp_profile(load, top_oil_temp_profile, dt)
        logger.info("The calculation with the Thermal model is completed.")
        logger.info(f"Max top-oil temperature: {np.max(top_oil_temp_profile)}")
        logger.info(f"Max hot-spot temperature: {np.max(hot_spot_temp_profile)}")

        if isinstance(self.transformer, ThreeWindingTransformer):
            return OutputProfile(
                top_oil_temp_profile=pd.Series(top_oil_temp_profile, index=self.data.datetime_index),
                hot_spot_temp_profile=pd.DataFrame(
                    hot_spot_temp_profile.transpose(),
                    columns=["low_voltage_side", "middle_voltage_side", "high_voltage_side"],
                    index=self.data.datetime_index,
                ),
            )
        else:
            # For a two winding transformer, hot_spot_temp_profile is a Series
            return OutputProfile(
                top_oil_temp_profile=pd.Series(top_oil_temp_profile, index=self.data.datetime_index),
                hot_spot_temp_profile=pd.Series(hot_spot_temp_profile, index=self.data.datetime_index),
            )
