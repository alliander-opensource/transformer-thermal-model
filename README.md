<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->
# Transformer thermal model

[![PyPI version](https://badge.fury.io/py/transformer-thermal-model.svg?no-cache)](https://badge.fury.io/py/transformer-thermal-model.svg) <!-- markdownlint-disable-line first-line-h1 line-length -->
[![License: MPL2.0](https://img.shields.io/badge/License-MPL2.0-informational.svg)](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/transformer-thermal-model)](https://pepy.tech/project/transformer-thermal-model)
[![Downloads](https://static.pepy.tech/badge/transformer-thermal-model/month)](https://pepy.tech/project/transformer-thermal-model)
[![DOI](https://zenodo.org/badge/984616930.svg)](https://doi.org/10.5281/zenodo.17434808)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=alliander-opensource_transformer-thermal-model&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=alliander-opensource_transformer-thermal-model)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=alliander-opensource_transformer-thermal-model&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=alliander-opensource_transformer-thermal-model)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=alliander-opensource_transformer-thermal-model&metric=coverage)](https://sonarcloud.io/summary/new_code?id=alliander-opensource_transformer-thermal-model)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=alliander-opensource_transformer-thermal-model&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=alliander-opensource_transformer-thermal-model)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=alliander-opensource_transformer-thermal-model&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=alliander-opensource_transformer-thermal-model)

A Python library for modelling transformer top-oil and hot-spot temperatures based on IEC 60076-7 (Loading Guide).
Predicts temperature profiles from load and ambient temperature profile, and transformer specifications.

## Quick Start

Install from PyPI:

```bash
pip install transformer-thermal-model
```

Simple example:

```python
import pandas as pd
from transformer_thermal_model.model import Model
from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import UserTransformerSpecifications, InputProfile
from transformer_thermal_model.transformer import PowerTransformer

# Create transformer specs
tr_specs = UserTransformerSpecifications(
    load_loss=1000, nom_load_sec_side=1500, no_load_loss=200, amb_temp_surcharge=20
)
transformer = PowerTransformer(user_specs=tr_specs, cooling_type=CoolerType.ONAF)

# Create load and ambient temperature profiles
datetime_index = pd.date_range("2020-01-01", periods=168, freq="15min")
profile_input = InputProfile.create(
    datetime_index=datetime_index,
    load_profile=pd.Series([100] * 168, index=datetime_index),
    ambient_temperature_profile=pd.Series([21] * 168, index=datetime_index),
)

# Run the model
model = Model(temperature_profile=profile_input, transformer=transformer)
results = model.run()
```

For more examples, see the [documentation](https://alliander-opensource.github.io/transformer-thermal-model/).

## Features

- **Temperature modeling**: Calculate top-oil and hot-spot temperatures according to IEC 60076-7
- **Multiple transformer types**: Power, distribution, and three-winding transformers
- **Hot-spot calibration**: Automatic calibration of hot-spot factors
- **Component analysis**: Calculate load capacities of transformer components
- **Aging calculations**: Analyze transformer aging and life expectancy
- **Flexible profiles**: Support for time-varying load and ambient temperature inputs

## Documentation

- [Getting Started](https://alliander-opensource.github.io/transformer-thermal-model/get_started/about/)
- [API Reference](https://alliander-opensource.github.io/transformer-thermal-model/api_reference/model/)
- [Examples](https://alliander-opensource.github.io/transformer-thermal-model/examples/quickstart/)
- [Technical Documentation](https://alliander-opensource.github.io/transformer-thermal-model/theoretical_documentation/overview/)

## License

This project is licensed under the Mozilla Public License, version 2.0 - see
[LICENSE](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/LICENSE)
for details.

## Contributing

We welcome contributions! Please see
[CONTRIBUTING.md](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/CONTRIBUTING.md)
and
[CODE_OF_CONDUCT.md](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/CODE_OF_CONDUCT.md)
for guidelines.

## Support

For questions and support, please see [SUPPORT.md](https://github.com/alliander-opensource/transformer-thermal-model/blob/main/SUPPORT.md).
