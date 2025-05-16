<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Model input

The thermal model requires four inputs:

1. Relevant transformer specifications
2. Load profile
3. Ambient temperature profile
4. Initial value hot-spot and top-oil temperature

## Relevant transformer specifications

Below are all transformer-specific properties that influence the thermal behavior of the transformer:

### Nominal secondary current

- **Unit:** Ampère.

- **Description:** The nominal current on the secondary side of the transformer. When the transformer carries this
current on the secondary side, we refer to it as 100% loading of the transformer.

- **Source:** Nameplate on the transformer or Factory Acceptance Test (FAT) report.

- **Fallback/guarantee value:** n/a (always known)

### No-load loss

- **Unit:** Watt.
- **Description:** The no-load loss refers to the losses within a transformer that are always present when the
transformer is energized, even when there is no load connected to the transformer. These losses occur in the core of the
transformer, which is magnetized by the alternating current. For this reason, they are also called _**iron losses**_ or
_**core losses**_. These losses mostly translate into heat, making this parameter an important thermal property.
- **Source:**  Factory Acceptance Test (FAT) report: during these tests, a no-load test is performed to determine these
losses. This test is conducted individually for each transformer.
- **Fallback/guarantee value:** This value is usually known.

### Short-circuit loss

- **Unit:** Watt.
- **Description:** The short-circuit loss is the counterpart of the no-load loss. This type of loss is load-dependent
and represents the losses in the windings due to resistance. For this reason, they are also called _**copper losses**_.
These losses are quadratically dependent on the current.
- **Source:** Factory Acceptance Test (FAT) report: during these tests, a short-circuit test is performed to determine
the short-circuit losses at a nominal short-circuit current. This test is conducted individually for each transformer.
- **Fallback/guarantee value:** This value is usually known.

### Top-oil temperature rise

- **Unit:** Kelvin.
- **Description:** The top-oil temperature is the temperature at the top of the transformer. During a heating test of
the transformer, this temperature is measured under nominal and constant load. The top-oil temperature rise indicates
how much the temperature of the top-oil rises above the ambient temperature when it stabilizes under these nominal
conditions.
- **Source:** Factory Acceptance Test (FAT) report: during these tests, a temperature-rise test is performed on the
transformer. Often, this test is only performed for one transformer per series. If the information is not available for
a specific transformer, a temperature-rise test of a comparable transformer can be used.

- **Fallback/guarantee value:** If no temperature-rise test is available for any transformer in the series, the
guaranteed value of the top-oil temperature rise can be used. For all modern transformers, this is 60 Kelvin. For very
old transformers, this can sometimes fall back to 55 or 50 Kelvin. These guaranteed values can always by found on the
type plate.

### Winding-oil gradient

- **Unit:** Kelvin.
- **Description:** To determine the temperature drop between the winding and the oil, the winding-oil gradient is an
important thermal property of a transformer. This can also be determined during a temperature-rise test by taking the
difference between the average oil temperature rise and the average winding temperature rise.
- **Source:** Factory Acceptance Test (FAT) report: during these tests, a temperature-rise test is performed on the
transformer. Often, this test is only performed for one transformer per series. If the information is not available for
a specific transformer, a comparable transformer can be used.
- **Fallback/guarantee value:** The average oil temperature rise is not always known from a heating test. In that case,
the average oil temperature rise can be estimated at 80% of the top-oil temperature rise. If the average winding
temperature rise is not known, the guarantee value can be used. For all modern transformers, this is 65 Kelvin. For very
old transformers, this can sometimes fall back to 60 or 55 Kelvin. Assuming a 60 Kelvin top-oil temperature rise and a
65 Kelvin average winding temperature rise, a gradient of 17 Kelvin can be assumed
(gradient = (average winding temperature) - 0.8*(top-oil temperature)).

### Hot-spot factor

- **Unit:** unitless.
- **Description:** The hot-spot factor, together with the gradient, indicates the difference between the hot-spot
temperature and the top-oil temperature.

- **Source:** Factory Acceptance Test (FAT) report: during these tests, a temperature-rise test is performed on the
transformer. Often, this test is only performed for one transformer per series. If the information is not available for
a specific transformer, a comparable transformer can be used.

- **Fallback/guarantee value:** The hot-spot factor is often not known from the temperature-rise test. In that case, the
worst-case hot-spot factor of 1.3 can be used. It is generally expected that the hot-spot factor ranges between 1.1 and
1.3. Whether these are indeed the most extreme limits is not certain. It should be noted that for older transformers,
the hot-spot factor can be much higher. This is due to the use of solid wire, where eddy current losses in the upper
regions of the windings are higher than with modern CTC wire (= continuously transposed conductor).

- **Hot-spot factor calibration**: The hot-spot factor can be calibrated using the model. For more information, see
[Hot-spot factor calibration](hotspot_calibration.md).

### Cooling type

- **Unit:** n/a
- **Description:** The transformer can generally be cooled in two ways:

  - **ONAN**: _Oil Natural, Air Natural_. In this type of transformer, both the flow of the oil and the flow of the
  air along the radiators are natural. The oil is heated, rises, and is pushed into the radiators without actively
  forcing this flow to appear. The oil then cools in the radiators, sinks down, and is pushed into the oil tank. The air
  between the radiators is heated and rises. This creates a natural airflow along the radiators.
  - **ONAF**: _Oil Natural, Air Forced._ The difference with ONAN is that fans are placed under the radiators. These
  force an active airflow between the radiators. This allows the oil to more easily transfer its heat to the
  environment.

- **Source:** Nameplate on the transformer.

- **Fallback/guarantee value:** n/a

### Ambient temperature surcharge

- **Unit:** Kelvin.
- **Description:** This parameter is used differently for distribution and power transformers:
  - **Power transformers**: For this type of transformer it is expected to be placed outside. In that case, this
    parameter should be set to 0 and does nothing. In some cases, however, power transformers are placed inside. In that
    situation, it is more difficult for the heat to escape the surroundings of the transformer. Therefore, a 10 Kelvin
    temperature surcharge can be filled in here, which will be added to the ambient temperature to compensate for this
    phenomenon. Other values can of course also be chosen.
  - **Distribution transformers**: Distribution transformers are (in the Netherlands) always placed inside. Still, a
    distinction can be made between compact and normal stations. As the name suggests, compact stations have a lot less
    free space, which means the surroundings heat up a lot quicker. To take this phenomenon into account a temperature
    surcharge can be added to the rated top-oil temperature rise, which is also a transformer specification.
- **Source:**: n/a
- **Fallback/guarantee value:** n/a

### Relevant constants for winding and oil

The transformer model uses several constants that characterize the thermal behavior of the windings and the oil in the
transformer. Values for these constants can be experimentally determined. The loading guide also recommends some
conservative values for these constants (IEC 60076-7, Table 4):

- _**Oil exponent x:**_ Determines how the top-oil temperature depends on the load level and the losses of the
transformer.

- _**Winding exponent y**_: Determines how the gradient depends on the load level of the transformer.

- _**Oil constant $k_{11}$**_: Empirical model parameter.

- _**Winding constant $k_{21}$**_: Empirical model parameter.

- _**Winding constant $k_{22}$**_: Empirical model parameter.

- _**Oil time constant $τ_o$**_:  the tau time in minutes for the oil. This number governs the rate at which the oil
reaches its final temperature.

- _**Winding time constant $τ_w$**_: the tau time in minutes for the winding. This number governs the rate at with which
the windings reach their final temperature.
