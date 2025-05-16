# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.hot_spot_calibration.calibrate_hotspot_factor import calibrate_hotspot_factor
from transformer_thermal_model.schemas import UserTransformerSpecifications
from transformer_thermal_model.transformer import PowerTransformer


@pytest.fixture
def trafo_specs_onan_uncalibrated():
    """Fixture for the specifications of an uncalibrated ONAF transformer.

    Specific values have been used to be able to predict the outcome of the calibration.
    """
    return UserTransformerSpecifications(
        no_load_loss=12590,
        top_oil_temp_rise=52.3,
        load_loss=69867,
        nom_load_sec_side=1050,
        winding_oil_gradient=15.6,
        amb_temp_surcharge=0,
        hot_spot_fac=None,
    )


@pytest.fixture
def trafo_specs_onaf_uncalibrated():
    """Fixture for the specifications of an uncalibrated ONAN transformer.

    Specific values have been used to be able to predict the outcome of the calibration.
    """
    return UserTransformerSpecifications(
        no_load_loss=12590,
        top_oil_temp_rise=51.3,
        load_loss=157200,
        nom_load_sec_side=1575,
        winding_oil_gradient=22.6,
        amb_temp_surcharge=0,
        hot_spot_fac=None,
    )


@pytest.fixture
def transformer_onan_uncalibrated(trafo_specs_onan_uncalibrated):
    """Fixture for the uncalibrated ONAN transformer."""
    return PowerTransformer(
        cooling_type=CoolerType.ONAN,
        user_specs=trafo_specs_onan_uncalibrated,
    )


@pytest.fixture
def transformer_onaf_uncalibrated(trafo_specs_onaf_uncalibrated):
    """Fixture for the uncalibrated ONAF transformer."""
    return PowerTransformer(
        cooling_type=CoolerType.ONAF,
        user_specs=trafo_specs_onaf_uncalibrated,
    )


def test_hot_spot_factor_calibration_onan(transformer_onan_uncalibrated):
    """Test the calibration of the HS factor for an ONAN transformer."""
    transformer_calibrated = calibrate_hotspot_factor(
        uncalibrated_transformer=transformer_onan_uncalibrated,
        hot_spot_limit=98,
        ambient_temp=20,
        hot_spot_factor_min=1.1,
        hot_spot_factor_max=1.3,
    )

    assert transformer_calibrated.specs.hot_spot_fac == pytest.approx(1.3)
    assert transformer_calibrated.specs.amb_temp_surcharge == transformer_onan_uncalibrated.specs.amb_temp_surcharge


def test_hotspot_fac_calibration_onaf(transformer_onaf_uncalibrated):
    """Test the calibration of the HS factor for an ONAN transformer."""
    transformer_calibrated = calibrate_hotspot_factor(
        uncalibrated_transformer=transformer_onaf_uncalibrated,
        hot_spot_limit=98,
        ambient_temp=20,
        hot_spot_factor_min=1.1,
        hot_spot_factor_max=1.3,
    )

    assert transformer_calibrated.specs.hot_spot_fac == pytest.approx(1.18)
    assert transformer_calibrated.specs.amb_temp_surcharge == transformer_onaf_uncalibrated.specs.amb_temp_surcharge


def test_that_hot_spot_factor_calibration_caps_at_minimal_value(transformer_onaf_uncalibrated):
    """Test that the hot-spot factor calibration caps at the minimal value by setting the winding oil gradient high."""
    transformer_onaf_uncalibrated.specs.winding_oil_gradient = 30

    transformer_calibrated = calibrate_hotspot_factor(
        uncalibrated_transformer=transformer_onaf_uncalibrated,
        hot_spot_limit=98,
        ambient_temp=20,
        hot_spot_factor_min=1.1,
        hot_spot_factor_max=1.3,
    )

    assert transformer_calibrated.specs.hot_spot_fac == pytest.approx(1.1)
    assert transformer_calibrated.specs.amb_temp_surcharge == transformer_onaf_uncalibrated.specs.amb_temp_surcharge


def test_that_hot_spot_factor_fails_with_wrong_limits(transformer_onaf_uncalibrated):
    """Test that the hot-spot factor calibration raises an error if the bounds are not defined correctly."""
    with pytest.raises(
        ValueError, match="The upper bound cannot be smaller than the lower bound of the hot-spot factor limits."
    ):
        calibrate_hotspot_factor(
            uncalibrated_transformer=transformer_onaf_uncalibrated,
            hot_spot_limit=98,
            ambient_temp=20,
            hot_spot_factor_min=5,
            hot_spot_factor_max=1,
        )
