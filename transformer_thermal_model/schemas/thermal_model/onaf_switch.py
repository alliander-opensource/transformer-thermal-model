# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from typing import Self

from pydantic import BaseModel, Field, model_validator


class ONAFSwitch(BaseModel):
    """Class representing the ONAF (Oil Natural Air Forced) cooling switch status."""

    is_on: list[bool] | None = Field(
        None, description="List indicating the ONAF cooling switch status at each time step."
    )
    temperature_threshold: float | None = Field(
        None, description="Temperature threshold for activating the ONAF cooling switch."
    )
    time_const_oil_ONAF: float = Field(
        description="Time constant for the oil temperature rise when ONAF cooling is ON."
    )
    time_const_windings_ONAF: float = Field(
        description=("Time constant for the winding temperature rise when ONAF cooling is ON."),
    )

    @model_validator(mode="after")
    def check_consistency(self) -> Self:
        """Check that either is_on or temperature_threshold is provided, but not both.

        There are two ways to model a switch between ON and OFF for the ONAF cooling:
            1. Provide a list of booleans indicating whether the switch is ON (True) or OFF (False) at each time step.
            2. Provide a temperature threshold, where the switch turns ON when the hot-spot temperature
            exceeds this threshold.
        """
        if self.is_on is not None and self.temperature_threshold is not None:
            raise ValueError("Provide either 'is_on' or 'temperature_threshold', not both.")
        if self.is_on is None and self.temperature_threshold is None:
            raise ValueError("Either 'is_on' or 'temperature_threshold' must be provided.")
        return self
