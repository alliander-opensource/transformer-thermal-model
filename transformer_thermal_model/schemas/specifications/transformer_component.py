# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

from pydantic import BaseModel, ConfigDict, Field

from transformer_thermal_model.components import BushingConfig, TransformerSide, VectorConfig


class TransformerComponentSpecifications(BaseModel):
    """Component specifications for internal components of the power transformer.

    These specifications are used to calculate the limiting component in a `PowerTransformer`, which is optional
    entirely. It is used to define the components in the `PowerTransformer`, to then determine the limiting component.

    Attributes:
        nom_load_prim_side (float): Nominal current on the primary side of the transformer [A].
        tap_chang_capacity (float | None): Tap changer nominal current [A].
        tap_chang_conf (VectorConfig | None): Tap Changer configuration.
        tap_chang_side (TransformerSide | None): Tap changer side.
        prim_bush_capacity (float | None): Primary bushing nominal current [A].
        prim_bush_conf (BushingConfig | None): Primary bushing configuration.
        sec_bush_capacity (float | None): Secondary bushing nominal current [A].
        sec_bush_conf (BushingConfig | None): Secondary bushing configuration.
        cur_trans_capacity (float | None): Current transformer nominal current [A].
        cur_trans_conf (VectorConfig | None): Current transformer configuration.
        cur_trans_side (TransformerSide | None): Current transformer side.

    Example: Initialising a power transformer with component specifications.
        ```python
        >>> from transformer_thermal_model.cooler import CoolerType
        >>> from transformer_thermal_model.components import VectorConfig, TransformerSide
        >>> from transformer_thermal_model.schemas import (
        ...     TransformerComponentSpecifications,
        ...     UserTransformerSpecifications
        ... )
        >>> from transformer_thermal_model.transformer import PowerTransformer

        >>> tr_specs = UserTransformerSpecifications(
        ...         load_loss=1000,  # Transformer load loss [W]
        ...         nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
        ...         no_load_loss=200,  # Transformer no-load loss [W]
        ...         amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
        ... )
        >>> comp_specs = TransformerComponentSpecifications(
        ...     tap_chang_capacity=600,
        ...     nom_load_prim_side=550,
        ...     tap_chang_conf=VectorConfig.STAR,
        ...     tap_chang_side=TransformerSide.PRIMARY
        ... )
        >>> tr = PowerTransformer(
        ...     user_specs=tr_specs,
        ...     cooling_type=CoolerType.ONAF,
        ...     internal_component_specs=comp_specs
        ... )
        >>> tr.component_capacities
        {'tap_changer': 1.0909090909090908, 'primary_bushings': None,
        'secondary_bushings': None, 'current_transformer': None}

        ```
    """

    nom_load_prim_side: float = Field(..., description="Transformer nominal current primary side [A]")
    tap_chang_capacity: float | None = Field(None, description="Tap changer nominal current [A]", ge=0)
    tap_chang_conf: VectorConfig | None = Field(None, description="Tap Changer configuration")
    tap_chang_side: TransformerSide | None = Field(None, description="Tap changer side")
    prim_bush_capacity: float | None = Field(None, description="Primary bushing nominal current [A]")
    prim_bush_conf: BushingConfig | None = Field(None, description="Primary bushing configuration")
    sec_bush_capacity: float | None = Field(None, description="Secondary bushing nominal current [A]")
    sec_bush_conf: BushingConfig | None = Field(None, description="Secondary bushing configuration")
    cur_trans_capacity: float | None = Field(None, description="Current transformer nominal current [A]")
    cur_trans_conf: VectorConfig | None = Field(None, description="Current transformer configuration")
    cur_trans_side: TransformerSide | None = Field(None, description="Current transformer side")

    model_config = ConfigDict(populate_by_name=True)
