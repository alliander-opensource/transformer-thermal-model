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
from transformer_thermal_model.schemas.thermal_model.onaf_switch import ONAFSwitch


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

    def __init__(self, cooling_type: CoolerType, ONAF_switch: ONAFSwitch | None = None):
        """Initialize the Transformer object.

        Args:
            user_specs (UserTransformerSpecifications): The transformer specifications that you need to
                provide to build the transformer. Any optional specifications not provided will be taken from the
                default specifications.
            cooling_type (CoolerType): The cooling type. Can be ONAN, ONAF.
            ONAF_switch (ONAFSwitch, optional): The ONAF switch settings. Only used when the cooling type is ONAN.
        """
        self.cooling_type: CoolerType = cooling_type
        if cooling_type == CoolerType.ONAN and ONAF_switch is not None:
            raise ValueError("ONAF switch only works when the cooling type is ONAF.")
        self.ONAF_switch = ONAF_switch

    def set_ONAN_ONAF_first_timestamp(self) -> None:
        """Set the initial cooling type based on the ONAF switch settings."""
        if self.ONAF_switch is not None:
            if self.ONAF_switch.fans_status is not None:
                if not self.ONAF_switch.fans_status[0]:
                    self._switch_cooling(to_onaf=False)
            elif self.ONAF_switch.temperature_threshold is not None:
                self._switch_cooling(to_onaf=False)

    def check_onaf_switch(self, top_oil_temp: int, previous_top_oil_temp: int, index: int) -> None:
        """Check and handle the ONAF/ONAN switch based on the top-oil temperature and the switch settings."""
        if self.ONAF_switch is None:
            return

        fans_status = self.ONAF_switch.fans_status
        temp_threshold = self.ONAF_switch.temperature_threshold

        if fans_status is not None and index < len(fans_status) - 1:
            prev, curr = fans_status[index], fans_status[index + 1]
            if prev != curr:
                self._switch_cooling(to_onaf=curr)
        elif temp_threshold is not None:
            act, deact = temp_threshold.activation_temp, temp_threshold.deactivation_temp
            if previous_top_oil_temp < act <= top_oil_temp:
                self._switch_cooling(to_onaf=True)
            elif previous_top_oil_temp > deact >= top_oil_temp:
                self._switch_cooling(to_onaf=False)

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

    @abstractmethod
    def _switch_cooling(self, to_onaf: bool) -> None:
        """Switch the cooling type from ONAN to ONAF."""
        pass
