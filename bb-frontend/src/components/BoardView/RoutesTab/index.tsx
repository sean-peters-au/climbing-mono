import React, { useState, useContext } from 'react';
import {
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import RoutesSection from './RoutesSection';
import BetaAnalysisSection from './BetaAnalysisSection';

const RoutesTab: React.FC = () => {

  const [expanded, setExpanded] = useState<string | false>('routes');

  const handleAccordionChange =
    (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
      setExpanded(isExpanded ? panel : false);
    };

  return (
    <Box>
      {/* Accordion for Routes */}
      <Accordion
        expanded={expanded === 'routes'}
        onChange={handleAccordionChange('routes')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography sx={{ fontSize: '1.8rem' }}>
            Routes
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <RoutesSection />
        </AccordionDetails>
      </Accordion>

      {/* Accordion for Beta & Analysis */}
      <Accordion
        expanded={expanded === 'beta'}
        onChange={handleAccordionChange('beta')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography sx={{ fontSize: '1.8rem' }}>
            Beta & Analysis
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <BetaAnalysisSection />
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default RoutesTab;
