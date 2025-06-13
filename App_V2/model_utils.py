import os
import streamlit as st
import numpy as np
import tensorflow as tf
from datetime import datetime, timedelta
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, GRU, Dropout, Bidirectional
from tensorflow.keras.metrics import MeanSquaredError, MeanAbsoluteError
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import matplotlib.pyplot as plt

@st.cache_resource
def load_prediction_models():
    """Load pre-trained models."""
    model_path = "models/"
    
    # Create models directory if it doesn't exist
    os.makedirs(model_path, exist_ok=True)
    
    load_model_path = os.path.join(model_path, 'best_model_RNN_LOAD.h5')
    solar_model_path = os.path.join(model_path, 'best_model_BILSTM_SolarEnergy.h5')
    ev_model_path = os.path.join(model_path, 'RNN_CarsEnergy_v2g.h5')
    diesel_model_path = os.path.join(model_path, 'best_model_diesel_gru_15.h5')

    # Check if all models exist
    if not (os.path.exists(load_model_path) and
            os.path.exists(solar_model_path) and
            os.path.exists(ev_model_path)):
        st.error("Pre-trained models not found in 'models/' directory.")
        return None, None, None

    # Load the models
    try:
        grid_load_model = tf.keras.models.load_model(
            load_model_path,
            custom_objects={'mse': MeanSquaredError(), 'mae': MeanAbsoluteError()}
        )

        solar_energy_model = tf.keras.models.load_model(
            solar_model_path,
            custom_objects={'mse': MeanSquaredError(), 'mae': MeanAbsoluteError()}
        )

        ev_model = tf.keras.models.load_model(
            ev_model_path,
            custom_objects={'mse': MeanSquaredError(), 'mae': MeanAbsoluteError()}
        )

        diesel_model = tf.keras.models.load_model(
            diesel_model_path,
            custom_objects={'mse': MeanSquaredError(), 'mae': MeanAbsoluteError()}
        )

        return grid_load_model, solar_energy_model, ev_model, diesel_model
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None


def make_predictions(days,
                     X_test_load, X_test_solar, X_test_ev,
                     scaler_load, scaler_solar, scaler_ev,
                     grid_load_model, solar_energy_model, ev_model,
                     last_date):
    """Make predictions for the specified number of days (forecast horizon)."""
    hours = days * 24
    predictions = []

    current_load_input = X_test_load.copy()
    current_solar_input = X_test_solar.copy()
    current_ev_input = X_test_ev.copy()

    # Start predictions from the last available date plus one hour
    start_date = last_date + timedelta(hours=1)
    date_range = [start_date + timedelta(hours=i) for i in range(hours)]

    for _ in range(hours):
        # Predict scaled values
        load_pred_scaled = grid_load_model.predict(current_load_input, verbose=0)
        solar_pred_scaled = solar_energy_model.predict(current_solar_input, verbose=0)
        ev_pred_scaled = ev_model.predict(current_ev_input, verbose=0)

        # Inverse transform predictions
        load_pred = scaler_load.inverse_transform(load_pred_scaled)[0, 0]
        solar_pred = scaler_solar.inverse_transform(solar_pred_scaled)[0, 0]
        ev_pred = scaler_ev.inverse_transform(ev_pred_scaled)[0, 0]

        # Store predictions
        predictions.append({
            'load': load_pred,
            'solar': max(0, solar_pred),  # Ensure non-negative solar
            'ev': ev_pred
        })

        # Update input for next step (use scaled values!)
        current_load_input = np.roll(current_load_input, -1, axis=1)
        current_load_input[0, -1, 0] = load_pred_scaled[0, 0]

        current_solar_input = np.roll(current_solar_input, -1, axis=1)
        current_solar_input[0, -1, 0] = solar_pred_scaled[0, 0]

        current_ev_input = np.roll(current_ev_input, -1, axis=1)
        current_ev_input[0, -1, 0] = ev_pred_scaled[0, 0]

    # Convert to arrays
    load_forecast = np.array([p['load'] for p in predictions]).reshape(-1, 1)
    solar_forecast = np.array([p['solar'] for p in predictions]).reshape(-1, 1)
    ev_forecast = np.array([p['ev'] for p in predictions]).reshape(-1, 1)

    return load_forecast, solar_forecast, ev_forecast, date_range

from datetime import timedelta
import numpy as np

