import React, { useState } from 'react';
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
import { Route, Hold, SensorReadingFrame } from '../../../types';

interface RoutesPanelProps {
  wallId: string;
  holds: Hold[];
  selectedHolds: string[];
  setSelectedHolds: (holds: string[]) => void;
  setPlaybackData: (data: SensorReadingFrame[] | null) => void;
}

const RoutesPanel: React.FC<RoutesPanelProps> = ({
  wallId,
  holds,
  selectedHolds,
  setSelectedHolds,
  setPlaybackData,
}) => {
  const [expanded, setExpanded] = useState<string | false>('routes');
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);

  const handleAccordionChange =
    (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
      setExpanded(isExpanded ? panel : false);
    };

  const handleRouteSelect = (route: Route | null) => {
    setSelectedRoute(route);
    if (route) {
      setSelectedHolds(route.holds.map((hold) => hold.id));
    } else {
      setSelectedHolds([]);
    }
    setPlaybackData(null); // Reset playback when route changes
  };

  return (
    <Box>
      {/* Accordion for Routes */}
      <Accordion
        expanded={expanded === 'routes'}
        onChange={handleAccordionChange('routes')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography sx={{ fontSize: '1.5rem' }}>1. Routes</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <RoutesSection
            wallId={wallId}
            selectedHolds={selectedHolds}
            setSelectedHolds={setSelectedHolds}
            selectedRoute={selectedRoute}
            onRouteSelect={handleRouteSelect}
          />
        </AccordionDetails>
      </Accordion>

      {/* Accordion for Beta & Analysis */}
      <Accordion
        expanded={expanded === 'beta'}
        onChange={handleAccordionChange('beta')}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography sx={{ fontSize: '1.5rem' }}>2. Beta & Analysis</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <BetaAnalysisSection
            route={selectedRoute}
            holds={holds}
            setPlaybackData={setPlaybackData}
          />
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default RoutesPanel;
