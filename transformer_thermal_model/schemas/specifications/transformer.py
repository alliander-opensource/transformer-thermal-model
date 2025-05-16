# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class UserTransformerSpecifications(BaseModel):
    """The transformer specifications that the user must and can provide.

    If any of the optional values are provided, they will overwrite the `defaults` that are set in the
    respective `Transformer` class.
    """

    load_loss: float = Field(
        ...,
        description=(
            "Transformer load loss or short-circuit loss or copper loss from the windings "
            "(taken from worst-case from FA-test) [W]"
        ),
    )
    nom_load_sec_side: float = Field(
        ..., description="Transformer nominal current secondary side from the type plate [A]"
    )
    no_load_loss: float = Field(
        ...,
        description=(
            "Transformer no-load loss, the passive loss when a transformer is under voltage. Also called iron-loss "
            "because the loss occurs in the core of the transformer. (taken from worst-case from FA-test) [W]"
        ),
    )
    amb_temp_surcharge: float = Field(
        ...,
        description=(
            "Ambient temperature surcharge, A flat temperature surcharge due to some environmental factors related to "
            "the transformer (e.g. +10K when standing inside) [K]"
        ),
    )

    # Cooler specific specs
    time_const_oil: float | None = Field(default=None, description="Time constant oil [min]", gt=0)
    time_const_windings: float | None = Field(default=None, description="Time constant windings [min]", gt=0)
    top_oil_temp_rise: float | None = Field(default=None, description="Top-oil temperature rise [K]", ge=0)
    winding_oil_gradient: float | None = Field(default=None, description="Winding oil gradient (worst case) [K]", ge=0)
    hot_spot_fac: float | None = Field(default=None, description="Hot-spot factor [-]", ge=0)

    # Transformer specific specs
    oil_const_k11: float | None = Field(default=None, description="Oil constant k11 [-]", gt=0)
    winding_const_k21: int | None = Field(default=None, description="Winding constant k21 [-]", gt=0)
    winding_const_k22: int | None = Field(default=None, description="Winding constant k22 [-]", gt=0)
    oil_exp_x: float | None = Field(default=None, description="Oil exponent x [-]", ge=0)
    winding_exp_y: float | None = Field(default=None, description="Winding exponent y [-]", ge=0)
    end_temp_reduction: float | None = Field(
        default=None, description="Lowering of the end temperature with respect to the current specification [K]"
    )


class DefaultTransformerSpecifications(BaseModel):
    """The default transformer specifications that will be defined when the user does not provide them.

    Each `Transformer` object has a class variable `defaults` that contains the default transformer specifications.
    """

    # Cooler specific specs
    time_const_oil: float
    time_const_windings: float
    top_oil_temp_rise: float
    winding_oil_gradient: float
    hot_spot_fac: float

    # Transformer specific specs
    oil_const_k11: float
    winding_const_k21: int
    winding_const_k22: int
    oil_exp_x: float
    winding_exp_y: float
    end_temp_reduction: float


class TransformerSpecifications(BaseModel):
    """Class containing transformer specifications.

    This class is a combination of the mandatory user-provided specifications and the default transformer
    specifications. Should the user provide any of the optional specifications, they will override the default
    specifications, via the `create` class method.
    """

    # mandatory user-provided specs
    load_loss: float
    nom_load_sec_side: float
    no_load_loss: float
    amb_temp_surcharge: float

    # Cooler specific specs
    time_const_oil: float
    time_const_windings: float
    top_oil_temp_rise: float
    winding_oil_gradient: float
    hot_spot_fac: float

    # Transformer specific specs
    oil_const_k11: float
    winding_const_k21: int
    winding_const_k22: int
    oil_exp_x: float
    winding_exp_y: float
    end_temp_reduction: float

    @classmethod
    def create(
        cls, defaults: DefaultTransformerSpecifications, user: UserTransformerSpecifications
    ) -> "TransformerSpecifications":
        """Create the transformer specifications from the defaults and the user specifications."""
        data = defaults.model_dump()
        data.update(user.model_dump(exclude_none=True))
        logger.info("Complete transformer specifications: %s", data)
        return cls(**data)
