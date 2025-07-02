# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging

import numpy as np

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import DefaultTransformerSpecifications, UserTransformerSpecifications

from .base import Transformer

logger = logging.getLogger(__name__)


class DistributionTransformer(Transformer):
    """A distribution transformer.

    The DistributionTransformer class represents a distribution transformer.
    This class inherits from the Transformer class. This transformer can only
    be used with ONAN (Oil Natural Air Natural) cooling type.

    Example: Initialising a distribution transformer.
        ```python
        >>> from transformer_thermal_model.schemas import UserTransformerSpecifications
        >>> from transformer_thermal_model.transformer import DistributionTransformer

        >>> transformer_specifications = UserTransformerSpecifications(
        ...     load_loss=5200,  # Transformer load loss [W]
        ...     nom_load_sec_side=900,  # Transformer nominal current secondary side [A]
        ...     no_load_loss=800,  # Transformer no-load loss [W]
        ...     amb_temp_surcharge=10,  # Ambient temperature surcharge [K]
        ... )
        >>> # note that no cooling type can be specified here, as this is a distribution transformer
        >>> my_transformer = DistributionTransformer(user_specs=transformer_specifications)
        >>> # the default specifications that will be used when not provided
        >>> print(my_transformer.defaults)
        time_const_oil=180.0 time_const_windings=4.0 top_oil_temp_rise=60.0
        winding_oil_gradient=23.0 hot_spot_fac=1.2 oil_const_k11=1.0
        winding_const_k21=1 winding_const_k22=2 oil_exp_x=0.8 winding_exp_y=1.6
        end_temp_reduction=0.0
        >>> # the combination of the user specifications and the default specifications
        >>> print(my_transformer.specs)
        load_loss=5200.0 nom_load_sec_side=900.0 no_load_loss=800.0
        amb_temp_surcharge=10.0 time_const_oil=180.0 time_const_windings=4.0
        top_oil_temp_rise=60.0 winding_oil_gradient=23.0 hot_spot_fac=1.2
        oil_const_k11=1.0 winding_const_k21=1 winding_const_k22=2 oil_exp_x=0.8
        winding_exp_y=1.6 end_temp_reduction=0.0

        ```
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
        logger.info("Creating a distribution transformer object.")
        logger.info("User transformer specifications: %s", user_specs)

        super().__init__(
            user_specs=user_specs,
            cooling_type=CoolerType.ONAN,
        )

    @property
    def defaults(self) -> DefaultTransformerSpecifications:
        """Return the default transformer specifications."""
        return DefaultTransformerSpecifications(
            time_const_oil=180,
            time_const_windings=4,
            top_oil_temp_rise=60,
            winding_oil_gradient=23,
            hot_spot_fac=1.2,
            oil_const_k11=1.0,
            winding_const_k21=1,
            winding_const_k22=2,
            oil_exp_x=0.8,
            winding_exp_y=1.6,
            end_temp_reduction=0,
        )

    @property
    def _pre_factor(self) -> float:
        return self.specs.top_oil_temp_rise + self.specs.amb_temp_surcharge

    def _calculate_internal_temp(self, ambient_temperature: np.ndarray) -> np.ndarray:
        """Calculate the internal temperature of the transformer.

        This function currently returns the ambient temperature directly without
        performing any calculations. It serves as a placeholder for future
        implementation where the internal temperature will be calculated based
        on the ambient temperature and other factors such as room classification
        or transformer-specific heat characteristics.

        Args:
            ambient_temperature (np.ndarray): A numpy array representing the
                ambient temperature values.

        Returns:
            pd.Series: The internal temperature, which is currently the same as
            the ambient temperature.

        """
        return ambient_temperature
