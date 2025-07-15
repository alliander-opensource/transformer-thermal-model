# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging

import numpy as np

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import DefaultTransformerSpecifications, UserTransformerSpecifications

from .base import Transformer

logger = logging.getLogger(__name__)


class ThreePhaseTransformer(Transformer):
    """A three-phase transformer.

    The ThreePhaseTransformer class represents a three-phase transformer.
    This class inherits from the Transformer class. This transformer can be
    used with ONAN (Oil Natural Air Natural) cooling type.
    """

    def __init__(
        self,
        user_specs: UserTransformerSpecifications,
    ):
        """Initialize the transformer object.

        Args:
            user_specs (UserTransformerSpecifications): The transformer specifications that you need to
                provide to build the transformer. Any optional specifications not provided will be taken from the
                default specifications.
        """
        super().__init__(user_specs, cooling_type=CoolerType.ONAN)

    @property
    def defaults(self) -> DefaultTransformerSpecifications:
        """The default transformer specifications."""
        return DefaultTransformerSpecifications(
            time_const_oil=180.0,
            time_const_windings=4.0,
            top_oil_temp_rise=60.0,
            winding_oil_gradient=23.0,
            hot_spot_fac=1.2,
            oil_const_k11=1.0,
            winding_const_k21=1,
            winding_const_k22=2,
            oil_exp_x=0.8,
            winding_exp_y=1.6,
            end_temp_reduction=0.0,
        )
    
    def _end_temperature_top_oil(self, load: np.ndarray) -> np.ndarray:
        """Calculate the end temperature of the top-oil."""
        load_ratio = np.power(load / self.specs.nom_load_sec_side, 2)
        total_loss_ratio = (self.specs.no_load_loss + self.specs.load_loss * load_ratio) / (
            self.specs.no_load_loss + self.specs.load_loss
        )
        step_one_end_t0 = self._pre_factor * np.power(total_loss_ratio, self.specs.oil_exp_x)

        return step_one_end_t0