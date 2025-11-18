# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.hot_spot_calibration.calibrate_hotspot_factor import calibrate_hotspot_factor
from transformer_thermal_model.schemas import (
    UserThreeWindingTransformerSpecifications,
    UserTransformerSpecifications,
    WindingSpecifications,
)
from transformer_thermal_model.transformer import PowerTransformer, ThreeWindingTransformer


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
def threewind_specs_HS_13():
    """Fixture for the specifications of a threewind transformer with known hotspotfactor of 1.3."""
    return UserThreeWindingTransformerSpecifications(
        no_load_loss=33930,
        amb_temp_surcharge=0,
        lv_winding=WindingSpecifications(nom_load=1300, winding_oil_gradient=11.8, time_const_winding=7, nom_power=25),
        mv_winding=WindingSpecifications(nom_load=1045, winding_oil_gradient=11.4, time_const_winding=7, nom_power=95),
        hv_winding=WindingSpecifications(nom_load=366, winding_oil_gradient=11.8, time_const_winding=7, nom_power=95),
        load_loss_hv_lv=102100,
        load_loss_hv_mv=259000,
        load_loss_mv_lv=100300,
    )


@pytest.fixture
def threewind_specs_HS_11():
    """Fixture for the specifications of a threewind transformer with known hotspotfactor of 1.1."""
    return UserThreeWindingTransformerSpecifications(
        no_load_loss=51590,
        amb_temp_surcharge=0,
        lv_winding=WindingSpecifications(nom_load=1560, winding_oil_gradient=20.0, time_const_winding=7, nom_power=30),
        mv_winding=WindingSpecifications(nom_load=1100, winding_oil_gradient=16.5, time_const_winding=7, nom_power=100),
        hv_winding=WindingSpecifications(nom_load=385, winding_oil_gradient=22.1, time_const_winding=7, nom_power=100),
        load_loss_hv_lv=142300,
        load_loss_hv_mv=462700,
        load_loss_mv_lv=135800,
    )


@pytest.fixture
def threewind_specs_HS_12():
    """Fixture for the specifications of a threewind transformer with known hotspotfactor of 1.19."""
    return UserThreeWindingTransformerSpecifications(
        no_load_loss=34000,
        amb_temp_surcharge=0,
        lv_winding=WindingSpecifications(
            nom_load=1300,
            winding_oil_gradient=15.0,
            time_const_winding=7,
            nom_power=25,
        ),
        mv_winding=WindingSpecifications(
            nom_load=1045,
            winding_oil_gradient=15.5,
            time_const_winding=7,
            nom_power=95,
        ),
        hv_winding=WindingSpecifications(
            nom_load=366,
            winding_oil_gradient=15.0,
            time_const_winding=7,
            nom_power=95,
        ),
        load_loss_hv_lv=95000,
        load_loss_hv_mv=245000,
        load_loss_mv_lv=95000,
    )


@pytest.fixture
def transformer_onan_uncalibrated(trafo_specs_onan_uncalibrated: UserTransformerSpecifications):
    """Fixture for the uncalibrated ONAN transformer."""
    return PowerTransformer(
        cooling_type=CoolerType.ONAN,
        user_specs=trafo_specs_onan_uncalibrated,
    )


@pytest.fixture
def transformer_onaf_uncalibrated(trafo_specs_onaf_uncalibrated: UserTransformerSpecifications):
    """Fixture for the uncalibrated ONAF transformer."""
    return PowerTransformer(
        cooling_type=CoolerType.ONAF,
        user_specs=trafo_specs_onaf_uncalibrated,
    )


@pytest.fixture
def threewind_transformer_HS_11(threewind_specs_HS_11: UserThreeWindingTransformerSpecifications):
    """Fixture for the threewind transformer with known hotspotfactor of 1.1."""
    return ThreeWindingTransformer(user_specs=threewind_specs_HS_11, cooling_type=CoolerType.ONAF)


@pytest.fixture
def threewind_transformer_HS_12(threewind_specs_HS_12: UserThreeWindingTransformerSpecifications):
    """Fixture for the threewind transformer with known hotspotfactor of 1.19."""
    return ThreeWindingTransformer(user_specs=threewind_specs_HS_12, cooling_type=CoolerType.ONAF)


@pytest.fixture
def threewind_transformer_HS_13(threewind_specs_HS_13: UserThreeWindingTransformerSpecifications):
    """Fixture for the threewind transformer with known hotspotfactor of 1.3."""
    return ThreeWindingTransformer(user_specs=threewind_specs_HS_13, cooling_type=CoolerType.ONAF)


