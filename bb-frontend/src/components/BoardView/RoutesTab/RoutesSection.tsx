import React, { useContext } from 'react';
import { Box } from '@mui/material';
import RoutesList from './RoutesList';
import { Route } from '../../../types';
import { BoardViewContext } from '../BoardViewContext';

const RoutesSection: React.FC = () => {
  const { wall, selectedRoute, setSelectedRoute, setSelectedHolds } = useContext(BoardViewContext)!;

  const onRouteSelect = (route: Route | null) => {
    setSelectedHolds([]);
    setSelectedRoute(route);
  };

  return (
    <Box>
      <RoutesList
        wallId={wall.id}
        selectedRoute={selectedRoute}
        onRouteSelect={onRouteSelect}
      />
    </Box>
  );
};

export default RoutesSection;