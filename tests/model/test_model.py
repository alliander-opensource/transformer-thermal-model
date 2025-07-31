# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pandas as pd
import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.model import Model
from transformer_thermal_model.schemas import UserTransformerSpecifications
from transformer_thermal_model.toolbox.temp_sim_profile_tools import create_temp_sim_profile_from_df
from transformer_thermal_model.transformer import PowerTransformer
from transformer_thermal_model.transformer.threewinding import ThreeWindingTransformer


@pytest.fixture
def transformer(default_user_trafo_specs) -> PowerTransformer:
    """Create a transformer object with 0 losses."""
    zero_loss_transformer_specs = default_user_trafo_specs.model_copy(
        update={
            "hot_spot_fac": 1.3,
            "no_load_loss": 0,
            "amb_temp_surcharge": 0,
        }
    )
    transformer = PowerTransformer(user_specs=zero_loss_transformer_specs, cooling_type=CoolerType.ONAN)
    return transformer


def test_temp_rise_with_zero_load(transformer):
    """Test if the temperature rise is zero when the load and losses are zero."""
    profile = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2021-01-01 00:00:00", "2021-01-01 01:00:00", "2021-01-01 02:00:00"]),
            "load": [0, 0, 0],
            "ambient_temperature": [5, 5, 5],
        }
    )

    model = Model(temperature_profile=create_temp_sim_profile_from_df(profile), transformer=transformer)
    result = model.run().convert_to_dataframe()

    assert result["top_oil_temperature"].equals(pd.Series([5.0, 5.0, 5.0], index=profile["timestamp"]))
    assert result["hot_spot_temperature"].equals(pd.Series([5.0, 5.0, 5.0], index=profile["timestamp"]))


def test_temp_rise_with_losses_and_zero_load(onan_power_transformer):
    """Test if the temperature rise is non zero when the load is zero but the losses are not."""
    profile = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2021-01-01 00:00:00",
                    "2021-01-01 01:00:00",
                    "2021-01-01 02:00:00",
                    "2021-01-02 02:00:00",
                    "2021-01-03 02:00:00",
                ]
            ),
            "load": [0, 0, 0, 0, 0],
            "ambient_temperature": [5, 5, 5, 5, 5],
        }
    )
    model = Model(temperature_profile=create_temp_sim_profile_from_df(profile), transformer=onan_power_transformer)
    result = model.run()
    top_oil_temp = np.array(result.top_oil_temp_profile)
    hot_spot_temp = np.array(result.hot_spot_temp_profile)
    expected_temps = [
        25.0,
        31.22874909,
        34.74623658,
        39.30968576,
        39.30969081,
    ]
    assert top_oil_temp == pytest.approx(expected_temps, rel=1e-6)
    assert hot_spot_temp == pytest.approx(expected_temps, rel=1e-6)


def test_temp_rise_to_ambient_temperature(transformer):
    """Test if the temperature of the transformer rises to the ambient temperature when the load is zero."""
    # A timestep of 1 year is used to make sure the temperature rises to the ambient temperature
    profile = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2021-01-01 00:00:00", "2022-01-01 00:00:00", "2023-01-01 02:00:00"]),
            "load": [0, 0, 0],
            "ambient_temperature": [20, 30, 50],
        }
    )

    model = Model(temperature_profile=create_temp_sim_profile_from_df(profile), transformer=transformer)
    result = model.run().convert_to_dataframe()

    assert result["top_oil_temperature"].equals(pd.Series([20.0, 30.0, 50.0], index=profile["timestamp"]))
    assert result["hot_spot_temperature"].equals(pd.Series([20.0, 30.0, 50.0], index=profile["timestamp"]))


