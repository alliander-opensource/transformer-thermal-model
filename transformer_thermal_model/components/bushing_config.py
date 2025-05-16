# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

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
