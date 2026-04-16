# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging

import numpy as np

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import (
    DefaultTransformerSpecifications,
    TransformerSpecifications,
    UserTransformerSpecifications,
)
from transformer_thermal_model.schemas.thermal_model import CoolingSwitchSettings
from transformer_thermal_model.transformer.cooling_switch_controller import CoolingSwitchController

from .base import Transformer

logger = logging.getLogger(__name__)


class PowerTransformer(Transformer):
    """A power transformer.

    This class represents a power transformer. This class inherits from the Transformer class.

    Example: initialise a power transformer:
    ```python
    >>> from transformer_thermal_model.schemas import UserTransformerSpecifications
    >>> from transformer_thermal_model.cooler import CoolerType
    >>> from transformer_thermal_model.transformer import PowerTransformer

    >>> user_specs = UserTransformerSpecifications(
    ...     load_loss=1000,
    ...     nom_load_sec_side=1500,
    ...     no_load_loss=200,
    ... )
    >>> cooling_type = CoolerType.ONAN
    >>> transformer = PowerTransformer(
    ...     user_specs=user_specs,
    ...     cooling_type=cooling_type
    ... )

    ```
    """

    specs: TransformerSpecifications

    _onan_defaults = DefaultTransformerSpecifications(
        time_const_oil=210,
        time_const_windings=10,
        top_oil_temp_rise=60,
        winding_oil_gradient=17,
        hot_spot_fac=1.3,
        oil_const_k11=0.5,
        winding_const_k21=2,
        winding_const_k22=2,
        oil_exp_x=0.8,
        winding_exp_y=1.3,
        end_temp_reduction=0,
        amb_temp_surcharge=0,
    )
    _onaf_defaults = DefaultTransformerSpecifications(
        time_const_oil=150,
        time_const_windings=7,
        top_oil_temp_rise=60,
        winding_oil_gradient=17,
        hot_spot_fac=1.3,
        oil_const_k11=0.5,
        winding_const_k21=2,
        winding_const_k22=2,
        oil_exp_x=0.8,
        winding_exp_y=1.3,
        end_temp_reduction=0,
        amb_temp_surcharge=0,
    )
    def __init__(
        self,
        user_specs: UserTransformerSpecifications,
        cooling_type: CoolerType,
        cooling_switch_settings: CoolingSwitchSettings | None = None,
    ):
        """Initialize the transformer object.

        Args:
            user_specs (UserTransformerSpecifications): The transformer specifications that you need to
                provide to build the transformer. Any optional specifications not provided will be taken from the
                default specifications.
            cooling_type (CoolerType): The cooling type. Can be ONAN or ONAF.
            internal_component_specs (TransformerComponentSpecifications, optional): The internal component
                specifications, which are used to calculate the limiting component. Defaults to None.
            cooling_switch_settings (CoolingSwitchSettings, optional): The ONAF switch settings.
                Only used when the cooling type is ONAF.

        """
        logger.info("Creating a power transformer object.")
        logger.info("User transformer specifications: %s", user_specs)
        logger.info("Cooling type: %s", cooling_type)

        self.cooling_type: CoolerType = cooling_type

        self.specs = TransformerSpecifications.create(self.defaults, user_specs)

        # Use CoolingSwitchController if cooling_switch_settings is provided
        self.cooling_controller = (
            CoolingSwitchController(onaf_switch=cooling_switch_settings, specs=self.specs)
            if cooling_switch_settings
            else None
        )

        super().__init__(cooling_type=cooling_type, cooling_controller=self.cooling_controller)

    @property
    def defaults(self) -> DefaultTransformerSpecifications:
        """The ClassVar for default TransformerSpecifications.

        If PowerTransformer is not initialised, uses the ONAF specifications.
        """
        if self.cooling_type == CoolerType.ONAN:
            return self._onan_defaults
        else:
            return self._onaf_defaults

    @property
    def _pre_factor(self) -> float:
        return self.specs.top_oil_temp_rise

    def _end_temperature_top_oil(self, load: np.ndarray) -> float:
        """Calculate the end temperature of the top-oil.

        The load is expected to be a 1D array with a single value for a power transformer. This is to keep the
        interface consistent with the three-winding transformer, which can have multiple load profiles. In the
        code we therefore access the first element of the array.
        """
        load_ratio = np.power(load[0] / self.specs.nom_load_sec_side, 2)
        total_loss_ratio = (self.specs.no_load_loss + self.specs.load_loss * load_ratio) / (
            self.specs.no_load_loss + self.specs.load_loss
        )
        step_one_end_t0 = self._pre_factor * np.power(total_loss_ratio, self.specs.oil_exp_x)

        return step_one_end_t0

    def _calculate_internal_temp(self, ambient_temperature: np.ndarray) -> np.ndarray:
        """Calculate the internal temperature of the transformer."""
        return ambient_temperature + self.specs.amb_temp_surcharge

    def _set_hs_fac(self, hot_spot_factor: float) -> None:
        """Set hot-spot factor to specified value.

        This function is (and should only be) used by hot-spot calibration.

        Args:
            hot_spot_factor (float): The new hot-spot factor resulting from calibration.
        """
        self.specs.hot_spot_fac = hot_spot_factor
