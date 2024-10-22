import React, { useState } from 'react';
import { Box } from '@mui/material';
import RoutesList from './RoutesList';
import RouteDetail from './RouteDetail';
import RouteRecordings from './RouteRecordings';
import { Route, Hold, Recording, SensorReadingFrame } from '../../types';

interface RoutesPanelProps {
  wallId: string;
  holds: Hold[];
  selectedHolds: string[];
  setSelectedHolds: (holds: string[]) => void;
  setPlaybackData: (data: SensorReadingFrame[] | null) => void; // Updated prop
}

const RoutesPanel: React.FC<RoutesPanelProps> = ({
  wallId,
  holds,
  selectedHolds,
  setSelectedHolds,
  setPlaybackData,
}) => {
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);
  const [recordings, setRecordings] = useState<Recording[]>([]);

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
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Routes List (Top 1/3) */}
      <Box sx={{ flex: '1 1 33%', overflow: 'auto' }}>
        <RoutesList
          wallId={wallId}
          selectedRoute={selectedRoute}
          onRouteSelect={handleRouteSelect}
        />
      </Box>

      {/* Route Detail (Middle 1/3) */}
      <Box sx={{ flex: '1 1 33%', overflow: 'auto', borderTop: 1, borderColor: 'divider' }}>
        <RouteDetail route={selectedRoute} />
      </Box>

      {/* Route Recordings (Bottom 1/3) */}
      <Box sx={{ flex: '1 1 33%', overflow: 'auto', borderTop: 1, borderColor: 'divider' }}>
        <RouteRecordings
          route={selectedRoute}
          recordings={recordings}
          setRecordings={setRecordings}
          holds={holds}
          setPlaybackData={setPlaybackData} // Pass the setter function
        />
      </Box>
    </Box>
  );
};

export default RoutesPanel;