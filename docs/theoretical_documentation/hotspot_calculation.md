<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Hot-spot factor calculation

When the hot-spot factor is uncertain or unknown, it can be derived from the
thermal design parameters. The approach is based on the thermal limits defined
in IEC 60076-1 paragraph 4.2 and IEC 60076-2 Table 1 (see also [Thermal
limits](temperature_limits.md)) and derives the hot-spot factor from the
steady-state temperature conditions associated with nominal load.

At nominal loading, the hot-spot temperature rise can be expressed as:

Δθ_h = Δθ_or + H · g_r

where:

- Δθ_h is the hot-spot temperature rise above ambient temperature [K]
- Δθ_or is the rated top-oil temperature rise above ambient temperature [K]
- H is the hot-spot factor [-]
- g_r is the rated winding-to-oil gradient [K]

Assuming that the hot-spot temperature rise reaches a specified steady-state

limit Δθ_h,lim, the hot-spot factor can be calculated as:

H = (Δθ_h,lim - Δθ_or) / g_r

The calculated hot-spot factor represents the value required to reach the
specified steady-state hot-spot temperature rise limit at nominal load.

According to IEC 60076-7, a hot-spot temperature rise limit of 78 K can be used
for transformers with normal Kraft insulation paper. For transformers with
thermally upgraded paper, a value of 90 K can be used. For normal Kraft paper,
the equation therefore becomes:

H = (78 K - Δθ_or) / g_r

The resulting hot-spot factor is then clipped between the values 1.1 and 1.3
as these are considered realistic values
for the hot-spot factor. Note that it is also possible to choose other values
for the temperature-rise limit and the hot-spot factor bounds.

This method is intended for power transformers only and should not be applied
to distribution transformers.
