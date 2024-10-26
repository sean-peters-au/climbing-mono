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
    load_time_series_plot = generate_load_time_series_plot(active_df, recording.id, hold_numbers)
    load_distribution_plot = generate_load_distribution_plot(active_df, hold_numbers)
    
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
            'load_distribution': load_distribution_plot,
        }
    }
    
    return recording_result

def calculate_total_load(df: pd.DataFrame) -> float:
    """
    Calculate the total load in Newtons.
    """
    total_load = df['force_magnitude'].sum()
    return total_load

def calculate_active_duration(active_timestamps: pd.DatetimeIndex) -> pd.Timedelta:
    """
    Calculate the active duration in seconds.
    """
    active_duration = active_timestamps[-1] - active_timestamps[0]
    return active_duration

def calculate_load_per_second(df: pd.DataFrame, active_duration: pd.Timedelta) -> float:
    """
    Calculate the load per second in Newtons per second.
    """
    total_load = df['force_magnitude'].sum()
    total_seconds = active_duration.total_seconds()
    if total_seconds > 0:
        load_per_second = total_load / total_seconds
    else:
        load_per_second = 0
    return load_per_second

def calculate_peak_load(df: pd.DataFrame) -> float:
    """
    Calculate the peak load in Newtons.
    """
    peak_load = df['force_magnitude'].max()
    return peak_load

def calculate_average_load_per_hold(df: pd.DataFrame, hold_numbers: dict) -> pd.Series:
    """
    Calculate the average load per hold in Newtons.
    """
    avg_load_per_hold = df.groupby('hold_id')['force_magnitude'].mean()
    avg_load_per_hold.rename(index=hold_numbers, inplace=True)
    return avg_load_per_hold

def calculate_load_distribution(df: pd.DataFrame, hold_numbers: dict) -> pd.Series:
    """
    Calculate the load distribution as a percentage of total load per hold.
    """
    total_load = df['force_magnitude'].sum()
    load_per_hold = df.groupby('hold_id')['force_magnitude'].sum()
    load_distribution = load_per_hold / total_load
    load_distribution.rename(index=hold_numbers, inplace=True)
    return load_distribution

def calculate_peak_load_rate(df: pd.DataFrame) -> float:
    """
    Calculate the peak load rate in Newtons per second.
    """
    # Calculate load difference between consecutive timestamps
    df_sorted = df.sort_values('timestamp')
    df_sorted['total_force'] = df_sorted.groupby('timestamp')['force_magnitude'].transform('sum')
    df_time = df_sorted[['timestamp', 'total_force']].drop_duplicates()
    df_time['load_rate'] = df_time['total_force'].diff() / 0.1  # Assuming 10 Hz data, so dt = 0.1s
    peak_load_rate = df_time['load_rate'].max()
    return peak_load_rate

def extract_hold_engagement_sequence(df: pd.DataFrame, hold_numbers: dict) -> list[int]:
    """
    Extract the hold engagement sequence.
    """
    hold_engagement = df[df['force_magnitude'] > 0].groupby('hold_id')['timestamp'].min()
    hold_sequence = hold_engagement.sort_values().index.tolist()
    hold_sequence_numbers = [hold_numbers[hold_id] for hold_id in hold_sequence]
    return hold_sequence_numbers

