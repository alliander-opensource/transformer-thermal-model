# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pandas as pd
import pytest

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.model import Model
from transformer_thermal_model.schemas import (
    InputProfile,
    ThreeWindingInputProfile,
    UserThreeWindingTransformerSpecifications,
    UserTransformerSpecifications,
    WindingSpecifications,
)
from transformer_thermal_model.toolbox.temp_sim_profile_tools import create_temp_sim_profile_from_df
from transformer_thermal_model.transformer import PowerTransformer
from transformer_thermal_model.transformer.distribution import DistributionTransformer
from transformer_thermal_model.transformer.threewinding import ThreeWindingTransformer


@pytest.fixture
def transformer(default_user_trafo_specs: UserTransformerSpecifications) -> PowerTransformer:
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


def test_temp_rise_with_zero_load(transformer: PowerTransformer):
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


def test_temp_rise_with_losses_and_zero_load(onan_power_transformer: PowerTransformer):
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


def test_temp_rise_to_ambient_temperature(transformer: PowerTransformer):
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


def test_temp_rise_zero_timesteps(transformer: PowerTransformer):
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


def test_good_result_with_large_time_steps(transformer: PowerTransformer):
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


def test_expected_rise_distribution(distribution_transformer: DistributionTransformer):
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


def test_expected_rise_onan(onan_power_transformer: PowerTransformer):
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


def test_expected_rise_onaf(onaf_power_transformer: PowerTransformer):
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


def test_if_rise_matches_iec(iec_load_profile: InputProfile):
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


def test_three_winding_transformer(
    user_three_winding_transformer_specs: UserThreeWindingTransformerSpecifications,
    three_winding_input_profile: ThreeWindingInputProfile,
):
    """Test the three-winding transformer model."""
    transformer = ThreeWindingTransformer(user_specs=user_three_winding_transformer_specs, cooling_type=CoolerType.ONAF)
    length = len(three_winding_input_profile.datetime_index)

    # With high load on high voltage side
    three_winding_input_profile.load_profile_high_voltage_side = [2000] * length
    three_winding_input_profile.load_profile_middle_voltage_side = [1000] * length
    three_winding_input_profile.load_profile_low_voltage_side = [1000] * length
    thermal_model = Model(temperature_profile=three_winding_input_profile, transformer=transformer)
    results = thermal_model.run()
    hot_spot_temp = results.hot_spot_temp_profile
    assert hot_spot_temp["high_voltage_side"].sum() > hot_spot_temp["middle_voltage_side"].sum()
    assert hot_spot_temp["high_voltage_side"].sum() > hot_spot_temp["low_voltage_side"].sum()

    # with high load on middle voltage side
    three_winding_input_profile.load_profile_high_voltage_side = [1000] * length
    three_winding_input_profile.load_profile_middle_voltage_side = [2000] * length
    three_winding_input_profile.load_profile_low_voltage_side = [1000] * length
    thermal_model = Model(temperature_profile=three_winding_input_profile, transformer=transformer)
    results = thermal_model.run()
    hot_spot_temp = results.hot_spot_temp_profile
    assert hot_spot_temp["middle_voltage_side"].sum() > hot_spot_temp["high_voltage_side"].sum()
    assert hot_spot_temp["middle_voltage_side"].sum() > hot_spot_temp["low_voltage_side"].sum()

    # with high load on low voltage side
    three_winding_input_profile.load_profile_high_voltage_side = [1000] * length
    three_winding_input_profile.load_profile_middle_voltage_side = [1000] * length
    three_winding_input_profile.load_profile_low_voltage_side = [2000] * length
    thermal_model = Model(temperature_profile=three_winding_input_profile, transformer=transformer)
    results = thermal_model.run()
    hot_spot_temp = results.hot_spot_temp_profile
    assert hot_spot_temp["low_voltage_side"].sum() > hot_spot_temp["high_voltage_side"].sum()
    assert hot_spot_temp["low_voltage_side"].sum() > hot_spot_temp["middle_voltage_side"].sum()


def test_three_winding_equals_power():
    """Test if the three-winding transformer model equals the power transformer model.

    If we use the same load and normal load for all three windings, and choose the losses such that the
    top-oil temperature rise is the same, the three-winding transformer model should yield the same
    results as the power transformer model.
    """
    # Define the time range for your simulation
    datetime_index = [pd.to_datetime("2025-07-01 00:00:00") + pd.Timedelta(minutes=2 * i) for i in np.arange(0, 180)]

    load_series = pd.Series(data=1 * 500 + 500, index=datetime_index)
    ambient_series = pd.Series(data=20, index=datetime_index)

    # Create the input profile for the three-winding transformer
    three_winding_profile_input = ThreeWindingInputProfile.create(
        datetime_index=datetime_index,
        ambient_temperature_profile=ambient_series,
        load_profile_high_voltage_side=load_series,
        load_profile_middle_voltage_side=load_series,
        load_profile_low_voltage_side=load_series,
    )
    power_input_profile = InputProfile.create(
        datetime_index=datetime_index,
        ambient_temperature_profile=ambient_series,
        load_profile=load_series,
    )

    # Define the transformer specifications for each winding
    user_specs_three_winding = UserThreeWindingTransformerSpecifications(
        no_load_loss=10000,
        amb_temp_surcharge=0,
        lv_winding=WindingSpecifications(nom_load=1600, winding_oil_gradient=23, nom_power=150),
        mv_winding=WindingSpecifications(nom_load=1600, winding_oil_gradient=23, nom_power=150),
        hv_winding=WindingSpecifications(nom_load=1600, winding_oil_gradient=23, nom_power=150),
        load_loss_hv_lv=20000,
        load_loss_hv_mv=20000,
        load_loss_mv_lv=20000,
    )
    three_winding_transformer = ThreeWindingTransformer(
        user_specs=user_specs_three_winding, cooling_type=CoolerType.ONAN
    )

    user_specs_power = UserTransformerSpecifications(
        load_loss=30000,  # Transformer load loss [W]
        nom_load_sec_side=1600,  # Transformer nominal current secondary side [A]
        no_load_loss=10000,  # Transformer no-load loss [W]
        amb_temp_surcharge=0,  # Ambient temperature surcharge [K]
        winding_oil_gradient=23,  # Winding oil gradient (worst case) [K]
    )
    power_transformer = PowerTransformer(user_specs=user_specs_power, cooling_type=CoolerType.ONAN)

    model_three_winding = Model(temperature_profile=three_winding_profile_input, transformer=three_winding_transformer)
    results_three_winding = model_three_winding.run()

    model_power = Model(temperature_profile=power_input_profile, transformer=power_transformer)
    results_power = model_power.run()

    # Compare the results
    # Use numpy.allclose for approximate equality
    assert np.allclose(
        results_three_winding.top_oil_temp_profile.values,
        results_power.top_oil_temp_profile.values,
        rtol=1e-6,
        atol=1e-4,
    )
    assert np.allclose(
        results_three_winding.hot_spot_temp_profile["low_voltage_side"].values,
        results_power.hot_spot_temp_profile.values,
        rtol=1e-6,
        atol=1e-4,
    )


