# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import warnings
from enum import StrEnum


class VectorConfig(StrEnum):
    """Vector configuration of a transformer.

    Attributes:
        STAR (str): Star configuration.
        TRIANGLE_INSIDE (str): Triangle inside configuration.
        TRIANGLE_OUTSIDE (str): Triangle outside configuration.
    """

    STAR = "star"
    TRIANGLE_INSIDE = "triangle inside"
    TRIANGLE_OUTSIDE = "triangle outside"

    def __new__(cls, value: str) -> "VectorConfig":
        """Create a new enum member and emit deprecation warnings when accessed.

        Args:
            value: The string value assigned to the enum member.
        """
        # Issue a warning when an enumerator is accessed
        warnings.warn(
            "VectorConfig was deprecated in version v0.4.0 and will be removed in v1.0.0.",
            category=DeprecationWarning,
            stacklevel=1,
        )
        # Create the enum member using str.__new__ to avoid recursion and set the _value_
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj
