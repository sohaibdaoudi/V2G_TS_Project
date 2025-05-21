import numpy as np
import cvxpy as cp
import streamlit as st

def optimize_with_v2g(load_pred, solar_pred, v2g_pred, hours, v2g_price=200, diesel_price=2500, max_v2g_hours=3):
    """
    Optimize energy usage with V2G integration.
    
    Parameters:
    -----------
    load_pred : array-like
        Predicted load values
    solar_pred : array-like
        Predicted solar generation values
    v2g_pred : array-like
        Predicted V2G availability values
    hours : int
        Number of hours to optimize
    v2g_price : float
        Price of V2G energy in MAD/MWh
    diesel_price : float
        Price of diesel energy in MAD/MWh
    max_v2g_hours : int
        Maximum hours per day to use V2G
        
    Returns:
    --------
    dict
        Optimization results
    """
    # Display optimization information
    with st.expander("Optimization Details", expanded=False):
        st.markdown("""
        ### Optimization Problem
        
        The objective is to minimize the total cost of energy while meeting demand:
        
        **Objective Function**:
        - Minimize: Diesel Cost + V2G Cost
        
        **Constraints**:
        - Energy balance: Solar + V2G + Diesel ≥ Load (for each hour)
        - Solar availability: Solar used ≤ Solar generated (for each hour)
        - V2G availability: V2G used ≤ V2G available (for each hour)
        - V2G usage: Maximum of {} hours per day
        
        **Decision Variables**:
        - Solar energy used (each hour)
        - V2G energy used (each hour)
        - Diesel energy used (each hour)
        """.format(max_v2g_hours))
    
    try:
        # Decision variables
        solar_used = cp.Variable(hours, nonneg=True)
        v2g_used = cp.Variable(hours, nonneg=True)
        diesel_used = cp.Variable(hours, nonneg=True)
        
        # Objective function: Minimize total cost
        total_cost = (cp.sum(diesel_used) * diesel_price + cp.sum(cp.multiply(v2g_used, v2g_price)))
        objective = cp.Minimize(total_cost)
        
        # Constraints
        constraints = []
        
        for t in range(hours):
            constraints.append(solar_used[t] + v2g_used[t] + diesel_used[t] >= load_pred[t])
            constraints.append(solar_used[t] <= solar_pred[t])
            constraints.append(v2g_used[t] <= v2g_pred[t])
        
        # V2G constraint: use only max_v2g_hours hours per day max
        v2g_binary = cp.Variable((hours,), boolean=True)
        M = 1000  # Big-M value
        
        for t in range(hours):
            constraints.append(v2g_used[t] <= M * v2g_binary[t])
        
        days = (hours + 23) // 24  # Calculate full days, rounding up
        for d in range(days):
            day_start = d * 24
            day_end = min((d + 1) * 24, hours)  # Ensure we don't go beyond the hours limit
            constraints.append(cp.sum(v2g_binary[day_start:day_end]) <= max_v2g_hours)
        
        # Solve the problem
        problem = cp.Problem(objective, constraints)
        
        # Try different solvers
        solver_status = "Failed"
        solver_tried = []
        
        for solver in [cp.ECOS_BB, cp.CBC, cp.GLPK_MI]:
            solver_name = str(solver).split('.')[-1]
            solver_tried.append(solver_name)
            
            try:
                if solver == cp.ECOS_BB:
                    result = problem.solve(solver=solver, abstol=1e-4, reltol=1e-4, feastol=1e-4)
                else:
                    result = problem.solve(solver=solver)
                
                if problem.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
                    solver_status = f"Solved with {solver_name}"
                    break
            except Exception as e:
                continue
        
        if problem.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
            return {
                'status': solver_status,
                'solar_used': solar_used.value,
                'v2g_used': v2g_used.value,
                'diesel_used': diesel_used.value,
                'total_diesel_energy': float(np.sum(diesel_used.value)),
                'total_diesel_cost': float(np.sum(diesel_used.value) * diesel_price),
                'total_v2g_energy': float(np.sum(v2g_used.value)),
                'total_v2g_cost': float(np.sum(v2g_used.value) * v2g_price),
                'total_cost': float(problem.value)
            }
        else:
            st.error(f"Optimization failed with all solvers: {', '.join(solver_tried)}. Status: {problem.status}")
            
            # Fall back to a simpler heuristic optimization
            return heuristic_optimize_with_v2g(load_pred, solar_pred, v2g_pred, hours, v2g_price, diesel_price, max_v2g_hours)
            
    except Exception as e:
        st.error(f"Error in optimization: {e}")
        return heuristic_optimize_with_v2g(load_pred, solar_pred, v2g_pred, hours, v2g_price, diesel_price, max_v2g_hours)

