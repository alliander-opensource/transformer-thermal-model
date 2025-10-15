# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from transformer_thermal_model.schemas.specifications.transformer import (
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

    def get_starting_specs(self) -> TransformerSpecifications | ThreeWindingTransformerSpecifications:
        """Get the initial specifications based on the ONAF switch settings.

        If the fans are off at the start or if a temperature threshold is set,
        the transformer starts with ONAN specifications. Otherwise, it starts with ONAF specifications.
        """
        if self.onaf_switch.fans_status is not None:
            if not self.onaf_switch.fans_status[0]:
                return self.get_onan_specs()
        elif self.onaf_switch.temperature_threshold is not None:
            return self.get_onan_specs()
        return self.original_onaf_specs

    def get_onan_specs(self) -> TransformerSpecifications | ThreeWindingTransformerSpecifications:
        """Function that returns the onan specs for a transformer.

        It decides, based on the specs whether to use the three winding specs or not.
        """
        specs = self.original_onaf_specs.model_copy(deep=True)
        specs.top_oil_temp_rise = self.onaf_switch.onan_parameters.top_oil_temp_rise
        specs.time_const_oil = self.onaf_switch.onan_parameters.time_const_oil

        if isinstance(specs, TransformerSpecifications) and isinstance(self.onaf_switch, ONAFSwitch):
            specs.winding_oil_gradient = self.onaf_switch.onan_parameters.winding_oil_gradient
            specs.time_const_windings = self.onaf_switch.onan_parameters.time_const_windings
            specs.nom_load_sec_side = self.onaf_switch.onan_parameters.nom_load_sec_side
            specs.load_loss = self.onaf_switch.onan_parameters.load_loss
            specs.hot_spot_fac = self.onaf_switch.onan_parameters.hot_spot_fac

        elif isinstance(specs, ThreeWindingTransformerSpecifications) and isinstance(
            self.onaf_switch, ThreeWindingONAFSwitch
        ):
            specs.lv_winding.winding_oil_gradient = (
                self.onaf_switch.onan_parameters.onan_lv_winding.winding_oil_gradient
            )
            specs.lv_winding.nom_load = self.onaf_switch.onan_parameters.onan_lv_winding.nom_load
            specs.lv_winding.hot_spot_fac = self.onaf_switch.onan_parameters.onan_lv_winding.hot_spot_fac
            specs.lv_winding.time_const_winding = self.onaf_switch.onan_parameters.onan_lv_winding.time_const_winding

            specs.mv_winding.winding_oil_gradient = (
                self.onaf_switch.onan_parameters.onan_mv_winding.winding_oil_gradient
            )
            specs.mv_winding.nom_load = self.onaf_switch.onan_parameters.onan_mv_winding.nom_load
            specs.mv_winding.hot_spot_fac = self.onaf_switch.onan_parameters.onan_mv_winding.hot_spot_fac
            specs.mv_winding.time_const_winding = self.onaf_switch.onan_parameters.onan_mv_winding.time_const_winding

            specs.hv_winding.winding_oil_gradient = (
                self.onaf_switch.onan_parameters.onan_hv_winding.winding_oil_gradient
            )
            specs.hv_winding.nom_load = self.onaf_switch.onan_parameters.onan_hv_winding.nom_load
            specs.hv_winding.hot_spot_fac = self.onaf_switch.onan_parameters.onan_hv_winding.hot_spot_fac
            specs.hv_winding.time_const_winding = self.onaf_switch.onan_parameters.onan_hv_winding.time_const_winding

            specs.load_loss_mv_lv = self.onaf_switch.onan_parameters.load_loss_mv_lv
            specs.load_loss_hv_lv = self.onaf_switch.onan_parameters.load_loss_hv_lv
            specs.load_loss_hv_mv = self.onaf_switch.onan_parameters.load_loss_hv_mv

        return specs

    def check_switch_and_get_new_specs(
        self, top_oil_temp: float, previous_top_oil_temp: float, index: int
    ) -> TransformerSpecifications | ThreeWindingTransformerSpecifications | None:
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

    def _handle_fan_status_switch(
        self, fans_status: list[bool], index: int
    ) -> TransformerSpecifications | ThreeWindingTransformerSpecifications | None:
        """Handle switching based on fan status list."""
        prev, curr = fans_status[index], fans_status[index + 1]
        if prev != curr:
            if curr:
                return self.original_onaf_specs
            else:
                return self.get_onan_specs()
        return None

    def _handle_temp_threshold_switch(
        self, temp_threshold: FanSwitchConfig, top_oil_temp: float, previous_top_oil_temp: float
    ) -> TransformerSpecifications | ThreeWindingTransformerSpecifications | None:
        """Handle switching based on temperature thresholds."""
        act, deact = temp_threshold.activation_temp, temp_threshold.deactivation_temp
        if previous_top_oil_temp < act <= top_oil_temp:
            return self.original_onaf_specs
        elif previous_top_oil_temp > deact >= top_oil_temp:
            return self.get_onan_specs()
        return None
