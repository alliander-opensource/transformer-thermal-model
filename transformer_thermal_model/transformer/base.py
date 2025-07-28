# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from abc import ABC, abstractmethod

import numpy as np

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import (
    BaseTransformerSpecifications,
    DefaultTransformerSpecifications,
)


class Transformer(ABC):
    """Abstract class to define the transformer object.

    Depending on the type of transformer (either PowerTransformer or DistributionTransformer), the transformer attains
    certain default attributes. These attributes can be overwritten by using the TR_Specs dictionary.

    Attributes:
        cooling_type (CoolerType): The cooling type. Can be CoolerType.ONAN or CoolerType.ONAF.
    (TransformerSpecifications): The transformer specifications that you need to
        provide to build the transformer. Any optional specifications not provided
        will be taken from the default specifications.
    """

    cooling_type: CoolerType
    specs: BaseTransformerSpecifications

    def __init__(
        self,
        cooling_type: CoolerType,
    ):
        """Initialize the Transformer object.

        Args:
            user_specs (UserTransformerSpecifications): The transformer specifications that you need to
                provide to build the transformer. Any optional specifications not provided will be taken from the
                default specifications.
            cooling_type (CoolerType): The cooling type. Can be ONAN, ONAF.
        """
        self.cooling_type: CoolerType = cooling_type

    @property
    @abstractmethod
    def defaults(self) -> DefaultTransformerSpecifications:
        """The default transformer specifications."""
        pass

    @property
    @abstractmethod
    def _pre_factor(self) -> float:
        pass

    @abstractmethod
    def _calculate_internal_temp(self, ambient_temperature: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def _end_temperature_top_oil(self, load_profile: np.ndarray) -> np.ndarray:
        pass

    def _set_HS_fac(self, hot_spot_factor: float) -> None:
        """Set hot-spot factor to specified value.

        This function is (and should only be) used by hot-spot calibration.

        Args:
            hot_spot_factor (float): The new hot-spot factor resulting from calibration.
        """
        self.specs.hot_spot_fac = hot_spot_factor
