# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from enum import StrEnum


class CoolerType(StrEnum):
    """Cooler setup of a transformer.

    There are two types of cooling methods for this model.
     - ONAN: Oil Natural Air Natural, meaning that the oil is cooled by natural
        convection and the air is cooled by natural convection.
     - ONAF: which is Oil Natural Air Forced, meaning that the oil is cooled by natural
        convection and the air is cooled by forced convection.

    Attributes:
        ONAN (str): Oil Natural Air Natural.
        ONAF (str): Oil Natural Air Forced.
    """

    ONAN = "ONAN"
    ONAF = "ONAF"
