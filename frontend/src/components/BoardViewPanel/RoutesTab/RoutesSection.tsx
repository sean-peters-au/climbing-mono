import React from 'react';
import { Box, Button } from '@mui/material';
import RoutesList from './RoutesList';
import { Route } from '../../../types';

interface RoutesSectionProps {
  wallId: string;
  selectedRoute: Route | null;
  onRouteSelect: (route: Route | null) => void;
}

const RoutesSection: React.FC<RoutesSectionProps> = ({
  wallId,
  selectedRoute,
  onRouteSelect,
}) => {
  const handleCreateRoute = () => {
    // Navigate to create route page or open a modal
    console.log('Create Route Clicked');
  };

  return (
    <Box>
      <Button
        variant="contained"
        color="primary"
        onClick={handleCreateRoute}
        sx={{ mb: 2 }}
      >
        Create Route
      </Button>
      <RoutesList
        wallId={wallId}
        selectedRoute={selectedRoute}
        onRouteSelect={onRouteSelect}
      />
    </Box>
  );
};

export default RoutesSection;