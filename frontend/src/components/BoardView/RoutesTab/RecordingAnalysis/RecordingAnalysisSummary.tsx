import { Box, Typography } from "@mui/material";

interface RecordingAnalysisSummaryProps {   
  recordingIds: string[];
}

export const RecordingAnalysisSummary: React.FC<RecordingAnalysisSummaryProps> = ({
  recordingIds
}) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Summary Analysis
      </Typography>
      You selected {recordingIds.length} recordings.
    </Box>
  );
};
