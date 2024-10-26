import React from 'react';
import { Box } from '@mui/material';
import { AnalysisDetails } from './RecordingAnalysisDetailed';
import { RecordingAnalysisSummary } from './RecordingAnalysisSummary';

interface RecordingAnalysisProps {
  recordingIds: string[];
  isSummary: boolean;
}

export const RecordingAnalysis: React.FC<RecordingAnalysisProps> = ({
  recordingIds,
  isSummary
}) => {
  if (isSummary) {
    return (
      <Box>
        <RecordingAnalysisSummary recordingIds={recordingIds} />
      </Box>
    );
  }
  else {
    return (
      <Box>
        <AnalysisDetails selectedRecordingIds={recordingIds} />
      </Box>
    );
  }
};
