# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import warnings
from enum import StrEnum


class BushingConfig(StrEnum):
    """The bushing configuration of a transformer.

    Each bushing configuration has a different capacity calculation method
    that is used in the `PowerTransformer` class. The configuration can be
    provided using the `ComponentSpecifications` class when initializing
    a `PowerTransformer`.

    Attributes:
        SINGLE_BUSHING (str): A single bushing configuration.
        DOUBLE_BUSHING (str): A double bushing configuration.
        TRIANGLE_INSIDE (str): A triangle inside configuration.
    """

    SINGLE_BUSHING = "single bushing"
    DOUBLE_BUSHING = "double bushing"
    TRIANGLE_INSIDE = "triangle inside"

    def __new__(cls, value: str) -> "BushingConfig":
        """Create a new enum member and emit deprecation warnings when accessed.

        Args:
            value: The string value assigned to the enum member.
        """
        # Issue a warning when an enumerator is accessed
        warnings.warn(
            "BushingConfig was deprecated in version v0.4.0 and will be removed in v1.0.0.",
            category=DeprecationWarning,
            stacklevel=1,
        )
        # Create the enum member using str.__new__ to avoid recursion and set the _value_
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj
