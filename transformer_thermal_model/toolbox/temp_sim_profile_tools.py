# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import pandas as pd

from transformer_thermal_model.schemas import InputProfile


def create_temp_sim_profile_from_df(profile_as_dataframe: pd.DataFrame) -> InputProfile:
    """Create an InputProfile from a dataframe.

    This function is added as support for the transformer thermal model. It is
    handy if you have a dataframe with the temperature simulation profile and
    you want to use it in the transformer thermal model. Be mindful of the
    names of the columns, since these are directly called in the function.

    If you do not want to change column names, consider using the
    [InputProfile.create][transformer_thermal_model.schemas.thermal_model.input_profile.InputProfile.create]
    method directly.

    The dataframe should contain the following columns:
        - timestamp: The timestamp of the profile.
        - load: The load profile.
        - ambient_temperature: The ambient temperature profile.

    Example: Creating an input profile from a dataframe.
        ```python
        >>> import pandas as pd

        >>> profile = pd.DataFrame(
        ...     {
        ...         "timestamp": pd.to_datetime(["2021-01-01 00:00:00", "2021-01-01 01:00:00", "2021-01-01 02:00:00"]),
        ...         "load": [0, 0, 0],
        ...         "ambient_temperature": [5, 5, 5],
        ...     }
        ... )
        >>> input_profile = create_temp_sim_profile_from_df(profile)

        ```

    Args:
        profile_as_dataframe (pd.DataFrame): The dataframe containing the profile data.

    Returns:
        InputProfile: The temperature simulation profile.

    """
    return InputProfile.create(
        datetime_index=profile_as_dataframe["timestamp"],
        load_profile=profile_as_dataframe["load"],
        ambient_temperature_profile=profile_as_dataframe["ambient_temperature"],
    )
