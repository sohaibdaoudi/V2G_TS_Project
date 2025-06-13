import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np

# Import our modules
from data_utils import load_data, prepare_data_for_models
from model_utils import load_prediction_models, make_predictions
from optimization import optimize_with_v2g, optimize_without_v2g
from visualization import (
    plot_predictions_with_historical,
    plot_optimization_results,
    create_energy_distribution_charts,
    create_cost_comparison_chart,
    plot_v2g_usage
)
from utils import create_excel_report

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

# App header
st.markdown("""
<div class="header">
    <h1>V2G Energy Optimization Dashboard</h1>
    <p class="subtitle">Intelligent energy management with Vehicle-to-Grid technology</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://images.pexels.com/photos/250609/pexels-photo-250609.jpeg", width=80)
    st.markdown("## Dashboard Controls")
    
    # Forecast settings
    st.markdown("### Forecast Settings")
    forecast_days = st.slider(
        "Forecast Duration (Days)", 
        min_value=1, 
        max_value=7, 
        value=3,
        help="Select the number of days to forecast"
    )
    
    st.markdown("### Optimization Parameters")
    diesel_price = st.number_input(
        "Diesel Price (MAD/MWh)", 
        min_value=1000, 
        max_value=5000, 
        value=2500,
        step=100
    )
    
    v2g_price = st.number_input(
        "V2G Price (MAD/MWh)", 
        min_value=50, 
        max_value=500, 
        value=200,
        step=10
    )
    
    max_v2g_hours = st.slider(
        "Maximum V2G Hours per Day", 
        min_value=1, 
        max_value=6, 
        value=3
    )
    
    st.markdown("---")
    st.markdown("*© 2025 V2G Energy Optimization*")

# Main content
tab1, tab2, tab3 = st.tabs(["Dashboard", "Detailed Analysis", "Reports"])

with tab1:
    # Load data and models
    with st.spinner("Loading data and models..."):
        load_df, solar_energy_df, ev_dispo_df = load_data()
        grid_load_model, solar_energy_model, ev_model = load_prediction_models()
        
        if load_df is not None and solar_energy_df is not None and ev_dispo_df is not None:
            # Prepare data for models
            time_steps = 15
            X_test_load, X_test_solar, X_test_ev, scaler_y, historical_data, last_date = prepare_data_for_models(
                load_df, solar_energy_df, ev_dispo_df, time_steps, forecast_days
            )

    # Setup app state for storing results
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    # Auto-run analysis
    with st.spinner("Running analysis..."):
        # Make predictions
        load_pred, solar_energy_pred, ev_pred_inv, date_range = make_predictions(
            forecast_days, X_test_load, X_test_solar, X_test_ev, scaler_y,
            grid_load_model, solar_energy_model, ev_model, last_date
        )
        
        # Run optimization
        hours = len(load_pred)
        
        # Run optimization with V2G
        results_with_v2g = optimize_with_v2g(
            load_pred.flatten(), 
            solar_energy_pred.flatten(), 
            ev_pred_inv.flatten(), 
            hours, 
            v2g_price, 
            diesel_price,
            max_v2g_hours
        )
        
        # Run optimization without V2G
        results_without_v2g = optimize_without_v2g(
            load_pred.flatten(), 
            solar_energy_pred.flatten(), 
            hours, 
            diesel_price
        )
        
        # Store results in session state
        st.session_state.results = {
            "load_pred": load_pred,
            "solar_energy_pred": solar_energy_pred,
            "ev_pred_inv": ev_pred_inv,
            "date_range": date_range,
            "results_with_v2g": results_with_v2g,
            "results_without_v2g": results_without_v2g,
            "forecast_days": forecast_days,
            "historical_data": historical_data
        }
    
    # Use stored results
    results = st.session_state.results
    load_pred = results["load_pred"]
    solar_energy_pred = results["solar_energy_pred"]
    ev_pred_inv = results["ev_pred_inv"]
    date_range = results["date_range"]
    results_with_v2g = results["results_with_v2g"]
    results_without_v2g = results["results_without_v2g"]
    historical_data = results["historical_data"]
    
    # Display summary metrics
    st.markdown("## Key Performance Indicators")
    
    # Calculate key metrics
    if results_with_v2g and results_without_v2g:
        col1, col2, col3, col4 = st.columns(4)
        
        total_load = float(sum(load_pred.flatten()))
        cost_savings = results_without_v2g['total_cost'] - results_with_v2g['total_cost']
        percent_savings = (cost_savings / results_without_v2g['total_cost']) * 100 if results_without_v2g['total_cost'] > 0 else 0
        diesel_reduction = results_without_v2g['total_diesel_energy'] - results_with_v2g['total_diesel_energy']
        percent_diesel_reduction = (diesel_reduction / results_without_v2g['total_diesel_energy']) * 100 if results_without_v2g['total_diesel_energy'] > 0 else 0
        
        with col1:
            st.metric(
                "Total Load", 
                f"{total_load:.2f} MWh", 
                delta=None
            )
        
        with col2:
            st.metric(
                "Cost Savings", 
                f"{cost_savings:,.2f} MAD", 
                f"{percent_savings:.1f}%",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "Diesel Reduction", 
                f"{diesel_reduction:.2f} MWh", 
                f"{percent_diesel_reduction:.1f}%",
                delta_color="normal"
            )
        
        with col4:
            st.metric(
                "V2G Energy Used", 
                f"{results_with_v2g['total_v2g_energy']:.2f} MWh", 
                delta=None
            )
        
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


with tab2:
    if 'results' not in st.session_state or st.session_state.results is None:
        st.info("Analysis is running...")
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
                "Solar Used (without V2G) (MW)": results["results_without_v2g"]["solar_used"],
                "Diesel Used (without V2G) (MW)": results["results_without_v2g"]["diesel_used"]
            })
            
            # Add calculated columns
            hourly_data["Diesel Savings (MW)"] = hourly_data["Diesel Used (without V2G) (MW)"] - hourly_data["Diesel Used (with V2G) (MW)"]
            hourly_data["Diesel Cost (with V2G) (MAD)"] = hourly_data["Diesel Used (with V2G) (MW)"] * diesel_price
            hourly_data["Diesel Cost (without V2G) (MAD)"] = hourly_data["Diesel Used (without V2G) (MW)"] * diesel_price
            hourly_data["V2G Cost (MAD)"] = hourly_data["V2G Used (MW)"] * v2g_price
            hourly_data["Cost Savings (MAD)"] = hourly_data["Diesel Cost (without V2G) (MAD)"] - (hourly_data["Diesel Cost (with V2G) (MAD)"] + hourly_data["V2G Cost (MAD)"])
            
            # Display the hourly data
            st.dataframe(hourly_data, use_container_width=True)

with tab3:
    if 'results' not in st.session_state or st.session_state.results is None:
        st.info("Analysis is running...")
    else:
        st.markdown("## Optimization Reports")
        
        results = st.session_state.results
        
        # Create Excel report for download
        if results["results_with_v2g"] and results["results_without_v2g"]:
            excel_file = create_excel_report(
                results["results_with_v2g"], 
                results["results_without_v2g"], 
                results["date_range"], 
                results["load_pred"],
                results["forecast_days"],
                diesel_price,
                v2g_price
            )
            
            st.download_button(
                label="📊 Download Complete Report (Excel)",
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


