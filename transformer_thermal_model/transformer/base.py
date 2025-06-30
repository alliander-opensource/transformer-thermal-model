# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from abc import ABC, abstractmethod

import numpy as np

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import (
    DefaultTransformerSpecifications,
    TransformerSpecifications,
    UserTransformerSpecifications,
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
    specs: TransformerSpecifications

    def __init__(
        self,
        user_specs: UserTransformerSpecifications,
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
        self.specs = TransformerSpecifications.create(self.defaults, user_specs)

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

    def _end_temperature_top_oil(self, load: np.ndarray) -> np.ndarray:
        """Calculate the end temperature of the top-oil."""
        load_ratio = np.power(load / self.specs.nom_load_sec_side, 2)
        total_loss_ratio = (self.specs.no_load_loss + self.specs.load_loss * load_ratio) / (
            self.specs.no_load_loss + self.specs.load_loss
        )
        step_one_end_t0 = self._pre_factor * np.power(total_loss_ratio, self.specs.oil_exp_x)

        return step_one_end_t0

    def _set_HS_fac(self, hot_spot_factor: float) -> None:
        """Set hot-spot factor to specified value.

        This function is (and should only be) used by hot-spot calibration.

        Args:
            hot_spot_factor (float): The new hot-spot factor resulting from calibration.
        """
        self.specs.hot_spot_fac = hot_spot_factor
