from io import BytesIO
import pandas as pd
import numpy as np
import streamlit as st

def create_excel_report(results_with_v2g, results_without_v2g, date_range, load_pred, 
                        forecast_days, diesel_price, v2g_price):
    """
    Create a downloadable Excel report with complete analysis results.
    
    Parameters:
    -----------
    results_with_v2g : dict
        Optimization results with V2G
    results_without_v2g : dict
        Optimization results without V2G
    date_range : array-like
        Array of dates
    load_pred : array-like
        Predicted load values
    forecast_days : int
        Number of days forecasted
    diesel_price : float
        Price of diesel energy in MAD/MWh
    v2g_price : float
        Price of V2G energy in MAD/MWh
        
    Returns:
    --------
    BytesIO
        Excel file as bytes for download
    """
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    workbook = writer.book
    
    # Add some custom formats
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'border': 1,
        'fg_color': '#D9E1F2',
        'font_size': 12
    })
    
    number_format = workbook.add_format({
        'num_format': '#,##0.00',
        'border': 1
    })
    
    currency_format = workbook.add_format({
        'num_format': '#,##0.00 "MAD"',
        'border': 1
    })
    
    percent_format = workbook.add_format({
        'num_format': '0.00%',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'num_format': 'yyyy-mm-dd hh:mm',
        'border': 1
    })
    
    total_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'fg_color': '#F2F2F2',
        'num_format': '#,##0.00'
    })
    
    total_currency_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'fg_color': '#F2F2F2',
        'num_format': '#,##0.00 "MAD"'
    })
    
    # Create summary sheet
    summary_data = {
        "Metric": [
            "Forecast Period (Days)",
            "Total Load (MWh)", 
            "Total Solar Energy Used (MWh)",
            "Diesel Price (MAD/MWh)",
            "V2G Price (MAD/MWh)"
        ],
        "Value": [
            forecast_days,
            float(np.sum(load_pred)),
            float(np.sum(results_with_v2g['solar_used'])) if results_with_v2g else float(np.sum(results_without_v2g['solar_used'])),
            diesel_price,
            v2g_price
        ]
    }
    
    if results_with_v2g:
        summary_data["Metric"].extend([
            "Total V2G Energy Used (MWh)",
            "Total Diesel Energy Used (with V2G) (MWh)",
            "Total Diesel Cost (with V2G) (MAD)",
            "Total V2G Cost (MAD)",
            "Total Cost (with V2G) (MAD)"
        ])
        summary_data["Value"].extend([
            results_with_v2g['total_v2g_energy'],
            results_with_v2g['total_diesel_energy'],
            results_with_v2g['total_diesel_cost'],
            results_with_v2g['total_v2g_cost'],
            results_with_v2g['total_cost']
        ])
    
    if results_without_v2g:
        summary_data["Metric"].extend([
            "Total Diesel Energy Used (without V2G) (MWh)",
            "Total Diesel Cost (without V2G) (MAD)"
        ])
        summary_data["Value"].extend([
            results_without_v2g['total_diesel_energy'],
            results_without_v2g['total_diesel_cost']
        ])
    
    if results_with_v2g and results_without_v2g:
        cost_savings = results_without_v2g['total_diesel_cost'] - results_with_v2g['total_cost']
        percent_savings = (cost_savings / results_without_v2g['total_diesel_cost']) * 100 / 100  # Convert to decimal for Excel
        diesel_savings = results_without_v2g['total_diesel_energy'] - results_with_v2g['total_diesel_energy']
        percent_diesel_savings = (diesel_savings / results_without_v2g['total_diesel_energy']) * 100 / 100  # Convert to decimal for Excel
        
        summary_data["Metric"].extend([
            "Diesel Energy Savings (MWh)",
            "Diesel Energy Savings (%)",
            "Cost Savings (MAD)",
            "Cost Savings (%)"
        ])
        summary_data["Value"].extend([
            diesel_savings,
            percent_diesel_savings,
            cost_savings,
            percent_savings
        ])
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    # Format summary sheet
    summary_sheet = writer.sheets['Summary']
    summary_sheet.set_column('A:A', 40)
    summary_sheet.set_column('B:B', 20)
    
    # Write headers with format
    for col_num, value in enumerate(summary_df.columns.values):
        summary_sheet.write(0, col_num, value, header_format)
    
    # Apply conditional formatting to key metrics
    summary_sheet.conditional_format('B12:B12', {'type': 'cell',
                                              'criteria': '>',
                                              'value': 0,
                                              'format': workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})})
    
    summary_sheet.conditional_format('B14:B14', {'type': 'cell',
                                              'criteria': '>',
                                              'value': 0,
                                              'format': workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})})
    
    hours = len(date_range)
    
    # Create hourly data sheet with V2G
    if results_with_v2g:
        df_with_v2g = pd.DataFrame({
            "Date": date_range,
            "Hour": [d.hour for d in date_range],
            "Day": [d.day for d in date_range],
            "Load (MW)": load_pred.flatten(),
            "Solar Used (MW)": results_with_v2g['solar_used'],
            "V2G Used (MW)": results_with_v2g['v2g_used'],
            "Diesel Used (MW)": results_with_v2g['diesel_used'],
            "Diesel Cost (MAD)": results_with_v2g['diesel_used'] * diesel_price,
            "V2G Cost (MAD)": results_with_v2g['v2g_used'] * v2g_price,
            "Total Cost (MAD)": (results_with_v2g['diesel_used'] * diesel_price) + 
                               (results_with_v2g['v2g_used'] * v2g_price)
        })
        
        df_with_v2g.to_excel(writer, sheet_name='With V2G', index=False)
        
        # Format With V2G sheet
        with_v2g_sheet = writer.sheets['With V2G']
        with_v2g_sheet.set_column('A:A', 20, date_format)
        with_v2g_sheet.set_column('B:D', 8)
        with_v2g_sheet.set_column('E:G', 15, number_format)
        with_v2g_sheet.set_column('H:J', 18, currency_format)
        
        # Write headers with format
        for col_num, value in enumerate(df_with_v2g.columns.values):
            with_v2g_sheet.write(0, col_num, value, header_format)
        
        # Add totals row
        total_row = len(df_with_v2g) + 1
        with_v2g_sheet.write(total_row, 0, "TOTAL", total_format)
        with_v2g_sheet.write_formula(total_row, 4, f'=SUM(E2:E{total_row})', total_format)
        with_v2g_sheet.write_formula(total_row, 5, f'=SUM(F2:F{total_row})', total_format)
        with_v2g_sheet.write_formula(total_row, 6, f'=SUM(G2:G{total_row})', total_format)
        with_v2g_sheet.write_formula(total_row, 7, f'=SUM(H2:H{total_row})', total_currency_format)
        with_v2g_sheet.write_formula(total_row, 8, f'=SUM(I2:I{total_row})', total_currency_format)
        with_v2g_sheet.write_formula(total_row, 9, f'=SUM(J2:J{total_row})', total_currency_format)
    
    # Create hourly data sheet without V2G
    if results_without_v2g:
        df_without_v2g = pd.DataFrame({
            "Date": date_range,
            "Hour": [d.hour for d in date_range],
            "Day": [d.day for d in date_range],
            "Load (MW)": load_pred.flatten(),
            "Solar Used (MW)": results_without_v2g['solar_used'],
            "Diesel Used (MW)": results_without_v2g['diesel_used'],
            "Diesel Cost (MAD)": results_without_v2g['diesel_used'] * diesel_price,
            "Total Cost (MAD)": results_without_v2g['diesel_used'] * diesel_price
        })
        
        df_without_v2g.to_excel(writer, sheet_name='Without V2G', index=False)
        
        # Format Without V2G sheet
        without_v2g_sheet = writer.sheets['Without V2G']
        without_v2g_sheet.set_column('A:A', 20, date_format)
        without_v2g_sheet.set_column('B:D', 8)
        without_v2g_sheet.set_column('E:F', 15, number_format)
        without_v2g_sheet.set_column('G:H', 18, currency_format)
        
        # Write headers with format
        for col_num, value in enumerate(df_without_v2g.columns.values):
            without_v2g_sheet.write(0, col_num, value, header_format)
        
        # Add totals row
        total_row = len(df_without_v2g) + 1
        without_v2g_sheet.write(total_row, 0, "TOTAL", total_format)
        without_v2g_sheet.write_formula(total_row, 4, f'=SUM(E2:E{total_row})', total_format)
        without_v2g_sheet.write_formula(total_row, 5, f'=SUM(F2:F{total_row})', total_format)
        without_v2g_sheet.write_formula(total_row, 6, f'=SUM(G2:G{total_row})', total_currency_format)
        without_v2g_sheet.write_formula(total_row, 7, f'=SUM(H2:H{total_row})', total_currency_format)
    
    # Create comparison sheet
    if results_with_v2g and results_without_v2g:
        df_comparison = pd.DataFrame({
            "Date": date_range,
            "Hour": [d.hour for d in date_range],
            "Day": [d.day for d in date_range],
            "Load (MW)": load_pred.flatten(),
            "Diesel Used (with V2G) (MW)": results_with_v2g['diesel_used'],
            "Diesel Used (without V2G) (MW)": results_without_v2g['diesel_used'],
            "Diesel Savings (MW)": results_without_v2g['diesel_used'] - results_with_v2g['diesel_used'],
            "Cost (with V2G) (MAD)": (results_with_v2g['diesel_used'] * diesel_price) + 
                                    (results_with_v2g['v2g_used'] * v2g_price),
            "Cost (without V2G) (MAD)": results_without_v2g['diesel_used'] * diesel_price,
            "Cost Savings (MAD)": (results_without_v2g['diesel_used'] * diesel_price) - 
                                 ((results_with_v2g['diesel_used'] * diesel_price) + 
                                  (results_with_v2g['v2g_used'] * v2g_price)),
            "Savings (%)": (((results_without_v2g['diesel_used'] * diesel_price) - 
                           ((results_with_v2g['diesel_used'] * diesel_price) + 
                            (results_with_v2g['v2g_used'] * v2g_price))) / 
                          (results_without_v2g['diesel_used'] * diesel_price) * 100) / 100  # Convert to decimal for Excel
        })
        
        df_comparison.to_excel(writer, sheet_name='Comparison', index=False)
        
        # Format Comparison sheet
        comparison_sheet = writer.sheets['Comparison']
        comparison_sheet.set_column('A:A', 20, date_format)
        comparison_sheet.set_column('B:D', 8)
        comparison_sheet.set_column('E:G', 15, number_format)
        comparison_sheet.set_column('H:J', 18, currency_format)
        comparison_sheet.set_column('K:K', 12, percent_format)
        
        # Write headers with format
        for col_num, value in enumerate(df_comparison.columns.values):
            comparison_sheet.write(0, col_num, value, header_format)
            
        # Add conditional formatting for savings
        comparison_sheet.conditional_format(f'G2:G{len(df_comparison)+1}', {
            'type': '3_color_scale',
            'min_color': "#FFFFFF",
            'mid_color': "#B7E1CD",
            'max_color': "#009E73"
        })
        
        comparison_sheet.conditional_format(f'J2:J{len(df_comparison)+1}', {
            'type': '3_color_scale',
            'min_color': "#FFFFFF",
            'mid_color': "#B7E1CD",
            'max_color': "#009E73"
        })
        
        # Add totals row
        total_row = len(df_comparison) + 1
        comparison_sheet.write(total_row, 0, "TOTAL", total_format)
        comparison_sheet.write_formula(total_row, 4, f'=SUM(E2:E{total_row})', total_format)
        comparison_sheet.write_formula(total_row, 5, f'=SUM(F2:F{total_row})', total_format)
        comparison_sheet.write_formula(total_row, 6, f'=SUM(G2:G{total_row})', total_format)
        comparison_sheet.write_formula(total_row, 7, f'=SUM(H2:H{total_row})', total_currency_format)
        comparison_sheet.write_formula(total_row, 8, f'=SUM(I2:I{total_row})', total_currency_format)
        comparison_sheet.write_formula(total_row, 9, f'=SUM(J2:J{total_row})', total_currency_format)
        comparison_sheet.write_formula(total_row, 10, f'=J{total_row+1}/I{total_row+1}', percent_format)
    
    # Create daily summary
    if results_with_v2g and results_without_v2g:
        # Create datetime objects for grouping
        date_only = [d.date() for d in date_range]
        
        daily_summary_data = {
            "Day": [],
            "Load (MWh)": [],
            "Solar Used (MWh)": [],
            "V2G Used (MWh)": [],
            "Diesel Used (with V2G) (MWh)": [],
            "Diesel Used (without V2G) (MWh)": [],
            "Diesel Savings (MWh)": [],
            "Cost (with V2G) (MAD)": [],
            "Cost (without V2G) (MAD)": [],
            "Cost Savings (MAD)": [],
            "Savings (%)": []
        }
        
        # Group by day
        unique_days = sorted(set(date_only))
        
        for day in unique_days:
            indices = [i for i, d in enumerate(date_only) if d == day]
            
            daily_summary_data["Day"].append(day)
            daily_summary_data["Load (MWh)"].append(sum(load_pred.flatten()[indices]))
            daily_summary_data["Solar Used (MWh)"].append(sum(results_with_v2g['solar_used'][indices]))
            daily_summary_data["V2G Used (MWh)"].append(sum(results_with_v2g['v2g_used'][indices]))
            daily_summary_data["Diesel Used (with V2G) (MWh)"].append(sum(results_with_v2g['diesel_used'][indices]))
            daily_summary_data["Diesel Used (without V2G) (MWh)"].append(sum(results_without_v2g['diesel_used'][indices]))
            
            diesel_savings = sum(results_without_v2g['diesel_used'][indices]) - sum(results_with_v2g['diesel_used'][indices])
            daily_summary_data["Diesel Savings (MWh)"].append(diesel_savings)
            
            cost_with_v2g = sum(results_with_v2g['diesel_used'][indices]) * diesel_price + sum(results_with_v2g['v2g_used'][indices]) * v2g_price
            cost_without_v2g = sum(results_without_v2g['diesel_used'][indices]) * diesel_price
            
            daily_summary_data["Cost (with V2G) (MAD)"].append(cost_with_v2g)
            daily_summary_data["Cost (without V2G) (MAD)"].append(cost_without_v2g)
            
            cost_savings = cost_without_v2g - cost_with_v2g
            daily_summary_data["Cost Savings (MAD)"].append(cost_savings)
            
            if cost_without_v2g > 0:
                savings_percent = cost_savings / cost_without_v2g
            else:
                savings_percent = 0
                
            daily_summary_data["Savings (%)"].append(savings_percent)
        
        # Create DataFrame and write to Excel
        daily_df = pd.DataFrame(daily_summary_data)
        daily_df.to_excel(writer, sheet_name='Daily Summary', index=False)
        
        # Format Daily Summary sheet
        daily_sheet = writer.sheets['Daily Summary']
        daily_sheet.set_column('A:A', 15)
        daily_sheet.set_column('B:G', 18, number_format)
        daily_sheet.set_column('H:J', 25, currency_format)
        daily_sheet.set_column('K:K', 15, percent_format)
        
        # Write headers with format
        for col_num, value in enumerate(daily_df.columns.values):
            daily_sheet.write(0, col_num, value, header_format)
            
        # Add chart for daily comparison
        chart = workbook.add_chart({'type': 'column'})
        
        # Add series to chart
        chart.add_series({
            'name': 'Cost (with V2G)',
            'categories': ['Daily Summary', 1, 0, len(daily_df), 0],
            'values': ['Daily Summary', 1, 7, len(daily_df), 7],
            'fill': {'color': '#3B82F6'}
        })
        
        chart.add_series({
            'name': 'Cost (without V2G)',
            'categories': ['Daily Summary', 1, 0, len(daily_df), 0],
            'values': ['Daily Summary', 1, 8, len(daily_df), 8],
            'fill': {'color': '#DC3545'}
        })
        
        # Set chart title, labels, and legend
        chart.set_title({'name': 'Daily Cost Comparison'})
        chart.set_x_axis({'name': 'Day'})
        chart.set_y_axis({'name': 'Cost (MAD)'})
        chart.set_legend({'position': 'bottom'})
        
        # Insert chart into the Daily Summary sheet
        daily_sheet.insert_chart('M2', chart, {'x_scale': 1.5, 'y_scale': 1.5})
        
        # Add totals row
        total_row = len(daily_df) + 1
        daily_sheet.write(total_row, 0, "TOTAL", total_format)
        for col in range(1, 10):
            daily_sheet.write_formula(total_row, col, f'=SUM({chr(65+col)}2:{chr(65+col)}{total_row})', total_format if col < 7 else total_currency_format)
        daily_sheet.write_formula(total_row, 10, f'=J{total_row+1}/I{total_row+1}', percent_format)
    
    # Close the writer and return the Excel file
    writer.close()
    output.seek(0)
    
    return output

