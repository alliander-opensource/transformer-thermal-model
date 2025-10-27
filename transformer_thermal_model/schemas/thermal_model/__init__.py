# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from .input_profile import InputProfile, ThreeWindingInputProfile
from .onaf_switch import (
    CoolingSwitchBase,
    CoolingSwitchConfig,
    CoolingSwitchSettings,
    ONANParameters,
    ThreeWindingCoolingSwitchSettings,
    ThreeWindingONANParameters,
)
from .output_profile import OutputProfile

__all__ = [
    "InputProfile",
    "OutputProfile",
    "ThreeWindingInputProfile",
    "CoolingSwitchBase",
    "CoolingSwitchConfig",
    "CoolingSwitchSettings",
    "ONANParameters",
    "ThreeWindingCoolingSwitchSettings",
    "ThreeWindingONANParameters",
]
