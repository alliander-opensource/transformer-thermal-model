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
    hot_spot_temp_profile: pd.Series

    def convert_to_dataframe(self) -> pd.DataFrame:
        """Process the two pandas Series and convert them to a single dataframe, linked by the timestamp."""
        df = pd.DataFrame(
            {
                "timestamp": self.top_oil_temp_profile.index,
                "top_oil_temperature": self.top_oil_temp_profile,
                "hot_spot_temperature": self.hot_spot_temp_profile,
            }
        )
        return df

    model_config = ConfigDict(arbitrary_types_allowed=True)
