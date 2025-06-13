import os
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

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
        # Check if data directory exists
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            
            # Create sample data for demo purposes
            create_sample_data(data_path)
            
        # Load data from files
        if not os.path.exists(os.path.join(data_path, "Total_Load.xlsx")):
            create_sample_data(data_path)
            
        load_df = pd.read_excel(os.path.join(data_path, "Total_Load.xlsx"))
        solar_energy_df = pd.read_excel(os.path.join(data_path, "Solar_Energy.xlsx"))
        ev_dispo_df = pd.read_excel(os.path.join(data_path, "total_power_EV_disponible.xlsx"))
        
        # Set up time index
        start_date = pd.to_datetime('2022-06-07 00:00')
        load_df['Time'] = start_date + pd.to_timedelta(load_df['Time'], unit='s')
        solar_energy_df['Time'] = start_date + pd.to_timedelta(solar_energy_df['Time'], unit='s')
        
        return load_df, solar_energy_df, ev_dispo_df
    except Exception as e:
        st.warning(f"Using synthetic data because: {e}")
        return create_synthetic_data()

def create_sample_data(data_path):
    """Create sample data for demonstration purposes."""
    # Generate sample time series data
    hours = 3 * 24  # 3 days of hourly data
    time_seconds = np.arange(0, hours * 3600, 3600)
    
    # Total Load data - follows a daily pattern with some noise
    load_pattern = 10 + 5 * np.sin(np.linspace(0, 2*np.pi*3, hours)) + 2 * np.sin(np.linspace(0, 2*np.pi*hours, hours))
    load_with_noise = load_pattern + np.random.normal(0, 0.5, hours)
    load_df = pd.DataFrame({
        'Time': time_seconds,
        'Load': load_with_noise
    })
    
    # Solar Energy data - peaks during day hours
    day_pattern = np.sin(np.linspace(0, 2*np.pi, 24)) * 0.5 + 0.5  # Daily solar pattern
    solar_pattern = np.tile(day_pattern, 3)  # Repeat for 3 days
    solar_with_noise = solar_pattern * 7 + np.random.normal(0, 0.3, hours)
    solar_with_noise = np.maximum(0, solar_with_noise)  # No negative solar generation
    solar_energy_df = pd.DataFrame({
        'Time': time_seconds,
        'SolarEnergy': solar_with_noise
    })
    
    # EV availability data - higher during night hours
    night_pattern = 1 - 0.7 * np.sin(np.linspace(0, 2*np.pi, 24)) * 0.5 - 0.5  # Inverse of day pattern
    ev_pattern = np.tile(night_pattern, 3) * 8 + np.random.normal(0, 0.2, hours)
    ev_pattern = np.maximum(0, ev_pattern)  # No negative EV availability
    ev_dispo_df = pd.DataFrame({
        'Hour': np.arange(hours),
        'total_usable_power_all_profiles_MW': ev_pattern
    })
    
    # Save to Excel files
    load_df.to_excel(os.path.join(data_path, "Total_Load.xlsx"), index=False)
    solar_energy_df.to_excel(os.path.join(data_path, "Solar_Energy.xlsx"), index=False)
    ev_dispo_df.to_excel(os.path.join(data_path, "total_power_EV_disponible.xlsx"), index=False)

def create_synthetic_data():
    """Create synthetic data for demonstration when real data is unavailable."""
    # Generate synthetic time series data
    hours = 3 * 24  # 3 days of hourly data
    time_seconds = np.arange(0, hours * 3600, 3600)
    start_date = pd.to_datetime('2022-06-07 00:00')
    
    # Total Load data
    load_pattern = 10 + 5 * np.sin(np.linspace(0, 2*np.pi*3, hours)) + 2 * np.sin(np.linspace(0, 2*np.pi*hours, hours))
    load_with_noise = load_pattern + np.random.normal(0, 0.5, hours)
    load_df = pd.DataFrame({
        'Time': [start_date + pd.Timedelta(seconds=s) for s in time_seconds],
        'Load': load_with_noise
    })
    
    # Solar Energy data
    day_pattern = np.sin(np.linspace(0, 2*np.pi, 24)) * 0.5 + 0.5
    solar_pattern = np.tile(day_pattern, 3)
    solar_with_noise = solar_pattern * 7 + np.random.normal(0, 0.3, hours)
    solar_with_noise = np.maximum(0, solar_with_noise)
    solar_energy_df = pd.DataFrame({
        'Time': [start_date + pd.Timedelta(seconds=s) for s in time_seconds],
        'SolarEnergy': solar_with_noise
    })
    
    # EV availability data
    night_pattern = 1 - 0.7 * np.sin(np.linspace(0, 2*np.pi, 24)) * 0.5 - 0.5
    ev_pattern = np.tile(night_pattern, 3) * 8 + np.random.normal(0, 0.2, hours)
    ev_pattern = np.maximum(0, ev_pattern)
    ev_dispo_df = pd.DataFrame({
        'Hour': np.arange(hours),
        'total_usable_power_all_profiles_MW': ev_pattern
    })
    
    return load_df, solar_energy_df, ev_dispo_df

def get_historical_data(load_df, solar_energy_df, ev_dispo_df, end_date, days):
    """Get historical data for comparison."""
    end_idx = load_df[load_df['Time'] <= end_date].index[-1]
    start_idx = max(0, end_idx - (days * 24) + 1)
    
    historical_data = {
        'date_range': load_df['Time'][start_idx:end_idx + 1],
        'load': load_df['Load'][start_idx:end_idx + 1].values,
        'solar': solar_energy_df['SolarEnergy'][start_idx:end_idx + 1].values,
        'ev': ev_dispo_df['total_usable_power_all_profiles_MW'][start_idx:end_idx + 1].values
    }
    
    return historical_data

def prepare_data_for_models(load_df, solar_energy_df, ev_dispo_df, time_steps, forecast_days):
    """Prepare data for model predictions."""
    # Get the last available date
    last_date = load_df['Time'].max()
    
    # Get historical data for comparison
    historical_data = get_historical_data(load_df, solar_energy_df, ev_dispo_df, last_date, forecast_days)
    
    # Prepare prediction data using the last time_steps points
    X_load = load_df['Load'].values[-time_steps:].reshape(1, time_steps, 1)
    
    # Scale solar data
    scaler_solar = MinMaxScaler()
    solar_scaled = scaler_solar.fit_transform(solar_energy_df['SolarEnergy'].values.reshape(-1, 1))
    X_solar = solar_scaled[-time_steps:].reshape(1, time_steps, 1)
    
    # Scale EV data
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    ev_data = ev_dispo_df['total_usable_power_all_profiles_MW'].values
    scaler_y.fit(ev_data.reshape(-1, 1))
    ev_scaled = scaler_X.fit_transform(ev_data.reshape(-1, 1))
    X_ev = ev_scaled[-time_steps:].reshape(1, time_steps, 1)
    
    return X_load, X_solar, X_ev, scaler_y, historical_data, last_date