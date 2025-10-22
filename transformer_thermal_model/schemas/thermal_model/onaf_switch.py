# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from typing import Self

from pydantic import BaseModel, Field, model_validator

from transformer_thermal_model.schemas.specifications.transformer import WindingSpecifications


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


class BaseONANParameters(BaseModel):
    """Base class representing common ONAN (Oil Natural Air Natural) cooling parameters.

    THis is used when an ONAF transformer switches to ONAN cooling.
    """

    top_oil_temp_rise: float
    time_const_oil: float


class ONANParameters(BaseONANParameters):
    """Class representing ONAN (Oil Natural Air Natural) cooling parameters."""

    time_const_windings: float
    load_loss: float
    nom_load_sec_side: float
    winding_oil_gradient: float
    hot_spot_fac: float


class ThreeWindingONANParameters(BaseONANParameters):
    """Class representing ONAN (Oil Natural Air Natural) cooling parameters for three-winding transformers."""

    lv_winding: WindingSpecifications = Field(..., description="ONAN parameters for the LV winding.")
    mv_winding: WindingSpecifications = Field(..., description="ONAN parameters for the MV winding.")
    hv_winding: WindingSpecifications = Field(..., description="ONAN parameters for the HV winding.")
    load_loss_mv_lv: float
    load_loss_hv_lv: float
    load_loss_hv_mv: float


class ONAFSwitchBase(BaseModel):
    """Class representing the ONAF (Oil Natural Air Forced) cooling switch status."""

    fans_status: list[bool] | None = Field(
        None, description="List indicating the ONAF cooling switch status at each time step."
    )
    temperature_threshold: FanSwitchConfig | None = Field(
        None, description="Temperature threshold for activating the ONAF cooling switch."
    )

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


class ONAFSwitch(ONAFSwitchBase):
    """Class representing the ONAF (Oil Natural Air Forced) cooling switch settings.

    This class includes the ONAN parameters to be used when the transformer switches to ONAN cooling.
    """

    onan_parameters: ONANParameters = Field(
        ..., description="ONAN parameters to be used when the transformer switches to ONAN cooling."
    )


class ThreeWindingONAFSwitch(ONAFSwitchBase):
    """Class representing the ONAF (Oil Natural Air Forced) cooling switch settings for three-winding transformers.

    This class includes the ONAN parameters to be used when the transformer switches to ONAN cooling.
    """

    onan_parameters: ThreeWindingONANParameters = Field(
        ..., description="ONAN parameters to be used when the transformer switches to ONAN cooling."
    )
