# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
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


class InitialThreeWindingLoad(InitialState):
    """Start with a known load - calculates initial temperatures from steady state."""

    lv_winding: float
    mv_winding: float
    hv_winding: float

    @property
    def initial_load(cls) -> np.ndarray:
        """Return the initial load as a numpy array."""
        return np.array([cls.lv_winding, cls.mv_winding, cls.hv_winding])
