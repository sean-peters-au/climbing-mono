import React from 'react';
import { Box, Typography, Divider } from '@mui/material';
import RouteRecordings from './RouteRecordings';
import { Route, Hold, SensorReadingFrame } from '../../../types';

interface BetaAnalysisSectionProps {
  route: Route | null;
  holds: Hold[];
  setPlaybackData: (data: SensorReadingFrame[] | null) => void;
}

const BetaAnalysisSection: React.FC<BetaAnalysisSectionProps> = ({
  route,
  holds,
  setPlaybackData,
}) => {
  if (!route) {
    return (
      <Typography variant="body1">
        Select a route to view beta and analysis.
      </Typography>
    );
  }

  return (
    <Box>
      {/* Selected Route Information */}
      <Typography variant="h6" gutterBottom>
        Selected Route: {route.name}
      </Typography>

      {/* Recordings Section */}
      <Typography variant="subtitle1" gutterBottom>
        Recordings
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <RouteRecordings
        route={route}
        holds={holds}
        setPlaybackData={setPlaybackData}
      />

      {/* Analysis Section */}
      <Typography variant="subtitle1" gutterBottom sx={{ mt: 4 }}>
        Analysis
      </Typography>
      <Divider sx={{ mb: 2 }} />
      {/* Include your analysis components here */}
      <Typography variant="body2">
        Analysis content will be available soon.
      </Typography>
    </Box>
  );
};

export default BetaAnalysisSection;