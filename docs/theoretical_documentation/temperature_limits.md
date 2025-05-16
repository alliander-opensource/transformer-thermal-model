<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Thermal limits

When modelling the hot-spot and top-oil temperature, it is also important to know what temperatures are considered
acceptable. Below, a brief description can be found of different temperatures prescribed by the loading guide.

## Static loadability

In the standards (IEC 60076-1 paragraph 4.2 & IEC 60076-2 Table 1), temperature limits are described for the
environment, oil, and windings that must not be exceeded under continuous load
with the assigned power.

- **Ambient temperature:**
  - Always between -25°C and +40°C;
  - The average temperature in the hottest month is less than +30°C;
  - The annual average does not exceed +20°C.
- **Transformer temperature:**
  - The top-oil temperature rise is less than 60 Kelvin;
  - The average winding temperature rise is less than 65 Kelvin;
  - The hot-spot temperature is less than:
    - **Normal paper**: 98°C (78 Kelvin temperature rise);
    - **Thermally Upgraded Paper (TUP)**: 110°C (90 Kelvin temperature rise).

## Cyclic loadability

In the loading guide, guidelines are given regarding cyclic
loadability (IEC 60076-7, chapter 7, table 2). A distinction is made between:

- _**Normal cyclic loadability**_: a loadability that can always be maintained
  with a cyclic profile.

  - Limit top-oil temperature: 105 °C
  - Limit hot-spot temperature: 120 °C
  - Limit current load: 150% (< 100MVA), 130% (> 100 MVA)

- _**Long-term emergency load**_: a loadability that can be maintained for
  several days with a cyclic profile.
  - Limit top-oil temperature: 115 °C
  - Limit hot-spot temperature: 140 °C
  - Limit current load: 180% (< 10MVA), 150% (10 - 100 MVA) and 130% (> 100 MVA)

- _**Short-term emergency load**_: a loadability that can be maintained for
  several hours with a cyclic profile.
  - Limit top-oil temperature: 115 °C
  - Limit hot-spot temperature: 160 °C
  - Limit current load: 200% (< 10MVA), 180% (10 - 100 MVA) and 150% (> 100 MVA)
  