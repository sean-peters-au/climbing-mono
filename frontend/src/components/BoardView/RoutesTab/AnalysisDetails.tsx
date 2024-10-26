// frontend/src/components/BoardView/RoutesTab/AnalysisDetails.tsx

import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import API from '../../../services/api';
import { Route } from '../../../types';
import Plot from 'react-plotly.js';
import Plotly from 'plotly.js';

interface AnalysisDetailsProps {
  selectedRecordingIds: string[];
  route: Route;
}

interface AnalysisResult {
  recording_id: string;
  total_load: number;
  active_duration: number;
  total_load_per_second: number;
  peak_load: number;
  average_load_per_hold: { [holdNumber: string]: number };
  load_distribution: { [holdNumber: string]: number };
  peak_load_rate: number;
  hold_engagement_sequence: number[];
  plots: {
    load_time_series: {
      data: Plotly.Data[];
      layout: Partial<Plotly.Layout>;
    };
    load_distribution: {
      data: Plotly.Data[];
      layout: Partial<Plotly.Layout>;
    };
  };
}

const AnalysisDetails: React.FC<AnalysisDetailsProps> = ({
  selectedRecordingIds,
}) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedRecordingIds.length === 0) {
      setAnalysisResults(null);
      return;
    }

    const fetchAnalysis = async () => {
      setLoading(true);
      try {
        const response = await API.post('/recording/analysis', {
          recording_ids: selectedRecordingIds,
        });
        setAnalysisResults(response.data.analysis_results.recordings);
        setError(null);
      } catch (err) {
        console.error('Error fetching analysis:', err);
        setError('Failed to fetch analysis.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [selectedRecordingIds]);

  if (loading) {
    return (
      <Box sx={{ mt: 2 }}>
        <CircularProgress />
        <Typography>Loading analysis...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 2 }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  if (!analysisResults) {
    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="body1">Select recordings to view analysis.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 2 }}>
      {analysisResults.map((result) => {
        // Parse plots if they are JSON strings
        const loadTimeSeriesPlot =
          typeof result.plots.load_time_series === 'string'
            ? JSON.parse(result.plots.load_time_series)
            : result.plots.load_time_series;

        const loadDistributionPlot = result.plots.load_distribution;

        return (
          <Box key={result.recording_id} sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Analysis for Recording ID: {result.recording_id}
            </Typography>
            <Typography>Total Load: {result.total_load.toFixed(2)} N</Typography>
            <Typography>
              Duration: {result.active_duration.toFixed(2)} seconds
            </Typography>
            <Typography>
              Total Load Per Second: {result.total_load_per_second.toFixed(2)} N/s
            </Typography>
            <Typography>Peak Load: {result.peak_load.toFixed(2)} N</Typography>

            <Typography>
              Peak Load Rate (Load Acceleration): {result.peak_load_rate.toFixed(2)} N/s
            </Typography>

            {/* Display Hold Engagement Sequence */}
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
              Hold Engagement Sequence:
            </Typography>
            <Typography>{result.hold_engagement_sequence.join(' ➔ ')}</Typography>

            {/* Display Load Time Series Plot */}
            <Box sx={{ mt: 4 }}>
              <Typography variant="subtitle1" gutterBottom>
                Load on Each Hold Over Time
              </Typography>
              <Plot
                data={loadTimeSeriesPlot.data}
                layout={loadTimeSeriesPlot.layout}
                style={{ width: '100%', height: '400px' }}
                config={{ responsive: true }}
              />
            </Box>

            {/* Display Load Distribution Plot */}
            <Box sx={{ mt: 4 }}>
              <Typography variant="subtitle1" gutterBottom>
                Load Distribution Across Holds Over Time
              </Typography>
              <Plot
                data={loadDistributionPlot.data}
                layout={loadDistributionPlot.layout}
                style={{ width: '100%', height: '400px' }}
                config={{ responsive: true }}
              />
            </Box>
          </Box>
        );
      })}
    </Box>
  );
};

export default AnalysisDetails;
