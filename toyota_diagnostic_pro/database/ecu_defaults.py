import pandas as pd
import numpy as np

def get_default_maps(model_name, engine_type):
    """
    Returns default ECU maps based on vehicle model and engine type.
    """
    rpm_points = [1000, 2000, 3000, 4000, 5000]
    load_points = [20, 40, 60, 80, 100]
    
    # Default base maps (Standard Toyota)
    fuel_map = pd.DataFrame(np.ones((5, 5)), index=rpm_points, columns=load_points)
    
    ign_map = pd.DataFrame(np.array([
        [15, 12, 10, 8, 5],
        [20, 18, 15, 12, 8],
        [25, 22, 18, 15, 10],
        [30, 26, 22, 18, 12],
        [35, 30, 25, 20, 15]
    ]), index=rpm_points, columns=load_points)
    
    vvt_in_map = pd.DataFrame(np.array([
        [0, 5, 10, 15, 20],
        [5, 15, 25, 35, 45],
        [10, 20, 30, 40, 50],
        [15, 25, 35, 45, 50],
        [20, 30, 40, 50, 50]
    ]), index=rpm_points, columns=load_points)
    
    vvt_ex_map = pd.DataFrame(np.array([
        [0, 2, 5, 8, 10],
        [2, 5, 10, 15, 20],
        [5, 10, 15, 20, 25],
        [8, 15, 20, 25, 30],
        [10, 20, 25, 30, 35]
    ]), index=rpm_points, columns=load_points)

    # Customizations based on model
    if "Hilux" in model_name or "Fortuner" in model_name:
        if "Diesel" in engine_type or "GD" in engine_type:
            # Diesel specific tuning (higher torque at low RPM, less advance)
            ign_map = ign_map - 5 # Less advance for diesel
            fuel_map.iloc[0:2, :] = 1.1 # Richer at low RPM for torque
        else:
            # TR engine (Gasoline)
            fuel_map.iloc[3:, 3:] = 1.05 # Richer at high load/RPM
            
    elif "Vios" in model_name or "Yaris" in model_name:
        # Small engine tuning (more advance at high RPM)
        ign_map.iloc[3:, :] = ign_map.iloc[3:, :] + 3
        vvt_in_map = vvt_in_map * 0.8 # Less aggressive VVT
        
    elif "Camry" in model_name or "Alphard" in model_name:
        # Luxury/Comfort tuning (smoother transitions)
        vvt_in_map = vvt_in_map * 1.1 # More aggressive VVT for efficiency
        ign_map = ign_map + 2 # Slightly more advance for efficiency

    return {
        "fuel_map": fuel_map,
        "ignition_map": ign_map,
        "vvt_intake_map": vvt_in_map,
        "vvt_exhaust_map": vvt_ex_map
    }
