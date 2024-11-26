import { Box, Table, TableBody, TableCell, TableContainer, TableRow, Typography, Paper } from "@mui/material";
import { RecordingAnalysis } from "../../../../types";

export const KeyMetrics: React.FC<{ recordingAnalysis: RecordingAnalysis }> = ({
  recordingAnalysis,
}) => {
  const metrics = recordingAnalysis.key_metrics;
  if (!metrics) {
    return null;
  }

  const metricsData = [
    { label: "Active Duration", value: `${metrics.active_duration.toFixed(1)}s` },
    { label: "Energy Expenditure", value: `${metrics.energy_expenditure.toFixed(1)}J` },
    { label: "Power Output", value: `${metrics.energy_expenditure_rate.toFixed(1)}W` },
    { label: "Peak Load", value: `${metrics.peak_load.toFixed(1)}N` },
    { label: "Peak Load Rate", value: `${metrics.peak_load_rate.toFixed(1)}N/s` },
    { label: "Average Stability", value: `${metrics.overall_stability.toFixed(1)}N/s` },
  ];

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="subtitle1" gutterBottom>
        Key Metrics
      </Typography>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableBody>
            {metricsData.map((row) => (
              <TableRow key={row.label}>
                <TableCell 
                  component="th" 
                  scope="row"
                  sx={{ 
                    color: 'text.secondary',
                    borderBottom: 'none',
                    width: '50%'
                  }}
                >
                  {row.label}
                </TableCell>
                <TableCell 
                  align="right"
                  sx={{ 
                    borderBottom: 'none',
                    fontWeight: 'medium'
                  }}
                >
                  {row.value}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
