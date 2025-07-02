# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging
from enum import StrEnum

import numpy as np

from transformer_thermal_model.components import BushingConfig, TransformerSide, VectorConfig
from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import (
    DefaultTransformerSpecifications,
    TransformerComponentSpecifications,
    UserTransformerSpecifications,
)

from .base import Transformer

logger = logging.getLogger(__name__)


class PowerTransformerComponents(StrEnum):
    """Components in a power transformer.

    This enumerator class describes the components in a power transformer
    required for relative component capacity calculations.

    Example: Initialising a power transformer.
        ```python
        >>> from transformer_thermal_model.transformer import PowerTransformer
        >>> from transformer_thermal_model.schemas import UserTransformerSpecifications
        >>> from transformer_thermal_model.cooler import CoolerType

        >>> my_transformer_specifications = UserTransformerSpecifications(
        ...     load_loss=1000,  # Transformer load loss [W]
        ...     nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
        ...     no_load_loss=200,  # Transformer no-load loss [W]
        ...     amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
        ... )
        >>> my_cooler_type = CoolerType.ONAN
        >>> my_transformer = PowerTransformer(
        ...     user_specs=my_transformer_specifications,
        ...     cooling_type=my_cooler_type
        ... )
        >>> # the default specifications that will be used when not provided
        >>> print(my_transformer.defaults)
        time_const_oil=210.0 time_const_windings=10.0 top_oil_temp_rise=60.0
        winding_oil_gradient=17.0 hot_spot_fac=1.3 oil_const_k11=0.5
        winding_const_k21=2 winding_const_k22=2 oil_exp_x=0.8 winding_exp_y=1.3
        end_temp_reduction=0.0
        >>> # the combination of the user specifications and the default specifications
        >>> print(my_transformer.specs)
        load_loss=1000.0 nom_load_sec_side=1500.0 no_load_loss=200.0
        amb_temp_surcharge=20.0 time_const_oil=210.0 time_const_windings=10.0
        top_oil_temp_rise=60.0 winding_oil_gradient=17.0 hot_spot_fac=1.3
        oil_const_k11=0.5 winding_const_k21=2 winding_const_k22=2 oil_exp_x=0.8
        winding_exp_y=1.3 end_temp_reduction=0.0

        ```

    Attributes:
        TAP_CHANGER (str): The tap changer component.
        PRIMARY_BUSHINGS (str): The primary bushings component.
        SECONDARY_BUSHINGS (str): The secondary bushings component.
        CURRENT_TRANSFORMER (str): The current transformer component.
    """

    TAP_CHANGER = "tap_changer"
    PRIMARY_BUSHINGS = "primary_bushings"
    SECONDARY_BUSHINGS = "secondary_bushings"
    CURRENT_TRANSFORMER = "current_transformer"


