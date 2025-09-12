# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import logging
from collections.abc import Collection
from datetime import datetime
from typing import Self

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, model_validator

logger = logging.getLogger(__name__)


class BaseInputProfile(BaseModel):
    """Base class for input profiles in the transformer thermal model.

    This class is intended to be extended by specific input profile classes.
    It provides a common interface and validation methods for input profiles.
    """

    datetime_index: np.typing.NDArray[np.datetime64]
    ambient_temperature_profile: np.typing.NDArray[np.float64]
    top_oil_temperature_profile: np.typing.NDArray[np.float64] | None = None

    @model_validator(mode="after")
    def _check_datetime_index_is_sorted(self) -> Self:
        """Check if the datetime index is sorted."""
        if not np.all(self.datetime_index[:-1] <= self.datetime_index[1:]):
            raise ValueError("The datetime index should be sorted.")
        return self

    @model_validator(mode="after")
    def _check_arrays_are_one_dimensional(self) -> Self:
        """Check if the arrays are one-dimensional (or two-dimensional for load_profiles_three_winding)."""
        if self.datetime_index.ndim != 1:
            raise ValueError("The datetime_index array must be one-dimensional.")
        if self.ambient_temperature_profile.ndim != 1:
            raise ValueError("The ambient_temperature_profile array must be one-dimensional.")
        if self.top_oil_temperature_profile is not None and self.top_oil_temperature_profile.ndim != 1:
            raise ValueError("The top_oil_temperature_profile array must be one-dimensional.")
        return self

    @model_validator(mode="after")
    def _check_top_oil_temperature_profile(self) -> Self:
        """Check if the top oil temperature profile is valid."""
        if self.top_oil_temperature_profile is not None and len(self.top_oil_temperature_profile) != len(
            self.datetime_index
        ):
            raise ValueError("The length of the top_oil_temperature_profile should match the datetime_index.")
        return self

    def __len__(self) -> int:
        """Return the length of the datetime index."""
        return len(self.datetime_index)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def load_profile_array(self) -> np.typing.NDArray[np.float64]:
        """Require subclasses to define a load_profile property."""
        raise NotImplementedError("Subclasses must define a load_profile field or property.")


