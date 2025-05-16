<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Potential model improvements

Our team is continuously working on improving the model. Below some potential model improvements are described.

## Model accuracy at larger timestep sizes

Currently, we trust the accuracy of the model, as long as a time step size of 15 minutes or smaller are used for the
input profiles. Larger time step sizes could potentially cause issues with the hotspot temperature modelling. Note that
this model is designed to work specifically for a constantly varying load profile, as is expected to appear in real-life
situations. When modelling different scenario's, such as step profiles, it is known that this model might not perform
accurately. We are currently looking into a solution for these accuracy and stability issues.

## Variable cooling stage for ONAF transformers

Currently, our model is only able to model an ONAF transformer as if the fans are always on. In reality the fans can be
turned on only at a certain temperature, even in multiple stages. To take this into account, it is proposed to allow
parameters that are dependent on ONAN/ONAF cooling dependent on top-oil temperature. When this temperature reaches a
certain threshold, the parameters will gradually shift to the ONAF values.

## Tap-dependent load-losses

Only a single value for load losses is used in the thermal model. It is possible, however, to make this dependent
on the tap position that the transformer is in at that moment. This will make the loss calculation slightly more
accurate, which also means a more accurate thermal model.

## Influence of the installation condition; outdoor vs. indoor temperature

The loadability of an asset is largely determined by the environmental condition. Currently there is no accurate method
to deal with the influence of the installation condition on the temperature of the transformer. Some research could
prove useful for modelling for example indoor transformers more accurately.
