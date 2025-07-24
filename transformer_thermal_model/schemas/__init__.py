# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0


from .specifications.transformer import (
    BaseTransformerSpecifications,
    DefaultTransformerSpecifications,
    ThreePhaseTransformerSpecifications,
    TransformerSpecifications,
    UserBaseTransformerSpecifications,
    UserTransformerSpecifications,
    UserTreePhaseTransformerSpecifications,
    WindingSpecifications,
)
from .specifications.transformer_component import TransformerComponentSpecifications
from .thermal_model import (
    BaseInputProfile,
    InputProfile,
    OutputProfile,
    ThreeWindingInputProfile,
)

__all__ = [
    "UserTransformerSpecifications",
    "DefaultTransformerSpecifications",
    "TransformerSpecifications",
    "TransformerComponentSpecifications",
    "BaseTransformerSpecifications",
    "ThreePhaseTransformerSpecifications",
    "BaseInputProfile",
    "InputProfile",
    "WindingSpecifications",
    "OutputProfile",
    "UserBaseTransformerSpecifications",
    "UserTreePhaseTransformerSpecifications",
    "ThreeWindingInputProfile",
]
