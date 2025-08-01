# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging
from typing import Self

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WindingSpecifications(BaseModel):
    """The specifications for a single winding of a transformer."""

    nom_load: float = Field(..., description="Nominal load from the type plate [A]")
    winding_oil_gradient: float = Field(..., description="Winding oil temperature gradient [K]", ge=0)


class BaseUserTransformerSpecifications(BaseModel):
    """The base transformer specifications that the user must and can provide.

    If any of the optional values are provided, they will overwrite the `defaults` that are set in the
    respective `Transformer` class.
    """

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


class UserTransformerSpecifications(BaseUserTransformerSpecifications):
    """An extended version of the base transformer specifications for power and distribution transformers.

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


class UserThreeWindingTransformerSpecifications(BaseUserTransformerSpecifications):
    """An extended version of the base transformer specifications for three-winding transformers."""

    # three-winding transformer specific specs
    lv_winding: WindingSpecifications = Field(
        ...,
        description="Low-voltage winding specifications, including nominal load and load loss [A, W]",
    )
    mv_winding: WindingSpecifications = Field(
        ...,
        description="Medium-voltage winding specifications, including nominal load and load loss [A, W]",
    )
    hv_winding: WindingSpecifications = Field(
        ...,
        description="High-voltage winding specifications, including nominal load and load loss [A, W]",
    )
    load_loss_hv_lv: float = Field(
        ...,
        description="Load loss between high-voltage and low-voltage winding [W]",
    )
    load_loss_hv_mv: float = Field(
        ...,
        description="Load loss between high-voltage and medium-voltage winding [W]",
    )
    load_loss_mv_lv: float = Field(
        ...,
        description="Load loss between medium-voltage and low-voltage winding [W]",
    )

    load_loss_total: float | None = None


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


class BaseTransformerSpecifications(BaseModel):
    """Base Class containing transformer specifications."""

    no_load_loss: float
    amb_temp_surcharge: float
    time_const_oil: float
    time_const_windings: float
    top_oil_temp_rise: float
    winding_oil_gradient: float
    hot_spot_fac: float
    oil_const_k11: float
    winding_const_k21: int
    winding_const_k22: int
    oil_exp_x: float
    winding_exp_y: float
    end_temp_reduction: float

    @property
    def nominal_load_array(cls) -> np.ndarray:
        """Return the nominal loads as a numpy array."""
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    def winding_oil_gradient_array(cls) -> np.ndarray:
        """Return the winding oil gradient as a numpy array."""
        raise NotImplementedError("This method should be implemented in subclasses.")


class TransformerSpecifications(BaseTransformerSpecifications):
    """Class containing transformer specifications.

    This class is a combination of the mandatory user-provided specifications and the default transformer
    specifications. Should the user provide any of the optional specifications, they will override the default
    specifications, via the `create` class method.
    """

    load_loss: float
    nom_load_sec_side: float

    @classmethod
    def create(
        cls, defaults: DefaultTransformerSpecifications, user: UserTransformerSpecifications
    ) -> "TransformerSpecifications":
        """Create the transformer specifications from the defaults and the user specifications."""
        data = defaults.model_dump()
        data.update(user.model_dump(exclude_none=True))
        logger.info("Complete transformer specifications: %s", data)
        return cls(**data)

    @property
    def nominal_load_array(cls) -> np.ndarray:
        """Return the nominal loads as a numpy array."""
        return np.array([cls.nom_load_sec_side])

    @property
    def winding_oil_gradient_array(cls) -> np.ndarray:
        """Return the winding oil gradient as a numpy array."""
        return np.array([cls.winding_oil_gradient])


class ThreeWindingTransformerSpecifications(BaseTransformerSpecifications):
    """The transformer specifications that are specific to a three-winding transformer.

    For all three windings the specs should be provided. Note that we use the following abbreviaties:
    *  Low voltage: lv
    *  Medium voltage: mv
    *  High voltage: hv
    """

    lv_winding: WindingSpecifications
    mv_winding: WindingSpecifications
    hv_winding: WindingSpecifications
    load_loss_hv_lv: float
    load_loss_hv_mv: float
    load_loss_mv_lv: float
    load_loss_total: float

    @classmethod
    def create(
        cls, defaults: DefaultTransformerSpecifications, user: UserThreeWindingTransformerSpecifications
    ) -> Self:
        """Create a ThreeWindingTransformerSpecifications instance by merging defaults with user specifications."""
        data = defaults.model_dump()
        data.update(user.model_dump(exclude_none=True))
        logger.info("Complete three-winding transformer specifications: %s", data)

        # If no load loss is not provided, it can be calculated based on the individual losses
        if user.load_loss_total is None:
            data["load_loss_total"] = user.load_loss_hv_lv + user.load_loss_hv_mv + user.load_loss_mv_lv

        return cls(**data)

    @property
    def nominal_load_array(cls) -> np.ndarray:
        """Return the nominal loads as a numpy array."""
        return np.array(
            [
                [cls.lv_winding.nom_load],
                [cls.mv_winding.nom_load],
                [cls.hv_winding.nom_load],
            ]
        )

    @property
    def winding_oil_gradient_array(cls) -> np.ndarray:
        """Return the winding oil gradient as a numpy array."""
        return np.array(
            [
                [cls.lv_winding.winding_oil_gradient],
                [cls.mv_winding.winding_oil_gradient],
                [cls.hv_winding.winding_oil_gradient],
            ]
        )
