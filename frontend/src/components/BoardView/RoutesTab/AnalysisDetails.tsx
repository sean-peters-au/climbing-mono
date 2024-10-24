// frontend/src/components/BoardView/RoutesTab/AnalysisDetails.tsx

import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import API from '../../../services/api';
import { Route } from '../../../types';

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
  average_load_per_hold: { [hold_id: string]: number };
  load_distribution: { [hold_id: string]: number };
  peak_load_rate: number;
  hold_engagement_sequence: string[];
  plots: {
    load_time_series: any;
    hold_load_time_series: { [hold_id: string]: any };
  };
}

const AnalysisDetails: React.FC<AnalysisDetailsProps> = ({
  selectedRecordingIds,
  route,
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
      {analysisResults.map((result) => (
        <Box key={result.recording_id} sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Analysis for Recording ID: {result.recording_id}
          </Typography>
          <Typography>Total Load Applied to Holds: {result.total_load.toFixed(2)}</Typography>
          <Typography>
            Duration of Load Applied: {result.active_duration.toFixed(2)} seconds
          </Typography>
          <Typography>
            Total Load Applied Per Second: {result.total_load_per_second.toFixed(2)}
          </Typography>
          <Typography>Peak Load: {result.peak_load.toFixed(2)}</Typography>

          {/* Display Average Load Applied to Holds */}
          <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
            Average Load Applied to Holds:
          </Typography>
          <ul>
            {Object.entries(result.average_load_per_hold).map(([holdId, load]) => (
              <li key={holdId}>
                Hold {holdId}: {load.toFixed(2)}
              </li>
            ))}
          </ul>

          {/* Display Load Distribution */}
          <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
            Load Distribution Across Holds:
          </Typography>
          <ul>
            {Object.entries(result.load_distribution).map(([holdId, distribution]) => (
              <li key={holdId}>
                Hold {holdId}: {(distribution * 100).toFixed(2)}%
              </li>
            ))}
          </ul>

          <Typography>
            Peak Load Rate (Load Acceleration): {result.peak_load_rate.toFixed(2)}
          </Typography>

          {/* Display Hold Engagement Sequence */}
          <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
            Hold Engagement Sequence:
          </Typography>
          <Typography>{result.hold_engagement_sequence.join(' ➔ ')}</Typography>

          {/* Add plots if necessary */}
        </Box>
      ))}
    </Box>
  );
};

export default AnalysisDetails;
