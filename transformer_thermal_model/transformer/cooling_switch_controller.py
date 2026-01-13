# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0
import numpy as np

from transformer_thermal_model.schemas.specifications.transformer import (
    BaseTransformerSpecifications,
    ThreeWindingTransformerSpecifications,
    TransformerSpecifications,
)
from transformer_thermal_model.schemas.thermal_model.onaf_switch import (
    CoolingSwitchBase,
    CoolingSwitchConfig,
    CoolingSwitchSettings,
    ThreeWindingCoolingSwitchSettings,
)


class CoolingSwitchController:
    """Encapsulates ONAN/ONAF cooling switch logic for transformers.

    This class manages the automatic switching between ONAN (Oil Natural Air Natural) and ONAF
    (Oil Natural Air Forced) cooling modes based on either:
    - A predefined fan status schedule (list of boolean values)
    - Temperature thresholds (activation and deactivation temperatures)

    The controller is used internally by transformer classes and handles the logic for determining
    when to switch cooling modes and what specifications to apply for each mode.

    Example: Using CoolingSwitchController with temperature-based switching
        ```python
        >>> import numpy as np
        >>> from transformer_thermal_model.transformer import PowerTransformer
        >>> from transformer_thermal_model.schemas import UserTransformerSpecifications
        >>> from transformer_thermal_model.schemas.thermal_model import (
        ...     CoolingSwitchSettings,
        ...     CoolingSwitchConfig,
        ...     ONANParameters,
        ... )
        >>> from transformer_thermal_model.cooler import CoolerType

        >>> # Define the transformer specifications for ONAF mode
        >>> user_specs = UserTransformerSpecifications(
        ...     load_loss=1000,
        ...     nom_load_sec_side=1500,
        ...     no_load_loss=200,
        ...     amb_temp_surcharge=20,
        ... )
        >>> # Define ONAN parameters (for when fans are off)
        >>> onan_params = ONANParameters(
        ...     nom_load_sec_side=1200,
        ...     top_oil_temp_rise=65,
        ...     winding_oil_gradient=20,
        ...     hot_spot_fac=1.3,
        ...     time_const_oil=210,
        ...     time_const_windings=10,
        ...     load_loss=800,
        ... )
        >>> # Create switch configuration with temperature thresholds
        >>> # Fans activate at 70°C, deactivate at 60°C
        >>> onaf_switch = CoolingSwitchSettings(
        ...     temperature_threshold=CoolingSwitchConfig(activation_temp=70, deactivation_temp=60),
        ...     onan_parameters=onan_params
        ... )
        >>> # Create transformer with automatic switching capability
        >>> transformer = PowerTransformer(
        ...     user_specs=user_specs,
        ...     cooling_type=CoolerType.ONAF,
        ...     cooling_switch_settings=onaf_switch
        ... )
        >>> # The CoolingSwitchController is now managing the cooling mode switches automatically

        ```

    Example: Using CoolingSwitchController with predefined fan status
        ```python
        >>> from transformer_thermal_model.transformer import PowerTransformer
        >>> from transformer_thermal_model.schemas.thermal_model import CoolingSwitchSettings, ONANParameters

        >>> # Create a fan status schedule: True = ONAF (fans on), False = ONAN (fans off)
        >>> # This represents 5 time steps with fans on, then off, then on again
        >>> fan_schedule = np.array([True, True, True, True, True, False, False, False, True, True])
        >>> # Define ONAN parameters for when fans are off
        >>> onan_params = ONANParameters(
        ...     nom_load_sec_side=1200,
        ...     top_oil_temp_rise=65,
        ...     winding_oil_gradient=20,
        ...     hot_spot_fac=1.3,
        ...     time_const_oil=210,
        ...     time_const_windings=10,
        ...     load_loss=800,
        ... )
        >>> onaf_switch = CoolingSwitchSettings(
        ...     fan_on=fan_schedule,
        ...     onan_parameters=onan_params
        ... )
        >>> transformer = PowerTransformer(
        ...     user_specs=user_specs,
        ...     cooling_type=CoolerType.ONAF,
        ...     cooling_switch_settings=onaf_switch
        ... )
        >>> # The controller will switch modes according to the predefined schedule

        ```

    Attributes:
        onaf_switch (CoolingSwitchSettings | ThreeWindingCoolingSwitchSettings): The switch configuration containing
            either fan status schedule or temperature thresholds, plus ONAN parameters.
        original_onaf_specs (BaseTransformerSpecifications): Deep copy of the original ONAF specifications,
            used as reference when switching back to ONAF mode.
    """

    def __init__(
        self,
        onaf_switch: CoolingSwitchBase,
        specs: BaseTransformerSpecifications,
    ):
        """Initialize the controller with the given ONAF switch settings and transformer specifications."""
        self.onaf_switch = onaf_switch
        self.original_onaf_specs = specs.model_copy(deep=True)

    def determine_initial_specifications(
        self,
        initial_top_oil_temperature: float,
    ) -> BaseTransformerSpecifications:
        """Get the initial specifications based on the ONAF switch settings.

        If the fans are off at the start or if a temperature threshold is set,
        the transformer starts with ONAN specifications. Otherwise, it starts with ONAF specifications.
        """
        if self.onaf_switch.fan_on is not None:
            if not self.onaf_switch.fan_on[0]:
                return self.create_onan_specifications()
        elif (
            self.onaf_switch.temperature_threshold is not None
            and initial_top_oil_temperature < self.onaf_switch.temperature_threshold.activation_temp
        ):
            return self.create_onan_specifications()
        return self.original_onaf_specs

    def create_onan_specifications(self) -> BaseTransformerSpecifications:
        """Create ONAN specifications by merging ONAN parameters into the original ONAF specifications.

        This method returns a deep copy of the original ONAF specifications with fields overridden by the
        ONAN parameters provided in the switch configuration. Only fields present in the ONAN parameters
        are updated; all other fields remain unchanged. The method automatically selects the correct
        specification type (standard or three-winding) based on the input objects.
        """
        transformer_specs = self.original_onaf_specs.model_copy(deep=True)

        if isinstance(transformer_specs, TransformerSpecifications) and isinstance(
            self.onaf_switch, CoolingSwitchSettings
        ):
            specs_dict = transformer_specs.model_dump()
            specs_dict.update(self.onaf_switch.onan_parameters.model_dump(exclude_none=True))
            transformer_specs = TransformerSpecifications(**specs_dict)

        elif isinstance(transformer_specs, ThreeWindingTransformerSpecifications) and isinstance(
            self.onaf_switch, ThreeWindingCoolingSwitchSettings
        ):
            specs_dict = transformer_specs.model_dump()
            specs_dict.update(self.onaf_switch.onan_parameters.model_dump(exclude_none=True))
            transformer_specs = ThreeWindingTransformerSpecifications(**specs_dict)

        return transformer_specs

    def get_new_specs(
        self, top_oil_temp: float, previous_top_oil_temp: float, index: int
    ) -> BaseTransformerSpecifications | None:
        """Check and handle the ONAF/ONAN switch based on the top-oil temperature and the switch settings.

        This method evaluates the current and previous top-oil temperatures, along with the fan status
        and temperature thresholds, to determine the appropriate transformer specifications to use.

        Args:
            top_oil_temp (float): Current top-oil temperature.
            previous_top_oil_temp (float): Previous top-oil temperature.
            index (int): Index for fan status or threshold evaluation.
        """
        fan_on = self.onaf_switch.fan_on
        temp_threshold = self.onaf_switch.temperature_threshold

        if fan_on is not None and index < len(fan_on) - 1:
            return self._handle_fan_status_switch(fan_on, index)
        elif temp_threshold is not None:
            return self._handle_temp_threshold_switch(temp_threshold, top_oil_temp, previous_top_oil_temp)
        return None

    def _handle_fan_status_switch(self, fan_on: np.ndarray, index: int) -> BaseTransformerSpecifications | None:
        """Handle switching based on fan status list."""
        previous_fan_status, current_fan_status = fan_on[index], fan_on[index + 1]
        if previous_fan_status != current_fan_status:
            if current_fan_status:
                return self.original_onaf_specs
            else:
                return self.create_onan_specifications()
        return None

    def _handle_temp_threshold_switch(
        self, temp_threshold: CoolingSwitchConfig, top_oil_temp: float, previous_top_oil_temp: float
    ) -> BaseTransformerSpecifications | None:
        """Handle switching based on temperature thresholds.

        This method evaluates the current and previous top-oil temperatures against the activation and
        deactivation thresholds to determine the appropriate transformer specifications to use.
        """
        activation_temp, deactivation_temp = temp_threshold.activation_temp, temp_threshold.deactivation_temp
        if previous_top_oil_temp < activation_temp <= top_oil_temp:
            return self.original_onaf_specs
        elif previous_top_oil_temp > deactivation_temp >= top_oil_temp:
            return self.create_onan_specifications()
        return None
