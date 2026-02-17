# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from abc import ABC, abstractmethod

import numpy as np

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import (
    BaseDefaultTransformerSpecifications,
    BaseTransformerSpecifications,
)
from transformer_thermal_model.transformer.cooling_switch_controller import CoolingSwitchController


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

    def __init__(self, cooling_type: CoolerType, cooling_controller: CoolingSwitchController | None = None):
        """Initialize the Transformer object.

        Args:
            cooling_type (CoolerType): The cooling type. Can be ONAN, ONAF.
            cooling_controller (CoolingSwitchController | None): The cooling controller that handles the ONAN/ONAF
                switching logic.
        """
        self.cooling_type: CoolerType = cooling_type
        if cooling_type != CoolerType.ONAF and cooling_controller is not None:
            raise ValueError("ONAF switch only works when the cooling type is ONAF.")
        self.cooling_controller = cooling_controller

    def set_ONAN_ONAF_first_timestamp(self, init_top_oil_temp: float) -> None:
        """Delegate initial cooling type logic to CoolingSwitchController."""
        if self.cooling_controller:
            self.specs = self.cooling_controller.determine_initial_specifications(
                initial_top_oil_temperature=init_top_oil_temp
            )

    def set_cooling_switch_controller_specs(
        self, top_oil_temp: float, previous_top_oil_temp: float, index: int
    ) -> BaseTransformerSpecifications | None:
        """Delegate ONAN/ONAF switch logic to CoolingSwitchController."""
        if self.cooling_controller:
            return self.cooling_controller.get_new_specs(top_oil_temp, previous_top_oil_temp, index)
        return None

    @property
    @abstractmethod
    def defaults(self) -> BaseDefaultTransformerSpecifications:
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
    def _end_temperature_top_oil(self, load: np.ndarray) -> float:
        pass
