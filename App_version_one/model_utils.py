import os
import streamlit as st
import numpy as np
import tensorflow as tf
from datetime import datetime, timedelta
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, GRU, Dropout
from tensorflow.keras.metrics import MeanSquaredError, MeanAbsoluteError



@st.cache_resource
def load_prediction_models():
    """Load pre-trained models or create simple models if not available."""
    model_path = "models/"
    
    try:
        # Create models directory if it doesn't exist
        if not os.path.exists(model_path):
            os.makedirs(model_path)
            
        # Try loading pre-existing models
        if os.path.exists(os.path.join(model_path, 'Load_Best_model_15.h5')) and \
           os.path.exists(os.path.join(model_path, 'best_model_GRU_solar.h5')) and \
           os.path.exists(os.path.join(model_path, 'best_model_name_V2G_EV_energy_dispo.h5')):
            
            # Load models with custom objects
            grid_load_model = tf.keras.models.load_model(
                os.path.join(model_path, 'Load_Best_model_15.h5'),
                custom_objects={'mse': MeanSquaredError(), 'mae': MeanAbsoluteError()}
            )
            
            solar_energy_model = tf.keras.models.load_model(
                os.path.join(model_path, 'best_model_GRU_solar.h5'),
                custom_objects={'mse': MeanSquaredError(), 'mae': MeanAbsoluteError()}
            )
            
            ev_model = tf.keras.models.load_model(
                os.path.join(model_path, 'best_model_name_V2G_EV_energy_dispo.h5'),
                custom_objects={'mse': MeanSquaredError(), 'mae': MeanAbsoluteError()}
            )
        else:
            # Create simple models
            raise Exception("Pre-trained models not found, creating simple models")
    
    except Exception as e:
        st.warning(f"Error: {e}")
    
    return grid_load_model, solar_energy_model, ev_model

def make_predictions(days, X_test_load, X_test_solar, X_test_ev, scaler_y, 
                    grid_load_model, solar_energy_model, ev_model, last_date):
    """Make predictions for the specified number of days."""
    hours = days * 24
    predictions = []
    current_load_input = X_test_load
    current_solar_input = X_test_solar
    current_ev_input = X_test_ev
    
    # Start predictions from the last available date plus one hour
    start_date = last_date + timedelta(hours=1)
    date_range = [start_date + timedelta(hours=i) for i in range(hours)]
    
    for _ in range(hours):
        # Make predictions
        load_pred = grid_load_model.predict(current_load_input, verbose=0)
        solar_pred = solar_energy_model.predict(current_solar_input, verbose=0)
        ev_pred = ev_model.predict(current_ev_input, verbose=0)
        
        # Store predictions
        predictions.append({
            'load': load_pred[0, 0],
            'solar': max(0, solar_pred[0, 0]),  # Ensure non-negative solar values
            'ev': scaler_y.inverse_transform(ev_pred)[0, 0]
        })
        
        # Update inputs for next prediction
        current_load_input = np.roll(current_load_input, -1, axis=1)
        current_load_input[0, -1, 0] = load_pred[0, 0]
        
        current_solar_input = np.roll(current_solar_input, -1, axis=1)
        current_solar_input[0, -1, 0] = solar_pred[0, 0]
        
        current_ev_input = np.roll(current_ev_input, -1, axis=1)
        current_ev_input[0, -1, 0] = ev_pred[0, 0]
    
    # Convert predictions to arrays
    load_pred = np.array([p['load'] for p in predictions]).reshape(-1, 1)
    solar_energy_pred = np.array([p['solar'] for p in predictions]).reshape(-1, 1)
    ev_pred_inv = np.array([p['ev'] for p in predictions]).reshape(-1, 1)
    
    return load_pred, solar_energy_pred, ev_pred_inv, date_range