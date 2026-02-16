# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import pandas as pd
from pydantic import BaseModel, ConfigDict


class OutputProfile(BaseModel):
    """Class containing the output data for the hot-spot and top-oil temperature calculations.

    The class consists of the top-oil and hot-spot temperature profiles. These have the datetime index as the timestamp
    that link both of these series together.

    Additionally, this class has a helper function to convert the output to a single dataframe for convenience.
    """

    top_oil_temp_profile: pd.Series
    hot_spot_temp_profile: pd.Series | pd.DataFrame

    def convert_to_dataframe(self) -> pd.DataFrame:
        """Convert the output profiles to a single pandas DataFrame.

        This method supports only the case where the output profile originates from a normal transformer.
        In that case, it returns a DataFrame with the timestamp index and two columns: ``"top_oil_temperature"`` and
        ``"hot_spot_temperature"``.

        If the output profile originates from a three-winding transformer, it raises a ValueError.
        """
        # Check whether there is a single or there are multiple hot-spot temperature profile(s).
        if isinstance(self.hot_spot_temp_profile, pd.DataFrame):
            raise ValueError("Cannot convert output to DataFrame for a Three Winding Transformer.")
        df = pd.DataFrame(
            {
                "timestamp": self.top_oil_temp_profile.index,
                "top_oil_temperature": self.top_oil_temp_profile,
                "hot_spot_temperature": self.hot_spot_temp_profile,
            }
        )
        return df

    model_config = ConfigDict(arbitrary_types_allowed=True)
