import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_predictions_with_historical(date_range, load_pred, solar_energy_pred, ev_pred_inv, historical_data):
    """Create an interactive plot comparing forecasts with historical data."""
    fig = make_subplots(rows=3, cols=1, 
                       subplot_titles=("Grid Load Comparison", 
                                     "Solar Generation Comparison",
                                     "EV Availability Comparison"),
                       vertical_spacing=0.1,
                       shared_xaxes=True)
    
    # Plot Load comparison
    fig.add_trace(
        go.Scatter(x=date_range, y=load_pred.flatten(),
                  name='Load Forecast', line=dict(color='#0068c9', width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=historical_data['date_range'], y=historical_data['load'],
                  name='Historical Load', line=dict(color='#0068c9', width=2, dash='dot')),
        row=1, col=1
    )
    
    # Add vertical line separating historical and forecast
    if len(historical_data['date_range']) > 0:
        last_historical = historical_data['date_range'].iloc[-1]
        for row in range(1, 4):
            fig.add_vline(x=last_historical, line=dict(color='rgba(0,0,0,0.3)', width=1, dash='dash'), row=row, col=1)
    
    # Plot Solar comparison
    fig.add_trace(
        go.Scatter(x=date_range, y=solar_energy_pred.flatten(),
                  name='Solar Forecast', line=dict(color='#f8b83c', width=2)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=historical_data['date_range'], y=historical_data['solar'],
                  name='Historical Solar', line=dict(color='#f8b83c', width=2, dash='dot')),
        row=2, col=1
    )
    
    # Plot EV comparison
    fig.add_trace(
        go.Scatter(x=date_range, y=ev_pred_inv.flatten(),
                  name='EV Forecast', line=dict(color='#39a275', width=2)),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=historical_data['date_range'], y=historical_data['ev'],
                  name='Historical EV', line=dict(color='#39a275', width=2, dash='dot')),
        row=3, col=1
    )
    
    # Add annotations explaining the vertical line
    fig.add_annotation(
        x=last_historical if len(historical_data['date_range']) > 0 else date_range[0],
        y=max(load_pred.flatten()) * 0.9,
        text="Historical | Forecast",
        showarrow=False,
        font=dict(size=12, color="rgba(0,0,0,0.5)"),
        xanchor="center",
        row=1, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        template="plotly_white",
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )
    
    # Update axes
    fig.update_xaxes(title_text="Time", row=3, col=1)
    fig.update_yaxes(title_text="Power (MW)", row=1, col=1)
    fig.update_yaxes(title_text="Power (MW)", row=2, col=1)
    fig.update_yaxes(title_text="Power (MW)", row=3, col=1)
    
    # Add range slider
    fig.update_layout(
        xaxis3=dict(
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    return fig

def plot_optimization_results(results_with_v2g, results_without_v2g, date_range, load_pred):
    """Create an interactive plot for optimization results."""
    fig = go.Figure()
    
    # Add load trace
    fig.add_trace(go.Scatter(
        x=date_range,
        y=load_pred.flatten(),
        mode='lines',
        name='Grid Load (MW)',
        line=dict(color='#0068c9', width=2, dash='dash')
    ))
    
    if results_with_v2g:
        # Add solar with V2G
        fig.add_trace(go.Scatter(
            x=date_range,
            y=results_with_v2g['solar_used'],
            mode='lines',
            name='Solar Used (with V2G)',
            line=dict(color='#f8b83c', width=2),
            stackgroup='with_v2g'
        ))
        
        # Add V2G
        fig.add_trace(go.Scatter(
            x=date_range,
            y=results_with_v2g['v2g_used'],
            mode='lines',
            name='V2G Used',
            line=dict(color='#39a275', width=2),
            stackgroup='with_v2g'
        ))
        
        # Add diesel with V2G
        fig.add_trace(go.Scatter(
            x=date_range,
            y=results_with_v2g['diesel_used'],
            mode='lines',
            name='Diesel Used (with V2G)',
            line=dict(color='#dc3545', width=2),
            stackgroup='with_v2g'
        ))
    
    if results_without_v2g:
        # Add diesel without V2G
        fig.add_trace(go.Scatter(
            x=date_range,
            y=results_without_v2g['diesel_used'],
            mode='lines',
            name='Diesel Used (without V2G)',
            line=dict(color='#9a031e', width=2, dash='dot')
        ))
    
    # Update layout
    fig.update_layout(
        title="Energy Source Usage Over Time",
        xaxis_title="Time",
        yaxis_title="Power (MW)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5
        ),
        template="plotly_white",
        margin=dict(l=20, r=20, t=70, b=20),
        hovermode="x unified"
    )
    
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    return fig

def create_energy_distribution_charts(results_with_v2g, results_without_v2g, load_pred):
    """Create energy distribution pie charts."""
    # Calculate energy values
    solar_energy_with_v2g = np.sum(results_with_v2g['solar_used'])
    v2g_energy = results_with_v2g['total_v2g_energy']
    diesel_energy_with_v2g = results_with_v2g['total_diesel_energy']
    
    solar_energy_without_v2g = np.sum(results_without_v2g['solar_used'])
    diesel_energy_without_v2g = results_without_v2g['total_diesel_energy']
    
    total_energy = np.sum(load_pred)
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "pie"}]],
        subplot_titles=("Energy Sources with V2G", "Energy Sources without V2G")
    )
    
    # Add traces
    fig.add_trace(
        go.Pie(
            labels=["Solar", "V2G", "Diesel"],
            values=[solar_energy_with_v2g, v2g_energy, diesel_energy_with_v2g],
            textinfo="percent+label",
            marker=dict(colors=['#f8b83c', '#39a275', '#dc3545']),
            hole=0.4,
            hoverinfo="label+percent+value",
            hovertemplate="%{label}: %{value:.2f} MWh (%{percent})<extra></extra>",
            pull=[0, 0.05, 0]
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Pie(
            labels=["Solar", "Diesel"],
            values=[solar_energy_without_v2g, diesel_energy_without_v2g],
            textinfo="percent+label",
            marker=dict(colors=['#f8b83c', '#9a031e']),
            hole=0.4,
            hoverinfo="label+percent+value",
            hovertemplate="%{label}: %{value:.2f} MWh (%{percent})<extra></extra>",
            pull=[0, 0.05]
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="Energy Source Distribution",
        template="plotly_white",
        margin=dict(t=80, b=20),
        annotations=[
            dict(
                text=f"Total: {total_energy:.2f} MWh",
                showarrow=False,
                x=0.225,
                y=0.5
            ),
            dict(
                text=f"Total: {total_energy:.2f} MWh",
                showarrow=False,
                x=0.775,
                y=0.5
            )
        ]
    )
    
    return fig

def create_cost_comparison_chart(results_with_v2g, results_without_v2g):
    """Create cost comparison chart."""
    # Calculate costs
    diesel_cost_with_v2g = results_with_v2g['total_diesel_cost']
    v2g_cost = results_with_v2g['total_v2g_cost']
    total_cost_with_v2g = results_with_v2g['total_cost']
    
    diesel_cost_without_v2g = results_without_v2g['total_diesel_cost']
    
    cost_savings = diesel_cost_without_v2g - total_cost_with_v2g
    percent_savings = (cost_savings / diesel_cost_without_v2g) * 100
    
    # Create figure
    fig = go.Figure()
    
    # Add with V2G costs
    fig.add_trace(go.Bar(
        x=["With V2G"],
        y=[diesel_cost_with_v2g],
        name="Diesel Cost",
        marker_color="#dc3545",
        text=f"{diesel_cost_with_v2g:,.0f} MAD",
        textposition="auto"
    ))
    
    fig.add_trace(go.Bar(
        x=["With V2G"],
        y=[v2g_cost],
        name="V2G Cost",
        marker_color="#39a275",
        text=f"{v2g_cost:,.0f} MAD",
        textposition="auto"
    ))
    
    # Add without V2G costs
    fig.add_trace(go.Bar(
        x=["Without V2G"],
        y=[diesel_cost_without_v2g],
        name="Diesel Cost",
        marker_color="#9a031e",
        text=f"{diesel_cost_without_v2g:,.0f} MAD",
        textposition="auto"
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Cost Comparison (Savings: {cost_savings:,.0f} MAD, {percent_savings:.1f}%)",
        xaxis_title="Scenario",
        yaxis_title="Cost (MAD)",
        barmode="stack",
        template="plotly_white",
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def plot_v2g_usage(date_range, v2g_usage, load_values):
    """Create a plot showing V2G usage patterns."""
    # Convert boolean mask to indices
    if isinstance(date_range, pd.Series):
        date_range = date_range.values
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add V2G usage as bars
    fig.add_trace(
        go.Bar(
            x=date_range,
            y=v2g_usage,
            name="V2G Usage (MW)",
            marker_color="#39a275",
            opacity=0.7,
            hovertemplate="Time: %{x}<br>V2G Usage: %{y:.2f} MW<extra></extra>"
        ),
        secondary_y=False
    )
    
    # Add load as line
    fig.add_trace(
        go.Scatter(
            x=date_range,
            y=load_values,
            mode="lines",
            name="Grid Load (MW)",
            line=dict(color="#0068c9", width=2),
            hovertemplate="Time: %{x}<br>Grid Load: %{y:.2f} MW<extra></extra>"
        ),
        secondary_y=True
    )
    
    # Add peak hour shading
    peak_hours = [h for h in range(len(date_range)) if pd.to_datetime(date_range[h]).hour in [9, 10, 11, 12, 17, 18, 19, 20]]
    
    for i in peak_hours:
        if i < len(date_range):
            fig.add_vrect(
                x0=date_range[i] - pd.Timedelta(minutes=30),
                x1=date_range[i] + pd.Timedelta(minutes=30),
                fillcolor="rgba(255, 235, 153, 0.2)",
                line_width=0,
                annotation_text="Peak" if i == min(peak_hours) else None,
                annotation_position="top left"
            )
    
    # Update layout
    fig.update_layout(
        title="V2G Usage During Peak Hours",
        template="plotly_white",
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5
        ),
        hovermode="x unified",
        barmode="relative"
    )
    
    # Update axes
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="V2G Power (MW)", secondary_y=False)
    fig.update_yaxes(title_text="Grid Load (MW)", secondary_y=True)
    
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    return fig