# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from enum import StrEnum


class TransformerType(StrEnum):
    """A type of transformer.

    Can be handy to quickly identify the type of transformer supported by the
    Transformer Thermal Model.

    Attributes:
        POWER (str): Power transformer.
        DISTRIBUTION (str): Distribution transformer.
    """

    POWER = "power"
    DISTRIBUTION = "distribution"
