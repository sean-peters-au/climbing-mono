import React, { useContext, useState } from 'react';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Typography,
} from '@mui/material';
import { BoardViewContext } from '../BoardViewContext';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DeleteHolds from './DeleteHolds';
import ShowAllHolds from './ShowAllHolds';
import AddDrawnHold from './AddDrawnHold';

type BoardTabProps = {};

const BoardTab: React.FC<BoardTabProps> = () => {
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

      {/* Hold Management */}
      <Accordion
        expanded={expanded === 'holds'}
        onChange={handleAccordionChange('holds')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography sx={{ fontSize: '1.5rem' }}>Hold Management</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: '1' }}>
            <ShowAllHolds />
            <AddDrawnHold />
            <DeleteHolds />
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Other accordions can be added here */}
    </Box>
  );
};

export default BoardTab;
