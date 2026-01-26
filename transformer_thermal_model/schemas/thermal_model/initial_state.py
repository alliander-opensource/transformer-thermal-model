# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ColdStart:
    """Cold start with no initial conditions - uses ambient temperature."""

    kind: Literal["COLD"] = "COLD"


@dataclass(frozen=True)
class InitialTopOilTemp:
    """Start with a known top oil temperature."""

    value: float
    kind: Literal["INIT_TOP_OIL_TEMP"] = "INIT_TOP_OIL_TEMP"


@dataclass(frozen=True)
class InitialLoad:
    """Start with a known load - calculates initial temperatures from steady state."""

    value: float
    kind: Literal["INIT_LOAD"] = "INIT_LOAD"


InitialCondition = ColdStart | InitialTopOilTemp | InitialLoad