class PowerTransformer(Transformer):
    """A power transformer.

    This class represents a power transformer. This class inherits from the Transformer class.

    Attributes:
        internal_component_specs (TransformerComponentSpecifications | None): The internal component specifications
            which are used to calculate the relative component capacities. Defaults to None.
    """

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
    )
    internal_component_specs: TransformerComponentSpecifications | None = None
    _err = "Internal components are not set. Please provide these if you wish to calculate the limiting component."

    def __init__(
        self,
        user_specs: UserTransformerSpecifications,
        cooling_type: CoolerType,
        internal_component_specs: TransformerComponentSpecifications | None = None,
    ):
        """Initialize the transformer object.

        Args:
            user_specs (UserTransformerSpecifications): The transformer specifications that you need to
                provide to build the transformer. Any optional specifications not provided will be taken from the
                default specifications.
            cooling_type (CoolerType): The cooling type. Can be ONAN or ONAF.
            internal_component_specs (TransformerComponentSpecifications, optional): The internal component
                specifications, which are used to calculate the limiting component. Defaults to None.

        """
        logger.info("Creating a power transformer object.")
        logger.info("User transformer specifications: %s", user_specs)
        logger.info("Cooling type: %s", cooling_type)

        if internal_component_specs is not None:
            logger.info("Internal component specifications: %s", internal_component_specs)
            self.internal_component_specs = internal_component_specs

        super().__init__(
            user_specs=user_specs,
            cooling_type=cooling_type,
        )

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

    @property
    def tap_changer_capacity_ratio(self) -> float | None:
        """The ratio between the tap changer capacity and the nominal load of the transformer."""
        if self.internal_component_specs is None:
            raise ValueError(
                self._err,
            )
        elif any(
            [
                self.internal_component_specs.tap_chang_side is None,
                self.internal_component_specs.tap_chang_conf is None,
                self.internal_component_specs.tap_chang_capacity is None,
            ]
        ):
            return None
        else:
            if self.internal_component_specs.tap_chang_side == TransformerSide.PRIMARY:
                nominal_load = self.internal_component_specs.nom_load_prim_side
            elif self.internal_component_specs.tap_chang_side == TransformerSide.SECONDARY:
                nominal_load = self.specs.nom_load_sec_side

            if self.internal_component_specs.tap_chang_conf == VectorConfig.TRIANGLE_INSIDE:
                tap_changer_load = np.sqrt(3) * self.internal_component_specs.tap_chang_capacity
            else:
                tap_changer_load = self.internal_component_specs.tap_chang_capacity

            return tap_changer_load / nominal_load

    @property
    def primary_bushing_capacity_ratio(self) -> float | None:
        """The ratio between the primary bushing capacity and the nominal load of the transformer."""
        if self.internal_component_specs is None:
            raise ValueError(
                self._err,
            )
        elif any(
            [
                self.internal_component_specs.prim_bush_conf is None,
                self.internal_component_specs.prim_bush_capacity is None,
            ]
        ):
            return None
        else:
            if self.internal_component_specs.prim_bush_conf == BushingConfig.TRIANGLE_INSIDE:
                primary_bushing_load = np.sqrt(3) * self.internal_component_specs.prim_bush_capacity
            elif self.internal_component_specs.prim_bush_conf == BushingConfig.DOUBLE_BUSHING:
                primary_bushing_load = 2 * self.internal_component_specs.prim_bush_capacity  # type: ignore
            else:
                primary_bushing_load = self.internal_component_specs.prim_bush_capacity
            return primary_bushing_load / self.internal_component_specs.nom_load_prim_side

    @property
    def secondary_bushing_capacity_ratio(self) -> float | None:
        """The ratio between the secondary bushing capacity and the nominal load of the transformer."""
        if self.internal_component_specs is None:
            raise ValueError(
                self._err,
            )
        elif any(
            [
                self.internal_component_specs.sec_bush_conf is None,
                self.internal_component_specs.sec_bush_capacity is None,
            ]
        ):
            return None
        else:
            if self.internal_component_specs.sec_bush_conf == BushingConfig.TRIANGLE_INSIDE:
                secondary_bushing_load = np.sqrt(3) * self.internal_component_specs.sec_bush_capacity
            elif self.internal_component_specs.sec_bush_conf == BushingConfig.DOUBLE_BUSHING:
                secondary_bushing_load = 2 * self.internal_component_specs.sec_bush_capacity  # type: ignore
            else:
                secondary_bushing_load = self.internal_component_specs.sec_bush_capacity

            return secondary_bushing_load / self.specs.nom_load_sec_side

    @property
    def int_cur_trans_capacity_ratio(self) -> float | None:
        """The ratio between the internal current transformer capacity and the nominal load of the transformer."""
        if self.internal_component_specs is None:
            raise ValueError(
                self._err,
            )
        elif any(
            [
                self.internal_component_specs.cur_trans_side is None,
                self.internal_component_specs.cur_trans_conf is None,
                self.internal_component_specs.cur_trans_capacity is None,
            ]
        ):
            return None
        else:
            if self.internal_component_specs.cur_trans_side == TransformerSide.PRIMARY:
                nominal_load = self.internal_component_specs.nom_load_prim_side
            elif self.internal_component_specs.cur_trans_side == TransformerSide.SECONDARY:
                nominal_load = self.specs.nom_load_sec_side

            if self.internal_component_specs.cur_trans_conf == VectorConfig.TRIANGLE_INSIDE:
                ct_load = np.sqrt(3) * self.internal_component_specs.cur_trans_capacity
            else:
                ct_load = self.internal_component_specs.cur_trans_capacity

            return ct_load / nominal_load

    @property
    def component_capacities(self) -> dict:
        """Puts the limits of all transformer components in a single dictionary."""
        component_capacities = {
            PowerTransformerComponents.TAP_CHANGER.value: self.tap_changer_capacity_ratio,
            PowerTransformerComponents.PRIMARY_BUSHINGS.value: self.primary_bushing_capacity_ratio,
            PowerTransformerComponents.SECONDARY_BUSHINGS.value: self.secondary_bushing_capacity_ratio,
            PowerTransformerComponents.CURRENT_TRANSFORMER.value: self.int_cur_trans_capacity_ratio,
        }
        return component_capacities

    def _calculate_internal_temp(self, ambient_temperature: np.ndarray) -> np.ndarray:
        """Calculate the internal temperature of the transformer."""
        return ambient_temperature + self.specs.amb_temp_surcharge
