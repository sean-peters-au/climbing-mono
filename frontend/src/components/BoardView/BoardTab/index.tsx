import React, { useContext, useState } from 'react';
import { Accordion, AccordionDetails, AccordionSummary, Box, Typography } from '@mui/material';
import { BoardViewContext } from '../BoardViewContext';
import BetaAnalysisSection from '../RoutesTab/BetaAnalysisSection';
import RoutesSection from '../RoutesTab/RoutesSection';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

type BoardPanelProps = {};

const BoardPanel: React.FC<BoardPanelProps> = () => {
  const { wall } = useContext(BoardViewContext)!;
  const [expanded, setExpanded] = useState<string | false>('general');

  const handleAccordionChange =
    (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
      setExpanded(isExpanded ? panel : false);
    };

  return (
    <Box>
      {/* General */}
      <Accordion
        expanded={expanded === 'general'}
        onChange={handleAccordionChange('general')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography sx={{ fontSize: '1.5rem' }}>General</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body1">Wall Name: {wall.name}</Typography>
        </AccordionDetails>
      </Accordion>

      {/* Holds */}
      <Accordion
        expanded={expanded === 'beta'}
        onChange={handleAccordionChange('beta')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography sx={{ fontSize: '1.5rem' }}>Holds</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body1">TODO</Typography>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default BoardPanel;