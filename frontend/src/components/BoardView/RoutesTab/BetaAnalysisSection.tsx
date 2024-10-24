// frontend/src/components/BoardView/RoutesTab/BetaAnalysisSection.tsx

import React, { useContext, useState } from 'react';
import { Box, Typography, Divider } from '@mui/material';
import RouteRecordings from './RouteRecordings';
import AnalysisDetails from './AnalysisDetails';
import { BoardViewContext } from '../BoardViewContext';

const BetaAnalysisSection: React.FC = () => {
  const { selectedRoute } = useContext(BoardViewContext)!;

  const [selectedRecordingIds, setSelectedRecordingIds] = useState<string[]>([]);

  if (!selectedRoute) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body1">
          Select a route to view beta and analysis.
        </Typography>
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
        route={selectedRoute}
        selectedRecordingIds={selectedRecordingIds}
        setSelectedRecordingIds={setSelectedRecordingIds}
      />

      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        Analysis
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <AnalysisDetails
        selectedRecordingIds={selectedRecordingIds}
        route={selectedRoute}
      />
    </Box>
  );
};

export default BetaAnalysisSection;
