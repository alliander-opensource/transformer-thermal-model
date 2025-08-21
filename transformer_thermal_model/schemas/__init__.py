# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0


from .specifications.transformer import (
    BaseTransformerSpecifications,
    BaseUserTransformerSpecifications,
    DefaultTransformerSpecifications,
    ThreeWindingTransformerSpecifications,
    TransformerSpecifications,
    UserThreeWindingTransformerSpecifications,
    UserTransformerSpecifications,
    WindingSpecifications,
)
from .specifications.transformer_component import TransformerComponentSpecifications
from .thermal_model import InputProfile, OutputProfile, ThreeWindingInputProfile

__all__ = [
    "UserTransformerSpecifications",
    "DefaultTransformerSpecifications",
    "TransformerSpecifications",
    "BaseTransformerSpecifications",
    "UserThreeWindingTransformerSpecifications",
    "ThreeWindingTransformerSpecifications",
    "BaseUserTransformerSpecifications",
    "TransformerComponentSpecifications",
    "WindingSpecifications",
    "InputProfile",
    "ThreeWindingInputProfile",
    "OutputProfile",
]
