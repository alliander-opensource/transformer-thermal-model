<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Hot-spot factor calculation

When the hot-spot factor is uncertain or unknown, it can be derived from the thermal design parameters. The approach is based on the thermal limits defined in the IEC 60076-1 paragraph 4.2 and IEC 60076-2 Table 1 (see also [Thermal limits](temperature_limits.md)) and derives the hot-spot factor from the steady-state temperature conditions associated with nominal load.

For transformers with normal paper insulation, IEC 60076 specifies a maximum hot-spot temperature of 98°C when the load is 100% and the ambient temperature is 20°C. This corresponds to a hot-spot temperature rise above ambient of:

Δθ_h = 98°C - 20°C = 78 K

At nominal loading, the hot-spot temperature rise can also be expressed as:

Δθ_h = Δθ_or + H · g_r

where:

- Δθ_h is the hot-spot temperature rise above ambient temperature [K]
- Δθ_or is the rated top-oil temperature rise above ambient temperature [K]
- H is the hot-spot factor [-]
- g_r is the rated winding-to-oil gradient [K]

Substituting Δθ_h = 78 K and solving for the hot-spot factor yields:

H = (78 K - Δθ_or) / g_r
 
The calculated hot-spot factor represents the value required to reach a steady-state hot-spot temperature of 98°C at nominal load and an ambient temperature of 20°C.

The resulting hot-spot factor is then clipped between the values 1.1 and 1.3 as these are considered realistic values
for the hot-spot factor. Note that it is also possible to choose other values for the end temperature and the hot-spot
factor bounds.

This method is intended for power transformers only and should not be applied to distribution transformers.