def test_temp_rise_zero_timesteps(transformer):
    """Test if the temperature rise is zero when the timesteps are zero."""
    profile = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2021-01-01 00:00:00", "2021-01-01 00:00:00", "2021-01-01 00:00:00"]),
            "load": [100, 100, 100],
            "ambient_temperature": [20, 20, 20],
        }
    )

    model = Model(temperature_profile=create_temp_sim_profile_from_df(profile), transformer=transformer)
    result = model.run().convert_to_dataframe()

    assert result["top_oil_temperature"].equals(pd.Series([20.0, 20.0, 20.0], index=profile["timestamp"]))
    assert result["hot_spot_temperature"].equals(pd.Series([20.0, 20.0, 20.0], index=profile["timestamp"]))


def test_good_result_with_large_time_steps(transformer):
    """Test if the temperature rise goes to expected value when using timesteps of one month.

    For large timesteps, and nominal load, the top-oil temperature should rise by the top-oil temperature rise,
    and the hot-spot temperature should rise by the top-oil temperature rise + hot-spot factor * winding oil gradient.
    """
    profile = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2021-01-01 00:00:00", "2021-02-01 00:00:00", "2021-03-01 00:00:00"]),
            "load": [
                transformer.specs.nom_load_sec_side,
                transformer.specs.nom_load_sec_side,
                transformer.specs.nom_load_sec_side,
            ],
            "ambient_temperature": [20, 20, 20],
        }
    )

    model = Model(temperature_profile=create_temp_sim_profile_from_df(profile), transformer=transformer)
    result = model.run().convert_to_dataframe()

    assert result["top_oil_temperature"].equals(
        pd.Series(
            [20, 20 + transformer.specs.top_oil_temp_rise, 20 + transformer.specs.top_oil_temp_rise],
            index=profile["timestamp"],
        )
    )

    flat_increase_for_long_period = transformer.specs.top_oil_temp_rise + (
        transformer.specs.hot_spot_fac * transformer.specs.winding_oil_gradient
    )

    assert result["hot_spot_temperature"].equals(
        pd.Series(
            [20.0, 20.0 + flat_increase_for_long_period, 20.0 + flat_increase_for_long_period],
            index=profile["timestamp"],
        )
    )


def test_no_hotspot_factor(transformer):
    """Test if the model raises an error when the hot-spot factor is not specified."""
    transformer.specs.hot_spot_fac = None
    profile = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2021-01-01 00:00:00", "2021-02-01 00:00:00", "2021-03-01 00:00:00"]),
            "load": [
                transformer.specs.nom_load_sec_side,
                transformer.specs.nom_load_sec_side,
                transformer.specs.nom_load_sec_side,
            ],
            "ambient_temperature": [20, 20, 20],
        }
    )

    with pytest.raises(AttributeError):
        Model(temperature_profile=create_temp_sim_profile_from_df(profile), transformer=transformer)


def test_expected_rise_distribution(distribution_transformer):
    """Test if the temperature rise matches the expected one."""
    tau_time = distribution_transformer.specs.oil_const_k11 * distribution_transformer.specs.time_const_oil
    ambient_temp = 20

    # create a dataframe with timesteps equal to the tau_time
    time_step_list = [pd.to_datetime("2021-01-01 00:00:00") + pd.Timedelta(minutes=i * tau_time) for i in range(0, 16)]
    profile = pd.DataFrame(
        {
            "timestamp": time_step_list,
            "load": [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 0, 0, 0, 0, 0, 0, 0, 0],
            "ambient_temperature": [ambient_temp] * len(time_step_list),
        }
    )
    thermal_model = Model(
        temperature_profile=create_temp_sim_profile_from_df(profile), transformer=distribution_transformer
    )
    results = thermal_model.run()
    top_oil_temp = np.array(results.top_oil_temp_profile)
    hot_spot_temp = np.array(results.hot_spot_temp_profile)

    # The first time step should be the ambient temperature
    assert top_oil_temp[0] == ambient_temp
    assert hot_spot_temp[0] == ambient_temp

    expected_results = np.array(
        [
            20.0,
            50.75341103,
            62.0669587,
            66.22898029,
            67.76010247,
            68.32337084,
            68.53058569,
            68.60681578,
            49.9420479,
            43.07566352,
            40.54966187,
            39.62039779,
            39.27854065,
            39.15277843,
            39.10651309,
            39.08949303,
        ]
    )
    expected_results_hotspot = np.array(
        [
            20.0,
            63.97776626,
            75.29131393,
            79.45333552,
            80.9844577,
            81.54772607,
            81.75494092,
            81.83117101,
            49.9420479,
            43.07566352,
            40.54966187,
            39.62039779,
            39.27854065,
            39.15277843,
            39.10651309,
            39.08949303,
        ]
    )

    assert sum(abs(top_oil_temp - expected_results)) < 1e-6
    assert sum(abs(hot_spot_temp - expected_results_hotspot)) < 1e-6


