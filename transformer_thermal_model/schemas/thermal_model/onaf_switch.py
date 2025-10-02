# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from typing import Self

from pydantic import BaseModel, Field, model_validator


class FanSwitchConfig(BaseModel):
    """Class representing the fan switch configuration for ONAF cooling."""

    activation_temp: float = Field(..., description="Temperature at which the fan cooling activates.")
    deactivation_temp: float = Field(..., description="Temperature at which the fan cooling deactivates.")

    @model_validator(mode="after")
    def check_temperatures(self) -> Self:
        """Check that the activation temperature is higher than the deactivation temperature."""
        if self.activation_temp <= self.deactivation_temp:
            raise ValueError("Activation temperature must be higher than deactivation temperature.")
        return self


class ONAFSwitch(BaseModel):
    """Class representing the ONAF (Oil Natural Air Forced) cooling switch status."""

    fans_status: list[bool] | None = Field(
        None, description="List indicating the ONAF cooling switch status at each time step."
    )
    temperature_threshold: FanSwitchConfig | None = Field(
        None, description="Temperature threshold for activating the ONAF cooling switch."
    )

    nom_load_sec_side_ONAN: float
    top_oil_temp_rise_ONAN: float
    winding_oil_gradient_ONAN: float
    hot_spot_fac_ONAN: float

    @model_validator(mode="after")
    def check_consistency(self) -> Self:
        """Check that either fans_status or temperature_threshold is provided, but not both.

        There are two ways to model a switch between ON and OFF for the ONAF cooling:
            1. Provide a list of booleans indicating whether the switch is ON (True) or OFF (False) at each time step.
            2. Provide a temperature threshold, where the switch turns ON when the hot-spot temperature
            exceeds this threshold.
        """
        if self.fans_status is not None and self.temperature_threshold is not None:
            raise ValueError("Provide either 'fans_status' or 'temperature_threshold', not both.")
        if self.fans_status is None and self.temperature_threshold is None:
            raise ValueError("Either 'fans_status' or 'temperature_threshold' must be provided.")
        return self
