# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0


from pydantic import BaseModel


class InitialState(BaseModel):
    """Defines the initial state of the transformer thermal model."""


class ColdStart(InitialState):
    """Start from cold conditions (ambient temperature)."""


class InitialTopOilTemp(InitialState):
    """Start with a known top-oil temperature."""

    initial_top_oil_temp: float


class InitialLoad(InitialState):
    """Start with a known load - calculates initial temperatures from steady state."""

    initial_load: float
