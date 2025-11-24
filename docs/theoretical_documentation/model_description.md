<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Model description

## Relevant temperatures

Inside a transformer, there are many different components, each with its own
thermal behavior. This makes a transformer thermally a very complex system. To
say something about the thermal behavior of a transformer, it can be simplified by only looking at the oil temperature and
the winding temperature. With this simplifications there are a few specific temperatures and parameters that are
important to consider:

- **Top-oil temperature** - temperature of the oil at the very top of the transformer. As this is generally also the
highest oil temperature in the transformer, it is one of the two temperatures that is modelled with this package.

- **Oil temperature outflow windings** - temperature of the oil at the top of
  the windings.

- **Average oil temperature** - temperature of the oil in the middle of the
  tank. It is assumed that there is a linear relationship between the height in
  the tank and the oil temperature. For this reason, the temperature of the oil in the middle of the tank is equated to the
  average oil temperature in the tank.

- **Oil temperature inflow windings** - temperature of the oil at the bottom
  of the windings.

- **Average winding temperature** - winding temperature in the middle (in
  terms of height) of the transformer. This temperature is often determined by a
  resistance measurement.

- **Gradient** - temperature difference between the _average oil temperature_ and the _average winding temperature_.

- **Hot-spot temperature** - Temperature of the windings at the hottest point.
  This point is usually just below the top of the windings. Together with the top-oil temperature, this is one of the
  two temperatures that is modelled with this package.

- **Hot-spot factor** - It is assumed that the difference between the _top-oil
  temperature_ and the _hot-spot temperature_ is greater than the difference
  between the _average oil temperature_ and the _average winding temperature_
  (i.e., the gradient). This is quantified with the _Hot-spot factor_. This
  factor, multiplied by the _gradient_, indicates the difference between the _Hot-spot temperature_ and
  the _top-oil temperature_.

The thermal model can model the **top-oil temperature** and the **hot-spot
temperature** based on the thermal properties of the transformer. These are
the most indicative temperatures because they indicate the highest temperatures
for the oil and the windings. Additionally, the standard (IEC 60076-7) also
prescribes temperature limits for these two quantities.

## Model equations

As discussed in the previous section, there are different specific locations in the transformer where the temperature
can be determined. This package focuses on modelling the top-oil and hot-spot temperature as these indicate the highest
oil and winding temperatures, respectively. The equations below describe how these two temperatures are modelled. In
essence, package uses a recursive method where the temperature at the next time step is calculated using the current
temperature. This means an initial value has to be set (or the package initializes the transformer at ambient
temperatures).

### Top-oil temperature

The model calculates the top-oil temperature at time $t$ as follows:

$$
\theta_\text{o}[t] =
    \theta_\text{o}[t-1] +
    \left[
        \theta_\text{a}[t] + \Delta\theta_\text{or} \cdot
        \left[
            \frac{1+R \cdot {K[t]}^2}{1 + R}
        \right]^x -
        \theta_\text{o}[t-1]
    \right] \cdot
    \left[
        1 - \exp(- \frac{\rm d t}{\tau_\text{o}k_{11}})
    \right],
$$

where:

- **$\theta_{\rm o}[t]$**: top-oil temperature at time step _t;_
- **$\theta_{\rm o}[t-1]$**: top-oil temperature at the previous timestep;
- **$\theta_{a}[t]$**: ambient temperature at time step _t;_
- **$Δθ_{or}$**: top-oil temperature rise (from the temperature-rise-test);
- **$R$**: ratio of short-circuit and no-load loss;
- **$K[t]$**: load level as a percentage of nominal at time step _t;_
- **$x$**: oil exponent;
- **$dt$**: time step size in minutes;
- **$τ_{\rm o}$**: oil time constant;
- **$k_{11}$**: oil constant.

The equation for the top-oil temperature consists of several parts. First, the top-oil temperature from the previous
time step is taken as the starting point. Then, it is determined what the temperature of the oil would converge to under
the current load level and ambient temperature. The difference between this final temperature and the top-oil
temperature at the previous time step is calculated in the middle section of the formula (between the large square
brackets). Because the transformer does not immediately reach the final temperature but reacts with a certain inertia
(according to Newton's heating/cooling law), a delaying part is added to the equation in the rightmost square brackets.
This inertia is dependent on the oil time constant.

### Hot-spot temperature

Based on formula (12), (15) and  (16) from IEC-60076-7-2018, the hot-spot temperature rise above the top-oil temperature
 at time _t_ can be calculated as follows:
$$
\Delta\theta_{\text{h}}[t] = \Delta\theta_{\text{h1}}[t] + \Delta\theta_{\text{h2}}[t]
$$
where
$$
\Delta \theta_{h1}[t] =k_{21}Hg_rK[t]^y + \{\Delta \theta_{h1}[t-1] - k_{21}Hg_rK[t]^y\}\times e^{(-\Delta t)/(k_{22}\times\tau_w)}
$$
and
$$
\Delta \theta_{h2} [t] = (k_{21} -1)Hg_rK[t]^y + \{\Delta \theta_{h2}[t-1] - (k_{21} -1)Hg_rK[t]^y\}\times e^
{(-\Delta t)/(\tau_0 / k_{22})}
$$

where:

- **$\Delta\theta_{\text{h}}[t]$**: hot-spot temperature rise at time step _t;_
- **$\Delta\theta_{\text{h}}[t-1]$**: hot-spot temperature rise at the previous time step;
- **$H$**: hot-spot factor;
- **$gr$**: winding-oil gradient (from the temperature-rise-test);
- **$K[t]$**: load level as a percentage of nominal at time step _t;_
- **$y$**: winding exponent;
- **$k_{21}$**: winding constant;
- **$k_{22}$**: winding constant;
- **$\Delta t$**: time step size in minutes;
- **$\tau_{\text{w}}$**: winding time constant;
- **$\tau_{\text{\rm o}}$**: oil time constant.

When the hot-spot temperature rise and the top-oil temperature at time t are known, the hot-spot temperature can simply
be determined as:

$$
\theta_{\text{h}}[t] = \theta_{\text{\rm o}}[t] + \Delta\theta_{\text{h}}[t]
$$

The mentioned equations have a memory up to 1 time step back in time. This means that for a given load profile and
ambient temperature profile, the temperature profile of the top-oil and hot-spot are calculated sequentially.
