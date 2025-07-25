# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0


from .specifications.transformer import (
    BaseTransformerSpecifications,
    BaseUserTransformerSpecifications,
    DefaultTransformerSpecifications,
    ThreePhaseTransformerSpecifications,
    TransformerSpecifications,
    UserTransformerSpecifications,
    UserTreePhaseTransformerSpecifications,
    WindingSpecifications,
)
from .specifications.transformer_component import TransformerComponentSpecifications
from .thermal_model import InputProfile, OutputProfile

__all__ = [
    "UserTransformerSpecifications",
    "DefaultTransformerSpecifications",
    "TransformerSpecifications",
    "BaseTransformerSpecifications",
    "UserTreePhaseTransformerSpecifications",
    "ThreePhaseTransformerSpecifications",
    "BaseUserTransformerSpecifications",
    "TransformerComponentSpecifications",
    "WindingSpecifications",
    "InputProfile",
    "OutputProfile",
]
