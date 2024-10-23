import React from 'react';
import { Box } from '@mui/material';
import RoutesList from './RoutesList';
import { Route } from '../../../types';

interface RoutesSectionProps {
  wallId: string;
  selectedHolds: string[];
  setSelectedHolds: (holds: string[]) => void;
  selectedRoute: Route | null;
  onRouteSelect: (route: Route | null) => void;
}

const RoutesSection: React.FC<RoutesSectionProps> = ({
  wallId,
  selectedHolds,
  selectedRoute,
  onRouteSelect,
}) => {
  return (
    <Box>
      <RoutesList
        wallId={wallId}
        selectedRoute={selectedRoute}
        onRouteSelect={onRouteSelect}
        selectedHolds={selectedHolds}
      />
    </Box>
  );
};

export default RoutesSection;