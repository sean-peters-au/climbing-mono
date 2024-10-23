// frontend/src/components/BoardViewPanel/RoutesTab/BetaAnalysisSection.tsx

import React, { useState } from 'react';
import { Box, Typography, Divider } from '@mui/material';
import RouteRecordings from './RouteRecordings';
import AnalysisDetails from './AnalysisDetails';
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
  const [selectedRecordingIds, setSelectedRecordingIds] = useState<string[]>([]);

  if (!route) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body1">Select a route to view beta and analysis.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Recordings
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <RouteRecordings
        route={route}
        holds={holds}
        setPlaybackData={setPlaybackData}
        selectedRecordingIds={selectedRecordingIds}
        setSelectedRecordingIds={setSelectedRecordingIds}
      />

      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        Analysis
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <AnalysisDetails
        selectedRecordingIds={selectedRecordingIds}
        holds={holds}
        route={route}
      />
    </Box>
  );
};

export default BetaAnalysisSection;