def generate_load_time_series_plot(df: pd.DataFrame, recording_id: str, hold_numbers: dict) -> dict:
    """
    Generate a plot of the total load (N) over time.
    """
    # Map hold IDs to hold numbers for readability
    df['hold_number'] = df['hold_id'].map(hold_numbers)

    # Prepare data for individual holds
    df_holds = df.groupby(['timestamp', 'hold_number'])['force_magnitude'].sum().reset_index()

    # Prepare data for total load
    df_total = df.groupby('timestamp')['force_magnitude'].sum().reset_index()
    df_total['hold_number'] = 'Total Load'

    # Combine data
    df_combined = pd.concat([df_holds, df_total], ignore_index=True)

    # Create the line plot
    fig = px.line(
        df_combined,
        x='timestamp',
        y='force_magnitude',
        color='hold_number',
        title='Load on Each Hold Over Time',
        labels={
            'timestamp': 'Time (s)',
            'force_magnitude': 'Load (N)',
            'hold_number': 'Hold'
        }
    )

    # Update layout to match frontend style
    fig.update_layout(
        template='plotly_dark',
        title_font=dict(size=20),
        legend_title_text='Hold Number',
        font=dict(size=12),
        plot_bgcolor='#111111',
        paper_bgcolor='#111111',
        xaxis=dict(showgrid=False, linewidth=2, linecolor='#a2a2a2'),
        yaxis=dict(showgrid=False, linewidth=2, linecolor='#a2a2a2'),
        legend=dict(
            bgcolor='#111111',
            bordercolor='#a2a2a2',
            borderwidth=1
        )
    )

    # Update axes lines and ticks
    fig.update_xaxes(
        showline=True,
        mirror=True,
        ticks='outside',
        tickwidth=2,
        tickcolor='#a2a2a2',
        ticklen=5
    )
    fig.update_yaxes(
        showline=True,
        mirror=True,
        ticks='outside',
        tickwidth=2,
        tickcolor='#a2a2a2',
        ticklen=5
    )

    plot_dict = fig.to_json()
    return plot_dict

def generate_load_distribution_plot(df: pd.DataFrame, hold_numbers: dict) -> dict:
    """
    Generate a plot of the load distribution across holds over time.
    """
    # Map hold IDs to hold numbers
    df['hold_number'] = df['hold_id'].map(hold_numbers)

    # Calculate load per hold and total load at each timestamp
    df_load = df.groupby(['timestamp', 'hold_number'])['force_magnitude'].sum().reset_index()
    df_total_load = df.groupby('timestamp')['force_magnitude'].sum().reset_index()
    df_total_load.rename(columns={'force_magnitude': 'total_force'}, inplace=True)

    # Merge to calculate percentage
    df_load = df_load.merge(df_total_load, on='timestamp')
    df_load['load_percentage'] = (df_load['force_magnitude'] / df_load['total_force']) * 100

    # Create area plot for load distribution
    fig = px.area(
        df_load,
        x='timestamp',
        y='load_percentage',
        color='hold_number',
        title='Load Distribution Across Holds Over Time',
        labels={
            'timestamp': 'Time (s)',
            'load_percentage': 'Load Distribution (%)',
            'hold_number': 'Hold'
        },
        groupnorm=None
    )

    # Update layout to match frontend style
    fig.update_layout(
        template='plotly_dark',
        title_font=dict(size=20),
        legend_title_text='Hold Number',
        font=dict(size=12),
        plot_bgcolor='#111111',
        paper_bgcolor='#111111',
        xaxis=dict(showgrid=False, linewidth=2, linecolor='#a2a2a2'),
        yaxis=dict(showgrid=False, linewidth=2, linecolor='#a2a2a2'),
        legend=dict(
            bgcolor='#111111',
            bordercolor='#a2a2a2',
            borderwidth=1
        )
    )

    # Update axes lines and ticks
    fig.update_xaxes(
        showline=True,
        mirror=True,
        ticks='outside',
        tickwidth=2,
        tickcolor='#a2a2a2',
        ticklen=5
    )
    fig.update_yaxes(
        showline=True,
        mirror=True,
        ticks='outside',
        tickwidth=2,
        tickcolor='#a2a2a2',
        ticklen=5
    )

    plot_dict = fig.to_json()
    return plot_dict

def _get_hold_numbers(holds: list[business.models.holds.HoldModel]):
    holds.sort(key=lambda x: (x.bbox[1], x.bbox[0]))
    hold_numbers = {hold.id: index + 1 for index, hold in enumerate(holds)}
    return hold_numbers
