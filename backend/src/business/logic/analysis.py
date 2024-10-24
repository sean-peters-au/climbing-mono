import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio

import business.models.recordings

def perform_recordings_analysis(recordings: list[business.models.recordings.RecordingModel]):
    # Collect all analysis results
    analysis_results = {
        'recordings': []
    }
    
    # Perform analysis for each recording
    for recording in recordings:
        recording_result = analyze_single_recording(recording)
        analysis_results['recordings'].append(recording_result)

    # Perform cross-recording analyses
    # TODO

    # Build plots
    # TODO
    plots = {}
    
    return analysis_results, plots

def analyze_single_recording(recording):
    # Get the holds from the recording's route
    holds = business.logic.route.get_route(recording.route_id).holds
    hold_numbers = _get_hold_numbers(holds)

    # Convert sensor readings to DataFrame
    sensor_data = []
    for frame_index, frame in enumerate(recording.sensor_readings):
        timestamp = recording.start_time + pd.Timedelta(seconds=frame_index * 0.1)  # Assuming 10 Hz
        for reading in frame:
            sensor_data.append({
                'timestamp': timestamp,
                'hold_id': reading.hold_id,
                'x': reading.x,
                'y': reading.y,
            })
    df = pd.DataFrame(sensor_data)
    
    if df.empty:
        raise ValueError(f"No sensor data available for recording ID {recording.id}")
    
    # Calculate the magnitude of force vectors
    df['force_magnitude'] = np.sqrt(df['x']**2 + df['y']**2)
    
    # Filter out non-climbing periods based on a load threshold
    load_threshold = 5  # Define an appropriate threshold based on your data
    active_periods = df.groupby('timestamp')['force_magnitude'].sum() > load_threshold
    active_timestamps = active_periods[active_periods].index
    active_df = df[df['timestamp'].isin(active_timestamps)]
    
    # Perform analyses
    total_load = calculate_total_load(active_df)
    active_duration = calculate_active_duration(active_timestamps)
    total_load_per_second = calculate_load_per_second(active_df, active_duration)
    peak_load = calculate_peak_load(active_df)
    average_load_per_hold = calculate_average_load_per_hold(active_df, hold_numbers)
    load_distribution = calculate_load_distribution(active_df, hold_numbers)
    peak_load_rate = calculate_peak_load_rate(active_df)
    hold_engagement_sequence = extract_hold_engagement_sequence(active_df, hold_numbers)
    
    # Generate plots
    load_time_series_plot = generate_load_time_series_plot(df, recording.id)
    hold_load_time_series_plots = generate_hold_load_time_series_plots(df, recording.id, hold_numbers)
    
    # Package results
    recording_result = {
        'recording_id': recording.id,
        'total_load': total_load,
        'active_duration': active_duration.total_seconds(),
        'total_load_per_second': total_load_per_second,
        'peak_load': peak_load,
        'average_load_per_hold': average_load_per_hold.to_dict(),
        'load_distribution': load_distribution.to_dict(),
        'peak_load_rate': peak_load_rate,
        'hold_engagement_sequence': hold_engagement_sequence,
        'plots': {
            'load_time_series': load_time_series_plot,
            'hold_load_time_series': hold_load_time_series_plots,
        }
    }
    
    return recording_result

# Analysis Functions
def calculate_total_load(df):
    total_load = df['force_magnitude'].sum()
    return total_load

def calculate_active_duration(active_timestamps):
    active_duration = active_timestamps[-1] - active_timestamps[0]
    return active_duration

def calculate_load_per_second(df, active_duration):
    total_load = df['force_magnitude'].sum()
    total_seconds = active_duration.total_seconds()
    if total_seconds > 0:
        load_per_second = total_load / total_seconds
    else:
        load_per_second = 0
    return load_per_second

def calculate_peak_load(df):
    peak_load = df['force_magnitude'].max()
    return peak_load

def calculate_average_load_per_hold(df, hold_numbers):
    avg_load_per_hold = df.groupby('hold_id')['force_magnitude'].mean()
    avg_load_per_hold.rename(index=hold_numbers, inplace=True)
    return avg_load_per_hold

def calculate_load_distribution(df, hold_numbers):
    total_load = df['force_magnitude'].sum()
    load_per_hold = df.groupby('hold_id')['force_magnitude'].sum()
    load_distribution = load_per_hold / total_load
    load_distribution.rename(index=hold_numbers, inplace=True)
    return load_distribution

def calculate_peak_load_rate(df):
    # Calculate load difference between consecutive timestamps
    df_sorted = df.sort_values('timestamp')
    df_sorted['total_force'] = df_sorted.groupby('timestamp')['force_magnitude'].transform('sum')
    df_time = df_sorted[['timestamp', 'total_force']].drop_duplicates()
    df_time['load_rate'] = df_time['total_force'].diff() / 0.1  # Assuming 10 Hz data, so dt = 0.1s
    peak_load_rate = df_time['load_rate'].max()
    return peak_load_rate

def extract_hold_engagement_sequence(df, hold_numbers):
    hold_engagement = df[df['force_magnitude'] > 0].groupby('hold_id')['timestamp'].min()
    hold_sequence = hold_engagement.sort_values().index.tolist()
    hold_sequence_numbers = [hold_numbers[hold_id] for hold_id in hold_sequence]
    return hold_sequence_numbers

# Plotting Functions
def generate_load_time_series_plot(df, recording_id):
    df_time = df.groupby('timestamp')['force_magnitude'].sum().reset_index()
    fig = px.line(df_time, x='timestamp', y='force_magnitude', title=f'Total Load Over Time for Recording {recording_id}')
    fig.update_layout(xaxis_title='Time', yaxis_title='Total Load')
    plot_json = pio.to_json(fig)
    return plot_json

def generate_hold_load_time_series_plots(df, recording_id, hold_numbers):
    hold_plots = {}
    holds = df['hold_id'].unique()
    for hold in holds:
        df_hold = df[df['hold_id'] == hold]
        df_hold_time = df_hold.groupby('timestamp')['force_magnitude'].sum().reset_index()
        hold_number = hold_numbers[hold]
        fig = px.line(
            df_hold_time,
            x='timestamp',
            y='force_magnitude',
            title=f'Load Over Time for Hold {hold_number} in Recording {recording_id}'
        )
        fig.update_layout(xaxis_title='Time', yaxis_title='Load')
        plot_json = pio.to_json(fig)
        hold_plots[hold_number] = plot_json
    return hold_plots

def _get_hold_numbers(holds: list[business.models.holds.HoldModel]):
    holds.sort(key=lambda x: (x.bbox[1], x.bbox[0]))
    hold_numbers = {hold.id: index + 1 for index, hold in enumerate(holds)}
    return hold_numbers
