# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

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
