import React, { useContext, useState } from 'react';
import { 
  Box, 
  Typography, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import RouteRecordings from './RouteRecordings';
import { SingleAnalysis } from './RecordingAnalysis/SingleAnalysis';
import { BoardViewContext } from '../BoardViewContext';
import { ComparisonAnalysis } from './RecordingAnalysis/ComparisonAnalysis';

const BetaAnalysisSection: React.FC = () => {
  const { selectedRoute } = useContext(BoardViewContext)!;
  const [selectedRecordingIds, setSelectedRecordingIds] = useState<string[]>([]);
  const [expandedPanel, setExpandedPanel] = useState<string | false>('recordings');

  const handleAccordionChange = (panel: string) => (
    _event: React.SyntheticEvent,
    isExpanded: boolean
  ) => {
    setExpandedPanel(isExpanded ? panel : false);
  };

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
    <Box sx={{ margin: 0 }}>
      {/* Recordings Section */}
      <Accordion 
        expanded={expandedPanel === 'recordings'}
        onChange={handleAccordionChange('recordings')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>
            Recordings ({selectedRecordingIds.length} selected)
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <RouteRecordings
            route={selectedRoute}
            selectedRecordingIds={selectedRecordingIds}
            setSelectedRecordingIds={setSelectedRecordingIds}
          />
        </AccordionDetails>
      </Accordion>

      {/* Individual Recording Analysis */}
      {selectedRecordingIds.map((recordingId) => (
        <Accordion
          key={recordingId}
          expanded={expandedPanel === `recording-${recordingId}`}
          onChange={handleAccordionChange(`recording-${recordingId}`)}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Recording {recordingId} Analysis</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <SingleAnalysis 
              selectedRecordingIds={[recordingId]}
            />
          </AccordionDetails>
        </Accordion>
      ))}

      {/* Comparison Analysis */}
      {selectedRecordingIds.length > 1 && (
        <Accordion
          expanded={expandedPanel === 'comparison'}
          onChange={handleAccordionChange('comparison')}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Comparison Analysis</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <ComparisonAnalysis recordingIds={selectedRecordingIds} />
          </AccordionDetails>
        </Accordion>
      )}
    </Box>
  );
};

export default BetaAnalysisSection;