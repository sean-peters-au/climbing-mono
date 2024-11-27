import flask

import betaboard.business.models.recordings as recordings_model
import betaboard.business.models.holds as holds_model
import betaboard.business.logic.recording_analysis.plots as plots
import betaboard.business.logic.recording_analysis.prepare as prepare
import betaboard.business.logic.recording_analysis.calculations as calculations
import betaboard.business.logic.recording_analysis.kinematics as kinematics
import betaboard.business.logic.route as route_logic

def analyze_recordings(recordings: list[recordings_model.RecordingModel]):
    """
    Analyzes a list of recordings and returns a dictionary with the analysis results.

    Args:
        recordings (list[recordings_model.RecordingModel]): A list of recordings to analyze.

    Returns:
        dict: A dictionary with the analysis results.
    """
    analysis_results = {
        'recordings': [],
    }
    
    # Perform analysis for each recording
    for recording in recordings:
        recording_result = _analyze_single_recording(recording)
        analysis_results['recordings'].append(recording_result)
    
    # TODO: Perform cross-recording analyses and populate 'comparison' field

    # Then before returning analysis_results:
    analysis_results = _convert_to_native_types(analysis_results)
    return analysis_results

def _analyze_single_recording(recording: recordings_model.RecordingModel):
    # Get route and holds
    route = route_logic.get_route(recording.route_id)
    holds = route.holds
    hold_numbers = _get_hold_numbers(holds)
    
    # Prepare sensor readings
    frame_rate = 10  # Hz
    sensor_readings = recording.sensor_readings
    if not sensor_readings:
        raise ValueError(f"No sensor data for recording ID {recording.id}")
    
    # Base DataFrame
    base_df = prepare.prepare_sensor_dataframe(sensor_readings, frame_rate)
    base_df['hold_number'] = base_df['hold_id'].astype(str).map(hold_numbers)
    
    # Compute key metrics using existing functions
    key_metrics = {
        'active_duration': calculations.calculate_active_duration(base_df, frame_rate),
        'energy_expenditure': calculations.calculate_energy_expenditure(base_df, frame_rate),
        'energy_expenditure_rate': calculations.calculate_energy_expenditure_rate(base_df, frame_rate),
        'peak_load': calculations.calculate_peak_load(base_df),
        'peak_load_rate': calculations.calculate_peak_load_rate(base_df, frame_rate),
        'average_load_per_hold': calculations.calculate_average_load_per_hold(base_df, hold_numbers),
        'overall_stability': calculations.calculate_overall_stability(base_df, frame_rate),
    }
    
    # Prepare DataFrames for each visualization
    df_time_series = base_df.copy()
    df_load_distribution = prepare.prepare_load_percentage(base_df)
    df_load_velocity = prepare.prepare_load_velocity(base_df, frame_rate)
    # Generate plots
    load_time_series_plot = plots.generate_load_time_series_plot(df_time_series)
    load_distribution_plot = plots.generate_load_distribution_plot(df_load_distribution)
    load_velocity_plot = plots.generate_load_stability_plot(df_load_velocity)

    # Build VisualizationData structures
    load_time_series_visualization = _build_visualization_data(
        df=df_time_series,
        frame_rate=frame_rate,
        y_column='force_magnitude',
        plot=load_time_series_plot
    )

    load_distribution_visualization = _build_visualization_data(
        df=df_load_distribution,
        frame_rate=frame_rate,
        y_column='load_percentage',
        plot=load_distribution_plot
    )

    load_stability_visualization = _build_visualization_data(
        df=df_load_velocity,
        frame_rate=frame_rate,
        y_column='load_velocity',
        plot=load_velocity_plot
    )

    # Collect all visualizations
    visualizations = {
        'load_time_series': load_time_series_visualization,
        'load_distribution': load_distribution_visualization,
        'load_stability': load_stability_visualization,
    }

    # Get video data from S3 if available
    kinematics_data = None
    if recording.video_s3_key:
        s3_client = flask.current_app.extensions['s3']
        video_data = s3_client.get_file(recording.video_s3_key)
        
        # Analyze kinematics
        kinematics_data = kinematics.analyze_video(video_data)

    recording_result = {
        'kinematics': kinematics_data,
        'visualizations': visualizations,
        'key_metrics': key_metrics,
    }

    return recording_result

def _get_hold_numbers(holds: list[holds_model.HoldModel]):
    # Assign numbers to holds based on their position
    holds.sort(key=lambda x: (x.bbox[1], x.bbox[0]), reverse=True)
    hold_numbers = {hold.id: index + 1 for index, hold in enumerate(holds)}
    return hold_numbers


def _build_visualization_data(df, frame_rate, y_column, plot):
    """
    Builds visualization playback data using pre-processed DataFrame.
    """
    vector_playbacks = []
    annotation_playbacks = []

    hold_ids = df['hold_id'].unique()
    
    for hold_id in hold_ids:
        hold_df = df[df['hold_id'] == hold_id].reset_index(drop=True)
        vectors = hold_df[['x', 'y']].to_dict('records')
        annotations = hold_df[[y_column]].rename(columns={y_column: 'annotation'}).to_dict('records')

        vector_playbacks.append({
            'hold_id': hold_id,
            'frequency': frame_rate,
            'data': vectors,
        })

        annotation_playbacks.append({
            'hold_id': hold_id,
            'frequency': frame_rate,
            'data': annotations,
        })

    visualization_data = {
        'vector_playbacks': vector_playbacks,
        'annotation_playbacks': annotation_playbacks,
        'plot': plot,
    }

    return visualization_data

def _convert_to_native_types(obj):
    if isinstance(obj, dict):
        return {key: _convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_to_native_types(item) for item in obj]
    elif hasattr(obj, 'dtype'):  # Check if it's a numpy type
        return obj.item()  # Convert to native Python type
    return obj