def forecast_diesel_price(days, model, initial_sequence, last_data, last_week, time_steps=15):
    """
    Forecast diesel prices for the next n_forecast periods.
    Includes the last real diesel price and last date in the output.
    
    Parameters:
        days (int): Number of days to forecast (converted to weeks).
        model (keras.Model): Trained Keras model.
        initial_sequence (np.array): Last known sequence used for prediction (shape: time_steps).
        last_data (float): Last real diesel price.
        last_week (datetime): Date of the last known diesel price.
        time_steps (int): Number of time steps the model expects.

    Returns:
        diesel_forecast (np.array): Array including last real price + predictions.
        date_range_diesel (list): Corresponding list of datetime objects.

    Why?:
      for data to be compatible becaus eit weekly an dothers are hourly
    """

    n_forecast = days // 7 + 1  # Forecast number of weeks
    diesel_forecast = [last_data]  # Start with last known value
    date_range_diesel = [last_week]  # Start with last known date

    current_sequence = initial_sequence.copy()

    for i in range(n_forecast):
        input_seq = current_sequence.reshape(1, time_steps, 1)
        next_pred = model.predict(input_seq, verbose=0)[0][0]
        next_pred = max(next_pred, 9)  # Ensure minimum diesel price
        diesel_forecast.append(next_pred)

        next_date = last_week + timedelta(weeks=i+1)
        date_range_diesel.append(next_date)

        current_sequence = np.roll(current_sequence, -1)
        current_sequence[-1] = next_pred

    return np.array(diesel_forecast), date_range_diesel


def create_load_model(input_shape):
    """Create a model for load prediction."""
    model = Sequential([
        GRU(50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        GRU(50),
        Dropout(0.2),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mse', 'mae'])
    return model


def create_solar_model(input_shape):
    """Create a model for solar energy prediction."""
    model = Sequential([
        Bidirectional(LSTM(64, return_sequences=True), input_shape=input_shape),
        Dropout(0.2),
        Bidirectional(LSTM(32)),
        Dropout(0.2),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mse', 'mae'])
    return model


def create_ev_model(input_shape):
    """Create a model for EV availability prediction."""
    model = Sequential([
        GRU(32, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        GRU(16),
        Dropout(0.2),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mse', 'mae'])
    return model


def prepare_training_data(df, target_column, time_steps=15):
    """Prepare data for model training."""
    # Extract the target series
    target_series = df[target_column]
    
    # Scale the data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(target_series.values.reshape(-1, 1))
    
    # Create X, y pairs
    X, y = [], []
    for i in range(len(scaled_data) - time_steps):
        X.append(scaled_data[i:i + time_steps])
        y.append(scaled_data[i + time_steps])
    
    X = np.array(X)
    y = np.array(y)
    
    # Split into train/test
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    return X_train, y_train, X_test, y_test, scaler


def train_model(df, target_column, epochs=50, batch_size=32, time_steps=15, progress_callback=None):
    """Train a model with the given data."""
    # Prepare data
    X_train, y_train, X_test, y_test, scaler = prepare_training_data(df, target_column, time_steps)
    
    # Create model based on target
    input_shape = (time_steps, 1)
    
    if target_column == 'Load':
        model = create_load_model(input_shape)
        model_filename = 'best_model_RNN_LOAD.h5'
    elif target_column == 'SolarEnergy':
        model = create_solar_model(input_shape)
        model_filename = 'best_model_BILSTM_SolarEnergy.h5'
    else:  # EV model
        model = create_ev_model(input_shape)
        model_filename = 'RNN_CarsEnergy_v2g.h5'
    
    # Callbacks
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=5,
        min_lr=0.0001
    )
    
    checkpoint = ModelCheckpoint(
        os.path.join('models', model_filename),
        monitor='val_loss',
        save_best_only=True,
        mode='min',
        verbose=1
    )
    
    # Custom callback for progress tracking
    class ProgressCallback(tf.keras.callbacks.Callback):
        def on_epoch_end(self, epoch, logs=None):
            if progress_callback:
                progress = (epoch + 1) / epochs
                progress_callback(progress)
    
    # Train the model
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        callbacks=[early_stop, reduce_lr, checkpoint, ProgressCallback()],
        verbose=1
    )
    
    # Save the training history
    hist_df = pd.DataFrame(history.history)
    hist_df.to_csv(os.path.join('models', f'{target_column}_training_history.csv'), index=False)
    
    # Return the trained model and history
    return model, history