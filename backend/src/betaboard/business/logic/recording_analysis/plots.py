import pandas as pd
import plotly.express as px
import numpy as np

def generate_load_time_series_plot(df: pd.DataFrame) -> dict:
    """
    Generates a Plotly figure showing the load over time per hold.
    """
    df = df.fillna(0)
    fig = px.line(
        df,
        x='time',
        y='force_magnitude',
        color='hold_number',
        labels={
            'time': 'Time (s)',
            'force_magnitude': 'Load (N)',
            'hold_number': 'Hold',
        },
    )
    fig = _update_plot_style(fig)
    fig_dict = fig.to_dict()
    return _convert_plotly_dict_to_native(fig_dict)

def generate_load_distribution_plot(df: pd.DataFrame) -> dict:
    """
    Generates a Plotly figure showing the load distribution over time per hold.
    """
    df_total_force = df.groupby('frame')['force_magnitude'].sum().reset_index()
    
    df = df.merge(df_total_force, on='frame', suffixes=('', '_total'))
    df['load_percentage'] = (df['force_magnitude'] / df['force_magnitude_total']) * 100
    df = df.fillna(0)
    
    fig = px.area(
        df,
        x='time',
        y='load_percentage',
        color='hold_number',
        labels={
            'time': 'Time (s)',
            'load_percentage': 'Load Distribution (%)',
            'hold_number': 'Hold',
        },
    )
    fig = _update_plot_style(fig)
    fig_dict = fig.to_dict()
    return _convert_plotly_dict_to_native(fig_dict)

def generate_load_stability_plot(df: pd.DataFrame) -> dict:
    """
    Generates a Plotly figure showing load velocity over time per hold.
    """
    df = df.fillna(0)
    fig = px.line(
        df,
        x='time',
        y='load_velocity',
        color='hold_number',
        labels={
            'time': 'Time (s)',
            'load_velocity': 'Load Velocity (N/s)',
            'hold_number': 'Hold',
        },
    )
    fig = _update_plot_style(fig)
    fig_dict = fig.to_dict()
    return _convert_plotly_dict_to_native(fig_dict)

def _update_plot_style(fig):
    fig.update_layout(
        template='plotly_dark',
        title_font=dict(size=20),
        legend_title_text='Hold',
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
    return fig


def _convert_plotly_dict_to_native(d: dict) -> dict:
    """
    Recursively convert all numpy/pandas types to native Python types.
    """
    if isinstance(d, dict):
        return {k: _convert_plotly_dict_to_native(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [_convert_plotly_dict_to_native(v) for v in d]
    elif isinstance(d, (np.integer, np.floating)):
        return float(d)
    elif isinstance(d, np.ndarray):
        return d.tolist()
    else:
        return d
