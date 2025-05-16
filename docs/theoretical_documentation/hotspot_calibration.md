<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Hot-spot factor calibration

When the hot-spot factor is uncertain or unknown, a calibration can be performed to determine it. Note that this method
for finding the hot-spot factor is designed for power transformers, and should therefore not be used for distribution
transformers. This calibration is based on the static limits that are described in the IEC 60076-1 paragraph 4.2 and IEC
60076-2 Table 1 (see also [Thermal limits](temperature_limits.md)). For normal paper, it is assumed that the hot-spot
temperature reaches 98°C when the load is 100% and the ambient temperature is 20°C.

During the calibration, a constant load profile of 100% and a constant ambient temperature profile of 20°C is inserted
into the model until a stable end temperature is reached for the transformer hot-spot. Next, the hot-spot factor is adjusted
until this end temperature is 98°C.

The resulting hot-spot factor is then clipped between the values 1.1 and 1.3 as these are considered realistic values
for the hot-spot factor. Note that it is also possible to choose other values for the end temperature and the hot-spot
factor bounds.
