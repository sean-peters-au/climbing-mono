import React, { useEffect, useState } from 'react';
import { Box, Typography, Button, List, ListItem, ListItemText } from '@mui/material';
import { Route, Recording, Hold } from '../../types';
import SVGVisualization from '../SVGVisualisation';
import useRecordings from '../../hooks/useRecordings';

interface RouteRecordingsProps {
  route: Route | null;
  recordings: Recording[];
  setRecordings: (recordings: Recording[]) => void;
  holds: Hold[];
}

const RouteRecordings: React.FC<RouteRecordingsProps> = ({
  route,
  recordings,
  setRecordings,
  holds,
}) => {
  const [currentPlayback, setCurrentPlayback] = useState<Recording | null>(null);
  const [playbackData, setPlaybackData] = useState<any>(null);

  const { getRecordings, loading, error } = useRecordings();

  useEffect(() => {
    if (route) {
      fetchRecordings(route.id);
    } else {
      setRecordings([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [route]);

  const fetchRecordings = async (routeId: string) => {
    try {
      const recs = await getRecordings(routeId);
      setRecordings(recs);
    } catch (err) {
      console.error('Error fetching recordings:', err);
    }
  };

  const handlePlayRecording = async (recording: Recording) => {
    setCurrentPlayback(recording);
    try {
      // Fetch playback data (sensor readings)
      const response = await fetch(`/api/recordings/${recording.id}/sensor_readings`);
      const data = await response.json();
      setPlaybackData(data.sensor_readings);
    } catch (error) {
      console.error('Error fetching playback data:', error);
    }
  };

  if (!route) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body1">Select a route to view recordings.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6">Recordings</Typography>
      {loading && <Typography>Loading recordings...</Typography>}
      {error && <Typography>Error loading recordings: {error}</Typography>}
      {recordings.length > 0 ? (
        <List>
          {recordings.map((recording) => (
            <ListItem key={recording.id} disableGutters>
              <ListItemText
                primary={`Recording from ${new Date(recording.start_time).toLocaleString()}`}
              />
              <Button
                variant="outlined"
                size="small"
                onClick={() => handlePlayRecording(recording)}
              >
                Play
              </Button>
            </ListItem>
          ))}
        </List>
      ) : (
        <Typography variant="body2">No recordings available.</Typography>
      )}

      {/* Visualization Component */}
      {currentPlayback && playbackData && (
        <Box mt={2}>
          <Typography variant="h6">Playback Visualization</Typography>
          <SVGVisualization sensorReadings={playbackData} holds={holds} />
        </Box>
      )}
    </Box>
  );
};

export default RouteRecordings;