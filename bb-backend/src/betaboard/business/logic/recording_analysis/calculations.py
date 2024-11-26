import pandas as pd

def calculate_total_load(df: pd.DataFrame):
    """
    Calculates the total load of the recording.
    """
    return float(df['force_magnitude'].fillna(0).sum())

def calculate_active_duration(df: pd.DataFrame, frame_rate: float):
    """
    Calculates the active duration of the recording.
    """
    frames = df['frame'].fillna(0).unique()
    return float(len(frames) * (1 / frame_rate))

def calculate_load_per_second(df: pd.DataFrame, frame_rate: float):
    """
    Calculates the load per second of the recording.
    """
    total_load = calculate_total_load(df)
    active_duration = calculate_active_duration(df, frame_rate)
    return total_load / active_duration if active_duration > 0 else 0.0

def calculate_peak_load(df: pd.DataFrame):
    """
    Calculates the peak load of the recording.
    """
    return float(df['force_magnitude'].fillna(0).max())

def calculate_peak_load_rate(df: pd.DataFrame, frame_rate: float):
    """
    Calculates the peak load rate of the recording i.e the highest acceleration of the load.
    """
    peak_load = calculate_peak_load(df)
    return peak_load / frame_rate if frame_rate > 0 else 0.0

def calculate_average_load_per_hold(df: pd.DataFrame, hold_numbers: dict):
    """
    Calculates the average load per hold of the recording.
    """
    avg_loads = df.groupby('hold_id')['force_magnitude'].mean().reset_index()
    avg_loads['hold_number'] = avg_loads['hold_id'].astype(str).map(hold_numbers)
    
    # Convert DataFrame to list of dicts with native Python types
    records = avg_loads.to_dict('records')
    for record in records:
        record['force_magnitude'] = float(record['force_magnitude'])
        record['hold_number'] = int(record['hold_number'])
    return records

def calculate_overall_stability(df: pd.DataFrame, frame_rate: float):
    """
    Calculates the overall stability of the recording by measuring the average
    load velocity (rate of change in force) across all holds.
    A lower value indicates more stable climbing.
    Returns the average absolute load velocity in N/s.
    """
    # Calculate load velocity for each hold
    df = df.copy()
    df['load_velocity'] = df.groupby('hold_id')['force_magnitude'].diff() * frame_rate
    df['load_velocity'] = df['load_velocity'].abs()  # Take absolute value of velocity
    
    # Calculate mean velocity across all holds and frames
    mean_velocity = float(df['load_velocity'].fillna(0).mean())
    return mean_velocity

def calculate_energy_expenditure(df: pd.DataFrame, frame_rate: float, climber_mass: float = 60.0):
    """
    Calculates the total energy expenditure during the climb using:
    1. Work against gravity (mgh) where h is derived from vertical force components
    2. Work done in maintaining holds (force-time integral)
    
    Returns the total energy expenditure in Joules (J).
    """
    df = df.copy()
    g = 9.81  # gravitational acceleration in m/s²
    dt = 1.0 / frame_rate
    
    # Calculate vertical force component (y component represents vertical force)
    vertical_force = df['y'].fillna(0)
    
    # Estimate vertical displacement from force and mass
    # F = ma, so a = F/m
    vertical_acceleration = vertical_force / climber_mass
    
    # Calculate displacement: d = 1/2 * a * t²
    df['vertical_displacement'] = 0.5 * vertical_acceleration * (dt ** 2)
    
    # Calculate potential energy change: PE = mgh
    potential_energy = climber_mass * g * df['vertical_displacement'].sum()
    
    # Calculate work done in maintaining holds (force-time integral)
    hold_work = df['force_magnitude'].fillna(0).sum() * dt
    
    # Total energy is sum of potential energy and hold work
    total_energy = float(potential_energy + hold_work)
    return total_energy

def calculate_energy_expenditure_rate(df: pd.DataFrame, frame_rate: float, climber_mass: float = 60.0):
    """
    Calculates the rate of energy expenditure (power output) during the climb.
    Power = Energy/time
    Returns the power output in Watts (J/s).
    """
    energy = calculate_energy_expenditure(df, frame_rate, climber_mass)
    active_duration = calculate_active_duration(df, frame_rate)
    return energy / active_duration if active_duration > 0 else 0.0
