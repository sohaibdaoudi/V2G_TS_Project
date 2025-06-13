import os
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import timedelta

def create_dataset(serie, time_steps=1):
    """Create input/output pairs for time series prediction."""
    Xs, ys = [], []
    for i in range(len(serie) - time_steps):
        Xs.append(serie.iloc[i:(i + time_steps)].values)
        ys.append(serie.iloc[i + time_steps])
    return np.array(Xs), np.array(ys)

@st.cache_data
def load_data():
    """Load and preprocess the datasets."""
    data_path = "data/"
    
    try:
        # Check if required files exist
        load_path = os.path.join(data_path, "Total_Load.xlsx")
        solar_path = os.path.join(data_path, "Solar_Energy.xlsx")
        ev_path = os.path.join(data_path, "total_power_EV_disponible.xlsx")
        diesel_path = os.path.join(data_path, "diesel_price_weekly.xlsx")
        
        if not (os.path.exists(load_path) and os.path.exists(solar_path) and os.path.exists(ev_path)):
            st.warning("Data not found. Please ensure all required files are present in the data directory.")
            return None, None, None, None
        
        # Load data from files
        load_df = pd.read_excel(load_path)
        solar_energy_df = pd.read_excel(solar_path)
        ev_dispo_df = pd.read_excel(ev_path)
        
        # Load diesel price data if available
        diesel_df = None
        if os.path.exists(diesel_path):
            diesel_df = pd.read_excel(diesel_path)
            diesel_df['Date'] = pd.to_datetime(diesel_df['Date'])
        else:
            st.warning("Diesel price data not found. Using default constant value.")

        return load_df, solar_energy_df, ev_dispo_df, diesel_df
    except Exception as e:
        st.warning(f"Error loading data: {e}")
        return None, None, None, None


def get_historical_data(load_df, solar_energy_df, ev_dispo_df, diesel_df, end_date, days):
    """Get historical data for comparison."""
    end_idx = load_df[load_df['Time'] <= end_date].index[-1]
    start_idx = max(0, end_idx - (days * 24) + 1)
    
    historical_data = {
        'date_range': load_df['Time'][start_idx:end_idx + 1],
        'load': load_df['Load'][start_idx:end_idx + 1].values,
        'solar': solar_energy_df['SolarEnergy'][start_idx:end_idx + 1].values,
        'ev': ev_dispo_df['total_usable_power_all_profiles_MW'][start_idx:end_idx + 1].values,
    }
    
    if diesel_df is not None:
        historical_data['date_range_diesel'] = diesel_df['Date']
        historical_data['diesel_price'] = diesel_df['Price']
    
    return historical_data


def prepare_data_for_models(load_df, solar_energy_df, ev_dispo_df, diesel_df, time_steps, forecast_days):
    """Prepare scaled X and Y data for model predictions."""
    
    # Forecast horizon in hours
    forecast_horizon = forecast_days * 24
    
    # Get the last available index for slicing
    last_index = load_df.index[-1]
    
    # LOAD
    load_data = load_df['Load'].values.reshape(-1, 1)
    scaler_load = MinMaxScaler()
    load_scaled = scaler_load.fit_transform(load_data)
    X_load = load_scaled[-time_steps:].reshape(1, time_steps, 1)
    y_load = load_scaled[-(forecast_horizon + 1):-1].reshape(1, forecast_horizon, 1)
    
    # SOLAR ENERGY
    solar_data = solar_energy_df['SolarEnergy'].values.reshape(-1, 1)
    scaler_solar = MinMaxScaler()
    solar_scaled = scaler_solar.fit_transform(solar_data)
    X_solar = solar_scaled[-time_steps:].reshape(1, time_steps, 1)
    y_solar = solar_scaled[-(forecast_horizon + 1):-1].reshape(1, forecast_horizon, 1)
    
    # EV DATA
    ev_data = ev_dispo_df['total_usable_power_all_profiles_MW'].values.reshape(-1, 1)
    scaler_ev = MinMaxScaler()
    ev_scaled = scaler_ev.fit_transform(ev_data)
    X_ev = ev_scaled[-time_steps:].reshape(1, time_steps, 1)
    y_ev = ev_scaled[-(forecast_horizon + 1):-1].reshape(1, forecast_horizon, 1)
    
    # Diesel Data 
    X_diesel = None
    if diesel_df is not None:
        try:
            diesel_data = diesel_df['Price'].values.reshape(-1, 1)
            # Use last available weeks of data
            X_diesel = diesel_data[-time_steps:].reshape(1, time_steps, 1)
        except (IndexError, ValueError) as e:
            st.warning(f"Error processing diesel data: {e}")
            X_diesel = None

    # Get the last date for reference
    last_date = load_df['Time'].max()

    # Historical data for visualization (not scaled)
    historical_data = get_historical_data(load_df, solar_energy_df, ev_dispo_df, diesel_df, last_date, forecast_days)

    return (
        X_load, y_load, scaler_load,
        X_solar, y_solar, scaler_solar,
        X_ev, y_ev, scaler_ev,
        X_diesel,
        historical_data, last_date
    )


def diesel_cost_per_mwh(prices_mad_per_liter):
    """
    Calculate the cost per MWh (mechanical energy) from diesel prices (MAD per liter).

    Parameters:
    - prices_mad_per_liter: NumPy array of diesel prices in MAD per liter

    Returns:
    - NumPy array of diesel costs in MAD per MWh
    """
    # Constants
    specific_energy = 38  # MJ/litre
    efficiency = 0.35     # 35% engine efficiency
    mj_to_kwh = 0.278     # 1 MJ = 0.278 kWh

    # Formula for cost per MWh
    cost_per_mwh = (prices_mad_per_liter / specific_energy) * (1 / efficiency) * (1 / mj_to_kwh) * 1000

    return cost_per_mwh


def map_weekly_to_hourly_prices(hourly_dates, diesel_prices, diesel_dates):
    """
    Maps weekly diesel prices to hourly time series based on dates

    Parameters:
    hourly_dates: pandas Series or array of hourly timestamps
    diesel_prices: array/list of weekly diesel prices
    diesel_dates: pandas Series or array of weekly price dates

    Returns:
    hourly_diesel_prices: array of diesel prices for each hour
    """
    hourly_diesel_prices = np.zeros(len(hourly_dates))

    # Convert to pandas datetime if not already
    hourly_dates = pd.to_datetime(hourly_dates)
    diesel_dates = pd.to_datetime(diesel_dates)

    for i, hour_date in enumerate(hourly_dates):
        # Find the appropriate weekly price for this hour
        # Use the most recent diesel price available for this date

        # Find closest diesel price date that is <= hour_date
        valid_prices = diesel_dates <= hour_date
        if valid_prices.any():
            closest_idx = np.where(valid_prices)[0][-1]  # Get the last (most recent) valid price
            hourly_diesel_prices[i] = diesel_prices[closest_idx]
        else:
            # If no valid price found, use the first available price
            hourly_diesel_prices[i] = diesel_prices[0]

    return hourly_diesel_prices