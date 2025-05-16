# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

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