@st.cache_data
def get_user_recommendations(results_with_v2g, results_without_v2g, v2g_price, diesel_price, max_v2g_hours):
    """
    Generate customized recommendations based on optimization results.
    
    Parameters:
    -----------
    results_with_v2g : dict
        Optimization results with V2G
    results_without_v2g : dict
        Optimization results without V2G
    v2g_price : float
        Price of V2G energy in MAD/MWh
    diesel_price : float
        Price of diesel energy in MAD/MWh
    max_v2g_hours : int
        Maximum hours per day to use V2G
        
    Returns:
    --------
    list
        List of recommendation strings
    """
    recommendations = []
    
    # Calculate key metrics
    cost_savings = results_without_v2g['total_cost'] - results_with_v2g['total_cost']
    percent_savings = (cost_savings / results_without_v2g['total_cost']) * 100
    diesel_reduction = results_without_v2g['total_diesel_energy'] - results_with_v2g['total_diesel_energy']
    percent_diesel_reduction = (diesel_reduction / results_without_v2g['total_diesel_energy']) * 100
    
    # Overall V2G effectiveness
    if percent_savings > 15:
        recommendations.append("V2G integration shows substantial cost benefits. Consider increasing V2G capacity for greater savings.")
    elif percent_savings > 5:
        recommendations.append("V2G integration provides moderate cost benefits. Current implementation is effective.")
    else:
        recommendations.append("V2G benefits are minimal with current parameters. Consider adjusting V2G pricing or increasing maximum V2G hours.")
    
    # V2G price optimization
    if v2g_price > diesel_price * 0.15:
        recommendations.append(f"The current V2G price ({v2g_price} MAD/MWh) is relatively high compared to diesel price. Consider negotiating lower V2G rates to increase savings.")
    elif v2g_price < diesel_price * 0.05:
        recommendations.append(f"The current V2G price ({v2g_price} MAD/MWh) is very favorable. Consider increasing V2G utilization.")
    
    # Max V2G hours recommendation
    if max_v2g_hours < 4 and percent_savings > 10:
        recommendations.append(f"Increasing maximum V2G hours from {max_v2g_hours} to {max_v2g_hours+2} could provide additional cost savings.")
    elif max_v2g_hours > 5 and percent_savings < 5:
        recommendations.append(f"Consider reducing maximum V2G hours from {max_v2g_hours} to {max_v2g_hours-2} as current utilization may not be optimal.")
    
    # V2G utilization assessment
    v2g_usage = results_with_v2g['v2g_used']
    peak_v2g_usage = max(v2g_usage) if len(v2g_usage) > 0 else 0
    avg_v2g_usage = np.mean(v2g_usage[v2g_usage > 0]) if sum(v2g_usage > 0) > 0 else 0
    
    if peak_v2g_usage > 0 and avg_v2g_usage / peak_v2g_usage < 0.5:
        recommendations.append("V2G usage is inconsistent. Consider optimizing the availability schedule to better match peak demand periods.")
    
    return recommendations