class InputProfile(BaseInputProfile):
    """Class containing the temperature and load profiles of two winding transformers for the thermal model `Model()`.

    This class is also capable of converting the results to a single dataframe with the timestamp as the index
    for convenience.

    Attributes:
        datetime_index: A 1d array with the datetime index for the profiles.
        load_profile: A 1d array with the load profile for the transformer.
        ambient_temperature_profile: A 1d array with the ambient temperature profile for the transformer.

    """

    load_profile: np.typing.NDArray[np.float64]

    @classmethod
    def create(
        cls,
        datetime_index: Collection[datetime],
        load_profile: Collection[float],
        ambient_temperature_profile: Collection[float],
        top_oil_temperature_profile: Collection[float] | None = None,
    ) -> Self:
        """Create an InputProfile.

        Args:
            datetime_index: The datetime index for the profiles.
            load_profile: The load profile for the transformer.
            ambient_temperature_profile: The ambient temperature profile for the transformer.
            top_oil_temperature_profile: The top oil temperature profile for the transformer (optional).

        Returns:
            An InputProfile object.

        Example: Creating an InputProfile from collections.
            ```python
            >>> from datetime import datetime
            >>> from transformer_thermal_model.schemas import InputProfile

            >>> datetime_index = [
            ...     datetime(2023, 1, 1, 0, 0),
            ...     datetime(2023, 1, 1, 1, 0),
            ...     datetime(2023, 1, 1, 2, 0),
            ... ]
            >>> load_profile = [0.8, 0.9, 1.0]
            >>> ambient_temperature_profile = [25.0, 24.5, 24.0]
            >>> input_profile = InputProfile.create(
            ...     datetime_index=datetime_index,
            ...     load_profile=load_profile,
            ...     ambient_temperature_profile=ambient_temperature_profile,
            ... )
            >>> input_profile
            InputProfile(datetime_index=array(['2023-01-01T00:00:00.000000',
            '2023-01-01T01:00:00.000000', '2023-01-01T02:00:00.000000'],
            dtype='datetime64[us]'), ambient_temperature_profile=array([25. , 24.5, 24. ]),
            top_oil_temperature_profile=None, load_profile=array([0.8, 0.9, 1. ]))

        Example: Directly creating an InputProfile object using numpy arrays.
            ```python
            >>> import numpy as np
            >>> from datetime import datetime
            >>> from transformer_thermal_model.schemas import InputProfile

            >>> input_profile = InputProfile(
            ...     datetime_index=np.array(
            ...         [
            ...             datetime(2023, 1, 1, 0, 0),
            ...             datetime(2023, 1, 1, 1, 0),
            ...             datetime(2023, 1, 1, 2, 0)
            ...         ],
            ...         dtype=np.datetime64,
            ...     ),
            ...     load_profile=np.array([0.8, 0.9, 1.0], dtype=float),
            ...     ambient_temperature_profile=np.array([25.0, 24.5, 24.0], dtype=float)
            ... )
            >>> input_profile
            InputProfile(datetime_index=array(['2023-01-01T00:00:00.000000',
            '2023-01-01T01:00:00.000000', '2023-01-01T02:00:00.000000'],
            dtype='datetime64[us]'), ambient_temperature_profile=array([25. , 24.5, 24. ]),
            top_oil_temperature_profile=None, load_profile=array([0.8, 0.9, 1. ]))

        Example: Creating an InputProfile including the top oil temperature.
            ```python
            >>> from datetime import datetime
            >>> from transformer_thermal_model.schemas import InputProfile

            >>> datetime_index = [
            ...     datetime(2023, 1, 1, 0, 0),
            ...     datetime(2023, 1, 1, 1, 0),
            ...     datetime(2023, 1, 1, 2, 0),
            ... ]
            >>> load_profile = [0.8, 0.9, 1.0]
            >>> ambient_temperature_profile = [25.0, 24.5, 24.0]
            >>> top_oil_temperature = [37.0, 36.5, 36.0]
            >>> input_profile = InputProfile.create(
            ...     datetime_index=datetime_index,
            ...     load_profile=load_profile,
            ...     ambient_temperature_profile=ambient_temperature_profile,
            ...     top_oil_temperature_profile=top_oil_temperature,
            ... )
            >>> input_profile
            InputProfile(datetime_index=array(['2023-01-01T00:00:00.000000', '2023-01-01T01:00:00.000000',
            '2023-01-01T02:00:00.000000'], dtype='datetime64[us]'),
            ambient_temperature_profile=array([25. , 24.5, 24. ]),
            top_oil_temperature_profile=array([37. , 36.5, 36. ]), load_profile=array([0.8, 0.9, 1. ]))
        """
        return cls(
            datetime_index=np.array(datetime_index, dtype=np.datetime64),
            load_profile=np.array(load_profile, dtype=float),
            ambient_temperature_profile=np.array(ambient_temperature_profile, dtype=float),
            top_oil_temperature_profile=(
                np.array(top_oil_temperature_profile, dtype=float) if top_oil_temperature_profile is not None else None
            ),
        )

    @property
    def load_profile_array(self) -> np.typing.NDArray[np.float64]:
        """Return the single load profile for the transformer."""
        return self.load_profile

    @model_validator(mode="after")
    def _check_same_length_of_profiles(self) -> Self:
        """Check if the length of the profiles is the same."""
        if len(self.datetime_index) != len(self.load_profile) or len(self.datetime_index) != len(
            self.ambient_temperature_profile
        ):
            raise ValueError(
                f"The length of the profiles and index should be the same. Index length: {len(self.datetime_index)}, "
                f"load profile length: {len(self.load_profile)}"
            )
        return self

    @model_validator(mode="after")
    def _check_load_profile_is_one_dimensional(self) -> Self:
        """Check if the arrays are one-dimensional."""
        if self.load_profile.ndim != 1:
            raise ValueError("The load_profile array must be one-dimensional.")
        return self

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> Self:
        """Create an InputProfile from a dataframe.

        Args:
            df: The dataframe containing the profiles. The dataframe should have a datetime index and three columns:
                - 'datetime_index': The datetime index for the profiles.
                - 'load_profile': The load profile for the transformer.
                - 'ambient_temperature_profile': The ambient temperature profile for the transformer.

        Returns:
            An InputProfile object.

        """
        required_columns = {"datetime_index", "load_profile", "ambient_temperature_profile"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"The dataframe is missing the following required columns: {', '.join(missing_columns)}")

        return cls(
            datetime_index=df["datetime_index"].to_numpy(),
            load_profile=df["load_profile"].to_numpy(),
            ambient_temperature_profile=df["ambient_temperature_profile"].to_numpy(),
            top_oil_temperature_profile=df["top_oil_temperature_profile"].to_numpy()
            if "top_oil_temperature_profile" in df.columns
            else None,
        )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ThreeWindingInputProfile(BaseInputProfile):
    """Class for three-winding transformer input profiles.

    This class extends InputProfile to include three load profiles for three-winding transformers.
    It ensures that all three load profiles are provided and have the same length as the ambient temperature profile.
    """

    load_profile_high_voltage_side: np.typing.NDArray[np.float64]
    load_profile_middle_voltage_side: np.typing.NDArray[np.float64]
    load_profile_low_voltage_side: np.typing.NDArray[np.float64]

    @property
    def load_profile_array(self) -> np.typing.NDArray[np.float64]:
        """Return an array with shape (3,n) of the three load profiles (high, middle, low voltage sides)."""
        return np.array(
            [
                self.load_profile_low_voltage_side,
                self.load_profile_middle_voltage_side,
                self.load_profile_high_voltage_side,
            ]
        )

    @classmethod
    def create(
        cls,
        datetime_index: Collection[datetime],
        ambient_temperature_profile: Collection[float],
        load_profile_high_voltage_side: Collection[float],
        load_profile_middle_voltage_side: Collection[float],
        load_profile_low_voltage_side: Collection[float],
        top_oil_temperature_profile: Collection[float] | None = None,
    ) -> Self:
        """Create a ThreeWindingInputProfile from datetime index, ambient temperature profile, and three load profiles.

        Args:
            datetime_index: The datetime index for the profiles.
            ambient_temperature_profile: The ambient temperature profile for the transformer.
            load_profile_high_voltage_side: Load profile for the high voltage side.
            load_profile_middle_voltage_side: Load profile for the middle voltage side.
            load_profile_low_voltage_side: Load profile for the low voltage side.
            top_oil_temperature_profile: The top oil temperature profile for the transformer (optional).

        Returns:
            A ThreeWindingInputProfile object.

        Example: Creating a ThreeWindingInputProfile from collections.
            ```python
            >>> import numpy as np
            >>> from datetime import datetime
            >>> from transformer_thermal_model.schemas import ThreeWindingInputProfile

            >>> input_profile = ThreeWindingInputProfile.create(
            ...     datetime_index=np.array(
            ...         [
            ...             datetime(2023, 1, 1, 0, 0),
            ...             datetime(2023, 1, 1, 1, 0),
            ...             datetime(2023, 1, 1, 2, 0)
            ...         ],
            ...         dtype=np.datetime64,
            ...     ),
            ...     load_profile_high_voltage_side=np.array([0.8, 0.9, 1.0], dtype=float),
            ...     load_profile_middle_voltage_side=np.array([0.7, 0.8, 0.9], dtype=float),
            ...     load_profile_low_voltage_side=np.array([0.6, 0.7, 0.8], dtype=float),
            ...     ambient_temperature_profile=np.array([25.0, 24.5, 24.0], dtype=float)
            ... )
            >>> input_profile
            ThreeWindingInputProfile(datetime_index=array(['2023-01-01T00:00:00.000000', '2023-01-01T01:00:00.000000',
            '2023-01-01T02:00:00.000000'], dtype='datetime64[us]'),
            ambient_temperature_profile=array([25. , 24.5, 24. ]),
            top_oil_temperature_profile=None,
            load_profile_high_voltage_side=array([0.8, 0.9, 1. ]),
            load_profile_middle_voltage_side=array([0.7, 0.8, 0.9]),
            load_profile_low_voltage_side=array([0.6, 0.7, 0.8]))
        """
        return cls(
            datetime_index=np.array(datetime_index, dtype=np.datetime64),
            ambient_temperature_profile=np.array(ambient_temperature_profile, dtype=float),
            load_profile_high_voltage_side=np.array(load_profile_high_voltage_side, dtype=float),
            load_profile_middle_voltage_side=np.array(load_profile_middle_voltage_side, dtype=float),
            load_profile_low_voltage_side=np.array(load_profile_low_voltage_side, dtype=float),
            top_oil_temperature_profile=np.array(top_oil_temperature_profile, dtype=float)
            if top_oil_temperature_profile is not None
            else None,
        )

    @model_validator(mode="after")
    def _check_same_length_of_profiles(self) -> Self:
        """Check if the length of the profiles is the same."""
        if (
            len(self.datetime_index) != len(self.load_profile_high_voltage_side)
            or len(self.datetime_index) != len(self.load_profile_middle_voltage_side)
            or len(self.datetime_index) != len(self.load_profile_low_voltage_side)
        ):
            raise ValueError(
                f"The length of the profiles and index should be the same. Index length: {len(self.datetime_index)}, "
                f"high voltage load profile length: {len(self.load_profile_high_voltage_side)}, "
                f"middle voltage load profile length: {len(self.load_profile_middle_voltage_side)}, "
                f"low voltage load profile length: {len(self.load_profile_low_voltage_side)}, "
            )
        return self