def test_expected_rise_onan(onan_power_transformer):
    """Test if the temperature rise matches the expected one."""
    tau_time = onan_power_transformer.specs.oil_const_k11 * onan_power_transformer.specs.time_const_oil
    ambient_temp = 20
    time_step_list = [pd.to_datetime("2021-01-01 00:00:00") + pd.Timedelta(minutes=i * tau_time) for i in range(0, 16)]
    profile = pd.DataFrame(
        {
            "timestamp": time_step_list,
            "load": [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 0, 0, 0, 0, 0, 0, 0, 0],
            "ambient_temperature": [ambient_temp] * len(time_step_list),
        }
    )
    thermal_model = Model(
        temperature_profile=create_temp_sim_profile_from_df(profile), transformer=onan_power_transformer
    )
    results = thermal_model.run()
    top_oil_temp = np.array(results.top_oil_temp_profile)
    hot_spot_temp = np.array(results.hot_spot_temp_profile)

    # The first time step should be the ambient temperature
    assert top_oil_temp[0] == ambient_temp + onan_power_transformer.specs.amb_temp_surcharge
    assert hot_spot_temp[0] == ambient_temp + onan_power_transformer.specs.amb_temp_surcharge

    expected_results = np.array(
        [
            40.0,
            63.06505828,
            71.55021902,
            74.67173522,
            75.82007685,
            76.24252813,
            76.39793927,
            76.45511183,
            62.45653592,
            57.30674764,
            55.4122464,
            54.71529835,
            54.45890548,
            54.36458382,
            54.32988482,
            54.31711977,
        ]
    )

    expected_hotspot_temp = np.array(
        [
            40.0,
            78.04899136,
            84.08238209,
            86.260151,
            87.06108811,
            87.35573525,
            87.46412987,
            87.50400603,
            58.51513404,
            55.81477495,
            54.86315987,
            54.51329954,
            54.38459427,
            54.33724625,
            54.31982789,
            54.31342003,
        ]
    )

    assert sum(abs(top_oil_temp - expected_results)) < 1e-6
    assert sum(abs(hot_spot_temp - expected_hotspot_temp)) < 1e-6


def test_expected_rise_onaf(onaf_power_transformer):
    """Test if the temperature rise matches the expected one."""
    tau_time = onaf_power_transformer.specs.oil_const_k11 * onaf_power_transformer.specs.time_const_oil
    ambient_temp = 20
    time_step_list = [pd.to_datetime("2021-01-01 00:00:00") + pd.Timedelta(minutes=i * tau_time) for i in range(0, 16)]
    profile = pd.DataFrame(
        {
            "timestamp": time_step_list,
            "load": [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 0, 0, 0, 0, 0, 0, 0, 0],
            "ambient_temperature": [ambient_temp] * len(time_step_list),
        }
    )
    thermal_model = Model(
        temperature_profile=create_temp_sim_profile_from_df(profile), transformer=onaf_power_transformer
    )
    results = thermal_model.run()
    top_oil_temp = np.array(results.top_oil_temp_profile)
    hot_spot_temp = np.array(results.hot_spot_temp_profile)

    # The first time step should be the ambient temperature
    assert top_oil_temp[0] == ambient_temp + onaf_power_transformer.specs.amb_temp_surcharge
    assert hot_spot_temp[0] == ambient_temp + onaf_power_transformer.specs.amb_temp_surcharge

    expected_results = np.array(
        [
            40.0,
            63.06505828,
            71.55021902,
            74.67173522,
            75.82007685,
            76.24252813,
            76.39793927,
            76.45511183,
            62.45653592,
            57.30674764,
            55.4122464,
            54.71529835,
            54.45890548,
            54.36458382,
            54.32988482,
            54.31711977,
        ]
    )
    expected_hotspot_temp = np.array(
        [
            40.0,
            78.06076232,
            84.08249935,
            86.26015188,
            87.06108811,
            87.35573525,
            87.46412987,
            87.50400603,
            58.50336307,
            55.81465769,
            54.86315899,
            54.51329953,
            54.38459427,
            54.33724625,
            54.31982789,
            54.31342003,
        ]
    )

    assert sum(abs(top_oil_temp - expected_results)) < 1e-6
    assert sum(abs(hot_spot_temp - expected_hotspot_temp)) < 1e-6


