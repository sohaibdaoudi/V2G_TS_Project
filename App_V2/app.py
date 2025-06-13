import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import os

# Import our modules
from data_utils import load_data, prepare_data_for_models
from model_utils import load_prediction_models, make_predictions, train_model,forecast_diesel_price
from optimization import optimize_with_v2g, optimize_without_v2g
from visualization import (
    plot_predictions_with_historical,
    plot_optimization_results,
    create_energy_distribution_charts,
    create_cost_comparison_chart,
    plot_v2g_usage,
    plot_diesel_prices
)
from utils import create_excel_report, get_user_recommendations

# Page configuration
st.set_page_config(
    page_title="V2G Energy Optimization Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False
if 'training_completed' not in st.session_state:
    st.session_state.training_completed = False

# App header
st.markdown("""
<div class="header">
    <h1>V2G Energy Optimization Dashboard</h1>
    <p class="subtitle">Intelligent energy management with Vehicle-to-Grid technology</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## Dashboard Controls")
    
    # Data loading section
    st.markdown("### Data Settings")
    
    load_data_button = st.button("Load Data", use_container_width=True)
    
    if load_data_button or st.session_state.data_loaded:
        with st.spinner("Loading data..."):
            load_df, solar_energy_df, ev_dispo_df, diesel_df = load_data()
            if load_df is not None and solar_energy_df is not None and ev_dispo_df is not None:
                st.session_state.data_loaded = True
                st.session_state.load_df = load_df
                st.session_state.solar_energy_df = solar_energy_df
                st.session_state.ev_dispo_df = ev_dispo_df
                st.session_state.diesel_df = diesel_df
                
                st.success("Data loaded successfully!")
            else:
                st.error("Error loading data. Please check data files.")
    
    # Only show model and forecast settings if data is loaded
    if st.session_state.data_loaded:
        # Model loading section
        st.markdown("### Model Settings")
        load_models_button = st.button("Load Models", use_container_width=True)
        
        if load_models_button or st.session_state.models_loaded:
            with st.spinner("Loading models..."):
                grid_load_model, solar_energy_model, ev_model, diesel_model = load_prediction_models()
                if grid_load_model is not None and solar_energy_model is not None and ev_model is not None:
                    st.session_state.models_loaded = True
                    st.session_state.grid_load_model = grid_load_model
                    st.session_state.solar_energy_model = solar_energy_model
                    st.session_state.ev_model = ev_model
                    st.session_state.diesel_model = diesel_model
                    
                    st.success("Models loaded successfully!")
                else:
                    st.error("Error loading models. Please check model files.")
        
        # Only show forecast settings if models are loaded
        if st.session_state.models_loaded:
            # Forecast settings
            st.markdown("### Forecast Settings")
            forecast_days = st.slider(
                "Forecast Duration (Days)", 
                min_value=1, 
                max_value=10, 
                value=3,
                help="Select the number of days to forecast"
            )
            
            # Diesel price settings
            st.markdown("### Diesel Price Settings")
            diesel_price_type = st.radio(
                "Diesel Price Source",
                options=["Constant Value", "Time Series"],
                index=0,
                help="Choose between a constant diesel price or time-varying prices from historical data"
            )
            
            if diesel_price_type == "Constant Value":
                diesel_price_mad_liter = st.number_input(
                    "Diesel Price (MAD/L)", 
                    min_value=6.0, 
                    max_value=20.0, 
                    value=13.0,
                    step=0.5
                )
                from data_utils import diesel_cost_per_mwh
                diesel_price = diesel_cost_per_mwh(diesel_price_mad_liter)
            else:
                # Preview the diesel price time series
                if 'diesel_df' in st.session_state:
                    diesel_fig = plot_diesel_prices(st.session_state.diesel_df)
                    st.plotly_chart(diesel_fig, use_container_width=True)
            
            st.markdown("### Optimization Parameters")
            v2g_price = st.number_input(
                "V2G Price (MAD/MWh)", 
                min_value=1000, 
                max_value=3000, 
                value=2000,
                step=10
            )
            
            max_v2g_hours = st.slider(
                "Maximum V2G Hours per Day", 
                min_value=1, 
                max_value=10, 
                value=3
            )
    
    st.markdown("---")
    st.markdown("*© 2025 V2G Energy Optimization*")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Detailed Analysis", "Reports", "Model Training"])

with tab1:
    if not st.session_state.data_loaded:
        st.info("Please load data from the sidebar first.")
    elif not st.session_state.models_loaded:
        st.info("Please load models from the sidebar.")
    else:
        # Add run button
        st.markdown("## Analysis Controls")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Click the button below to run the V2G optimization analysis.")
        with col2:
            run_analysis = st.button("Run Analysis", type="primary", use_container_width=True)

        if run_analysis:
            # Setup progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Prepare data for models
            status_text.text("Preparing data for analysis...")
            time_steps = 15
            with st.spinner("Preparing data..."):
                X_load, y_load, scaler_load, X_solar, y_solar, scaler_solar, X_ev, y_ev, scaler_ev, X_diesel, historical_data, last_date = prepare_data_for_models(
                    st.session_state.load_df, 
                    st.session_state.solar_energy_df, 
                    st.session_state.ev_dispo_df,
                    st.session_state.diesel_df,
                    time_steps, 
                    forecast_days
                )
            progress_bar.progress(20)
            
            # Make predictions
            status_text.text("Making predictions...")
            with st.spinner("Generating forecasts..."):
                load_pred, solar_energy_pred, ev_pred_inv, date_range = make_predictions(
                    forecast_days, X_load, X_solar, X_ev,
                    scaler_load, scaler_solar, scaler_ev,
                    st.session_state.grid_load_model, 
                    st.session_state.solar_energy_model, 
                    st.session_state.ev_model,
                    last_date
                )


                initial_diesel = diesel_df['Price'].values[-15:]
                last_data = diesel_df['Price'].iloc[-1]  
                last_week = diesel_df['Date'].iloc[-1] 
                diesel_pred , date_range_diesel = forecast_diesel_price(
                    forecast_days,st.session_state.diesel_model, initial_diesel,last_data,last_week, time_steps=15
                    )

                
            progress_bar.progress(40)
            
            # Process diesel prices
            status_text.text("Processing diesel prices...")
            hours = len(load_pred)
            
            if diesel_price_type == "Time Series":
                # Map diesel prices to forecast period
                from data_utils import map_weekly_to_hourly_prices
                diesel_prices_hourly = map_weekly_to_hourly_prices(
                    date_range, 
                    diesel_pred, 
                    date_range_diesel
                )
            else:
                # Use constant diesel price
                diesel_prices_hourly = np.full(hours, diesel_price)
            
            progress_bar.progress(60)
            
            # Run optimization with V2G
            status_text.text("Running optimization with V2G...")
            with st.spinner("Optimizing with V2G..."):
                results_with_v2g = optimize_with_v2g(
                    load_pred.flatten(), 
                    solar_energy_pred.flatten(), 
                    ev_pred_inv.flatten(), 
                    hours, 
                    diesel_prices_hourly,
                    v2g_price, 
                    max_v2g_hours
                )
            progress_bar.progress(80)
            
            # Run optimization without V2G
            status_text.text("Running optimization without V2G...")
            with st.spinner("Optimizing without V2G..."):
                results_without_v2g = optimize_without_v2g(
                    load_pred.flatten(), 
                    solar_energy_pred.flatten(), 
                    hours, 
                    diesel_prices_hourly
                )
            progress_bar.progress(100)
            status_text.text("Analysis completed!")
            
            # Store results in session state
            st.session_state.results = {
                "load_pred": load_pred,
                "solar_energy_pred": solar_energy_pred,
                "ev_pred_inv": ev_pred_inv,
                "date_range": date_range,
                "diesel_prices_hourly": diesel_prices_hourly,
                "results_with_v2g": results_with_v2g,
                "results_without_v2g": results_without_v2g,
                "forecast_days": forecast_days,
                "historical_data": historical_data,
                "v2g_price": v2g_price,
                "diesel_price_type": diesel_price_type
            }
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.success("Analysis completed successfully! View the results below.")
    
    # Display results only if they exist in session state
    if 'results' in st.session_state and st.session_state.results is not None:
        results = st.session_state.results
        load_pred = results["load_pred"]
        solar_energy_pred = results["solar_energy_pred"]
        ev_pred_inv = results["ev_pred_inv"]
        date_range = results["date_range"]
        results_with_v2g = results["results_with_v2g"]
        results_without_v2g = results["results_without_v2g"]
        historical_data = results["historical_data"]
        diesel_prices_hourly = results["diesel_prices_hourly"]
        v2g_price = results["v2g_price"]
        
        # Display summary metrics
        st.markdown("## Key Performance Indicators")

        # Calculate key metrics
        if results_with_v2g and results_without_v2g:
            # Calculate all metrics
            total_load = float(sum(load_pred.flatten()))
            cost_savings = float(results_without_v2g['total_cost'] - results_with_v2g['total_cost'])
            percent_savings = float((cost_savings / results_without_v2g['total_cost']) * 100) if results_without_v2g['total_cost'] > 0 else 0
            diesel_reduction = float(results_without_v2g['total_diesel_energy'] - results_with_v2g['total_diesel_energy'])
            percent_diesel_reduction = float((diesel_reduction / results_without_v2g['total_diesel_energy']) * 100) if results_without_v2g['total_diesel_energy'] > 0 else 0
            
            # Load trend data
            prediction_length = len(load_pred)
            current_load = float(sum(load_pred))
            previous_load = float(sum(load_df['Load'][-prediction_length*2:-prediction_length]))
            load_diff = current_load - previous_load
            load_diff_percent = float((load_diff / previous_load) * 100) if previous_load > 0 else 0
            
            # Create main layout with two columns
            col_load, col_v2g = st.columns([1, 2])
            
            # Total Load with trend
            with col_load:
                st.metric(
                    "Total Load", 
                    f"{total_load:.2f} MWh", 
                    delta=f"{load_diff_percent:.1f}%" if load_diff != 0 else None,
                    delta_color="inverse" if load_diff < 0 else "normal"
                )
            
            # Right column - V2G vs Without V2G comparison
            with col_v2g:                
                # Create sub-columns for V2G metrics
                v2g_col1, v2g_col2, v2g_col3 = st.columns(3)
                
                with v2g_col1:
                    st.metric(
                        "Cost Savings with v2g", 
                        f"{cost_savings:,.2f} MAD", 
                        f"{percent_savings:.1f}%",
                        delta_color="normal"
                    )
                
                with v2g_col2:
                    st.metric(
                        "Diesel Reduction with v2g", 
                        f"{diesel_reduction:.2f} MWh", 
                        f"{percent_diesel_reduction:.1f}%",
                        delta_color="normal"
                    )
                
                with v2g_col3:
                    st.metric(
                        "V2G Energy Used", 
                        f"{results_with_v2g['total_v2g_energy']:.2f} MWh", 
                        delta=None
                    )
                                
            # Display diesel price info
            if results["diesel_price_type"] == "Time Series":
                st.info(f"Using time-varying diesel prices (range: {min(diesel_prices_hourly):.0f} - {max(diesel_prices_hourly):.0f} MAD/MWh)")
            else:
                st.info(f"Using constant diesel price: {diesel_prices_hourly[0]:.0f} MAD/MWh")
            
            # Display charts
            st.markdown("## Energy Forecast and Historical Comparison")
            
            # Predictions chart with historical data
            predictions_fig = plot_predictions_with_historical(
                date_range, load_pred, solar_energy_pred, ev_pred_inv, historical_data
            )
            st.plotly_chart(predictions_fig, use_container_width=True)
            
            st.markdown("## Optimization Results")
            
            # Optimization results chart
            optimization_fig = plot_optimization_results(
                results_with_v2g, results_without_v2g, date_range, load_pred
            )
            st.plotly_chart(optimization_fig, use_container_width=True)
            
            # Energy sources and cost comparison (side by side)
            st.markdown("## Energy Distribution & Cost Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                energy_charts = create_energy_distribution_charts(
                    results_with_v2g, results_without_v2g, load_pred
                )
                st.plotly_chart(energy_charts, use_container_width=True)
            
            with col2:
                cost_chart = create_cost_comparison_chart(
                    results_with_v2g, results_without_v2g
                )
                st.plotly_chart(cost_chart, use_container_width=True)
            
            # Display recommendations
            st.markdown("## Optimization Recommendations")
            recommendations = get_user_recommendations(
                results_with_v2g, 
                results_without_v2g, 
                v2g_price, 
                np.mean(diesel_prices_hourly), 
                max_v2g_hours
            )
            
            for i, recommendation in enumerate(recommendations):
                st.info(recommendation)

with tab2:
    if 'results' not in st.session_state or st.session_state.results is None:
        st.info("Please run the analysis from the Dashboard tab first.")
    else:
        results = st.session_state.results
        
        st.markdown("## V2G Usage Analysis")
        
        results["date_range"] = np.array(results["date_range"])

        # V2G usage analysis
        if results["results_with_v2g"]:
            v2g_usage = results["results_with_v2g"]['v2g_used']
            significant_v2g = (v2g_usage > 0.1)  # Using 0.1 MW as threshold
            
            if sum(significant_v2g) > 0:
                # V2G usage chart
                v2g_fig = plot_v2g_usage(
                    results["date_range"][significant_v2g], 
                    v2g_usage[significant_v2g],
                    results["load_pred"].flatten()[significant_v2g]
                )
                st.plotly_chart(v2g_fig, use_container_width=True)
                
                # V2G usage table
                st.markdown("### Peak Hours When V2G is Used")
                peak_v2g_df = pd.DataFrame({
                    "Date": results["date_range"][significant_v2g],
                    "Hour": [d.hour for d in results["date_range"][significant_v2g]],
                    "Load (MW)": results["load_pred"].flatten()[significant_v2g],
                    "V2G Used (MW)": v2g_usage[significant_v2g]
                })
                st.dataframe(peak_v2g_df, use_container_width=True)
            else:
                st.info("No significant V2G usage detected in this forecast period.")
        
        st.markdown("## Hourly Energy Analysis")
        
        if results["results_with_v2g"] and results["results_without_v2g"]:
            diesel_prices = results["diesel_prices_hourly"]
            v2g_price = results["v2g_price"]
            
            # Create detailed hourly comparison dataframe
            hourly_data = pd.DataFrame({
                "Date": results["date_range"],
                "Hour": [d.hour for d in results["date_range"]],
                "Load (MW)": results["load_pred"].flatten(),
                "Solar Generation (MW)": results["solar_energy_pred"].flatten(),
                "EV Available (MW)": results["ev_pred_inv"].flatten(),
                "Solar Used (with V2G) (MW)": results["results_with_v2g"]["solar_used"],
                "V2G Used (MW)": results["results_with_v2g"]["v2g_used"],
                "Diesel Used (with V2G) (MW)": results["results_with_v2g"]["diesel_used"],
                "Diesel Price (MAD/MWh)": diesel_prices,
                "Solar Used (without V2G) (MW)": results["results_without_v2g"]["solar_used"],
                "Diesel Used (without V2G) (MW)": results["results_without_v2g"]["diesel_used"]
            })
            
            # Add calculated columns
            hourly_data["Diesel Savings (MW)"] = hourly_data["Diesel Used (without V2G) (MW)"] - hourly_data["Diesel Used (with V2G) (MW)"]
            hourly_data["Diesel Cost (with V2G) (MAD)"] = hourly_data["Diesel Used (with V2G) (MW)"] * hourly_data["Diesel Price (MAD/MWh)"]
            hourly_data["Diesel Cost (without V2G) (MAD)"] = hourly_data["Diesel Used (without V2G) (MW)"] * hourly_data["Diesel Price (MAD/MWh)"]
            hourly_data["V2G Cost (MAD)"] = hourly_data["V2G Used (MW)"] * v2g_price
            hourly_data["Cost Savings (MAD)"] = hourly_data["Diesel Cost (without V2G) (MAD)"] - (hourly_data["Diesel Cost (with V2G) (MAD)"] + hourly_data["V2G Cost (MAD)"])
            
            # Display the hourly data
            st.dataframe(hourly_data, use_container_width=True)
            
            # Add download button for CSV
            csv = hourly_data.to_csv(index=False)
            st.download_button(
                label="Download Energy Analysis (CSV)",
                data=csv,
                file_name=f"v2g_hourly_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

with tab3:
    if 'results' not in st.session_state or st.session_state.results is None:
        st.info("Please run the analysis from the Dashboard tab first.")
    else:
        st.markdown("## Optimization Reports")
        
        results = st.session_state.results
        
        # Create Excel report for download
        if results["results_with_v2g"] and results["results_without_v2g"]:
            with st.spinner("Generating report..."):
                excel_file = create_excel_report(
                    results["results_with_v2g"], 
                    results["results_without_v2g"], 
                    results["date_range"], 
                    results["load_pred"],
                    results["forecast_days"],
                    results["diesel_prices_hourly"],
                    results["v2g_price"]
                )
            
            st.download_button(
                label="Download Complete Report (Excel)",
                data=excel_file,
                file_name=f"v2g_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("### Report Contents")
            st.markdown("""
            The downloaded report includes:
            - Complete hourly optimization data
            - Energy source distribution analysis
            - Cost comparison between V2G and non-V2G scenarios
            - Summary statistics and key performance indicators
            - V2G usage patterns and peak hour analysis
            """)
            
            st.markdown("### Recommendations")
            
            # Generate some simple recommendations based on the results
            cost_savings = results["results_without_v2g"]['total_cost'] - results["results_with_v2g"]['total_cost']
            percent_savings = (cost_savings / results["results_without_v2g"]['total_cost']) * 100
            
            if percent_savings > 15:
                recommendation = "V2G integration shows substantial cost benefits. Consider increasing V2G capacity for greater savings."
            elif percent_savings > 5:
                recommendation = "V2G integration provides moderate cost benefits. Current implementation is effective."
            else:
                recommendation = "V2G benefits are minimal with current parameters. Consider adjusting V2G pricing or increasing maximum V2G hours."
            
            st.info(recommendation)

with tab4:
    st.markdown("## Model Training")
    
    st.markdown("""
    ### Upload New Data and Retrain Models
    
    Use this section to upload new data and retrain the prediction models. This allows you to improve forecast accuracy 
    by incorporating the latest data points.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Upload New Data")
        st.markdown("Upload new data files in Excel format (.xlsx)")
        
        load_file = st.file_uploader("Upload Load Data", type=["xlsx"], key="load_uploader")
        solar_file = st.file_uploader("Upload Solar Energy Data", type=["xlsx"], key="solar_uploader")
        ev_file = st.file_uploader("Upload EV Availability Data", type=["xlsx"], key="ev_uploader")
        diesel_file = st.file_uploader("Upload Diesel Price Data", type=["xlsx"], key="diesel_uploader")
        
        if load_file and solar_file and ev_file:
            st.success("All required data files uploaded!")
            
            if st.button("Process Uploaded Data", use_container_width=True):
                # Create data directory if it doesn't exist
                os.makedirs("data", exist_ok=True)
                
                # Save uploaded files
                with open(os.path.join("data", "Total_Load.xlsx"), "wb") as f:
                    f.write(load_file.getvalue())
                
                with open(os.path.join("data", "Solar_Energy.xlsx"), "wb") as f:
                    f.write(solar_file.getvalue())
                
                with open(os.path.join("data", "total_power_EV_disponible.xlsx"), "wb") as f:
                    f.write(ev_file.getvalue())
                
                if diesel_file:
                    with open(os.path.join("data", "diesel_price_weekly.xlsx"), "wb") as f:
                        f.write(diesel_file.getvalue())
                
                st.session_state.data_loaded = False  # Reset to force reload
                st.success("Data saved successfully! Please reload data from the sidebar.")
    
    with col2:
        st.markdown("### Train Models")
        st.markdown("Retrain prediction models with the latest data")
        
        if not st.session_state.data_loaded:
            st.warning("Please load data first before training models.")
        else:
            epochs = st.slider("Training Epochs", min_value=10, max_value=200, value=50)
            batch_size = st.selectbox("Batch Size", options=[16, 32, 64, 128], index=1)
            
            train_button = st.button("Train Models", type="primary", use_container_width=True)
            
            if train_button:
                # Create models directory if it doesn't exist
                os.makedirs("models", exist_ok=True)
                
                # Training progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Train load model
                status_text.text("Training Load model...")
                with st.spinner("Training in progress..."):
                    train_model(
                        st.session_state.load_df, 
                        'Load', 
                        epochs, 
                        batch_size, 
                        progress_callback=lambda p: progress_bar.progress(p * 0.33)
                    )
                
                # Train solar model
                status_text.text("Training Solar Energy model...")
                with st.spinner("Training in progress..."):
                    train_model(
                        st.session_state.solar_energy_df, 
                        'SolarEnergy', 
                        epochs, 
                        batch_size, 
                        progress_callback=lambda p: progress_bar.progress(0.33 + p * 0.33)
                    )
                
                # Train EV model
                status_text.text("Training EV Availability model...")
                with st.spinner("Training in progress..."):
                    train_model(
                        st.session_state.ev_dispo_df, 
                        'total_usable_power_all_profiles_MW', 
                        epochs, 
                        batch_size, 
                        progress_callback=lambda p: progress_bar.progress(0.66 + p * 0.34)
                    )
                
                # Reset the progress indicators
                progress_bar.progress(100)
                status_text.text("Training completed!")
                
                st.session_state.models_loaded = False  # Reset to force reload
                st.session_state.training_completed = True
                
                st.success("Models trained successfully! Please reload models from the sidebar.")