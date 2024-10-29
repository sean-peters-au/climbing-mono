import pandas as pd
import numpy as np

def prepare_sensor_dataframe(sensor_readings, frame_rate):
    """
    Prepares the base DataFrame for sensor analysis.
    """
    data = []
    for frame_index, frame in enumerate(sensor_readings):
        for reading in frame:
            data.append({
                'frame': frame_index,
                'time': frame_index / frame_rate,
                'hold_id': reading.hold_id,
                'x': reading.x,
                'y': reading.y,
                'force_magnitude': np.sqrt(reading.x ** 2 + reading.y ** 2),
            })
    df = pd.DataFrame(data)
    df.fillna(0, inplace=True)
    return df

def prepare_load_percentage(df):
    """
    Prepares the DataFrame for the load percentage visualization.
    """
    df = df.copy()
    total_force_per_frame = df.groupby('frame')['force_magnitude'].transform('sum')
    df['load_percentage'] = (df['force_magnitude'] / total_force_per_frame) * 100
    df['load_percentage'].fillna(0, inplace=True)
    return df

def prepare_load_velocity(df, frame_rate):
    """
    Prepares a DataFrame with a new 'load_velocity' column.

    This is done by calculating the absolute rate of change of force magnitude (load velocity) per hold.
    """
    df = df.copy()
    df['load_velocity'] = df.groupby('hold_id')['force_magnitude'].diff() * frame_rate
    df['load_velocity'].fillna(0, inplace=True)
    df['load_velocity'] = df['load_velocity'].abs()
    return df