def test_if_rise_matches_iec(iec_load_profile):
    """Test if the temperature rise matches the expected one for an IEC transformer."""
    transformer_specifications = UserTransformerSpecifications(
        load_loss=1000,  # Transformer load loss [W]
        nom_load_sec_side=1000,  # Transformer nominal current secondary side [A]
        no_load_loss=1,  # Transformer no-load loss [W]
        amb_temp_surcharge=0,  # Ambient temperature surcharge [K]
        top_oil_temp_rise=38.3,
        winding_oil_gradient=14.5,  # 45.14,
        hot_spot_fac=1.4,
    )
    transformer = PowerTransformer(
        user_specs=transformer_specifications,
        cooling_type=CoolerType.ONAF,
    )
    iec_load_profile.load_profile = iec_load_profile.load_profile * transformer_specifications.nom_load_sec_side
    thermal_model = Model(temperature_profile=iec_load_profile, transformer=transformer, init_top_oil_temp=25.6 + 12.7)
    results = thermal_model.run()
    hot_spot_temp_profile = results.hot_spot_temp_profile
    top_oil_temp_profile = results.top_oil_temp_profile

    expected_results = [
        {"minutes": 190, "top_oil_temperature": 61.9, "hot_spot_temperature": 83.8},
        {"minutes": 365, "top_oil_temperature": 44.4, "hot_spot_temperature": 54.0},
        {"minutes": 500, "top_oil_temperature": 89.2, "hot_spot_temperature": 127},
        {"minutes": 705, "top_oil_temperature": 35, "hot_spot_temperature": 37.54},
        {"minutes": 730, "top_oil_temperature": 67.9, "hot_spot_temperature": 138.6},
        {"minutes": 745, "top_oil_temperature": 60.3, "hot_spot_temperature": 75.3},
    ]
    start = pd.to_datetime("2021-01-01 00:00:00")
    for _, expected in enumerate(expected_results):
        timestamp = start + pd.Timedelta(minutes=expected["minutes"])
        calculated_top_oil_temp = top_oil_temp_profile[timestamp]
        calculated_hot_spot_temp = hot_spot_temp_profile[timestamp]
        assert calculated_top_oil_temp == pytest.approx(expected["top_oil_temperature"], abs=1.5)
        assert calculated_hot_spot_temp == pytest.approx(expected["hot_spot_temperature"], abs=1.5)


def test_three_winding_transformer(user_three_winding_transformer_specs, three_winding_input_profile):
    """Test the three-winding transformer model."""
    transformer = ThreeWindingTransformer(user_specs=user_three_winding_transformer_specs, cooling_type=CoolerType.ONAF)
    thermal_model = Model(temperature_profile=three_winding_input_profile, transformer=transformer)
    results = thermal_model.run()
    top_oil_temp = results.top_oil_temp_profile
    hot_spot_temp = results.hot_spot_temp_profile
    print(top_oil_temp)
    print(hot_spot_temp)
    print(hot_spot_temp["high_voltage_side"])
    assert top_oil_temp.shape == (len(three_winding_input_profile.datetime_index),)
    assert hot_spot_temp.shape == (len(three_winding_input_profile.datetime_index), 3)
    assert False
