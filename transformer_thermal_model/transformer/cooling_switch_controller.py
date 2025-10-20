# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from transformer_thermal_model.schemas.specifications.transformer import (
    BaseTransformerSpecifications,
    ThreeWindingTransformerSpecifications,
    TransformerSpecifications,
)
from transformer_thermal_model.schemas.thermal_model.onaf_switch import (
    FanSwitchConfig,
    ONAFSwitch,
    ThreeWindingONAFSwitch,
)


class CoolingSwitchController:
    """Encapsulates ONAN/ONAF cooling switch logic for transformers."""

    def __init__(
        self,
        onaf_switch: ONAFSwitch | ThreeWindingONAFSwitch,
        specs: TransformerSpecifications | ThreeWindingTransformerSpecifications,
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
        if self.onaf_switch.fans_status is not None:
            if not self.onaf_switch.fans_status[0]:
                return self.create_onan_specifications()
        elif (
            self.onaf_switch.temperature_threshold is not None
            and initial_top_oil_temperature < self.onaf_switch.temperature_threshold.activation_temp
        ):
            return self.create_onan_specifications()
        return self.original_onaf_specs

    def create_onan_specifications(self) -> BaseTransformerSpecifications:
        """Create ONAN specifications by modifying the original ONAF specifications.

        It decides, based on the specs whether to use the three winding specs or not.
        """
        transformer_specs = self.original_onaf_specs.model_copy(deep=True)

        if isinstance(transformer_specs, TransformerSpecifications) and isinstance(self.onaf_switch, ONAFSwitch):
            specs_dict = transformer_specs.model_dump()
            specs_dict.update(self.onaf_switch.onan_parameters.model_dump(exclude_none=True))
            transformer_specs = TransformerSpecifications(**specs_dict)

        elif isinstance(transformer_specs, ThreeWindingTransformerSpecifications) and isinstance(
            self.onaf_switch, ThreeWindingONAFSwitch
        ):
            specs_dict = transformer_specs.model_dump()
            specs_dict.update(self.onaf_switch.onan_parameters.model_dump(exclude_none=True))
            transformer_specs = ThreeWindingTransformerSpecifications(**specs_dict)

        return transformer_specs

    def check_switch_and_get_new_specs(
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
        fans_status = self.onaf_switch.fans_status
        temp_threshold = self.onaf_switch.temperature_threshold

        if fans_status is not None and index < len(fans_status) - 1:
            return self._handle_fan_status_switch(fans_status, index)
        elif temp_threshold is not None:
            return self._handle_temp_threshold_switch(temp_threshold, top_oil_temp, previous_top_oil_temp)
        return None

    def _handle_fan_status_switch(self, fans_status: list[bool], index: int) -> BaseTransformerSpecifications | None:
        """Handle switching based on fan status list."""
        previous_fan_status, current_fan_status = fans_status[index], fans_status[index + 1]
        if previous_fan_status != current_fan_status:
            if current_fan_status:
                return self.original_onaf_specs
            else:
                return self.create_onan_specifications()
        return None

    def _handle_temp_threshold_switch(
        self, temp_threshold: FanSwitchConfig, top_oil_temp: float, previous_top_oil_temp: float
    ) -> BaseTransformerSpecifications | None:
        """Handle switching based on temperature thresholds."""
        activation_temp, deactivation_temp = temp_threshold.activation_temp, temp_threshold.deactivation_temp
        if previous_top_oil_temp < activation_temp <= top_oil_temp:
            return self.original_onaf_specs
        elif previous_top_oil_temp > deactivation_temp >= top_oil_temp:
            return self.create_onan_specifications()
        return None
