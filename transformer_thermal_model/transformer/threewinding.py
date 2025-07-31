# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging

import numpy as np

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import (
    DefaultTransformerSpecifications,
    ThreeWindingTransformerSpecifications,
    UserThreeWindingTransformerSpecifications,
)

from .base import Transformer

logger = logging.getLogger(__name__)

class ThreeWindingTransformer(Transformer): 
    """A three-winding transformer.
    
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
    specs: ThreeWindingTransformerSpecifications

    def __init__(
        self,
        user_specs: UserThreeWindingTransformerSpecifications,
        cooling_type: CoolerType,
    ):
        """Initialize the ThreeWindingTransformer object."""
        super().__init__(
            cooling_type=cooling_type,
        )
        self.specs = ThreeWindingTransformerSpecifications.create(self.defaults, user_specs)
        logger.debug("Initialized ThreePhaseTransformer with specifications: %s", user_specs)

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

    def _calculate_internal_temp(self, ambient_temperature: np.ndarray) -> np.ndarray:
        """Calculate the internal temperature of the transformer."""
        return ambient_temperature + self.specs.amb_temp_surcharge

    @property
    def _c1(self) -> float:
        """Calculate the constant c1 for the three-phase transformer."""
        return self.specs.hv_winding.nom_load / self.specs.mv_winding.nom_load

    @property
    def _c2(self) -> float:
        """Calculate the constant c2 for the three-phase transformer."""
        return self.specs.mv_winding.nom_load / self.specs.lv_winding.nom_load

    def _get_loss_hc(self) -> float:
        """Calculate the high side load loss."""
        return (0.5 / self._c1) * (
            self.specs.load_loss_hv_mv
            - (1 / self._c2) * self.specs.load_loss_mv_lv
            + (1 / self._c2) * self.specs.load_loss_hv_lv
        )

    def _get_loss_mc(self) -> float:
        """Calculate the medium side load loss."""
        return (0.5 / self._c2) * (
            self._c2 * self.specs.load_loss_hv_mv - self.specs.load_loss_hv_lv + self.specs.load_loss_mv_lv
        )

    def _get_loss_lc(self) -> float:
        """Calculate the low side load loss."""
        return 0.5 * (self.specs.load_loss_hv_lv - self._c2 * self.specs.load_loss_hv_mv + self.specs.load_loss_mv_lv)

    def _end_temperature_top_oil(self, load_profile: np.ndarray) -> np.ndarray:
        """Calculate the end temperature of the top-oil."""
        hv_rise = self._get_loss_hc() * np.power(load_profile[0] / self.specs.hv_winding.nom_load, 2)
        mv_rise = self._get_loss_mc() * np.power(load_profile[1] / self.specs.mv_winding.nom_load, 2)
        lv_rise = self._get_loss_lc() * np.power(load_profile[2] / self.specs.lv_winding.nom_load, 2)

        end_temp_top_oil = (
            self._pre_factor * (hv_rise + mv_rise + lv_rise + self.specs.no_load_loss) / self.specs.load_loss_total
        )
        return end_temp_top_oil