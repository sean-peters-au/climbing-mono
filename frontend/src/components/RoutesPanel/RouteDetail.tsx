import React from 'react';
import { Box, Typography } from '@mui/material';
import { Route } from '../../types';

interface RouteDetailProps {
  route: Route | null;
}

const RouteDetail: React.FC<RouteDetailProps> = ({ route }) => {
  if (!route) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body1">Select a route to see details.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6">Route Details</Typography>
      <Typography variant="body1">
        <strong>Name:</strong> {route.name}
      </Typography>
      <Typography variant="body1">
        <strong>Grade:</strong> {route.grade}
      </Typography>
      <Typography variant="body1">
        <strong>Description:</strong> {route.description}
      </Typography>
      {/* Include additional route details as needed */}
    </Box>
  );
};

export default RouteDetail;