def create_step_load_profile(max_load, datetime_index):
    """Create a step load profile with max_load for 1 day and 0% load for the next day.

    Function is used in the test_integration_three_winding_transformer test.
    """
    load_values = np.concatenate(
        [
            np.full(48, max_load),  # max load for 1 day (48 intervals of 15 minutes in 24 hours)
            np.full(48, 0.0),  # 0% load for the next day
        ]
    )
    return pd.Series(load_values, index=datetime_index)


def test_integration_three_winding_transformer():
    """Here we test the three-winding transformer model against validation results for a step load profile.

    The top_oil validation data comes from the original Dep three-winding-excel excel model. The hotspot validation
    data was generated using this three_winding_model (TTM). Because we are using a newer IEC hotspot calculation
    method than the excel uses we cannot
    """
    # Instead of using the above hardcoded validation data, we load it from a CSV file for better maintainability
    validation_data = pd.read_csv(
        "tests/model/three_winding_validation_data.csv", parse_dates=["datetime"], index_col="datetime", comment="#"
    )

    # Define the step load profile (120% load to 0% load)
    step_load_profile_hv = create_step_load_profile(461.88, validation_data.index)
    step_load_profile_mv = create_step_load_profile(1319.64, validation_data.index)
    step_load_profile_lv = create_step_load_profile(1979.52, validation_data.index)

    ambient_series = pd.Series(data=20, index=step_load_profile_hv.index)

    # Create the input profile for the three-winding transformer
    profile_input = ThreeWindingInputProfile.create(
        datetime_index=step_load_profile_hv.index,
        ambient_temperature_profile=ambient_series,
        load_profile_high_voltage_side=step_load_profile_hv,
        load_profile_middle_voltage_side=step_load_profile_mv,
        load_profile_low_voltage_side=step_load_profile_lv,
    )

    # Define transformer specifications
    user_specs_three_winding = UserThreeWindingTransformerSpecifications(
        no_load_loss=51740,
        amb_temp_surcharge=0,
        hv_winding=WindingSpecifications(
            nom_load=384.9, winding_oil_gradient=17.6, hot_spot_fac=1.3, time_const_windings=7, nom_power=100
        ),
        mv_winding=WindingSpecifications(
            nom_load=1099.7, winding_oil_gradient=18.6, hot_spot_fac=1.3, time_const_windings=7, nom_power=100
        ),
        lv_winding=WindingSpecifications(
            nom_load=1649.6, winding_oil_gradient=25.4, hot_spot_fac=1.3, time_const_windings=7, nom_power=30
        ),
        load_loss_hv_lv=63130.50999999999,
        load_loss_hv_mv=93661 + 184439,
        load_loss_mv_lv=54960.49,
        load_loss_total=329800,
        top_oil_temp_rise=51.4,
    )

    # Initialize the transformer model
    transformer = ThreeWindingTransformer(user_specs=user_specs_three_winding, cooling_type=CoolerType.ONAF)

    model = Model(temperature_profile=profile_input, transformer=transformer)
    results = model.run()

    # test if results don't deviate more than 0.05 degree Celsius from validation data,
    # note that the hot-spot is modelled with the TTM 0.1.5 (IEC-2018) hotspot formula
    # TTM 0.1.4 would yeald slightly different results for the hotspot
    assert max(abs(results.top_oil_temp_profile - validation_data.top_oil)) < 0.05, (
        "Top-oil temperature profile does not match validation data"
    )
    assert max(abs(results.hot_spot_temp_profile.high_voltage_side - validation_data.hotspot_hs)) < 0.05, (
        "Hot-spot temperature profile HV does not match validation data"
    )
    assert max(abs(results.hot_spot_temp_profile.middle_voltage_side - validation_data.hotspot_ms)) < 0.05, (
        "Hot-spot temperature profile MV does not match validation data"
    )
    assert max(abs(results.hot_spot_temp_profile.low_voltage_side - validation_data.hotspot_ls)) < 0.05, (
        "Hot-spot temperature profile LV does not match validation data"
    )


# if name is main run three winding equals power test
if __name__ == "__main__":
    test_three_winding_equals_power()
