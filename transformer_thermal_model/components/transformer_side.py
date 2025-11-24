# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import warnings
from enum import StrEnum


class TransformerSide(StrEnum):
    """The possible side a component can be connected to in a transformer.

    A transformer has two sides, the primary and secondary side. The primary
    side is the side where the transformer is connected to the power source,
    while the secondary side is the side where the transformer is connected to
    the load.

    Attributes:
        PRIMARY (str): The primary side of the transformer.
        SECONDARY (str): The secondary side of the transformer.
    """

    PRIMARY = "primary"
    SECONDARY = "secondary"

    def __new__(cls, value: str) -> "TransformerSide":
        """Create a new enum member and emit deprecation warnings when accessed.

        Args:
            value: The string value assigned to the enum member.
        """
        # Issue a warning when an enumerator is accessed
        warnings.warn(
            "TransformerSide was deprecated in version v0.4.0 and will be removed in v1.0.0.",
            category=DeprecationWarning,
            stacklevel=1,
        )
        # Create the enum member using str.__new__ to avoid recursion and set the _value_
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj
