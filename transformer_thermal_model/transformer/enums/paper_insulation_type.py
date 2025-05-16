# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from enum import StrEnum


class PaperInsulationType(StrEnum):
    """The insulation type of the windings of the transformer.

    Two options: NORMAL and TUP. NORMAL thermal paper has a degradation of
    one day per day at a hot-spot temperature of 98°C. Thermal Upgraded Paper (TUP)
    has a degradation of one day per day at a hot-spot temperature of 110°C.

    More detailed information on this can be found in IEC 60076-7.

    Attributes:
        NORMAL (str): Normal thermal paper.
        THERMAL_UPGRADED (str): Thermal upgraded paper.
    """

    NORMAL = "normal"
    THERMAL_UPGRADED = "thermal upgraded"
