<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Specifications

## Transformer specifications

A transformer object in our package needs to be initiated using a set of
specifications. A user will typically only interact with
`UserTransformerSpecifications`. The `DefaultTransformerSpecifications` are used
to set the [`Transformer.defaults`][1] values. The `TransformerSpecifications`
is created to make sure the `UserTransformerSpecifications` and the
`DefaultTransformerSpecifications` are neatly combined.

::: transformer_thermal_model.schemas.specifications.transformer
    options:
        summary: true
        heading_level: 3

### Transformer component specifications

::: transformer_thermal_model.schemas.specifications.transformer_component
    options:
        summary: true
        heading_level: 4

[1]: ./transformer.md#transformer_thermal_model.transformer.Transformer.defaults