def test_hot_spot_factor_calibration_onan(transformer_onan_uncalibrated: PowerTransformer):
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


def test_hotspot_fac_calibration_onaf(transformer_onaf_uncalibrated: PowerTransformer):
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


def test_that_hot_spot_factor_calibration_caps_at_minimal_value(transformer_onaf_uncalibrated: PowerTransformer):
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


def test_that_hot_spot_factor_fails_with_wrong_limits(transformer_onaf_uncalibrated: PowerTransformer):
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


def test_hot_spot_factor_calibration_threewind_HS11(threewind_transformer_HS_11: ThreeWindingTransformer):
    """Test the calibration of the HS factor for the threewind transformer with known hotspotfactor 1.1."""
    transformer_calibrated = calibrate_hotspot_factor(
        uncalibrated_transformer=threewind_transformer_HS_11,
        hot_spot_limit=98,
        ambient_temp=20,
        hot_spot_factor_min=1.1,
        hot_spot_factor_max=1.3,
    )

    assert transformer_calibrated.specs.lv_winding.hot_spot_fac == pytest.approx(1.1)
    assert transformer_calibrated.specs.amb_temp_surcharge == threewind_transformer_HS_11.specs.amb_temp_surcharge


def test_hot_spot_factor_calibration_threewind_HS12(threewind_transformer_HS_12: ThreeWindingTransformer):
    """Test the calibration of the HS factor for the threewind transformer with known hotspotfactor 1.16."""
    transformer_calibrated = calibrate_hotspot_factor(
        uncalibrated_transformer=threewind_transformer_HS_12,
        hot_spot_limit=98,
        ambient_temp=20,
        hot_spot_factor_min=1.1,
        hot_spot_factor_max=1.3,
    )

    assert transformer_calibrated.specs.lv_winding.hot_spot_fac == pytest.approx(1.16)
    assert transformer_calibrated.specs.amb_temp_surcharge == threewind_transformer_HS_12.specs.amb_temp_surcharge


def test_hot_spot_factor_calibration_threewind_HS13(threewind_transformer_HS_13: ThreeWindingTransformer):
    """Test the calibration of the HS factor for the threewind transformer with known hotspotfactor 1.3."""
    transformer_calibrated = calibrate_hotspot_factor(
        uncalibrated_transformer=threewind_transformer_HS_13,
        hot_spot_limit=98,
        ambient_temp=20,
        hot_spot_factor_min=1.1,
        hot_spot_factor_max=1.3,
    )

    assert transformer_calibrated.specs.lv_winding.hot_spot_fac == pytest.approx(1.3)
    assert transformer_calibrated.specs.amb_temp_surcharge == threewind_transformer_HS_13.specs.amb_temp_surcharge


def test_that_hot_spot_factor_fails_with_wrong_limits_threewind(threewind_transformer_HS_11: ThreeWindingTransformer):
    """Test that the hot-spot factor calibration raises an error if the bounds are not defined correctly.

    Test for the threewind transformer.
    """
    with pytest.raises(
        ValueError, match="The upper bound cannot be smaller than the lower bound of the hot-spot factor limits."
    ):
        calibrate_hotspot_factor(
            uncalibrated_transformer=threewind_transformer_HS_11,
            hot_spot_limit=98,
            ambient_temp=20,
            hot_spot_factor_min=5,
            hot_spot_factor_max=1,
        )


def test_that_hot_spot_factor_calibration_caps_at_minimal_value_threewind(
    threewind_transformer_HS_13: ThreeWindingTransformer,
):
    """Test that the hot-spot factor calibration caps at the minimal value by setting the winding oil gradient high."""
    threewind_transformer_HS_13.specs.lv_winding.winding_oil_gradient = 30
    threewind_transformer_HS_13.specs.mv_winding.winding_oil_gradient = 30
    threewind_transformer_HS_13.specs.hv_winding.winding_oil_gradient = 30

    transformer_calibrated = calibrate_hotspot_factor(
        uncalibrated_transformer=threewind_transformer_HS_13,
        hot_spot_limit=98,
        ambient_temp=20,
        hot_spot_factor_min=1.1,
        hot_spot_factor_max=1.3,
    )

    assert transformer_calibrated.specs.lv_winding.hot_spot_fac == pytest.approx(1.1)
    assert transformer_calibrated.specs.amb_temp_surcharge == threewind_transformer_HS_13.specs.amb_temp_surcharge
