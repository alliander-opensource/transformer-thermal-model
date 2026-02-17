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

        The resulting DataFrame will have the following columns:
        - 'timestamp': The datetime index of the profiles.
        - 'top_oil_temperature': The top-oil temperature profile.
        - 'hot_spot_temperature': The hot-spot temperature profile (if it's a Series)
        or separate columns for each winding (if it's a DataFrame).
        """
        # Check whether there is a single or there are multiple hot-spot temperature profile(s).
        if isinstance(self.hot_spot_temp_profile, pd.DataFrame):
            df = pd.DataFrame(
                {
                    "timestamp": self.top_oil_temp_profile.index,
                    "top_oil_temperature": self.top_oil_temp_profile,
                    "hot_spot_temperature_low_voltage_side": self.hot_spot_temp_profile.low_voltage_side,
                    "hot_spot_temperature_middle_voltage_side": self.hot_spot_temp_profile.middle_voltage_side,
                    "hot_spot_temperature_high_voltage_side": self.hot_spot_temp_profile.high_voltage_side,
                }
            )
        else:
            df = pd.DataFrame(
                {
                    "timestamp": self.top_oil_temp_profile.index,
                    "top_oil_temperature": self.top_oil_temp_profile,
                    "hot_spot_temperature": self.hot_spot_temp_profile,
                }
            )
        return df

    model_config = ConfigDict(arbitrary_types_allowed=True)
