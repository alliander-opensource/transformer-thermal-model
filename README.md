<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->
# Transformer thermal model

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=alliander-opensource_transformer-thermal-model&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=alliander-opensource_transformer-thermal-model)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=alliander-opensource_transformer-thermal-model&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=alliander-opensource_transformer-thermal-model)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=alliander-opensource_transformer-thermal-model&metric=coverage)](https://sonarcloud.io/summary/new_code?id=alliander-opensource_transformer-thermal-model)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=alliander-opensource_transformer-thermal-model&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=alliander-opensource_transformer-thermal-model)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=alliander-opensource_transformer-thermal-model&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=alliander-opensource_transformer-thermal-model)

`transformer-thermal-model` is a library for modelling the transformer top-oil and
hot-spot temperature based on the transformer specifications, a load profile and an ambient temperature profile.
The model is an implementation according to the standard IEC 60076-7, also known as de Loading Guide.

Check out our [documentation page](https://alliander-opensource.github.io/transformer-thermal-model/),
the [technical documentation](https://alliander-opensource.github.io/transformer-thermal-model/theoretical_documentation/overview/),
the [quick start](https://alliander-opensource.github.io/transformer-thermal-model/examples/quickstart/)
or one of the many other examples!

## Installation

### Install from PyPI

You can directly install the package from PyPI.

``` bash
pip install transformer-thermal-model
```

## Structure of the code

This package contains the following modules to work with:

- `transformer_thermal_model.model`: the core of the package to calculate a temperature profile of a transformer using
the thermal model;
- `transformer_thermal_model.transformer`: a module containing multiple
  transformer classes to be used to define a transformer;
- `transformer_thermal_model.cooler`: a module containing the enumerators to define the cooler type of the transformer;
- `transformer_thermal_model.schemas`: in schemas one can find a.o. the definition of the model interfaces and how the
transformer specificitations should be specified;
- `transformer_thermal_model.hot_spot_calibration`: a module that is used to
determine the transformer hot-spot factor to be used in the thermal model.

The following modules contain elements that are not required for thermal modelling but are used to get more insight in
aging and load capacity:

- `transformer_thermal_model.aging`: a module to calculate the aging of a transformer according to IEC 60076-7
paragraph 6.3;
- `transformer_thermal_model.components`: a module containing enumerators to define components of a power transformer if
one wants to calculate the relative load capacity of each component in the transformer.

## How to create a transformer

Before performing a calculation, a transformer object must be created with all
necessary details about the transformer.  Default values will be used for any
attribute not specified by the user.

`transformer_thermal_model.transformer`: This module has multiple `Transformer`
children, which will be elements used for the temperature calculation inside `Model`.

- `PowerTransformer`: A power transformer class, child of the `Transformer`
  class.
- `DistributionTransformer`: A distribution transformer class, also child of
  the `Transformer` class.
- `TransformerType` (`Enum`): For easily checking all available types. Does not
   have any use in our code, but might be useful for your use-case.

### Transformer specifications

A `Transformer` needs a couple of specifications (`user_specs`) and a
cooling type (in `cooling_type`). The specifications are defined in
`transformer_thermal_model.schemas.UserTransformerSpecifications`, and are
a composition of some mandatory specifications and some optionals. When the
optionals are left unchanged, the default values per class will be used.
These can be found by `defaults`, e.g. `PowerTransformer.defaults` will show
you the default specifications.

An example on how to initialise a `PowerTransformer`:

```Python
from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.transformer import PowerTransformer
from transformer_thermal_model.schemas import UserTransformerSpecifications

tr_specs = UserTransformerSpecifications(
   load_loss=1000,  # Transformer load loss [W]
   nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
   no_load_loss=200,  # Transformer no-load loss [W]
   amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
)
transformer = PowerTransformer(user_specs=tr_specs, cooling_type=CoolerType.ONAF)
```

It is recommended to adjust the following parameters when modelling a specific
transformer as these influence the thermal modelling and are
transformer-specifically defined (_the ones with a '*' are mandatory_):

- `load_loss`*: load loss of the transformer.
- `no_load_loss`*: no load loss of the transformer.
- `nom_load_sec_side`*: nominal current of the secondary side of
  the transformer.
- `amb_temp_surcharge`*:
  - `PowerTransformer`: temperature surcharge on ambient temperature due to
    installation conditions.
  - `DistributionTransformer`: Building or placement thermal classification.
- `top_oil_temp_rise`: top-oil temperature increase under
  nominal conditions.
- `winding_oil_gradient`: temperature difference between the average
winding and average oil temperature under nominal conditions
- `hot_spot_fac`: factor determining the temperature difference
between top-oil and hot-spot. Only specify when known, otherwise see [hot-spot
factor calibration](#hot-spot-factor-calibration-for-power-transformers).

#### Cooler

`transformer_thermal_model.cooler`: Similarly, you must provide the type of
cooling of your transformer. This is only for a `PowerTransformer`, since a
`DistributionTransformer` is always ONAN.
To adjust the cooler type for a `PowerTransformer`, you can do the following:

```Python
from transformer_thermal_model.transformer import PowerTransformer
from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import UserTransformerSpecifications

tr_specs = UserTransformerSpecifications(
                load_loss=10000,
                nom_load_sec_side=1000,
                no_load_loss=1000,
                amb_temp_surcharge=0,
            )

# You can create a power transformer with ONAF cooling.
onaf_trafo = PowerTransformer(user_specs = tr_specs, cooling_type = CoolerType.ONAF)
# Or you can create a power transformer with ONAN cooling
onan_trafo = PowerTransformer(user_specs = tr_specs, cooling_type = CoolerType.ONAN)
```

#### Hot-spot factor calibration for power transformers

When the hot-spot factor of a transformer is known, it can be given as a
specification as `hot_spot_fact` in a `UserTransformerSpecifications`
object.

It often occurs, however, that a transformer hot-spot factor is not
known. If this is the case, a hot-spot factor calibration can be performed to determine
the hot-spot factor of a given `PowerTransformer` object. Note that for
`DistributionTransformer` objects, hot-spot calibrations _**should not be performed**_ and the
default value can be used. For both the `PowerTransformer` and the `DistributionTransformer` the `hot_spot_fac`
in the specification is set to the default value of no hot-spot factor is provided via the `UserTransformerSpecifications`.

The following example shows how to calibrate a `PowerTransformer` object.

```Python
from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import UserTransformerSpecifications
from transformer_thermal_model.transformer import PowerTransformer
from transformer_thermal_model.hot_spot_calibration import calibrate_hotspot_factor

tr_specs = UserTransformerSpecifications(
   load_loss=1000,  # Transformer load loss [W]
   nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
   no_load_loss=200,  # Transformer no-load loss [W]
   amb_temp_surcharge=20,  # Ambient temperature surcharge [K]
)
uncalibrated_transformer = PowerTransformer(user_specs=tr_specs, cooling_type=CoolerType.ONAF)
calibrated_trafo = calibrate_hotspot_factor(
   uncalibrated_transformer=uncalibrated_transformer,
   ambient_temp=20.0,
   hot_spot_limit=98, # in most cases a hot-spot temperature limit of 98 can be used
   hot_spot_factor_min=1.1,
   hot_spot_factor_max=1.3,
)
```

The new hot-spot factor is available via `calibrated_trafo.specs.hot_spot_fac`, and from now on used in the thermal model.

```text
>>> print(calibrated_trafo.specs.hot_spot_fac)
1.1
```

#### Component capacities of a power transformer

For load capacity calculations it can be required to take into account the capacity of the different components of a
power transformers.
Therefore a functionality is available to calculate the relative capacity of the tap changers, the bushings (primary and
secondary) and the internal current transformer. The capacity is defined as the ratio of the component capacity and the
nominal load of the transformer.

The capacities are properties of the `PowerTransformer` and require the `TransformerComponentSpecifications` to be given
during initiating a PowerTransformer object.

In the following example for all components the required information is provided.

``` python
from transformer_thermal_model.components import BushingConfig, TransformerSide, VectorConfig
from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import (
    TransformerComponentSpecifications,
    UserTransformerSpecifications,
)
from transformer_thermal_model.transformer import PowerTransformer

comp_specs = TransformerComponentSpecifications(
        tap_chang_capacity=600,  # Tap changer nominal current [A]
        nom_load_prim_side=550,  # Transformer nominal current primary side [A]
        tap_chang_conf=VectorConfig.TRIANGLE_OUTSIDE,  # Tap Changer configuration
        tap_chang_side=TransformerSide.SECONDARY,  # Tap changer side
        prim_bush_capacity=600,  # Primary bushing nominal current [A]
        prim_bush_conf=BushingConfig.SINGLE_BUSHING,  # Primary bushing configuration
        sec_bush_capacity=1800,  # Secondary bushing nominal current [A]
        sec_bush_conf=BushingConfig.SINGLE_BUSHING,  # Secondary bushing configuration
        cur_trans_capacity=1300,  # Current transformer nominal current [A]
        cur_trans_conf=VectorConfig.STAR,  # Current transformer configuration
        cur_trans_side=TransformerSide.PRIMARY,  # Current transformer side
    )
user_specs = UserTransformerSpecifications(
        load_loss=1000,  # Transformer load loss [W]
        nom_load_sec_side=1500,  # Transformer nominal current secondary side [A]
        no_load_loss=200,  # Transformer no-load loss [W]
        amb_temp_surcharge=20,
    )
power_transformer = PowerTransformer(
        user_specs=user_specs, cooling_type=CoolerType.ONAF, internal_component_specs=comp_specs
    )
```

The resulting component capacities are available in `power_transformer.component_capacities`:

```text
>>> print(power_transformer.component_capacities)
{'tap_changer': 0.4, 'primary_bushings': 1.0909090909090908, 'secondary_bushings': 1.2, 'current_transformer': 2.3636363636363638}
```

Note that it is also possible to
only define a subset of the components if not all components are present. Then only the component capacities of the
provided components are available:

``` python
comp_specs = TransformerComponentSpecifications(
    tap_chang_capacity=600,  # Tap changer nominal current [A]
    nom_load_prim_side=550,  # Transformer nominal current primary side [A]
    tap_chang_conf=VectorConfig.TRIANGLE_OUTSIDE,  # Tap Changer configuration
    tap_chang_side=TransformerSide.SECONDARY,  # Tap changer side
)
power_transformer = PowerTransformer(
        user_specs=user_specs, cooling_type=CoolerType.ONAF, internal_component_specs=comp_specs
    )
```

This will generate the following result:

``` text
>>> print(power_transformer.component_capacities)
{'tap_changer': 0.4, 'primary_bushings': None, 'secondary_bushings': None, 'current_transformer': None}
```

### Thermal modelling

When a `Transformer` object is completely defined, the temperatures can be calculated using
`transformer_thermal_model.model`: the core of the package. The `Model` is
built as follows:

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

You can use the `Model` to run a calculation with either a `PowerTransformer` or
a `DistributionTransformer`. The model will return `results` with the
`top_oil_temperature` and `hot_spot_temperature` as `pd.Series`. More
specifically, the output will be in the form of `OutputProfile`, as
defined in `transformer_thermal_model.schemas`. The reason for using pd.Series
as output, is that the model uses the `index` of the series that you have provided to run the
calculation, which also creates the benefit for you that you can
relate the result to your provided input for eventual
cross-validation or analysis.

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
for details on the process
for submitting pull requests to us.

## Contact

Please read [SUPPORT](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/SUPPORT.md) for how to
get in touch with the Transformer Thermal Model project.
