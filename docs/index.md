<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Welcome to Transformer Thermal Model

`transformer-thermal-model` is a library for modelling the transformer top-oil and
hot-spot temperature based on the transformer specifications, a load profile and an ambient temperature profile.
The model is an implementation according to the standard IEC 60076-7, also known as de Loading Guide.

## Features

The Transformer Thermal model is designed to model the heat generation in transformers using a simple Python API.
In short, it has the following features:

* Creating a power or distribution transformer based on user specifications or IEC prescribed specifications;
* model the heat generation based on a static or dynamic load profile and ambient temperature profile;
* calculate the aging based on the hot-spot temperature;
* perform hot-spot factor, being one of the transformer specifications, calibration;
* calculate the relative component capacities.

## Example of a model of a power transformer

This example demonstrates how the heat generation in a power transformer is calculated.

The required information is:

* The load: For example the load [A] during a week.
* The ambient temperature: The temperature during the same period as the load.
* The transformer specifications: The minimal required specifications are the cooling type, the load losses,
the nominal current at the secondary side, and the temperature surcharge to compensate for building the transformer
might be placed in.

Now we will calculate transformer
temperatures using `transformer_thermal_model.model` and some simulated ambient temperature and loads.

```Python
import pandas as pd

from transformer_thermal_model.model import Model
from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import UserTransformerSpecifications, InputProfile
from transformer_thermal_model.transformer import PowerTransformer

# In this example the model is used to calculate the transformer temperature based on a load and ambient
# profile with a period of one week. Any duration can be chosen preferably with timestamps with an interval of
# 15 minute or lower. Larger timesteps will result in incorrect results but it *is* possible to calculate with them.
one_week = 4*24*7
datetime_index = pd.date_range("2020-01-01", periods=one_week, freq="15min")

# For the load (in A) and ambient temperature (in C) arbitrary constants profiles are chosen.
# It is also possible to use a realistic profile.
nominal_load = 100
load_points = pd.Series([nominal_load] * one_week, index=datetime_index)
ambient_temp = 21
temperature_points = pd.Series([ambient_temp] * one_week, index=datetime_index)

# Create an input object with the profiles
profile_input = InputProfile.create(
   datetime_index = datetime_index,
   load_profile = load_points,
   ambient_temperature_profile = temperature_points
)

# Initialise a power transformer with cooling type ONAF and, besides the mandatory user specifications, default values.
tr_specs = UserTransformerSpecifications(
   load_loss=1000,  # Transformer load loss [W]
   nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
   no_load_loss=200,  # Transformer no-load loss [W]
   amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
)
transformer = PowerTransformer(user_specs=tr_specs, cooling_type=CoolerType.ONAF)
model = Model(
   temperature_profile = profile_input,
   transformer = transformer
)

results = model.run()

# Get the results as pd.Series, with the same datetime_index as your input.
top_oil_temp_profile = results.top_oil_temp_profile
hot_spot_temp_profile = results.hot_spot_temp_profile
```

```text
>>> top_oil_temp_profile.head(3)
2020-01-01 00:00:00    41.000000
2020-01-01 00:15:00    43.639919
2020-01-01 00:30:00    45.801302

>>> hot_spot_temp_profile.head(3)
2020-01-01 00:00:00    41.000000
2020-01-01 00:15:00    44.381177
2020-01-01 00:30:00    46.443459
```

## Who is using the Transformer Thermal Model?

The Transformer Thermal Model is designed with three major cases in mind:

- **Modelling the top-oil temperature:** to elevate our understanding on how to take maximal use of a transformer,
   we want to know if we can increase the load without damaging the asset with higher temperatures. If a transformer
   is not equipped with a top-oil sensor already, adding one to an operational transformer is not straightforward,
   so a model providing us with an estimate of this value is highly appreciated.
- **Modelling the hot-spot temperature:** the hot-spot measurement has proven to be even more interesting in
   measuring the state of a transformer under load and this information required to estimate the aging.
   Some transformers are equipped with an hot-spot temperature sensor. But if this is not the case, one can use
   this model to calculate an estimate of this temperature from the top-oil measurements.
- **Creating awareness within the company:** all these values together we use to combine into one important metric:
  the _aging_ of the transformer. We want our transformers to stay in the field for as long as we estimated when
  purchasing it. If we start increasing the load on these transformers, we do not want them defecting sooner than
  expected. To show that we can confidently increase the load on certain transformers, we use the Transformer Thermal
  Model together with measurements from the field to empower our decisions to comfortably increase the load on specific
  assets.

## License

This project is licensed under the Mozilla Public License, version 2.0 - see
[LICENSE](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/LICENSE) for details.

## Licenses third-party libraries

This project includes third-party libraries,
which are licensed under their own respective Open-Source licenses.
SPDX-License-Identifier headers are used to show which license is applicable.

The concerning license files can be found in the
[LICENSES](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/LICENSES) directory.

## Contributing

Please read
[CODE_OF_CONDUCT](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/CODE_OF_CONDUCT.md),
[CONTRIBUTING](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/CONTRIBUTING.md)
and
[PROJECT GOVERNANCE](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/GOVERNANCE.md)
for details on the process for submitting pull requests to us.

## Contact

Please read [SUPPORT](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/SUPPORT.md) for how to
connect and get into contact with the Transformer Thermal Model project.