def heuristic_optimize_with_v2g(load_pred, solar_pred, v2g_pred, hours, v2g_price, diesel_price, max_v2g_hours):
    """
    Perform a simplified heuristic optimization as a fallback when CVXPY fails.
    
    This uses a greedy approach to decide when to use V2G.
    """
    solar_used = np.minimum(solar_pred, load_pred)
    remaining_load = load_pred - solar_used
    
    # Find the hours with highest load for each day to prioritize V2G usage
    v2g_used = np.zeros(hours)
    diesel_used = np.zeros(hours)
    
    days = (hours + 23) // 24
    for d in range(days):
        day_start = d * 24
        day_end = min((d + 1) * 24, hours)
        
        # Get this day's remaining load and available V2G
        day_load = remaining_load[day_start:day_end].flatten()
        day_v2g = v2g_pred[day_start:day_end].flatten()
        
        # Find the hours with highest load-to-v2g ratio
        # (only consider hours where v2g is available)
        ratios = np.zeros(len(day_load))
        for i in range(len(day_load)):
            if day_v2g[i] > 0:
                ratios[i] = day_load[i] / day_v2g[i]
            else:
                ratios[i] = 0
        
        # Get indices of top hours by ratio
        if len(ratios) > 0 and max(ratios) > 0:
            top_hours = np.argsort(ratios)[-max_v2g_hours:]
            
            # Use V2G for these hours
            for h in top_hours:
                if h < len(day_load) and day_load[h] > 0:
                    hour_idx = day_start + h
                    v2g_amount = min(remaining_load[hour_idx], v2g_pred[hour_idx])
                    v2g_used[hour_idx] = v2g_amount
                    remaining_load[hour_idx] -= v2g_amount
    
    # Use diesel for any remaining load
    diesel_used = remaining_load
    
    # Calculate costs
    total_diesel_energy = float(np.sum(diesel_used))
    total_diesel_cost = total_diesel_energy * diesel_price
    total_v2g_energy = float(np.sum(v2g_used))
    total_v2g_cost = total_v2g_energy * v2g_price
    total_cost = total_diesel_cost + total_v2g_cost
    
    st.warning("Using heuristic optimization as fallback method.")
    
    return {
        'status': 'Solved with heuristic method',
        'solar_used': solar_used.flatten(),
        'v2g_used': v2g_used.flatten(),
        'diesel_used': diesel_used.flatten(),
        'total_diesel_energy': total_diesel_energy,
        'total_diesel_cost': total_diesel_cost,
        'total_v2g_energy': total_v2g_energy,
        'total_v2g_cost': total_v2g_cost,
        'total_cost': total_cost
    }

def optimize_without_v2g(load_pred, solar_pred, hours, diesel_price=2500):
    """
    Optimize energy usage without V2G integration.
    
    Parameters:
    -----------
    load_pred : array-like
        Predicted load values
    solar_pred : array-like
        Predicted solar generation values
    hours : int
        Number of hours to optimize
    diesel_price : float
        Price of diesel energy in MAD/MWh
        
    Returns:
    --------
    dict
        Optimization results
    """
    try:
        # Decision variables
        solar_used = cp.Variable(hours, nonneg=True)
        diesel_used = cp.Variable(hours, nonneg=True)
        
        # Objective function: Minimize total cost
        total_cost = cp.sum(diesel_used) * diesel_price
        objective = cp.Minimize(total_cost)
        
        # Constraints
        constraints = []
        
        for t in range(hours):
            constraints.append(solar_used[t] + diesel_used[t] >= load_pred[t])
            constraints.append(solar_used[t] <= solar_pred[t])
        
        # Solve the problem
        problem = cp.Problem(objective, constraints)
        
        solver_status = "Failed"
        solver_tried = []
        
        # Try different solvers
        for solver in [cp.ECOS, cp.CBC, cp.GLPK]:
            solver_name = str(solver).split('.')[-1]
            solver_tried.append(solver_name)
            
            try:
                result = problem.solve(solver=solver)
                
                if problem.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
                    solver_status = f"Solved with {solver_name}"
                    break
            except Exception as e:
                continue
        
        if problem.status in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
            return {
                'status': solver_status,
                'solar_used': solar_used.value,
                'diesel_used': diesel_used.value,
                'total_diesel_energy': float(np.sum(diesel_used.value)),
                'total_diesel_cost': float(np.sum(diesel_used.value) * diesel_price),
                'total_cost': float(problem.value)
            }
        else:
            st.error(f"Optimization without V2G failed with all solvers: {', '.join(solver_tried)}. Status: {problem.status}")
            # Fall back to a simplified optimization
            return heuristic_optimize_without_v2g(load_pred, solar_pred, hours, diesel_price)
            
    except Exception as e:
        st.error(f"Error in optimization without V2G: {e}")
        return heuristic_optimize_without_v2g(load_pred, solar_pred, hours, diesel_price)

def heuristic_optimize_without_v2g(load_pred, solar_pred, hours, diesel_price):
    """
    Perform a simplified heuristic optimization as a fallback when CVXPY fails.
    
    This uses a straightforward greedy approach to maximize solar usage.
    """
    # Use as much solar as possible
    solar_used = np.minimum(solar_pred, load_pred)
    
    # Use diesel for the remaining load
    diesel_used = load_pred - solar_used
    
    # Calculate costs
    total_diesel_energy = float(np.sum(diesel_used))
    total_diesel_cost = total_diesel_energy * diesel_price
    
    st.warning("Using heuristic optimization (without V2G) as fallback method.")
    
    return {
        'status': 'Solved with heuristic method',
        'solar_used': solar_used.flatten(),
        'diesel_used': diesel_used.flatten(),
        'total_diesel_energy': total_diesel_energy,
        'total_diesel_cost': total_diesel_cost,
        'total_cost': total_diesel_cost
    }